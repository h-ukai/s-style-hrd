#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
#from google.appengine.dist import use_library
#use_library('django', '1.2')

import webapp2

from application.login import Login, Logout
from application.regist import Regist, Confirm, Resign
from application.proc import Proc
from application.bkedit import BKEdit
from application.blobstoreutl import BlobstoreUtlHandler
from application.blobstoreutl import UploadHandler
from application.blobstoreutl import ServeHandler
from application import handler
from application.RemoveAll import RemoveAll
from application.uploadbkdata import BKdataupload
from application.uploadbkdataformaster import BKdatauploadformaster
from application.duplicationcheck import DuplicationCheck
from application.json import jsonservice
from application.memberedit import MemberEdit
from application.test import test
from application.bksearch import bksearch
from application.follow import follow
from application.mypage import mypage
from application.bkjoukyoulist import bkjoukyoulist
from application.bkdchk import bkdchk
from application.addresslist import addresslist
from application.show import Show
from application.mailinglist import mailinglist
from application.uploadaddressset import addresssetupload
from application.memberSearchandMail import memberSearchandMail
from application.memberSearchandMail import memberSearchandMailback
from application.memberSearchandMail  import mailsendback
from application.bksearchutl import filterWorker
from application.bksearchutl import filterWorker2
from application.cron import cronjobs
from application.sendmsg import Sendmsg
from application.email_receiver import MailHandler
from application.matching import matching
from application.matching import matchingworker
from application.matching import matchingtask
from application.matching import sendmailtask
from application.matching import sendmailworker
from application.messageManager import changetantoWorker
from application.messageManager import changetantotask
from application.tantochange import tantochange
from application.index import index

app=webapp2.WSGIApplication([
                                          ('/', index),
                                          ('/index.html', index),
                                          ('/logout', Logout),
                                          ('/login.html', Login),
                                          ('/login', Login),
                                          ('/regist', Regist),
                                          ('/confirm', Confirm),
                                          ('/resign', Resign),
                                          ('/bkedit.html', BKEdit),
                                          ('/csvupload/bkdata.html', BKdataupload),
                                          ('/csvupload/bkdataformaster.html', BKdatauploadformaster),
                                          ('/csvupload/addressset.html', addresssetupload),
                                          ('/duplicationcheck/bkdata.html',DuplicationCheck),
                                          ('/proc', Proc),
                                          ('/BlobstoreUtl/.*', BlobstoreUtlHandler),
                                          ('/upload/.*', UploadHandler),
                                          ('/serve/(.*)', ServeHandler),
                                          ('/FileUploadFormHandler', handler.FileUploadFormHandler),
                                          ('/FileUploadFormHandler/upload', handler.FileUploadHandler),
                                          ('/FileUploadFormHandler/generate_upload_url', handler.GenerateUploadUrlHandler),
                                          ('/FileUploadFormHandler/file/([0-9]+)', handler.FileInfoHandler),
                                          ('/FileUploadFormHandler/file/([0-9]+)/download', handler.FileDownloadHandler),
                                          ('/FileUploadFormHandler/file/([0-9]+)/success', handler.AjaxSuccessHandler),
                                          ('/show/.*', Show),
                                          ('/RemoveAll', RemoveAll),
                                          ('/jsonservice', jsonservice),
                                          ('/test', test),
                                          ('/memberedit/.*', MemberEdit),
                                          ('/bkjoukyoulist.html', bkjoukyoulist),
                                          ('/bkdchk.html', bkdchk),
                                          ('/bksearch/.*', bksearch),
                                          ('/follow/.*', follow),
                                          ('/mypage/.*', mypage),
                                          ('/addresslist.html', addresslist),
                                          ('/mailinglist.html',mailinglist),
                                          ('/tasks/mailinglistsend',memberSearchandMailback),
                                          ('/tasks/mailsendback',mailsendback),
                                          ('/tasks/filterWorker',filterWorker),
                                          ('/tasks/filterWorker2',filterWorker2),
                                          ('/tasks/changetantoWorker',changetantoWorker),
                                          ('/tasks/changetantotask',changetantotask),
                                          ('/cron/cronjobs',cronjobs),
                                          ('/memberSearchandMail/.*',memberSearchandMail),
                                          ('/_ah/mail/.*',MailHandler),
                                          ('/sendmsg/.*',Sendmsg),
                                          ('/matching/tasks/matchingworker',matchingworker),
                                          ('/matching/tasks/matchingtask',matchingtask),
                                          ('/matching/tasks/sendmailtask',sendmailtask),
                                          ('/matching/tasks/sendmailworker',sendmailworker),
                                          ('/matching/.*',matching),
                                          ('/tantochange/.*',tantochange)
                                           ],debug=True)
