#!/usr/bin/env python3
""" W3301 test case. """

mydict = {0: 0, 1: 1, 2: 2}
print(min(min(mydict.values()), 3))
print(min(mydict.values(), 3))
