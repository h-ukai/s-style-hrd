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

from django.conf.urls.defaults import *

urlpatterns = patterns('gaeoauth.views',
  url(r'^otp$', 'create_otp', name='gaeoauth_create_otp'),
  url(r'^os_init$', 'os_init', name='gaeoauth_os_init'),
  url(r'^otp_post$', 'otp_post', name='gaeoauth_otp_post'),
)
