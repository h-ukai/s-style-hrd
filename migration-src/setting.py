# Python 3.11 では appstats は廃止されました
# Django ミドルウェアも不要です（Flask に移行するため）

# 注意:
# - AppStatsDjangoMiddleware は廃止
# - Flask では標準的な監視ツールとして Cloud Trace / Cloud Profiler を使用
# - Flask ミドルウェアが必要な場合は Flask の before_request / after_request デコレータを使用

MIDDLEWARE_CLASSES = (
    # 'google.appengine.ext.appstats.recording.AppStatsDjangoMiddleware',  # 廃止
)
