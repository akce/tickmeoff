""" unique media key type """

import re

from . import dbutil

xwords = {'a', 'for', 'of', 'to', 'the'}

def parse(title, year=None):
    m = Mkey()
    if year:
        m.year = year
        m.string = m._converttitle(title)
    else:
        m.string, m.year = m._convertwithyear(title)
    return m

def fromdb(mkeyid, string, year):
    m = Mkey()
    m.mkeyid = mkeyid
    m.string = string
    m.year = year
    return m

class Mkey:

    def _convertwithyear(self, title):
        # Always assuming year is 4 digits.
        # title (year)
        # Note the leading '.' in the split regex, that's so that it skips titles that start with a year.
        # Works for now, but will fail if 4 digits occur elsewhere in the name.
        # Maybe should split on rightmost year?
        left, year, right = re.split(r'.(\d{4})', title, maxsplit=1)
        return self._converttitle(left), int(year)

    def _converttitle(self, title):
        # lower case and remove punctuation.
        apost = title.lower().replace("'", '')
        spaced = re.sub(r"[[\]\.,'():-]", " ", apost)
        return " ".join(sorted(set(spaced.strip().split()) - xwords))

    def __hash__(self):
        return hash((self.year, self.string))

    def __str__(self):
        return '({}, {})'.format(self.string, self.year)

def addmkey(db, title, year):
    m = parse(title=title, year=year)
    return dbutil.insert(db, 'INSERT INTO mkey (string, yearmade) VALUES (?, ?)', m.string, m.year)

def getmkey(db, mkey=None, mkeyid=None):
    if mkeyid is not None:
        m = dbutil.getone(db, 'SELECT * FROM mkey WHERE mkeyid = ?', mkeyid)
    elif mkey:
        m = dbutil.getone(db, 'SELECT * FROM mkey WHERE string = ? AND yearmade = ?', mkey.string, mkey.year)
    if m:
        mobj = fromdb(mkeyid=m['mkeyid'], string=m['string'], year=m['yearmade'])
    else:
        mobj = None
    return mobj
