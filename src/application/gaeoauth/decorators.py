#!/usr/bin/env python
#:coding=utf-8:
#:mode=python:tabSize=2:indentSize=2:
#:noTabs=true:folding=explicit:collapseFolds=1:

# Copyright 2009 by Takashi Matsuo
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License. You may
# obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0 
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

import logging
import gaeoauth
#from django.http import HttpResponseForbidden, HttpResponse
#from google.appengine.dist import use_library
#use_library('django', '1.2')
from django.utils import simplejson

def request_must_be_signed(func):
  """
  A decorator for checking that opensocial request is signed. If the
  check fails, it just returns 403 http status code.
  """
  def wrap(request, *args, **kw):
    signed = getattr(request, gaeoauth.OS_SIGN_VERIFICATION_ATTRNAME)
    if signed:
      ret = func(request, *args, **kw)
      return ret
    else:
      message = 'The request was not signed properly.'
      logging.error(message)
      return HttpResponseForbidden(message)
  return wrap


def json_view(func):
  """
  A decorator for Ajax/JSON views. It was derived from smipple's
  json_view decorator but made a bit simpler.
  """
  def wrap(request, *a, **kw):
    response = None
    status = 200
    try:
      func_val = func(request, *a, **kw)
      assert isinstance(func_val, dict)
      response = dict(func_val)
      if 'result' not in response:
        response['result'] = 'ok'
      if response['result'] == 'ok':
        status = 200
      elif response['result'] == 'invalid':
        status = 403
      else:
        status = 500
    except KeyboardInterrupt:
      # Allow keyboard interrupts through for debugging.
      raise
    except Exception, e:
      status = 500
      # No matter what, we return JSON.
      if hasattr(e, 'message'):
        msg = e.message
      else:
        msg = _('Internal error')+': '+str(e)
        response = {'result': 'error',
                    'msg': msg}

    json = simplejson.dumps(response)
    # mimetype not application/json because IE is dumb
    return HttpResponse(json, status=status, mimetype='text/javascript')
  return wrap

