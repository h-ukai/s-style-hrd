# -*- coding: utf-8 -*-

from google.appengine.api import taskqueue

"""
changetantoWorkerとchangetantotaskは循環参照を避けるためmessaageManagerの中に記述
"""

class chagetanto:
    #https://localhost:8080/tasks/changetantoWorker?corp_name=s-style&tantoID=3&oldtantoID=1
    @classmethod
    def tantoallchange(cls,corp,tantoID,oldtantoID):
        mytask = taskqueue.Queue('mintask')
        task = taskqueue.Task(url='/tasks/changetantoWorker', params={
                                                                          "corp_name":corp,
                                                                          "tantoID":tantoID,
                                                                          "oldtantoID":oldtantoID
                                                                          },target="memdb2")
        mytask.add(task)


    #https://localhost:8080/tasks/changetantotask?corp_name=s-style&mamberID=2&tantoID=3&oldtantoID=1
    @classmethod
    def tantochange(cls,corp,memberID,tantoID,oldtantoID):
        mytask = taskqueue.Queue('mintask')
        task = taskqueue.Task(url='/tasks/changetantotask', params={
                                                                          "corp_name":corp,
                                                                          "memberID":memberID,
                                                                          "tantoID":tantoID,
                                                                          "oldtantoID":oldtantoID
                                                                          },target="memdb2")
        mytask.add(task)


