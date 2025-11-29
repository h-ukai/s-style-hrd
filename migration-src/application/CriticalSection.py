# -*- coding: utf-8 -*-

import redis
import time

# Redis client initialization (should be configured with your Redis instance)
# For Cloud Memorystore: host='10.x.x.x', port=6379
# For local development: host='localhost', port=6379
try:
  redis_client = redis.Redis(host='redis-host', port=6379, decode_responses=True)
except:
  # Fallback for development
  redis_client = None

# Exception
class CriticalSectionError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return str(self.value)

class CriticalSection(object):
    def __init__(self, key, namespace=None, autolock=False):
        self.key = key
        self.namespace = namespace
        self.locked = False
        if self.namespace:
            self.full_key = f"{self.namespace}:{self.key}"
        else:
            self.full_key = self.key
        if autolock:
            self.lock()

    def __del__(self):
        self.unlock()

    def lock(self):
        assert not self.locked

        # Maximum retry time: 250ms * 60 times = 15 seconds
        for retry in range(60):
            try:
                if redis_client is None:
                    raise CriticalSectionError("Redis client not available")

                # Use Redis INCR for atomic increment
                count = redis_client.incr(self.full_key)
                if count == 1:
                    # Set expiration to prevent deadlock (15 seconds)
                    redis_client.expire(self.full_key, 15)
                    self.locked = True
                    return True
                else:
                    # Decrement since we failed to acquire lock
                    redis_client.decr(self.full_key)

                # Wait 250ms before retrying
                time.sleep(0.25)
            except Exception as e:
                raise CriticalSectionError(f"Lock failed: {str(e)}")
        raise CriticalSectionError("CriticalSection: Lock timeout after 15 seconds")

    def unlock(self):
        if self.locked:
            self.locked = False
            try:
                if redis_client:
                    # Decrement to release lock
                    redis_client.decr(self.full_key)
            except Exception as e:
                # Log but don't raise on unlock errors
                pass
