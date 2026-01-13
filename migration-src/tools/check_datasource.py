# -*- coding: utf-8 -*-
"""
bkdataのdataSourceフィールドを調査
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import ndb
from application.models.bkdata import BKdata


def check_datasource():
    """最新のbkdataレコードのdataSourceを調査"""
    print("=" * 60)
    print("bkdata dataSource 調査")
    print("=" * 60)

    # 最新10件を取得（日付降順）
    query = BKdata.query().order(-BKdata.date)
    records = query.fetch(10)

    print(f"\n最新 {len(records)} 件のレコード:\n")
    print("-" * 80)

    for i, bk in enumerate(records, 1):
        print(f"[{i}] key: {bk.key.id() if bk.key else 'N/A'}")
        print(f"    date: {bk.date}")
        print(f"    CorpOrg_key: {bk.CorpOrg_key}")
        print(f"    Branch_Key: {bk.Branch_Key}")
        print(f"    dataSource: {bk.dataSource if bk.dataSource else '(空)'}")
        print(f"    bknbng: {bk.bknbng if bk.bknbng else '(空)'}")
        print(f"    nyrykkisyID: {bk.nyrykkisyID if bk.nyrykkisyID else '(空)'}")
        print(f"    nyrykstnID: {bk.nyrykstnID if bk.nyrykstnID else '(空)'}")
        print("-" * 80)

    # dataSourceの値別の件数
    print("\n\ndataSource 値の分布（サンプル1000件）:")
    print("-" * 40)

    sample = BKdata.query().fetch(1000)
    datasource_counts = {}
    for bk in sample:
        ds = bk.dataSource if bk.dataSource else "(空)"
        datasource_counts[ds] = datasource_counts.get(ds, 0) + 1

    for ds, count in sorted(datasource_counts.items(), key=lambda x: -x[1]):
        print(f"  {ds}: {count} 件")


def main():
    client = ndb.Client()
    with client.context():
        check_datasource()


if __name__ == '__main__':
    main()
