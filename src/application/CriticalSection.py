# -*- coding: utf-8 -*-

from google.appengine.api import memcache
import time

# 例外
class CriticalSectionError(Exception):
  def __init__(self,value):
    self.value = value
  def __str__(self):
    return self.value

class CriticalSection(object):
    def __init__(self, key, namespace = None, autolock = False):
        self.key = key
        self.namespace = namespace
        self.locked = False
        if autolock:
            self.lock()
 
    def __del__(self):
        self.unlock()
 
    def lock(self):
        assert not self.locked
 
        # �ő僊�g���C 250ms * 60times = 15sec
        for retry in range(60):
            # �����Ń��b�N
            count = memcache.incr(key = self.key, namespace = self.namespace, initial_value = 0)
            if count == 1:
                self.locked = True
                return True
 
            memcache.decr(key = self.key, namespace = self.namespace)
 
            # 250ms �҂�
            time.sleep(0.25)
        CriticalSectionError(u"CriticalSection：Lock Exception ロック解除に失敗しました")
 
    def unlock(self):
        if self.locked:
            self.locked = False
            # �����ŃA�����b�N
            memcache.decr(key = self.key, namespace = self.namespace)