# -*- coding: utf-8 -*-

"""
email_decoder

License: The MIT License
Copyright (c) 2011 furyu-tei
"""

__author__ = 'furyutei@gmail.com'
__version__ = '0.0.1b'

import re
import urllib.parse
import logging
from email import message_from_string
from email.header import decode_header
from email.utils import getaddresses

DEBUG=True                  # False:  disable log() (wrapper of logging.debug())
DEBUG_LEVEL = logging.DEBUG # for logger

#{ // def log_except()
def log_except(*args):
  _log = logging.exception
  for arg in args:
    try:
      _log(arg)
    except Exception as s:
      try:
        logging.error('*** Error in log_except(): %s' % (str(s)))
      except:
        pass
    _log = logging.info

#} // end of log_except()


#{ // def log()
def log(*args):
  if not DEBUG: return
  for arg in args:
    try:
      logging.debug(arg)
    except Exception as s:
      try:
        logging.error('*** Error in log(): %s' % (str(s)))
      except:
        pass

#} end of def log()


#{ // class email_decoder()
class email_decoder(object):
  _mailaddr_key = {'from':True,'to':True,'cc':True,'bcc':True,'reply-to':True,'sender':True,}
  _one_line_key = {'subject':True,'date':True,}

  def __init__(self,mime_string='',decode_mime=True,decode_char=True):
    self._decode_mime = decode_mime
    self._decode_char = decode_char
    message = self.message = message_from_string(mime_string)
    msg_dic = self._dic = {
      'body':[],
      'html':[],
      'attachments':[],
    }
    mbody = msg_dic['body']
    mhtml = msg_dic['html']
    mattach = msg_dic['attachments']
    _decode = self._decode
    for part in message.walk():
      _ctype = part.get_content_type()
      #log('*** %s' % (_ctype))

      for _key in part.keys():
        _lkey = _key.lower()
        msg_dic.setdefault(_lkey,[])
        msg_dic[_lkey] += [_decode(_val) for _val in part.get_all(_key)]
        #log( u'%s = %s' % (_lkey, u', '.join(msg_dic[_lkey])) )

      if not part.is_multipart():
        payload = part.get_payload(decode=decode_mime)
        if decode_char:
          charset = part.get_content_charset(failobj=None)
          if charset:
            if isinstance(payload, bytes):
              payload = payload.decode(charset)
        if _ctype == 'text/plain':
          mbody.append(payload)
          #log(payload)
        elif _ctype == 'text/html':
          mhtml.append(payload)
          #log(payload)
        filename = part.get_filename(failobj=None)
        if filename:
          filename = _decode(filename)
          filename_ext = filename
          ctype_main = part.get_content_maintype()
          ctype_sub = part.get_content_subtype()
          if not re.search(r'\.[^.]*$',filename_ext) and ctype_sub:
            filename_ext = filename_ext + '.' + ctype_sub
          #log(u'filename=%s' % (filename))
          mattach.append({
            'filename': filename,
            'filename_ext': filename_ext,
            'ctype': _ctype,
            'ctype_main': ctype_main,
            'ctype_sub': ctype_sub,
            'payload': payload,
          })
    if 'sender' not in msg_dic and 'from' in msg_dic:
      msg_dic['sender'] = msg_dic['from']

    self._body = ''.join(mbody)
    self._html = ''.join(mhtml)

  def _decode(self,payload):
    if not self._decode_char:
      return payload
    _dclist = decode_header(payload)
    _texts = []
    for _dc,_code in _dclist:
      try:
        if _code:
          if isinstance(_dc, bytes):
            _dc = _dc.decode(encoding=_code)
        else:
          if isinstance(_dc, bytes):
            _dc = _dc.decode('utf-8')
      except Exception as s:
        log_except('email_decoder()._decode()',[_dc])
        try:
          _dc = urllib.parse.unquote(_dc)
          if isinstance(_dc, bytes):
            _dc = _dc.decode('utf-8')
        except Exception as s:
          log_except('email_decoder()._decode()',[_dc])
          if isinstance(_dc, bytes):
            _dc = _dc.decode('utf-8', errors='ignore')
      _texts.append(_dc)

    return ''.join(_texts)

  def __getattr__(self,name,*opt):
    name = name.lower()
    try:
      attr=super(email_decoder,self).__getattr__(name)
    except:
      if name not in self._dic:
        if len(opt) > 0:
          return opt[0]
        else:
          raise AttributeError(name)
      attr = self._dic.get(name)
      if self._mailaddr_key.get(name):
        all_addresses = getaddresses(attr)
        attr = '; '.join([_email for _realname,_email in all_addresses])
      if self._one_line_key.get(name):
        attr = ''.join(attr)
    return attr

  def is_decoded_mime(self):
    return self._decode_mime

  def is_decoded_char(self):
    return self._decode_char

  def get_original_message(self):
    return self.message

  def get_bodies(self,content_type='text'):
    if content_type=='text/plain':
      return self._body
    elif content_type=='text/html':
      return self._html
    else:
      return {'text/plain':self._body,'text/html':self._html}

  def get_body_plain(self):
    #return self.get_bodies('text/plain')
    return self._body

  def get_body_html(self):
    #return self.get_bodies('text/html')
    return self._html

  def bodies(self,content_type='text'):
    if content_type=='text/plain':
      return ('text/plain',self._body)
    elif content_type=='text/html':
      return ('text/html',self._html)
    else:
      return [('text/plain',self._body),('text/html',self._html)]

  def listaddr(self,name,address_only=True):
    name = name.lower()
    if name not in self._mailaddr_key or name not in self._dic:
      return []
    all_addresses = getaddresses(self._dic.get(name))
    if address_only:
      return [_email for _realname,_email in all_addresses]
    else:
      return all_addresses

  def listattr(self):
    return list(self._dic.keys())

#} // end of class email_decoder()

if __name__ == '__main__':
  import sys

  logging.getLogger().setLevel(DEBUG_LEVEL)

  mail_text = sys.stdin.read()
  mail = email_decoder(mail_text)

  print('[attribute-key list]')
  for _key in mail.listattr():
    print(_key)
  print('')

  subject = mail.subject
  print('[subject]')
  print(subject)
  print('')

  plaintext = mail.get_body_plain() # plaintext = mail.bodies(content_type='text/plain')[1]
  print('[body(plain text)]')
  print(plaintext)
  print('')

  html = mail.get_body_html()   # html = mail.bodies(content_type='text/html')[1]
  print('[html]')
  print(html)
  print('')

  from_list = mail.listaddr('from',address_only=False)
  print('[from]')
  for (_name,_addr) in from_list:
    if not _name: _name = _addr
    print('%s <%s>' % (_name, _addr))
  print('')

  to_list = mail.listaddr('to',address_only=False)
  print('[to]')
  for (_name,_addr) in to_list:
    if not _name: _name = _addr
    print('%s <%s>' % (_name, _addr))
  print('')

  cc_list = mail.listaddr('cc',address_only=False)
  print('[cc]')
  for (_name,_addr) in cc_list:
    if not _name: _name = _addr
    print('%s <%s>' % (_name, _addr))
  print('')

  print('[attachments]')
  attachments = mail.attachments
  for attachment in attachments:
    print('filename    : %s' % (attachment.get('filename')))
    print('filename.ext: %s' % (attachment.get('filename_ext')))
    print('ctype       : %s' % (attachment.get('ctype')))
    print('ctype_main  : %s' % (attachment.get('ctype_main')))
    print('ctype_sub   : %s' % (attachment.get('ctype_sub')))
    print('payload size: %d' % (len(attachment.get('payload'))))
    print('')

# ■ end of file
