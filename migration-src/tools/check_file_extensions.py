# -*- coding: utf-8 -*-
"""
ファイル拡張子の統計を確認
"""

import sys
import os
from collections import Counter
from datetime import datetime

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
        boundary = datetime(2023, 1, 1)

        print("=" * 60)
        print("ファイル拡張子の統計")
        print("=" * 60)

        # 全体
        all_blobs = Blob.query().fetch()
        extensions_all = Counter()
        extensions_before = Counter()
        extensions_after = Counter()

        for blob in all_blobs:
            ext = (blob.fileextension or '').lower().strip('.')
            if not ext and blob.filename:
                # filenameから拡張子を抽出
                parts = blob.filename.rsplit('.', 1)
                if len(parts) > 1:
                    ext = parts[1].lower()
            if not ext:
                ext = '(なし)'

            extensions_all[ext] += 1

            if blob.date and blob.date < boundary:
                extensions_before[ext] += 1
            else:
                extensions_after[ext] += 1

        print("\n【全体の拡張子分布】")
        for ext, count in extensions_all.most_common(20):
            print(f"  {ext}: {count:,} 件")

        print("\n【2023/01/01 より前】")
        for ext, count in extensions_before.most_common(10):
            print(f"  {ext}: {count:,} 件")

        print("\n【2023/01/01 以降】")
        for ext, count in extensions_after.most_common(10):
            print(f"  {ext}: {count:,} 件")

        # 画像ファイルの割合
        image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
        image_count = sum(extensions_all[ext] for ext in image_exts)
        total_count = sum(extensions_all.values())

        print(f"\n【画像ファイルの割合】")
        print(f"  画像ファイル: {image_count:,} 件 ({image_count/total_count*100:.1f}%)")
        print(f"  その他: {total_count - image_count:,} 件 ({(total_count-image_count)/total_count*100:.1f}%)")

        # サイズ推定
        print("\n【推定ファイルサイズ】")
        print("  ※ 一般的な画像サイズ（100KB〜500KB）で推定")

        # 保守的な推定（平均200KB）
        avg_size_kb = 200
        estimated_total_mb = (image_count * avg_size_kb) / 1024
        estimated_total_gb = estimated_total_mb / 1024

        print(f"  平均200KB想定: 約 {estimated_total_gb:.1f} GB")

        # 大きめの推定（平均500KB）
        avg_size_kb = 500
        estimated_total_gb = (image_count * avg_size_kb) / 1024 / 1024
        print(f"  平均500KB想定: 約 {estimated_total_gb:.1f} GB")


if __name__ == '__main__':
    main()
