# -*- coding: utf-8 -*-
"""
blobKey の形式を確認するスクリプト
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import ndb

os.environ['GOOGLE_CLOUD_PROJECT'] = 's-style-hrd'


class Blob(ndb.Model):
    date = ndb.DateTimeProperty()
    blobKey = ndb.StringProperty()
    filename = ndb.StringProperty()
    fileextension = ndb.StringProperty()


def main():
    client = ndb.Client(project='s-style-hrd')

    with client.context():
        print("=" * 60)
        print("blobKey 形式サンプル")
        print("=" * 60)

        # 最新10件
        print("\n【最新10件】")
        query = Blob.query().order(-Blob.date)
        blobs = query.fetch(10)

        for blob in blobs:
            key_preview = blob.blobKey[:80] if blob.blobKey else "(なし)"
            if blob.blobKey and len(blob.blobKey) > 80:
                key_preview += "..."
            print(f"  日付: {blob.date}")
            print(f"  ファイル名: {blob.filename}")
            print(f"  blobKey: {key_preview}")
            print()

        # 古い10件
        print("\n【古い10件】")
        query = Blob.query().order(Blob.date)
        blobs = query.fetch(10)

        for blob in blobs:
            key_preview = blob.blobKey[:80] if blob.blobKey else "(なし)"
            if blob.blobKey and len(blob.blobKey) > 80:
                key_preview += "..."
            print(f"  日付: {blob.date}")
            print(f"  ファイル名: {blob.filename}")
            print(f"  blobKey: {key_preview}")
            print()

        # blobKeyの形式統計
        print("\n【blobKey形式の統計】")
        all_blobs = Blob.query().fetch()

        formats = {
            'encoded_gs_file': 0,
            'AMIfv': 0,
            'gcs_object_name': 0,  # 既に移行済み（/を含む）
            'other': 0,
            'empty': 0
        }

        for blob in all_blobs:
            if not blob.blobKey:
                formats['empty'] += 1
            elif blob.blobKey.startswith('encoded_gs_file:'):
                formats['encoded_gs_file'] += 1
            elif blob.blobKey.startswith('AMIfv'):
                formats['AMIfv'] += 1
            elif '/' in blob.blobKey:
                formats['gcs_object_name'] += 1
            else:
                formats['other'] += 1

        for fmt, count in formats.items():
            print(f"  {fmt}: {count:,} 件")


if __name__ == '__main__':
    main()
