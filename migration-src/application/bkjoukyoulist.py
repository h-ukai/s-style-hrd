#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import render_template


class Bkjoukyoulist:
    """Handler for book situation list"""

    def get(self):
        tmpl_val = {}
        # Use render_template instead of template.render
        return render_template('bkjoukyoulist.html', **tmpl_val)

    def post(self):
        return self.get()


def bkjoukyoulist_route():
    """Flask route function for book situation list"""
    handler = Bkjoukyoulist()
    return handler.get()
