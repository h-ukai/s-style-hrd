# -*- coding: utf-8 -*-
"""
dataSourceが空のデータ件数を調査
"""

from google.cloud import ndb


# BKdataモデルの必要なフィールドのみ定義
class BKdata(ndb.Model):
    dataSource = ndb.StringProperty()
    bkID = ndb.StringProperty()
    nyrykkisyID = ndb.StringProperty()
    nyrykstnID = ndb.StringProperty()


def count_datasource():
    """dataSourceの分布を調査"""
    print("=" * 60)
    print("dataSource 分布調査（全件）")
    print("=" * 60)

    # 全体件数
    total = BKdata.query().count()
    print(f"\n全体件数: {total:,} 件")

    # dataSource別にカウント
    # レインズ
    reins_count = BKdata.query(BKdata.dataSource == "レインズ").count()
    print(f"\ndataSource = 'レインズ': {reins_count:,} 件 ({reins_count/total*100:.1f}%)")

    # 空（None または 空文字）
    # NDBではNoneと空文字は別なので両方チェック
    none_count = BKdata.query(BKdata.dataSource == None).count()
    empty_count = BKdata.query(BKdata.dataSource == "").count()
    empty_total = none_count + empty_count
    print(f"dataSource = 空: {empty_total:,} 件 ({empty_total/total*100:.1f}%)")
    print(f"  - None: {none_count:,} 件")
    print(f"  - 空文字: {empty_count:,} 件")

    # その他
    other = total - reins_count - empty_total
    print(f"その他: {other:,} 件 ({other/total*100:.1f}%)")

    # 空のデータのサンプルを表示
    print("\n" + "-" * 60)
    print("dataSourceが空のデータ サンプル10件:")
    print("-" * 60)

    empty_records = BKdata.query(BKdata.dataSource == None).fetch(10)
    for i, bk in enumerate(empty_records, 1):
        print(f"[{i}] bkID: {bk.bkID}, nyrykkisyID: {bk.nyrykkisyID}, nyrykstnID: {bk.nyrykstnID}")


def main():
    client = ndb.Client()
    with client.context():
        count_datasource()


if __name__ == '__main__':
    main()
