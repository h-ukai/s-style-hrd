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
import pubkey
from Crypto.PublicKey import RSA
import oauth
import gaeoauth
import hashlib
import urllib
import base64
from models import OpenSocialUser

def add_element_gently(key, val, params):
  """
  If params already has the key, value will be stored as list.
  """
  if params.has_key(key):
    if isinstance(params[key], list):
      params[key].append(val)
    else:
      params[key] = [params[key], val]
  else:
    params[key] = val
  return params

def create_oauth_params_from_request(request):
  """
  Aggregates the parameters in both GET and POST.
  """
  params = {}
  for key, val in request.GET.iteritems():
    params = add_element_gently(key, val, params)
  for key, val in request.POST.iteritems():
    params = add_element_gently(key, val, params)
  return params

class OpenSocialVerifySignatureMiddleware(object):
  """
  This is a middleware that verify the signature from opensocial
  container if any. Set request.is_os_signature_valid == True when the
  signature is successfully verified.  To use this middleware, please
  don't forget to append 'domain' parameter in the query string when
  creating the request in your opensocial application. Just for our
  convenience, verification always succeed if the app runs on
  localhost.
  """
  def verify_signature_RSA(self, request):
    """
    The implementation that do the actual verification when signature
    method is 'RSA-SHA1'.
    """
    domain = request.REQUEST.get('domain')
    key_data = pubkey.keys.get(domain)
    if key_data is None:
      logging.warn("We don't have the key for domain: %s." % domain)
      return False
    public_key = RSA.construct((long(key_data.get('public_key_str'), 16),
                               key_data.get('exponent')))
    params = create_oauth_params_from_request(request)
    oauth_request = oauth.OAuthRequest(
      http_method=request.method,
      http_url=request.build_absolute_uri(),
      parameters=params)
    message = '&'.join(
      (oauth.escape(oauth_request.get_normalized_http_method()),
       oauth.escape(oauth_request.get_normalized_http_url()),
       oauth.escape(oauth_request.get_normalized_parameters()),))
    local_hash = hashlib.sha1(message).digest()
    # Apply the public key to the signature from the remote host
    sig = base64.decodestring(urllib.unquote(
      request.REQUEST.get("oauth_signature")))
    remote_hash = public_key.encrypt(sig, '')[0][-20:]

    # Verify that the locally-built value matches the value from the
    # remote server.
    if local_hash==remote_hash:
      return True
    else:
      return False
  
  def verify_signature_HMAC(self, request):
    """
    The implementation that do the actual verification when signature
    method is 'HMAC-SHA1'.
    """
    import time
    from models import ConsumerSecret
    class MockConsumer:
      def __init__(mock, secret):
        mock.secret = secret

    consumer_key = self.request.get("oauth_consumer_key")
    query = ConsumerSecret.all.filter('consumer_key =', consumer_key)
    if query.count() != 1:
      logging.warn('Query result count is not 1, but continued.')
    consumer_secret = query.get()
    if consumer_secret is None:
      logging.warn("Cannot get consumer secret from the Datastore.")
      return False
    secret = consumer_secret.consumer_secret
    params = create_oauth_params_from_request(request)
    oauth_request = oauth.OAuthRequest(
      http_method=request.method,
      http_url=request.build_absolute_uri(),
      parameters=params)
    timestamp, nonce = oauth_request._get_timestamp_nonce()
    timestamp_allowance = 1000 * 60 * 5
    timestamp = int(timestamp)
    now = int(time.time())
    difference = now - timestamp
    if difference > timestamp_allowance:
      logging.warn("Failed to check timestamp.")
      return False
    signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
    signature = request.REQUEST.get('oauth_signature')
    built = signature_method.build_signature(
      oauth_request, MockConsumer(secret), oauth.OAuthToken('', ''))
    if signature != built:
      logging.warn("Failed to verify signature.")
      return False
    logging.debug("Succeeded to verify signature.")
    return True
  
  def process_request(self, request):
    """
    When working in local development environment, it will always
    return True. After that, just dispatching to the real
    implementation according to the signature method of the request.
    """
    status = False
    method = request.REQUEST.get('oauth_signature_method')
    if request.META['SERVER_SOFTWARE'].startswith('Development') and \
       request.META['SERVER_NAME'] == 'localhost' and \
       method is not None:
      status = True
    elif method == 'RSA-SHA1':
      status = self.verify_signature_RSA(request)
    elif method == 'HMAC-SHA1':
      status = self.verify_signature_HMAC(request)
    elif method is None:
      pass
    else:
      raise NotImplementedError("The method is not implemented: %s." % method)
    if status == True:
      domain = request.REQUEST.get('domain')
      os_uid = request.REQUEST.get('opensocial_viewer_id')
      os_user = OpenSocialUser.get_by_key_name(domain+':'+os_uid)
      if os_user and os_user.associated_user is not None:
        setattr(request, 'user', os_user.associated_user)
    setattr(request, gaeoauth.OS_SIGN_VERIFICATION_ATTRNAME, status)
