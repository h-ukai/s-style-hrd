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

from appengine_django.models import BaseModel
from google.appengine.ext import db
from django.utils.translation import ugettext_lazy as _

# Create your models here.

def create_temporary_id(len=40):
  """
  Just create random id
  """
  import random
  return ''.join([chr(random.randint(0, 15) + ord('a')) for i in range(len)])

class OpenSocialUser(db.Model):
  """
  An opensocial user associated with the real user. Please create a
  new entity with key_name = 'domain:uid'.
  """
  associated_user = db.ReferenceProperty()
  domain = db.StringProperty(required=True)
  opensocial_uid = db.StringProperty(required=True)
  utime = db.DateTimeProperty(verbose_name=_("Updated"),
                              required=True, auto_now=True)
  ctime = db.DateTimeProperty(verbose_name=_("Joined"),
                              required=True, auto_now_add=True)

class OneTimePassCode(db.Model):
  """
  One time pass code used when associate a particular opensocial user
  to the real user. Please create a new entity with key_name = user.key().
  """
  associated_user = db.ReferenceProperty()
  otp_str = db.StringProperty()
  otp_valid_until = db.DateTimeProperty()

def gen_otp(user):
  """
  Generate one time pass code for the user and returns it.
  """
  import sha
  import datetime
  id = create_temporary_id()
  otp_str = sha.new(str(user.key())+id).hexdigest()
  otp_valid_until = datetime.datetime.now()+datetime.timedelta(
    seconds=3600)
  otp = OneTimePassCode.get_or_insert(key_name=str(user.key()),
                                      associated_user=user,
                                      otp_str=otp_str,
                                      otp_valid_until=otp_valid_until)
  otp.otp_str=otp_str
  otp.otp_valid_until=otp_valid_until
  otp.put()
  return otp

class ConsumerSecret(db.Model):
  consumer_key = db.StringProperty(required=True)
  consumer_secret = db.StringProperty(required=True)
