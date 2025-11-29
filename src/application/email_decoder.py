# -*- coding: utf-8 -*-

"""
email_decoder

License: The MIT License
Copyright (c) 2011 furyu-tei
"""

__author__ = 'furyutei@gmail.com'
__version__ = '0.0.1b'

import re
import urllib
import logging
from email import message_from_string
from email.Header import decode_header
from email.utils import getaddresses

DEBUG=True                  # False:  disable log() (wrapper of logging.debug())
DEBUG_LEVEL = logging.DEBUG # for logger

#{ // def log_except()
def log_except(*args):
  _log = logging.exception
  for arg in args:
    try:
      _log(arg)
    except Exception, s:
      try:
        logging.error(u'*** Error in log_except(): %s' % (unicode(s)))
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
    except Exception, s:
      try:
        logging.error(u'*** Error in log(): %s' % (unicode(s)))
      except:
        pass

#} end of def log()


#{ // class email_decoder()
class email_decoder(object):
  _mailaddr_key = {'from':True,'to':True,'cc':True,'bcc':True,'reply-to':True,'sender':True,}
  _one_line_key = {'subject':True,'date':True,}
  
  def __init__(self,mime_string=u'',decode_mime=True,decode_char=True):
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
            payload = unicode(payload,charset)
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
          if not re.search(u'\.[^.]*$',filename_ext) and ctype_sub:
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
    if not msg_dic.has_key('sender') and msg_dic.has_key('from'):
      msg_dic['sender'] = msg_dic['from']
    
    self._body = u''.join(mbody)
    self._html = u''.join(mhtml)
  
  def _decode(self,payload):
    if not self._decode_char:
      return payload
    _dclist = decode_header(payload)
    _texts = []
    for _dc,_code in _dclist:
      try:
        if _code:
          _dc = unicode(_dc,encoding=_code)
        else:
          _dc = unicode(_dc)
      except Exception, s:
        log_except(u'email_decoder()._decode()',[_dc])
        try:
          _dc = urllib.unquote(_dc).decode('utf-8')
        except Exception, s:
          log_except(u'email_decoder()._decode()',[_dc])
          _dc = unicode(_dc,errors='ignore')
      _texts.append(_dc)
    
    return u''.join(_texts)
  
  def __getattr__(self,name,*opt):
    name = name.lower()
    try:
      attr=super(email_decoder,self).__getattr__(name)
    except:
      if not self._dic.has_key(name):
        if 0<len(opt):
          return opt[0]
        else:
          raise AttributeError,name
      attr = self._dic.get(name)
      if self._mailaddr_key.get(name):
        all_addresses = getaddresses(attr)
        attr = u'; '.join([_email for _realname,_email in all_addresses])
      if self._one_line_key.get(name):
        attr = u''.join(attr)
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
    if not self._mailaddr_key.get(name) or not self._dic.has_key(name):
      return []
    all_addresses = getaddresses(self._dic.get(name))
    if address_only:
      return [_email for _realname,_email in all_addresses]
    else:
      return all_addresses
  
  def listattr(self):
    return self._dic.keys()

#} // end of class email_decoder()

if __name__ == '__main__':
  import sys
  
  logging.getLogger().setLevel(DEBUG_LEVEL)
  
  mail_text = sys.stdin.read()
  mail = email_decoder(mail_text)
  
  print u'[(attribute-key list)]'
  for _key in mail.listattr():
    print _key
  print u''
  
  subject = mail.subject
  print u'[subject]'
  print subject
  print u''
  
  plaintext = mail.get_body_plain() # plaintext = mail.bodies(content_type='text/plain')[1]
  print u'[body(plain text)]'
  print plaintext
  print u''
  
  html = mail.get_body_html()   # html = mail.bodies(content_type='text/html')[1]
  print u'[html]'
  print html
  print u''
  
  from_list = mail.listaddr('from',address_only=False)
  print u'[from]'
  for (_name,_addr) in from_list:
    if not _name: _name = _addr
    print u'%s <%s>' % (_name, _addr)
  print u''
  
  to_list = mail.listaddr('to',address_only=False)
  print u'[to]'
  for (_name,_addr) in to_list:
    if not _name: _name = _addr
    print u'%s <%s>' % (_name, _addr)
  print u''

  cc_list = mail.listaddr('cc',address_only=False)
  print u'[cc]'
  for (_name,_addr) in cc_list:
    if not _name: _name = _addr
    print u'%s <%s>' % (_name, _addr)
  print u''
  
  print u'[attachments]'
  attachments = mail.attachments
  for attachment in attachments:
    print u'filename    : %s' % (attachment.get('filename'))
    print u'filename.ext: %s' % (attachment.get('filename_ext'))
    print u'ctype       : %s' % (attachment.get('ctype'))
    print u'ctype_main  : %s' % (attachment.get('ctype_main'))
    print u'ctype_sub   : %s' % (attachment.get('ctype_sub'))
    print u'payload size: %d' % (len(attachment.get('payload')))
    print u''

# ■ end of file
