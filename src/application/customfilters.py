#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#

from django import template
from django.template.defaultfilters import stringfilter
import urllib

#register = webapp.template.create_template_register()
register = template.Library()

@register.filter
@stringfilter
def CP932(value):
    return value.encode('CP932')

@register.filter(name='urlencode2')
@stringfilter
def urlencode2(value, encoding):
    return urllib.quote_plus(value.encode(encoding))