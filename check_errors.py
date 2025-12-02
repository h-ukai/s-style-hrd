#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome DevTools Protocolを使用してページのエラーを収集するスクリプト
"""

import json
import requests
import websocket
import time
import sys

def get_target():
    """現在のChromeターゲットを取得"""
    response = requests.get('http://localhost:9222/json/list')
    targets = response.json()
    if not targets:
        # 新しいタブを作成
        response = requests.get('http://localhost:9222/json/new?about:blank')
        target = response.json()
        return target['webSocketDebuggerUrl']
    return targets[0]['webSocketDebuggerUrl']

def send_command(ws, method, params=None):
    """Chrome DevTools Protocolコマンドを送信"""
    command_id = int(time.time() * 1000000) % 1000000
    command = {
        'id': command_id,
        'method': method,
        'params': params or {}
    }
    ws.send(json.dumps(command))
    return command_id

def wait_for_response(ws, command_id, timeout=10):
    """コマンドのレスポンスを待機"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            message = json.loads(ws.recv())
            if message.get('id') == command_id:
                return message.get('result', {})
        except:
            pass
    return None

def collect_errors(url):
    """指定URLのエラーを収集"""
    ws_url = get_target()
    ws = websocket.create_connection(ws_url)

    console_messages = []
    network_errors = []

    try:
        # コンソールとネットワークを有効化
        send_command(ws, 'Console.enable')
        send_command(ws, 'Network.enable')
        send_command(ws, 'Log.enable')
        send_command(ws, 'Runtime.enable')

        time.sleep(0.5)

        # ページにナビゲート
        cmd_id = send_command(ws, 'Page.navigate', {'url': url})
        wait_for_response(ws, cmd_id)

        # ページ読み込み完了を待機（最大30秒）
        print(f"ページ読み込み中: {url}", file=sys.stderr)
        start_time = time.time()
        page_loaded = False

        while time.time() - start_time < 30:
            try:
                ws.settimeout(1)
                message_str = ws.recv()
                message = json.loads(message_str)

                # コンソールメッセージを収集
                if message.get('method') == 'Console.messageAdded':
                    msg = message.get('params', {}).get('message', {})
                    if msg.get('level') in ['error', 'warning']:
                        console_messages.append({
                            'level': msg.get('level'),
                            'text': msg.get('text', ''),
                            'url': msg.get('url', ''),
                            'line': msg.get('line', 0)
                        })

                # ネットワークエラーを収集
                if message.get('method') == 'Network.responseReceived':
                    response = message.get('params', {}).get('response', {})
                    status = response.get('status', 0)
                    if status >= 400:
                        network_errors.append({
                            'url': response.get('url', ''),
                            'status': status,
                            'statusText': response.get('statusText', '')
                        })

                # ページ読み込み完了を検出
                if message.get('method') == 'Page.loadEventFired':
                    page_loaded = True
                    print("ページ読み込み完了", file=sys.stderr)
                    # 読み込み後、追加のエラーを収集
                    time.sleep(2)
                    break

            except websocket.WebSocketTimeoutException:
                if page_loaded:
                    break
                continue
            except Exception as e:
                print(f"エラー: {e}", file=sys.stderr)
                break

    finally:
        ws.close()

    return {
        'console_messages': console_messages,
        'network_errors': network_errors
    }

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://s-style-hrd.appspot.com/test/'
    errors = collect_errors(url)
    print(json.dumps(errors, ensure_ascii=False, indent=2))
