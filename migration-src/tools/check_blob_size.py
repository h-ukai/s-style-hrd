# -*- coding: utf-8 -*-
"""
Blob ファイルサイズ確認スクリプト

Blobstore内部GCSバケットからファイルサイズを取得
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import ndb
from google.cloud import storage

# 環境変数を設定
os.environ['GOOGLE_CLOUD_PROJECT'] = 's-style-hrd'

# Blobstore の内部 GCS バケット
BLOBSTORE_GCS_BUCKET = 's-style-hrd.appspot.com'


class Blob(ndb.Model):
    date = ndb.DateTimeProperty()
    blobKey = ndb.StringProperty()
    filename = ndb.StringProperty()
    fileextension = ndb.StringProperty()


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


def get_blobstore_gcs_path(blobstore_key):
    """Blobstore key から内部 GCS パスを取得"""
    if not blobstore_key:
        return None

    if blobstore_key.startswith('encoded_gs_file:'):
        return blobstore_key[len('encoded_gs_file:'):]

    # 通常の Blobstore key
    return f"encoded_gs_key/{blobstore_key}"


def check_blob_sizes_sample(limit=100):
    """サンプルデータでファイルサイズを確認"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BLOBSTORE_GCS_BUCKET)

    total_size = 0
    found_count = 0
    not_found_count = 0
    sizes = []

    query = Blob.query().order(-Blob.date)
    blobs = query.fetch(limit)

    print(f"サンプル {limit} 件のファイルサイズを確認中...")
    print("-" * 50)

    for blob in blobs:
        if not blob.blobKey:
            continue

        # 既に移行済み（GCS object name形式）の場合はスキップ
        if '/' in blob.blobKey and not blob.blobKey.startswith('encoded_gs_file'):
            continue

        gcs_path = get_blobstore_gcs_path(blob.blobKey)
        if not gcs_path:
            continue

        gcs_blob = bucket.blob(gcs_path)

        try:
            gcs_blob.reload()  # メタデータを取得
            size = gcs_blob.size
            sizes.append(size)
            total_size += size
            found_count += 1
        except Exception:
            # 別のパス形式を試す
            alt_path = blob.blobKey
            gcs_blob = bucket.blob(alt_path)
            try:
                gcs_blob.reload()
                size = gcs_blob.size
                sizes.append(size)
                total_size += size
                found_count += 1
            except Exception:
                not_found_count += 1

    return sizes, total_size, found_count, not_found_count


def estimate_total_size(sample_sizes, total_count):
    """サンプルから全体サイズを推定"""
    if not sample_sizes:
        return 0

    avg_size = sum(sample_sizes) / len(sample_sizes)
    return avg_size * total_count


def main():
    client = ndb.Client(project='s-style-hrd')

    with client.context():
        boundary = datetime(2023, 1, 1)

        print("=" * 60)
        print("Blob ファイルサイズ確認")
        print("=" * 60)

        # 全体カウント
        total_count = Blob.query().count()
        before_count = Blob.query(Blob.date < boundary).count()
        after_count = Blob.query(Blob.date >= boundary).count()

        print(f"\n全体件数: {total_count:,} 件")
        print(f"2023/01/01 より前: {before_count:,} 件")
        print(f"2023/01/01 以降: {after_count:,} 件")

        # サンプルでサイズ確認
        print("\n" + "-" * 60)
        print("サンプルからファイルサイズを推定...")

        sizes, total_size, found, not_found = check_blob_sizes_sample(100)

        if found > 0:
            print(f"\nサンプル結果:")
            print(f"  確認できたファイル: {found} 件")
            print(f"  見つからなかったファイル: {not_found} 件")
            print(f"  サンプル合計サイズ: {format_size(total_size)}")
            print(f"  平均ファイルサイズ: {format_size(total_size // found)}")

            if sizes:
                sizes.sort()
                print(f"  最小サイズ: {format_size(min(sizes))}")
                print(f"  最大サイズ: {format_size(max(sizes))}")
                median = sizes[len(sizes) // 2]
                print(f"  中央値: {format_size(median)}")

            # 全体推定
            estimated_total = estimate_total_size(sizes, total_count)
            print(f"\n推定全体サイズ: {format_size(int(estimated_total))}")
        else:
            print("ファイルサイズを取得できませんでした")
            print("（Blobstoreの内部GCS形式が異なる可能性があります）")


if __name__ == '__main__':
    main()
