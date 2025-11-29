# -*- coding: utf-8 -*-

#from google.appengine.ext import webapp
import webapp2

class backendsSterter(webapp2.RequestHandler):
    
    def post(self):
        mytask = taskqueue.Queue('mintask')
        if not msgkey:
            msgkey=""
        if not hnknngpL:
            hnknngpL = ""
        task = taskqueue.Task(url='/tasks/filterWorker', params={'sddbkey':str(sddb.key()),'msgkey':str(msgkey),'hnknngpL':hnknngpL},target="memdb")
        mytask.add(task)
        return sddb.name
    def get(cls):

