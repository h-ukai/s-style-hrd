# -*- coding: utf-8 -*-
"""
Blobstore → GCS データ移行ツール

使用方法:
    # dry-run（移行対象の確認のみ）
    python tools/migrate_blob_to_gcs.py --dry-run

    # 日付範囲を指定して移行
    python tools/migrate_blob_to_gcs.py --from 2024/01/01 --to 2024/12/31

    # 特定日以降のデータを移行
    python tools/migrate_blob_to_gcs.py --from 2024/06/01

    # 特定日以前のデータを移行
    python tools/migrate_blob_to_gcs.py --to 2024/06/01

    # 処理件数を指定
    python tools/migrate_blob_to_gcs.py --from 2024/01/01 --limit 500

    # ファイル転送も行う（メタデータ更新のみでない）
    python tools/migrate_blob_to_gcs.py --transfer-files

注意:
    - 日付は yyyy/mm/dd 形式で指定（午前0時を境界とする）
    - --from: 指定日の 00:00:00 以降
    - --to: 指定日の 00:00:00 より前（指定日は含まない）
"""

import argparse
import sys
import os
from datetime import datetime

# パスを追加してapplicationモジュールをインポート可能にする
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import ndb
from google.cloud import storage
from application.models.blob import Blob
from application import gcs_utils


# Blobstore の内部 GCS バケット名（GAE がデータを保存する場所）
# 形式: {project-id}.appspot.com
BLOBSTORE_GCS_BUCKET = os.environ.get('BLOBSTORE_GCS_BUCKET', 's-style-hrd.appspot.com')


class MigrationStats:
    """移行統計"""
    def __init__(self):
        self.total = 0
        self.success = 0
        self.skipped = 0
        self.error = 0
        self.transferred = 0
        self.errors = []

    def add_success(self, transferred=False):
        self.total += 1
        self.success += 1
        if transferred:
            self.transferred += 1

    def add_skipped(self, reason):
        self.total += 1
        self.skipped += 1
        print(f"  [SKIP] {reason}")

    def add_error(self, blob_key, error):
        self.total += 1
        self.error += 1
        self.errors.append((blob_key, str(error)))
        print(f"  [ERROR] {blob_key}: {error}")

    def print_summary(self):
        print("\n" + "=" * 60)
        print("移行結果サマリー")
        print("=" * 60)
        print(f"処理対象: {self.total} 件")
        print(f"  成功: {self.success} 件")
        if self.transferred > 0:
            print(f"    うちファイル転送: {self.transferred} 件")
        print(f"  スキップ: {self.skipped} 件")
        print(f"  エラー: {self.error} 件")
        if self.errors:
            print("\nエラー詳細:")
            for blob_key, error in self.errors[:10]:  # 最初の10件のみ表示
                print(f"  - {blob_key}: {error}")
            if len(self.errors) > 10:
                print(f"  ... 他 {len(self.errors) - 10} 件")


def parse_date(date_str):
    """
    yyyy/mm/dd 形式の日付をパース

    Args:
        date_str: 日付文字列（yyyy/mm/dd形式）

    Returns:
        datetime: パースされた日付（午前0時）
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y/%m/%d")
    except ValueError:
        raise ValueError(f"日付形式が不正です: {date_str} (yyyy/mm/dd形式で指定してください)")


def get_blobs_in_range(start_date=None, end_date=None, limit=100, cursor=None):
    """
    日付範囲で Blob を取得

    Args:
        start_date: 開始日（この日の00:00:00以降）
        end_date: 終了日（この日の00:00:00より前）
        limit: 取得件数上限
        cursor: ページネーション用カーソル

    Returns:
        tuple: (Blobリスト, 次のカーソル, 残りがあるか)
    """
    query = Blob.query()

    if start_date:
        query = query.filter(Blob.date >= start_date)
    if end_date:
        query = query.filter(Blob.date < end_date)

    query = query.order(Blob.date)

    # カーソルを使用したページネーション
    if cursor:
        blobs, next_cursor, more = query.fetch_page(limit, start_cursor=cursor)
    else:
        blobs, next_cursor, more = query.fetch_page(limit)

    return blobs, next_cursor, more


def is_already_migrated(blob):
    """
    既にGCSに移行済みかどうかを判定

    GCS object name形式（corp/branch/bkid/no.ext）であれば移行済みとみなす
    """
    if not blob.blobKey:
        return False
    # Blobstore の key は "AMIfv94..." や "encoded_gs_file:..." のような形式
    # GCS object name は "corp/branch/bkid/no.ext" のような形式
    # "/" が含まれていて、"encoded_gs_file" で始まらない場合は移行済み
    if '/' in blob.blobKey and not blob.blobKey.startswith('encoded_gs_file'):
        return True
    return False


def generate_object_name_for_blob(blob):
    """
    Blob エンティティから GCS object name を生成

    孤立データ（メタデータ不完全）の場合もハンドリング
    """
    corp = blob.CorpOrg_key or "_orphan"
    branch = blob.Branch_Key or "_unknown"
    bk_id = blob.bkID or f"_no-bkid-{blob.key.id()}"
    blob_no = blob.blobNo or 0
    ext = blob.fileextension or "bin"

    return gcs_utils.generate_object_name(corp, branch, bk_id, blob_no, ext)


def get_blobstore_gcs_path(blobstore_key):
    """
    Blobstore key から内部 GCS パスを取得

    Blobstore は内部的に GCS に保存されているため、
    適切なパスを構築すれば直接アクセス可能

    Args:
        blobstore_key: Blobstore の key (例: "AMIfv94...")

    Returns:
        str: GCS object path、または None（変換不可の場合）
    """
    if not blobstore_key:
        return None

    # encoded_gs_file 形式の場合は直接GCSパスを抽出
    if blobstore_key.startswith('encoded_gs_file:'):
        # 形式: encoded_gs_file:bucket/path
        return blobstore_key[len('encoded_gs_file:'):]

    # 通常の Blobstore key の場合
    # 内部的には gs://{app-id}.appspot.com/encoded_gs_key/{key} に保存される
    # または gs://{app-id}.appspot.com/{key} の場合もある
    return f"encoded_gs_key/{blobstore_key}"


def transfer_file_from_blobstore(old_blobstore_key, new_object_name):
    """
    Blobstore からファイルを読み取り、新しい GCS バケットにコピー

    Args:
        old_blobstore_key: 古い Blobstore key
        new_object_name: 新しい GCS object name

    Returns:
        bool: 成功した場合 True
    """
    try:
        storage_client = storage.Client()

        # ソースバケット（Blobstore の内部 GCS）
        source_bucket = storage_client.bucket(BLOBSTORE_GCS_BUCKET)
        source_path = get_blobstore_gcs_path(old_blobstore_key)

        if not source_path:
            print(f"    Blobstore key を GCS パスに変換できません: {old_blobstore_key}")
            return False

        source_blob = source_bucket.blob(source_path)

        # ソースファイルが存在するか確認
        if not source_blob.exists():
            # 別のパス形式を試す
            alt_path = old_blobstore_key
            source_blob = source_bucket.blob(alt_path)
            if not source_blob.exists():
                print(f"    ソースファイルが見つかりません: {source_path} or {alt_path}")
                return False

        # デスティネーションバケット
        dest_bucket = storage_client.bucket(gcs_utils.BUCKET_NAME)
        dest_blob = dest_bucket.blob(new_object_name)

        # 既にコピー済みの場合はスキップ
        if dest_blob.exists():
            print(f"    既にコピー済み: {new_object_name}")
            return True

        # コピー実行
        source_bucket.copy_blob(source_blob, dest_bucket, new_object_name)
        print(f"    ファイル転送: {source_path} -> {new_object_name}")
        return True

    except Exception as e:
        print(f"    ファイル転送エラー: {e}")
        return False


def migrate_blob(blob, stats, dry_run=False, transfer_files=False):
    """
    Blob エンティティを移行

    Args:
        blob: Blob エンティティ
        stats: MigrationStats インスタンス
        dry_run: True の場合、実際の更新は行わない
        transfer_files: True の場合、ファイル転送も行う
    """
    old_key = blob.blobKey

    # 既に移行済みの場合はスキップ
    if is_already_migrated(blob):
        stats.add_skipped(f"Already migrated: {blob.blobKey}")
        return

    # blobKey がない場合はスキップ
    if not old_key:
        stats.add_skipped(f"No blobKey: key={blob.key}")
        return

    try:
        # 新しい GCS object name を生成
        object_name = generate_object_name_for_blob(blob)

        if dry_run:
            print(f"  [DRY-RUN] Would migrate:")
            print(f"    Old blobKey: {old_key}")
            print(f"    New object_name: {object_name}")
            print(f"    Date: {blob.date}")
            if transfer_files:
                print(f"    File transfer: Yes")
            stats.add_success()
            return

        transferred = False

        # ファイル転送を行う場合
        if transfer_files:
            transferred = transfer_file_from_blobstore(old_key, object_name)
            if not transferred:
                # ファイル転送に失敗した場合はメタデータも更新しない
                stats.add_error(old_key, "File transfer failed")
                return

        # Datastore フィールドを更新
        blob.blobKey = object_name
        blob.bloburl = gcs_utils.get_blob_url(object_name)

        if gcs_utils.is_image_file(blob.fileextension):
            blob.thumbnailurl = gcs_utils.get_thumbnail_url(object_name)
            blob.html = gcs_utils.generate_html(
                object_name, blob.filename,
                title=blob.title, content=blob.content, is_image=True
            )
        else:
            blob.thumbnailurl = None
            blob.html = gcs_utils.generate_html(object_name, blob.filename, is_image=False)

        blob.put()
        print(f"  [OK] {old_key} -> {object_name}")
        stats.add_success(transferred=transferred)

    except Exception as e:
        stats.add_error(old_key, e)


def migrate_blobs(start_date, end_date, limit, dry_run=False, transfer_files=False, batch_size=100):
    """
    Blob エンティティを移行

    Args:
        start_date: 開始日
        end_date: 終了日
        limit: 処理件数上限（0で無制限）
        dry_run: ドライランモード
        transfer_files: ファイル転送を行うか
        batch_size: 一度に取得する件数
    """
    stats = MigrationStats()
    cursor = None
    processed = 0

    print("=" * 60)
    print("Blobstore → GCS データ移行ツール")
    print("=" * 60)
    print(f"モード: {'DRY-RUN（実際の更新なし）' if dry_run else '本番移行'}")
    print(f"ファイル転送: {'あり' if transfer_files else 'なし（メタデータのみ）'}")
    print(f"開始日: {start_date.strftime('%Y/%m/%d') if start_date else '指定なし'}")
    print(f"終了日: {end_date.strftime('%Y/%m/%d') if end_date else '指定なし'}")
    print(f"処理上限: {limit if limit > 0 else '無制限'}")
    print("-" * 60)

    while True:
        # 残り件数を計算
        fetch_limit = batch_size
        if limit > 0:
            remaining = limit - processed
            if remaining <= 0:
                break
            fetch_limit = min(batch_size, remaining)

        # Blob を取得
        blobs, next_cursor, more = get_blobs_in_range(
            start_date, end_date, fetch_limit, cursor
        )

        if not blobs:
            break

        print(f"\n処理中... (取得: {len(blobs)} 件)")

        for blob in blobs:
            migrate_blob(blob, stats, dry_run, transfer_files)
            processed += 1

        # 次のページがない、または上限に達した場合は終了
        if not more or not next_cursor:
            break
        if limit > 0 and processed >= limit:
            break

        cursor = next_cursor

    # サマリーを表示
    stats.print_summary()

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Blobstore → GCS データ移行ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 移行対象の確認（dry-run）
  python tools/migrate_blob_to_gcs.py --dry-run

  # 2024年のデータを移行（メタデータのみ）
  python tools/migrate_blob_to_gcs.py --from 2024/01/01 --to 2025/01/01

  # 2024年6月以降のデータを移行（ファイル転送あり）
  python tools/migrate_blob_to_gcs.py --from 2024/06/01 --transfer-files

  # 2024年6月1日より前のデータを移行（2024/06/01は含まない）
  python tools/migrate_blob_to_gcs.py --to 2024/06/01

  # 処理件数を指定
  python tools/migrate_blob_to_gcs.py --limit 1000

日付指定:
  --from: 指定日の 00:00:00 以降のデータが対象
  --to:   指定日の 00:00:00 より前のデータが対象（指定日は含まない）
"""
    )
    parser.add_argument(
        '--from', dest='start_date', metavar='DATE',
        help='開始日 (yyyy/mm/dd形式、指定日の00:00:00以降)'
    )
    parser.add_argument(
        '--to', dest='end_date', metavar='DATE',
        help='終了日 (yyyy/mm/dd形式、指定日の00:00:00より前)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='ドライランモード（実際の更新は行わない）'
    )
    parser.add_argument(
        '--transfer-files', action='store_true',
        help='ファイル転送も行う（デフォルトはメタデータ更新のみ）'
    )
    parser.add_argument(
        '--limit', type=int, default=0,
        help='処理件数上限（0で無制限、デフォルト: 0）'
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
        stats = migrate_blobs(
            start_date, end_date,
            args.limit, args.dry_run, args.transfer_files, args.batch_size
        )

    # エラーがあった場合は非ゼロで終了
    if stats.error > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
