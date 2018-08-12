""" unique media key type """

import re

from . import dbutil

xwords = {'a', 'for', 'of', 'to', 'the'}

def addmovie(db, title, year, info, syncid):
    return dbutil.insert(db, 'INSERT INTO movie (title, yearmade, notes, whenadded, mkey) VALUES (?, ?, ?, ?, ?)', title, year, info, syncid, makekeytitle(title))

def getmovie(db, title, year):
    return dbutil.getone(db, 'SELECT * FROM movie WHERE title = ? AND yearmade = ?', title, year)

def getmovies(db):
    return dbutil.getall(db, 'SELECT * FROM movie')

def search(db, title):
    try:
        key, year = makekeywithyear(title)
    except ValueError:
        return []
    return dbutil.getall(db, 'SELECT * FROM movie WHERE mkey = ? AND yearmade = ?', key, year)

def makekeywithyear(title):
    # Always assuming year is 4 digits.
    # title (year)
    # Note the leading '.' in the split regex, that's so that it skips titles that start with a year.
    # Works for now, but will fail if 4 digits occur elsewhere in the name.
    # Maybe should split on rightmost year?
    left, year, right = re.split(r'.(\d{4})', title, maxsplit=1)
    return makekeytitle(left), int(year)

def makekeytitle(title):
    # lower case and remove punctuation.
    apost = title.lower().replace("'", '')
    spaced = re.sub(r"[[\]\.,'():-]", " ", apost)
    return " ".join(sorted(set(spaced.strip().split()) - xwords))
