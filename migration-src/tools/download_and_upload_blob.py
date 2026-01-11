# -*- coding: utf-8 -*-
"""
Blobstore → GCS ファイルコピーツール（HTTP経由）

Python 2.7アプリの /serve/ エンドポイントからダウンロードして
新しいGCSバケットにアップロード

※ Datastoreは更新しない（blobKeyはそのまま）
※ 元のBlobstoreファイルは削除しない
※ サイズ確認用

使用方法:
    # dry-run（対象確認のみ）
    python tools/download_and_upload_blob.py --from 2023/01/01 --dry-run

    # 2023年以降のデータをコピー
    python tools/download_and_upload_blob.py --from 2023/01/01

    # 処理件数を指定
    python tools/download_and_upload_blob.py --from 2023/01/01 --limit 10
"""

import argparse
import sys
import os
import time
import requests
from datetime import datetime

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
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


class CopyStats:
    """コピー統計"""
    def __init__(self):
        self.total = 0
        self.success = 0
        self.skipped = 0
        self.error = 0
        self.total_size = 0
        self.sizes = []
        self.errors = []

    def add_success(self, size):
        self.total += 1
        self.success += 1
        self.total_size += size
        self.sizes.append(size)

    def add_skipped(self, reason):
        self.total += 1
        self.skipped += 1
        print(f"  [SKIP] {reason}")

    def add_error(self, blob_key, error):
        self.total += 1
        self.error += 1
        self.errors.append((blob_key, str(error)))
        print(f"  [ERROR] {error}")

    def print_summary(self):
        print("\n" + "=" * 60)
        print("コピー結果サマリー")
        print("=" * 60)
        print(f"処理対象: {self.total} 件")
        print(f"  成功: {self.success} 件")
        print(f"  スキップ: {self.skipped} 件")
        print(f"  エラー: {self.error} 件")

        if self.sizes:
            print(f"\nファイルサイズ統計:")
            print(f"  合計サイズ: {format_size(self.total_size)}")
            print(f"  平均サイズ: {format_size(self.total_size // len(self.sizes))}")
            self.sizes.sort()
            print(f"  最小サイズ: {format_size(min(self.sizes))}")
            print(f"  最大サイズ: {format_size(max(self.sizes))}")
            median = self.sizes[len(self.sizes) // 2]
            print(f"  中央値: {format_size(median)}")

        if self.errors:
            print("\nエラー詳細:")
            for blob_key, error in self.errors[:10]:
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... 他 {len(self.errors) - 10} 件")


def parse_date(date_str):
    """yyyy/mm/dd 形式の日付をパース"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y/%m/%d")
    except ValueError:
        raise ValueError(f"日付形式が不正です: {date_str} (yyyy/mm/dd形式で指定してください)")


def generate_object_name_for_blob(blob):
    """Blob エンティティから GCS object name を生成"""
    corp = blob.CorpOrg_key or "_orphan"
    branch = blob.Branch_Key or "_unknown"
    bk_id = blob.bkID or f"_no-bkid-{blob.key.id()}"
    blob_no = blob.blobNo or 0
    ext = blob.fileextension or "bin"

    return gcs_utils.generate_object_name(corp, branch, bk_id, blob_no, ext)


def is_already_migrated(blob):
    """既にGCSに移行済みかどうかを判定"""
    if not blob.blobKey:
        return False
    if '/' in blob.blobKey and not blob.blobKey.startswith('encoded_gs_file'):
        return True
    return False


def download_and_upload(blob_key, object_name, filename, dry_run=False):
    """
    Python 2.7アプリからダウンロードしてGCSにアップロード

    Returns:
        tuple: (成功したか, ファイルサイズ, エラーメッセージ)
    """
    serve_url = f"{BASE_URL}/serve/{blob_key}"

    try:
        # ファイルをダウンロード（dry-runでもGETを使用）
        response = requests.get(serve_url, timeout=120, stream=True)
        if response.status_code != 200:
            return False, 0, f"HTTP {response.status_code}"

        # コンテンツを取得
        content = response.content
        size = len(content)

        if size == 0:
            return False, 0, "Empty file"

        # dry-runの場合はアップロードせずサイズのみ返す
        if dry_run:
            return True, size, None

        # Content-Typeを取得
        content_type = response.headers.get('Content-Type', 'application/octet-stream')

        # GCSにアップロード
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_utils.BUCKET_NAME)
        gcs_blob = bucket.blob(object_name)

        # 既にアップロード済みの場合はスキップ
        if gcs_blob.exists():
            gcs_blob.reload()
            return True, gcs_blob.size, None

        gcs_blob.upload_from_string(content, content_type=content_type)
        return True, size, None

    except requests.exceptions.Timeout:
        return False, 0, "Request timeout"
    except requests.exceptions.RequestException as e:
        return False, 0, f"Request error: {str(e)}"
    except Exception as e:
        return False, 0, f"Error: {str(e)}"


def copy_blobs(start_date, end_date, limit, dry_run=False, batch_size=100):
    """Blob ファイルをコピー（Datastoreは更新しない）"""
    stats = CopyStats()
    cursor = None
    processed = 0

    print("=" * 60)
    print("Blobstore → GCS ファイルコピー（HTTP経由）")
    print("=" * 60)
    print(f"モード: {'DRY-RUN（実際のコピーなし）' if dry_run else 'コピー実行'}")
    print(f"ソースURL: {BASE_URL}/serve/{{blobKey}}")
    print(f"宛先バケット: {gcs_utils.BUCKET_NAME}")
    print(f"開始日: {start_date.strftime('%Y/%m/%d') if start_date else '指定なし'}")
    print(f"終了日: {end_date.strftime('%Y/%m/%d') if end_date else '指定なし'}")
    print(f"処理上限: {limit if limit > 0 else '無制限'}")
    print(f"\n※ Datastoreは更新しません（blobKeyはそのまま）")
    print(f"※ 元のBlobstoreファイルは削除しません")
    print("-" * 60)

    while True:
        # クエリ作成
        query = Blob.query()
        if start_date:
            query = query.filter(Blob.date >= start_date)
        if end_date:
            query = query.filter(Blob.date < end_date)
        query = query.order(Blob.date)

        # 残り件数を計算
        fetch_limit = batch_size
        if limit > 0:
            remaining = limit - processed
            if remaining <= 0:
                break
            fetch_limit = min(batch_size, remaining)

        # Blob を取得
        if cursor:
            blobs, next_cursor, more = query.fetch_page(fetch_limit, start_cursor=cursor)
        else:
            blobs, next_cursor, more = query.fetch_page(fetch_limit)

        if not blobs:
            break

        print(f"\n処理中... (取得: {len(blobs)} 件)")

        for blob in blobs:
            # blobKey がない場合はスキップ
            if not blob.blobKey:
                stats.add_skipped(f"No blobKey: key={blob.key}")
                continue

            # 既に移行済みの場合はスキップ
            if is_already_migrated(blob):
                stats.add_skipped(f"Already migrated: {blob.blobKey[:30]}...")
                continue

            # GCS object name を生成
            object_name = generate_object_name_for_blob(blob)

            # ダウンロード＆アップロード実行
            success, size, error = download_and_upload(
                blob.blobKey, object_name, blob.filename, dry_run
            )

            if success:
                if dry_run:
                    print(f"  [DRY-RUN] {blob.filename}: {format_size(size)}")
                else:
                    print(f"  [OK] {blob.filename}: {format_size(size)} -> {object_name}")
                stats.add_success(size)
            else:
                stats.add_error(blob.blobKey[:50], f"{blob.filename}: {error}")

            processed += 1

            # レート制限対策（1秒待機）
            if not dry_run:
                time.sleep(1.0)

        # 次のページがない、または上限に達した場合は終了
        if not more or not next_cursor:
            break
        if limit > 0 and processed >= limit:
            break

        cursor = next_cursor

    # サマリーを表示
    stats.print_summary()

    # 全体推定を表示
    if stats.sizes and limit > 0:
        # サンプルから全体を推定
        total_count = Blob.query().count()
        before_count = Blob.query(Blob.date < datetime(2023, 1, 1)).count()
        after_count = Blob.query(Blob.date >= datetime(2023, 1, 1)).count()

        avg_size = stats.total_size / len(stats.sizes)

        print("\n" + "=" * 60)
        print("全体サイズ推定")
        print("=" * 60)
        print(f"サンプル平均サイズ: {format_size(int(avg_size))}")
        print(f"\n2023/01/01 以降 ({after_count:,} 件):")
        print(f"  推定サイズ: {format_size(int(avg_size * after_count))}")
        print(f"\n2023/01/01 より前 ({before_count:,} 件):")
        print(f"  推定サイズ: {format_size(int(avg_size * before_count))}")
        print(f"\n全体 ({total_count:,} 件):")
        print(f"  推定サイズ: {format_size(int(avg_size * total_count))}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Blobstore → GCS ファイルコピー（HTTP経由）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
※ このツールはDatastoreを更新しません（blobKeyはそのまま）
※ 元のBlobstoreファイルは削除しません
※ サイズ確認用

使用例:
  # 対象確認（dry-run）
  python tools/download_and_upload_blob.py --from 2023/01/01 --dry-run

  # 2023年以降のデータをコピー
  python tools/download_and_upload_blob.py --from 2023/01/01

  # 最初の10件だけコピー
  python tools/download_and_upload_blob.py --from 2023/01/01 --limit 10
"""
    )
    parser.add_argument(
        '--from', dest='start_date', metavar='DATE',
        help='開始日 (yyyy/mm/dd形式)'
    )
    parser.add_argument(
        '--to', dest='end_date', metavar='DATE',
        help='終了日 (yyyy/mm/dd形式)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='ドライランモード（実際のコピーは行わない）'
    )
    parser.add_argument(
        '--limit', type=int, default=0,
        help='処理件数上限（0で無制限）'
    )
    parser.add_argument(
        '--batch-size', type=int, default=100,
        help='一度に取得する件数（デフォルト: 100）'
    )

    args = parser.parse_args()

    # 日付をパース
    try:
        start_date = parse_date(args.start_date)
        end_date = parse_date(args.end_date)
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

    # NDB コンテキスト内で実行
    client = ndb.Client()
    with client.context():
        stats = copy_blobs(
            start_date, end_date,
            args.limit, args.dry_run, args.batch_size
        )

    # エラーがあった場合は非ゼロで終了
    if stats.error > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
