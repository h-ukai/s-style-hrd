# -*- coding: utf-8 -*-
"""
Blob データのボリューム確認スクリプト
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import ndb

# 環境変数を設定
os.environ['GOOGLE_CLOUD_PROJECT'] = 's-style-hrd'

# Blob モデルを定義（軽量版）
class Blob(ndb.Model):
    date = ndb.DateTimeProperty()
    blobKey = ndb.StringProperty()


def count_blobs_before(date):
    """指定日より前のBlobをカウント"""
    query = Blob.query(Blob.date < date)
    return query.count()


def count_blobs_after(date):
    """指定日以降のBlobをカウント"""
    query = Blob.query(Blob.date >= date)
    return query.count()


def count_all_blobs():
    """全Blobをカウント"""
    return Blob.query().count()


def main():
    client = ndb.Client(project='s-style-hrd')

    with client.context():
        # 境界日
        boundary = datetime(2023, 1, 1)

        print("=" * 50)
        print("Blob データ ボリューム確認")
        print("=" * 50)

        # 全体カウント
        total = count_all_blobs()
        print(f"\n全体: {total:,} 件")

        # 2023/1/1 より前
        before = count_blobs_before(boundary)
        print(f"2023/01/01 より前: {before:,} 件")

        # 2023/1/1 以降
        after = count_blobs_after(boundary)
        print(f"2023/01/01 以降: {after:,} 件")

        print("\n" + "-" * 50)
        print(f"合計確認: {before + after:,} 件 (全体: {total:,} 件)")


if __name__ == '__main__':
    main()
