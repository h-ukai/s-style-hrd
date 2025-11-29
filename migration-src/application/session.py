#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
Session management for Google App Engine with Datastore and Redis backend.
Migrated from Python 2.7 to Python 3.11 with google.cloud.ndb

Another login utility sample on Google AppEngine : Session

Author    : OKAZAKI Hiroki (okaz@teshigoto.net, https://www.teshigoto.net/)
Version   : $Id: session.py,v 1.3 2009/02/10 04:33:51 okaz Exp $
Copyright : Copyright (c) 2009 OKAZAKI Hiroki
License   : Python
"""

import os
import re
import time
import random
import hashlib
from google.cloud import ndb
import redis

# Optional: Uncomment to use Redis for session caching
# redis_client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)


# REVIEW-L1: Fixed db.Expando → ndb.Expando migration (was ndb.Model)
# Changed: SessionDb must inherit from ndb.Expando to support dynamic properties
class SessionDb(ndb.Expando):
    """Session storage model using Datastore with dynamic properties support"""
    sid = ndb.StringProperty()


DEFAULT_SID_NAME = 'alu_001'


class Session():
    """Session management class for Flask"""

    def __init__(self, request, sid_name=DEFAULT_SID_NAME):
        """
        Initialize session

        Args:
            request: Flask request object
            sid_name: Session ID cookie name (default: 'alu_001')
        """
        self.sid_name = sid_name
        self.request = request
        if sid_name in request.cookies:
            self.sid_value = request.cookies[sid_name]
        else:
            self.sid_value = ''

    def new_ssn(self, ssl=False):
        """
        Create new session

        Args:
            ssl: Set Secure flag on cookie (default: False)

        Returns:
            Session ID string
        """
        if not self.sid_value:
            random.seed()
            random_str = str(random.random()) + str(random.random())
            random_str = random_str + str(time.time())
            random_str = random_str + self.request.remote_addr
            self.sid_value = hashlib.sha256(random_str.encode('utf-8')).hexdigest()

        # Create new session in Datastore
        ssn_db = SessionDb(sid=self.sid_value)
        ssn_db.put()

        # Optional: Cache in Redis
        # if redis_client:
        #     redis_client.set(self.sid_value, 'active', ex=86400)  # 24 hour expiry

        return self.sid_value

    def dbdelete(self):
        """Delete session from database"""
        if self.sid_value:
            # Delete from Datastore
            query = SessionDb.query(SessionDb.sid == self.sid_value)
            for ssn in query.fetch():
                ssn.key.delete()

            # Optional: Delete from Redis cache
            # if redis_client:
            #     redis_client.delete(self.sid_value)

    def destroy_ssn(self):
        """Destroy session"""
        self.dbdelete()
        self.sid_value = None
        return self.sid_value

    def get_ssn_data(self, k):
        """
        Get session data by key

        Args:
            k: Key name

        Returns:
            Value or None if not found
        """
        ssn = self.get_ssn()
        try:
            # REVIEW-L2: ndb.Model does not have _properties attribute like db.Expando
            # Use getattr() for dynamic properties instead
            rs = getattr(ssn, k, None)
        except Exception as e:
            # REVIEW-L2: Added specific exception handling with logging
            print(f"Error getting session data key '{k}': {e}")
            rs = None
        return rs

    def set_ssn_data(self, k, v):
        """
        Set session data

        Args:
            k: Key name
            v: Value
        """
        ssn = self.get_ssn()
        setattr(ssn, k, v)
        ssn.put()

        # Optional: Cache in Redis
        # if redis_client:
        #     redis_client.set(f"{self.sid_value}:{k}", str(v), ex=86400)

    def chk_ssn(self):
        """
        Check if session exists

        Returns:
            True if session exists, False otherwise
        """
        query = SessionDb.query(SessionDb.sid == self.sid_value)
        count = query.count()
        return count == 1

    def get_ssn(self):
        """
        Get session object

        Returns:
            SessionDb object
        """
        query = SessionDb.query(SessionDb.sid == self.sid_value)
        ssn_list = query.fetch(1)

        if ssn_list:
            ssn = ssn_list[0]
        else:
            # Create new session if not found
            ssn = SessionDb(sid=self.sid_value)
            ssn.put()

        return ssn
