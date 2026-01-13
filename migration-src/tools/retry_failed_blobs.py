# -*- coding: utf-8 -*-
"""
エラーになったBlobファイルをリトライするスクリプト

対象:
- bkID=4492, filename=003_1.JPG
- bkID=53022 or 53023, filename contains '千種区東山元町2丁目'
"""

import sys
import os
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import ndb
from google.cloud import storage
from application.models.blob import Blob
from application import gcs_utils


# Python 2.7 アプリのベースURL
BASE_URL = os.environ.get('PY27_BASE_URL', 'https://s-style-hrd.appspot.com')


def format_size(size_bytes):
    """バイト数を人間が読みやすい形式に変換"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def generate_object_name_for_blob(blob):
    """Blob エンティティから GCS object name を生成"""
    corp = blob.CorpOrg_key or "_orphan"
    branch = blob.Branch_Key or "_unknown"
    bk_id = blob.bkID or f"_no-bkid-{blob.key.id()}"
    blob_no = blob.blobNo or 0
    ext = blob.fileextension or "bin"
    return gcs_utils.generate_object_name(corp, branch, bk_id, blob_no, ext)


def download_and_upload(blob_key, object_name, filename, retry_count=3):
    """
    Python 2.7アプリからダウンロードしてGCSにアップロード（リトライ付き）
    """
    serve_url = f"{BASE_URL}/serve/{blob_key}"

    for attempt in range(retry_count):
        try:
            print(f"  試行 {attempt + 1}/{retry_count}: {filename}")

            # ファイルをダウンロード
            response = requests.get(serve_url, timeout=180, stream=True)
            if response.status_code != 200:
                print(f"    HTTP {response.status_code}")
                continue

            # コンテンツを取得
            content = response.content
            size = len(content)

            if size == 0:
                print("    空ファイル")
                continue

            # Content-Typeを取得
            content_type = response.headers.get('Content-Type', 'application/octet-stream')

            # GCSにアップロード
            storage_client = storage.Client()
            bucket = storage_client.bucket(gcs_utils.BUCKET_NAME)
            gcs_blob = bucket.blob(object_name)

            # 既にアップロード済みの場合
            if gcs_blob.exists():
                gcs_blob.reload()
                print(f"    既存: {format_size(gcs_blob.size)}")
                return True, gcs_blob.size, None

            gcs_blob.upload_from_string(content, content_type=content_type)
            print(f"    成功: {format_size(size)}")
            return True, size, None

        except requests.exceptions.Timeout:
            print(f"    タイムアウト")
            time.sleep(5)  # リトライ前に待機
        except requests.exceptions.RequestException as e:
            print(f"    リクエストエラー: {str(e)}")
            time.sleep(5)
        except Exception as e:
            print(f"    エラー: {str(e)}")
            time.sleep(5)

    return False, 0, f"Failed after {retry_count} attempts"


def find_and_retry_failed_blobs():
    """エラーになったBlobを検索してリトライ"""

    print("=" * 60)
    print("エラーファイル リトライ")
    print("=" * 60)

    # エラー対象の条件
    error_targets = [
        {"bkID": "4492", "filename_contains": "003_1.JPG"},
        {"bkID": "53022", "filename_contains": "千種区東山元町2丁目"},
        {"bkID": "53023", "filename_contains": "千種区東山元町2丁目"},
    ]

    found_blobs = []

    # 各条件でBlobを検索
    for target in error_targets:
        print(f"\n検索中: bkID={target['bkID']}, filename含む '{target['filename_contains']}'")

        query = Blob.query(Blob.bkID == target['bkID'])
        blobs = query.fetch()

        for blob in blobs:
            if blob.filename and target['filename_contains'] in blob.filename:
                print(f"  発見: {blob.filename}")
                print(f"    key: {blob.key}")
                print(f"    blobKey: {blob.blobKey[:50]}..." if blob.blobKey else "    blobKey: なし")
                print(f"    CorpOrg_key: {blob.CorpOrg_key}")
                print(f"    Branch_Key: {blob.Branch_Key}")
                print(f"    blobNo: {blob.blobNo}")
                found_blobs.append(blob)

    if not found_blobs:
        print("\n対象のBlobが見つかりませんでした")
        return

    print(f"\n{'=' * 60}")
    print(f"リトライ対象: {len(found_blobs)} 件")
    print("=" * 60)

    success_count = 0
    error_count = 0

    for blob in found_blobs:
        if not blob.blobKey:
            print(f"\n[SKIP] blobKeyなし: {blob.filename}")
            continue

        print(f"\n処理中: {blob.filename}")

        object_name = generate_object_name_for_blob(blob)
        print(f"  GCS path: {object_name}")

        success, size, error = download_and_upload(
            blob.blobKey, object_name, blob.filename, retry_count=5
        )

        if success:
            success_count += 1
        else:
            error_count += 1
            print(f"  [FAILED] {error}")

        # 次のファイルの前に少し待機
        time.sleep(2)

    print(f"\n{'=' * 60}")
    print("リトライ結果")
    print("=" * 60)
    print(f"成功: {success_count} 件")
    print(f"失敗: {error_count} 件")


def main():
    client = ndb.Client()
    with client.context():
        find_and_retry_failed_blobs()


if __name__ == '__main__':
    main()
