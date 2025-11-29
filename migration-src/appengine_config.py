# -*- coding: utf-8 -*-

# Python 3.11 では appengine_config.py は不要になりました
# appstats は廃止されており、代替として Cloud Trace と Cloud Profiler を使用します

# 注意:
# - webapp_add_wsgi_middleware() は webapp2 専用のため廃止
# - appstats は Google Cloud の標準監視ツールに置き換えられました
#   - Cloud Trace: リクエストのトレース
#   - Cloud Profiler: CPU/メモリプロファイル
#   - Cloud Monitoring: メトリクス収集
# - これらのサービスは自動的に統合されるため、コード変更は不要です

# 移行後の監視:
# 1. Cloud Trace: https://console.cloud.google.com/traces
# 2. Cloud Profiler: https://console.cloud.google.com/profiler
# 3. Cloud Monitoring: https://console.cloud.google.com/monitoring

# このファイルは互換性のために残していますが、実質的な処理はありません
