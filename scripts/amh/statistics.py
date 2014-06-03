from parser import genamh
from itertools import chain
from collections import Counter
import json

kb, na = [genamh("./data/%s-indented.xml" % a) for a in ["kb", "na"]]

authors = []

for html, data in chain(kb, na):
    authors += data["authors"]

print Counter(authors)