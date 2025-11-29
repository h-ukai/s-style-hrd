import sys
import string
import random

class rotor():

    rotormap = [15, 11, 21, 23, 1, 18, 36, 0, 37, 17, 16, 14, 2, 9, 35, 28, 4, 26,
              27, 24, 32, 10, 25, 5, 3, 30, 19, 33, 29, 34, 7, 8, 31, 22, 12, 13, 20, 6]

    def encode(self,str):
        s = string.lowercase + string.digits + "_" + "-"
        table = { "d": "a", "a": "d", "1": "3", "3": "1" }
#        rotor = range(len(s))
#        random.shuffle(rotor)
#        sys.stdout.write("%2d" % len(rotor))
#        sys.stdout.write("".join("%02d" % i for i in rotor))
        r = 0
        rc = ""
        for c in map(lambda c: table.get(c, c), str):
            rc += s[self.rotormap[(r+s.find(c))%len(self.rotormap)]]
            r = (r+1) % len(self.rotormap)
        return rc

    def decode(self,str):
        s = string.lowercase + string.digits + "_" + "-"
        table = { "d": "a", "a": "d", "1": "3", "3": "1" }
        r = 0
        rc = ""
        for c2 in str:
            i = self.rotormap.index(s.index(c2)) # (r+s.find(c))%len(rotor)
            i = (i - r) % len(self.rotormap) # s.find(c)
            rc += table.get(s[i], s[i])
            r = (r + 1) % len(self.rotormap)
        return rc
