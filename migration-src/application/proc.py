#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""Another login utility sample on Google App Engine : Proc

Author    : OKAZAKI Hiroki (okaz@teshigoto.net, https://www.teshigoto.net/)
Version   : $Id: proc.py,v 1.3 2009/02/04 08:21:15 okaz Exp $
Copyright : Copyright (c) 2009 OKAZAKI Hiroki
License   : Python
"""
from flask import request, redirect, render_template
import application.view as view
import application.session as session


def proc_route():
    """
    Proc route handler (converted from webapp2.RequestHandler)

    Migrated from: webapp2.RequestHandler (Proc class)
    Original path: /proc
    """
    tmpl_val = {}
    tmpl_val['error_msg'] = ''

    # Get parameters from request (GET or POST)
    tmpl_val['corp_name'] = request.values.get('corp_name', '')
    tmpl_val['branch_name'] = request.values.get('branch_name', '')
    tmpl_val['sitename'] = request.values.get('sitename', '')

    # session management
    ssn = session.Session(request)
    if not ssn.chk_ssn():
        urlstr = "corp_name=" + tmpl_val['corp_name']
        urlstr = urlstr + "&branch_name=" + tmpl_val['branch_name']
        urlstr = urlstr + "&sitename=" + tmpl_val['sitename']
        urlstr = urlstr + "&togo=" + request.path
        return redirect('/login?' + urlstr)

    # main command processing here
    # REVIEW-L2: Unused variable 'output' - original code writes "proc" before template
    # Original: self.response.out.write("proc") then template.render()
    # Migrated: Both outputs were intended, but 'output' is not used in return
    # Recommendation: If "proc" output is needed, concatenate: return output + rendered_template
    output = "proc"

    # view rendering
    rendered_template = render_template('test.html', **tmpl_val)
    return rendered_template
