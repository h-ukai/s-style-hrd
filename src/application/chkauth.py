#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#from google.appengine.ext import webapp
import webapp2
import session
import datetime

from models.member import member

DEFAULT_Auth_Day = 1

class dbsession(session.Session):

    def __init__(self, req, res, sid_name = session.DEFAULT_SID_NAME,sid=None):
        session.Session.__init__(self,req, res, sid_name)
        if sid:
            self.setsid(sid)

    def chkauth(self, corp, branch, site):
        if self.chk_ssn() : #セッションがある場合
            try:
                timelimit = self.get_ssn_data('timelimit')
                if not timelimit or timelimit < datetime.datetime.utcnow():
                    if self.getauth(self.getsid(),corp,branch,site):
                        return True
                    else:
                        return False
                else:
                    return True
            except:
                if self.getauth(self.getsid(),corp,branch,site):
                    return True
                else:
                    return False

        else: #セッションがない場合
            self.new_ssn()
            return False

    def new_ssn(self, ssl=False):
        self.dbdelete()
        session.Session.new_ssn(self,ssl)
#        self.set_ssn_data('timelimit',datetime.datetime.utcnow() + datetime.timedelta(DEFAULT_Auth_Day))
        return self.getsid

    def getsid(self):
        if not self.sid_value:
            self.new_ssn()
#            self.set_ssn_data('timelimit',datetime.datetime.utcnow() + datetime.timedelta(DEFAULT_Auth_Day))
        return self.sid_value

    def setsid(self,sid):
        if self.sid_value <> sid:
            self.dbdelete()
            self.sid_value = sid
        self.new_ssn(ssl=False)
#        k = 'timelimit'
#        v = datetime.datetime.utcnow() + datetime.timedelta(DEFAULT_Auth_Day)
#        self.set_ssn_data(k, v)

    def getauth(self,sid,corp,branch,site):
#       gql.filter(" co = " ,corp)
        if not sid:
            sid = self.req.get("sid")
        if not corp:
            corp = self.req.get("corp")
        if not branch:
            branch = self.req.get("branch")
        if not site:
            site = self.req.get("site")
        data = None
        if sid and corp and site:
            gql = member.all()
            gql.filter(" sid = " ,sid)
            gql.filter(" sitename = " ,site)
            gql.filter(" Branch_Key_name = " ,branch)
            gql.filter(" CorpOrg_key_name = " ,corp)
            gql.filter(" seiyaku = ",u"未成約")
            data = gql.fetch(1)
        if data:
            self.set_ssn_data('timelimit',datetime.datetime.utcnow() + datetime.timedelta(DEFAULT_Auth_Day))
            return True
        else :
            return False


    """
    def getauth(self):
        url = config.DATABASE_URL + "/jsonservice?com=chkAuthbysid&corp=s-style&site=www.chikusaku-mansion.com&sid=" + self.sid_value
        res = urlfetch.fetch( url = url, method=urlfetch.GET,
        deadline=120 ,
        headers={'Content-Type': 'application/x-www-form-urlencoded',
                 'User-Agent': 'www.chikusaku-mansion'} )
        strbuf = str(res.content)
        if re.search('error', strbuf) == None and re.search('Error', strbuf) == None :
            resdic = json.loads(res.content)
            if resdic.get("Auth") == "True":
                self.Set_ssn_data('timelimit',datetime.datetime.utcnow() + datetime.timedelta(DEFAULT_Auth_Day))
                return True
            else:
                return False
        return False
    """
class setsid(webapp2.RequestHandler):
    def get(self):
        self.post()
    def post(self):
        sid = self.request.get("sid")
        self.tmpl_val = {}
        if sid:
            dssn = dbsession(self.request,self.response)
            if dssn.getsid() <> sid:
                self.tmpl_val['sid'] = dssn.new_ssn(ssl=False, sid=sid)
                k = 'timelimit'
                v = datetime.datetime.utcnow() + datetime.timedelta(DEFAULT_Auth_Day)
                dssn.set_ssn_data(k, v)
            else:
                self.tmpl_val['sid'] = sid
        else:
            self.tmpl_val['sid'] = ''

        self.response.headers['p3p']=str('CP="CAO PSA OUR"')
        """
        #Set-Cookie とかの処理
        2self.response.headers.add_header(
        3    "P3P",
        4    "CP=CAO PSA OUR"
        5)

        """
        str = u"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "https://www.w3.org/TR/html4/loose.dtd">
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf8">
        <title>auth_iframe_contents</title>
        </head>
        <body>
        sid =""" + self.tmpl_val['sid'] + u"""
        </body>
        </html>
        """
        self.response.out.write(str)