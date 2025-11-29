from json.tests import PyTest, CTest

# 2007-10-05
JSONDOCS = [
    # https://json.org/JSON_checker/test/fail1.json
    '"A JSON payload should be an object or array, not a string."',
    # https://json.org/JSON_checker/test/fail2.json
    '["Unclosed array"',
    # https://json.org/JSON_checker/test/fail3.json
    '{unquoted_key: "keys must be quoted"}',
    # https://json.org/JSON_checker/test/fail4.json
    '["extra comma",]',
    # https://json.org/JSON_checker/test/fail5.json
    '["double extra comma",,]',
    # https://json.org/JSON_checker/test/fail6.json
    '[   , "<-- missing value"]',
    # https://json.org/JSON_checker/test/fail7.json
    '["Comma after the close"],',
    # https://json.org/JSON_checker/test/fail8.json
    '["Extra close"]]',
    # https://json.org/JSON_checker/test/fail9.json
    '{"Extra comma": true,}',
    # https://json.org/JSON_checker/test/fail10.json
    '{"Extra value after close": true} "misplaced quoted value"',
    # https://json.org/JSON_checker/test/fail11.json
    '{"Illegal expression": 1 + 2}',
    # https://json.org/JSON_checker/test/fail12.json
    '{"Illegal invocation": alert()}',
    # https://json.org/JSON_checker/test/fail13.json
    '{"Numbers cannot have leading zeroes": 013}',
    # https://json.org/JSON_checker/test/fail14.json
    '{"Numbers cannot be hex": 0x14}',
    # https://json.org/JSON_checker/test/fail15.json
    '["Illegal backslash escape: \\x15"]',
    # https://json.org/JSON_checker/test/fail16.json
    '[\\naked]',
    # https://json.org/JSON_checker/test/fail17.json
    '["Illegal backslash escape: \\017"]',
    # https://json.org/JSON_checker/test/fail18.json
    '[[[[[[[[[[[[[[[[[[[["Too deep"]]]]]]]]]]]]]]]]]]]]',
    # https://json.org/JSON_checker/test/fail19.json
    '{"Missing colon" null}',
    # https://json.org/JSON_checker/test/fail20.json
    '{"Double colon":: null}',
    # https://json.org/JSON_checker/test/fail21.json
    '{"Comma instead of colon", null}',
    # https://json.org/JSON_checker/test/fail22.json
    '["Colon instead of comma": false]',
    # https://json.org/JSON_checker/test/fail23.json
    '["Bad value", truth]',
    # https://json.org/JSON_checker/test/fail24.json
    "['single quote']",
    # https://json.org/JSON_checker/test/fail25.json
    '["\ttab\tcharacter\tin\tstring\t"]',
    # https://json.org/JSON_checker/test/fail26.json
    '["tab\\   character\\   in\\  string\\  "]',
    # https://json.org/JSON_checker/test/fail27.json
    '["line\nbreak"]',
    # https://json.org/JSON_checker/test/fail28.json
    '["line\\\nbreak"]',
    # https://json.org/JSON_checker/test/fail29.json
    '[0e]',
    # https://json.org/JSON_checker/test/fail30.json
    '[0e+]',
    # https://json.org/JSON_checker/test/fail31.json
    '[0e+-1]',
    # https://json.org/JSON_checker/test/fail32.json
    '{"Comma instead if closing brace": true,',
    # https://json.org/JSON_checker/test/fail33.json
    '["mismatch"}',
    # https://code.google.com/p/simplejson/issues/detail?id=3
    u'["A\u001FZ control characters in string"]',
]

SKIPS = {
    1: "why not have a string payload?",
    18: "spec doesn't specify any nesting limitations",
}

class TestFail(object):
    def test_failures(self):
        for idx, doc in enumerate(JSONDOCS):
            idx = idx + 1
            if idx in SKIPS:
                self.loads(doc)
                continue
            try:
                self.loads(doc)
            except ValueError:
                pass
            else:
                self.fail("Expected failure for fail{0}.json: {1!r}".format(idx, doc))

    def test_non_string_keys_dict(self):
        data = {'a' : 1, (1, 2) : 2}

        #This is for c encoder
        self.assertRaises(TypeError, self.dumps, data)

        #This is for python encoder
        self.assertRaises(TypeError, self.dumps, data, indent=True)


class TestPyFail(TestFail, PyTest): pass
class TestCFail(TestFail, CTest): pass
