#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re


"""
https://www.geocities.jp/m_hiroi/light/python04.html
https://abalone.ununu.org/archives/270
https://d.hatena.ne.jp/fgshun/20090204/1233761360
"""

class mailvalidation():
    _r = {}
    _r['esc'] = u'\\\\'
    _r['Period'] = u'\\.'
    _r['space'] = u'\x20'
    _r['OpenBR'] = u'\\['
    _r['CloseBR'] = u'\\]'
    _r['NonASCII'] = u'\x80-\uffff' # UCS-2
    #_r['NonASCII'] = u'\x80-\U0010ffff' # UCS-4
    _r['ctrl'] = u'\x00-\x1f'
    _r['CRlist'] = u'\x0a\x0d'
    _r['qtext'] = u'[^%(esc)s%(NonASCII)s%(CRlist)s"]' % _r
    _r['dtext'] = u'[^%(esc)s%(NonASCII)s%(CRlist)s%(OpenBR)s%(CloseBR)s]' % _r
    _r['quoted_pair'] = u'%(esc)s[^%(NonASCII)s]' % _r
    _r['atom_char'] = u'[^%(space)s<>@,;:".%(esc)s%(OpenBR)s%(CloseBR)s%(ctrl)s%(NonASCII)s]' % _r
    _r['atom'] = u'%(atom_char)s+(?!%(atom_char)s)' % _r
    _r['quoted_str'] = u'"%(qtext)s*(?:%(quoted_pair)s%(qtext)s*)*"' % _r
    _r['word'] = '(?:%(atom)s|%(quoted_str)s)' % _r
    _r['domain_ref'] = _r['atom']
    _r['domain_lit'] = u'%(OpenBR)s(?:%(dtext)s|%(quoted_pair)s)*%(CloseBR)s' % _r
    _r['sub_domain'] = u'(?:%(domain_ref)s|%(domain_lit)s)' % _r
    _r['domain'] = u'%(sub_domain)s(?:%(Period)s%(sub_domain)s)*' % _r
    _r['local_part'] = u'%(word)s(?:%(Period)s%(word)s)*' % _r
    _r['addr_spec'] = u'%(local_part)s@%(domain)s' % _r
    
    mail_regex = re.compile(_r['addr_spec'])
    
    def chk(self,mail):
        d = self.mail_regex.match(mail)
        if d:
            return d.group()
        else:
            return None