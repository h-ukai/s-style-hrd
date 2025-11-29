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

from decorators import request_must_be_signed, json_view
from models import gen_otp, OneTimePassCode, OpenSocialUser
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import logging
import datetime

def get_template(base, name):
  if base is None:
    return name
  import os
  return os.path.join(base, name)

@request_must_be_signed
@json_view
def otp_post(request, template_base=None):
  """
  Handle post data that includes one time passcode and email from
  opensocial application.
  """
  query = OneTimePassCode.all().filter('otp_str =', request.POST.get('otp'))
  if query.count() > 1:
    logging.warn('Handler otp_post: Query count is larger than 1.')
  otp = query.get()
  if otp is None:
    message = 'No such One Time Passcode.'
    logging.warn(message)
    return {'authorized': False, 'message': message}
  if otp.otp_valid_until < datetime.datetime.now():
    message = 'One Time Passcode timeout.'
    logging.warn(message)
    return {'authorized': False, 'message': message}
  email = request.POST.get('email')
  if otp.associated_user.email != email:
    message = 'Email does not match.'
    logging.warn(message)
    return {'authorized': False, 'message': message}
  domain = request.REQUEST.get('domain')
  os_uid = request.REQUEST.get('opensocial_viewer_id')
  os_user = OpenSocialUser.get_or_insert(key_name=domain+':'+os_uid,
                                         domain=domain,
                                         opensocial_uid=os_uid)
  os_user.associated_user = otp.associated_user
  os_user.put()
  return {'authorized': True, 'username': os_user.associated_user.display_name}
  
@request_must_be_signed
@json_view
def os_init(request, template_base=None):
  """
  Opensocial app initialize.
  """
  logging.debug('Signed: %s' % request.is_os_signature_valid)
  if request.user.is_authenticated():
    return {'authorized': True, 'username': '%s' %
            request.user.display_name}
  else:
    return {'authorized': False}

@login_required
def create_otp(request, template_base=None):
  """
  Create one time passcode for associating opensocial user with real user.
  """
  otp = gen_otp(request.user)
  return direct_to_template(request, get_template(template_base, 'otp.tpl'),
                            { 'otp': otp.otp_str })

