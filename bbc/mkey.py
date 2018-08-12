""" unique media key type """

import re

xwords = {'a', 'for', 'of', 'to', 'the'}

def parse(title, year=None):
    m = Mkey()
    if year:
        m.year = year
        m.string = m._converttitle(title)
    else:
        m.string, m.year = m._convertwithyear(title)
    return m

def fromdb(string, year):
    m = Mkey()
    m.string = string
    m.year = year
    return m

class Mkey:

    def _convertwithyear(self, title):
        # Always assuming year is 4 digits.
        # title (year)
        left, year, right = re.split(r'(\d{4})', maxsplit=1)
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
