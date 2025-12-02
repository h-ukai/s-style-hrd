#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import json
from google.cloud import ndb
import datetime
import time
from decimal import Decimal
import locale
from application import timemanager

class GqlJsonEncoder(json.JSONEncoder):
    """Extends JSONEncoder to add support for NDB results and properties."""

    fieldname = ""
    floatformat = ""

    def default(self, obj):
        """Tests the input object, obj, to encode as JSON."""
        if hasattr(obj, '__json__'):
            return getattr(obj, '__json__')()

        if isinstance(obj, ndb.Query):
            return list(obj)

        elif isinstance(obj, ndb.Model):
            properties = {}
            for field in obj._properties:
                try:
                    v = getattr(obj, field)
                except:
                    continue

                if v:
                    if isinstance(v, ndb.Model):
                        v = str(v.key.urlsafe().decode())
                    if not self.floatformat == "false" and isinstance(v, float):
                        v = self.floatfmt(v)
                    if self.fieldname == "normal":
                        properties[field] = v
                    else:
                        properties[field] = v

            return properties

        elif isinstance(obj, ndb.Key):
            return str(obj.urlsafe().decode())

        elif isinstance(obj, ndb.GeoPt):
            output = str(getattr(obj, "lat")) + "," + str(getattr(obj, "lon"))
            return output

        elif isinstance(obj, datetime.datetime):
            output = timemanager.utc2jst_date(obj).strftime("%Y/%m/%d %H:%M:%S")
            return output

        elif isinstance(obj, time.struct_time):
            return list(obj)

        return json.JSONEncoder.default(self, obj)

    @classmethod
    def moneyfmt(cls, value, places=2, curr='', sep=',', dp='.',
                 pos='', neg='-', trailneg=''):
        if not value:
            return ""
        """Convert Decimal to currency string representation.
        places:  Number of digits after decimal point
        curr:    Currency symbol (optional)
        sep:     Thousands separator (optional)
        dp:      Decimal point (comma or period)
        pos:     Sign for positive numbers
        neg:     Sign for negative numbers
        trailneg: Trailing negative sign
        """
        value = Decimal(str(value))
        q = Decimal((0, (1,), -places))
        sign, digits, exp = value.quantize(q).as_tuple()
        assert exp == -places
        result = []
        digits = list(map(str, digits))
        build, next = result.append, digits.pop

        if sign:
            build(trailneg)
        for i in range(places):
            if digits:
                build(next())
            else:
                build('0')
        build(dp)
        i = 0
        while digits:
            build(next())
            i += 1
            if i == 3 and digits:
                i = 0
                build(sep)
        build(curr)
        if sign:
            build(neg)
        else:
            build(pos)
        result.reverse()
        return ''.join(result)

    @classmethod
    def GQLmoneyfmt(cls, gql):
        if not gql:
            return ""
        output = {}
        for field in gql._properties:
            v = getattr(gql, field)
            if v:
                if isinstance(v, float):
                    v = cls.floatfmt(v)
                output[field] = v

        return output

    @classmethod
    def GQLtimeandmoneyfmt(cls, gql):
        if not gql:
            return ""
        output = {}
        for field in gql._properties:
            v = getattr(gql, field)
            if v:
                if isinstance(v, float):
                    v = cls.floatfmt(v)
                elif isinstance(v, datetime.datetime):
                    v = timemanager.utc2jst_date(v)
                output[field] = v
        return output

    @classmethod
    def floatfmt(cls, num):
        result = ""
        mark = ""
        if num:
            nums = str(num).split(".")[0]
            # REVIEW-L3: 提案: 数値処理の堅牢性向上
            # 推奨: locale.format や格式文字列の活用で可読性向上
            if nums and (nums[0] == "+" or nums[0] == "-"):
                mark = nums[0]
                nums = nums[1:]
            for i, e in enumerate(reversed(nums)):
                if not i == 0 and i % 3 == 0:
                    result = e + "," + result
                else:
                    result = e + result
            if len(str(num).split(".")) == 2:
                if int(str(num).split(".")[1]):
                    result = result + "." + str(int(str(num).split(".")[1]))
        return mark + result

    @classmethod
    def floatfmt2(cls, num):
        if num:
            locale.setlocale(locale.LC_ALL, "")
            if len(str(num).split(".")) == 2:
                if int(str(num).split(".")[1]):
                    result = locale.format("%.3f", num, grouping=True)
                else:
                    result = locale.format("%.3d", num, grouping=True)
            else:
                result = locale.format("%.3d", num, grouping=True)
        return result

def JsonEncode(input):
    """
    Encode an input NDB object as JSON

    Args:
      input: A NDB object or DB property.

    Returns:
      A JSON string based on the input object.

    Raises:
      TypeError: Typically occurs when an input object contains an unsupported
        type.
    """
    return GqlJsonEncoder().encode(input)
