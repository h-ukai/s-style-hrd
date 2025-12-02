#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, render_template, jsonify
from application import session
import datetime

from application.models.member import member

DEFAULT_Auth_Day = 1


class dbsession(session.Session):
    """Database-backed session management with authentication"""

    def __init__(self, req=None, sid_name=session.DEFAULT_SID_NAME, sid=None):
        """
        Initialize database session

        Args:
            req: Flask request object (optional for backward compatibility)
            sid_name: Session ID cookie name
            sid: Specific session ID to use
        """
        if req is None:
            req = request  # Use Flask global request if not provided
        super().__init__(req, sid_name)
        if sid:
            self.setsid(sid)

    def chkauth(self, corp, branch, site):
        """
        Check authentication with time limit

        Args:
            corp: Corporation ID
            branch: Branch ID
            site: Site name

        Returns:
            True if authenticated and within time limit, False otherwise
        """
        if self.chk_ssn():  # セッションがある場合
            try:
                timelimit = self.get_ssn_data('timelimit')
                if not timelimit or timelimit < datetime.datetime.utcnow():
                    if self.getauth(self.getsid(), corp, branch, site):
                        return True
                    else:
                        return False
                else:
                    return True
            except:
                if self.getauth(self.getsid(), corp, branch, site):
                    return True
                else:
                    return False
        else:  # セッションがない場合
            self.new_ssn()
            return False

    def new_ssn(self, ssl=False):
        """Create new session"""
        self.dbdelete()
        result = super().new_ssn(ssl)
        # self.set_ssn_data('timelimit', datetime.datetime.utcnow() + datetime.timedelta(days=DEFAULT_Auth_Day))
        return self.getsid()

    def getsid(self):
        """Get current session ID"""
        if not self.sid_value:
            self.new_ssn()
            # self.set_ssn_data('timelimit', datetime.datetime.utcnow() + datetime.timedelta(days=DEFAULT_Auth_Day))
        return self.sid_value

    def setsid(self, sid):
        """Set specific session ID"""
        # REVIEW-L1: Python 2 comparison operator '<>' → Python 3 '!='
        # Fixed: Changed <> to !=
        if self.sid_value != sid:
            self.dbdelete()
            self.sid_value = sid
        self.new_ssn(ssl=False)
        # k = 'timelimit'
        # v = datetime.datetime.utcnow() + datetime.timedelta(days=DEFAULT_Auth_Day)
        # self.set_ssn_data(k, v)

    def getauth(self, sid, corp, branch, site):
        """
        Get authentication status from database

        Args:
            sid: Session ID
            corp: Corporation ID
            branch: Branch ID
            site: Site name

        Returns:
            True if user is authenticated, False otherwise
        """
        if not sid:
            sid = request.values.get("sid")
        if not corp:
            corp = request.values.get("corp")
        if not branch:
            branch = request.values.get("branch")
        if not site:
            site = request.values.get("site")

        data = None
        if sid and corp and site:
            # Query members using ndb
            # REVIEW-L2: Verify branch parameter handling - may be empty/None
            # Recommendation: Add branch filter only if branch is provided
            query = member.query(
                member.sid == sid,
                member.sitename == site,
                member.CorpOrg_key_name == corp,
                member.seiyaku == "未成約"
            )
            if branch:
                query = query.filter(member.Branch_Key_name == branch)
            data = query.fetch(1)

        if data:
            self.set_ssn_data('timelimit', datetime.datetime.utcnow() + datetime.timedelta(days=DEFAULT_Auth_Day))
            return True
        else:
            return False


class setsid_route():
    """
    Flask handler for setting session ID

    Note: This class represents the webapp2 RequestHandler (setsid).
    In Flask, this is typically implemented as a route function instead.
    See main.py for Flask @app.route implementation.
    """

    @staticmethod
    def handle_request(req=None):
        """Handle set session ID request"""
        if req is None:
            req = request

        sid = req.values.get("sid")
        tmpl_val = {}

        if sid:
            dssn = dbsession(req)
            if dssn.getsid() != sid:
                tmpl_val['sid'] = dssn.new_ssn(ssl=False)
                k = 'timelimit'
                v = datetime.datetime.utcnow() + datetime.timedelta(days=DEFAULT_Auth_Day)
                dssn.set_ssn_data(k, v)
            else:
                tmpl_val['sid'] = sid
        else:
            tmpl_val['sid'] = ''

        # Set P3P header for cross-domain cookie access
        response_headers = {
            'p3p': 'CP="CAO PSA OUR"',
            'Content-Type': 'text/html; charset=utf-8'
        }

        html_content = f"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "https://www.w3.org/TR/html4/loose.dtd">
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf8">
        <title>auth_iframe_contents</title>
        </head>
        <body>
        sid = {tmpl_val['sid']}
        </body>
        </html>
        """

        return html_content, response_headers
