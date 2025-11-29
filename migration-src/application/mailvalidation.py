#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re


"""
https://www.geocities.jp/m_hiroi/light/python04.html
https://abalone.ununu.org/archives/270
https://d.hatena.ne.jp/fgshun/20090204/1233761360

Migration Notes:
- u'...' → '...'（Python 3 では全て Unicode）
- 正規表現パターンはそのまま使用可能
"""


class mailvalidation():
    """メールアドレス検証クラス

    RFC に基づいたメールアドレス形式の正規表現によるチェック
    """

    _r = {}
    _r['esc'] = '\\\\'
    _r['Period'] = '\\.'
    _r['space'] = '\x20'
    _r['OpenBR'] = '\\['
    _r['CloseBR'] = '\\]'
    _r['NonASCII'] = '\x80-\uffff'  # UCS-2
    # _r['NonASCII'] = u'\x80-\U0010ffff' # UCS-4
    _r['ctrl'] = '\x00-\x1f'
    _r['CRlist'] = '\x0a\x0d'
    _r['qtext'] = '[^%(esc)s%(NonASCII)s%(CRlist)s"]' % _r
    _r['dtext'] = '[^%(esc)s%(NonASCII)s%(CRlist)s%(OpenBR)s%(CloseBR)s]' % _r
    _r['quoted_pair'] = '%(esc)s[^%(NonASCII)s]' % _r
    _r['atom_char'] = '[^%(space)s<>@,;:".%(esc)s%(OpenBR)s%(CloseBR)s%(ctrl)s%(NonASCII)s]' % _r
    _r['atom'] = '%(atom_char)s+(?!%(atom_char)s)' % _r
    _r['quoted_str'] = '"%(qtext)s*(?:%(quoted_pair)s%(qtext)s*)*"' % _r
    _r['word'] = '(?:%(atom)s|%(quoted_str)s)' % _r
    _r['domain_ref'] = _r['atom']
    _r['domain_lit'] = '%(OpenBR)s(?:%(dtext)s|%(quoted_pair)s)*%(CloseBR)s' % _r
    _r['sub_domain'] = '(?:%(domain_ref)s|%(domain_lit)s)' % _r
    _r['domain'] = '%(sub_domain)s(?:%(Period)s%(sub_domain)s)*' % _r
    _r['local_part'] = '%(word)s(?:%(Period)s%(word)s)*' % _r
    _r['addr_spec'] = '%(local_part)s@%(domain)s' % _r

    mail_regex = re.compile(_r['addr_spec'])

    def chk(self, mail):
        """メールアドレスの検証

        Args:
            mail: チェック対象のメールアドレス文字列

        Returns:
            マッチした文字列、または None（マッチしない場合）
        """
        d = self.mail_regex.match(mail)
        if d:
            return d.group()
        else:
            return None
