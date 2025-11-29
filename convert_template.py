#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
テンプレート変換スクリプト
Django/webapp2 テンプレート → Jinja2 テンプレート変換
"""

import re
import os
import sys

def convert_template(input_path, output_path):
    """テンプレートファイルを変換"""

    # ファイル読み込み
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. {% ifequal var "value" %} → {% if var == "value" %}
    # パターン: {% ifequal variable "string" %}
    content = re.sub(
        r'\{%\s*ifequal\s+(\S+)\s+"([^"]*)"\s*%\}',
        r'{% if \1 == "\2" %}',
        content
    )

    # パターン: {% ifequal variable 'string' %}
    content = re.sub(
        r"\{%\s*ifequal\s+(\S+)\s+'([^']*)'\s*%\}",
        r"{% if \1 == '\2' %}",
        content
    )

    # パターン: {% ifequal variable variable2 %}
    content = re.sub(
        r'\{%\s*ifequal\s+(\S+)\s+(\S+)\s*%\}',
        r'{% if \1 == \2 %}',
        content
    )

    # 2. {% endifequal %} → {% endif %}
    content = re.sub(
        r'\{%\s*endifequal\s*%\}',
        r'{% endif %}',
        content
    )

    # 3. {% ifnotequal var "value" %} → {% if var != "value" %}
    content = re.sub(
        r'\{%\s*ifnotequal\s+(\S+)\s+"([^"]*)"\s*%\}',
        r'{% if \1 != "\2" %}',
        content
    )

    content = re.sub(
        r"\{%\s*ifnotequal\s+(\S+)\s+'([^']*)'\s*%\}",
        r"{% if \1 != '\2' %}",
        content
    )

    # 4. {% endifnotequal %} → {% endif %}
    content = re.sub(
        r'\{%\s*endifnotequal\s*%\}',
        r'{% endif %}',
        content
    )

    # 5. {% comment %}...{% endcomment %} → {# ... #}
    content = re.sub(
        r'\{%\s*comment\s*%\}(.*?)\{%\s*endcomment\s*%\}',
        r'{# \1 #}',
        content,
        flags=re.DOTALL
    )

    # 6. {% extends variable %} → {% extends "variable.html" %} (引用符なしの場合)
    # ただし、既に引用符がある場合は変更しない
    content = re.sub(
        r'\{%\s*extends\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*%\}',
        r'{% extends "\1.html" %}',
        content
    )

    # 7. 絶対パス → 相対パス変換
    # /css/ → ../css/
    content = re.sub(r'href="/css/', r'href="../css/', content)
    content = re.sub(r'src="/css/', r'src="../css/', content)

    # /js/ → ../js/
    content = re.sub(r'href="/js/', r'href="../js/', content)
    content = re.sub(r'src="/js/', r'src="../js/', content)

    # /img/ → ../img/
    content = re.sub(r'href="/img/', r'href="../img/', content)
    content = re.sub(r'src="/img/', r'src="../img/', content)

    # /images/ → ../images/
    content = re.sub(r'href="/images/', r'href="../images/', content)
    content = re.sub(r'src="/images/', r'src="../images/', content)

    # /static/ → ../static/
    content = re.sub(r'href="/static/', r'href="../static/', content)
    content = re.sub(r'src="/static/', r'src="../static/', content)

    # url('/img/ → url('../img/
    content = re.sub(r"url\('/img/", r"url('../img/", content)
    content = re.sub(r'url\("/img/', r'url("../img/', content)

    # 8. .live() → .on() 変換 (jQuery)
    # $('selector').live('event', fn) → $(document).on('event', 'selector', fn)
    content = re.sub(
        r"\$\(['\"]([^'\"]+)['\"]\)\.live\(['\"]([^'\"]+)['\"],\s*function",
        r"$(document).on('\2', '\1', function",
        content
    )

    # 9. IE専用コード削除のためのマーカーを追加（手動確認用）
    # if(d.all) window.event.keyCode = 0 は削除せず、コメントを追加

    # 10. language="JavaScript" → type="text/javascript"
    content = re.sub(
        r'language\s*=\s*["\']?JavaScript["\']?',
        r'type="text/javascript"',
        content,
        flags=re.IGNORECASE
    )

    # 出力ディレクトリ作成
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # ファイル書き込み
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # 変更箇所のカウント
    changes = {
        'ifequal_to_if': len(re.findall(r'\{% if \S+ == ', content)) - len(re.findall(r'\{% if \S+ == ', original_content)),
        'path_changes': content.count('../css/') + content.count('../js/') + content.count('../img/') -
                       (original_content.count('../css/') + original_content.count('../js/') + original_content.count('../img/')),
    }

    return changes

def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_template.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    changes = convert_template(input_path, output_path)
    print(f"Converted: {input_path} -> {output_path}")
    print(f"Changes: {changes}")

if __name__ == '__main__':
    main()
