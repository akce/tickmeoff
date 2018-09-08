import html.parser as hp

class ChartParser(hp.HTMLParser):

    def __init__(self):
        super().__init__()
        self._inmovie = False
        self._tags = []
        self._movies = []

    def _hasattrval(self, attrs, key, value):
        d = dict(attrs)
        try:
            ret = d[key] == value
        except KeyError:
            ret = False
        return ret

    def handle_starttag(self, tag, attrs):
        # Movie entries begin with <td class="titleColumn">
        self._tags.append(tag)
        if self._inmovie is False:
            # Search for new movie entry.
            if tag == 'td' and self._hasattrval(attrs, 'class', 'titleColumn'):
                self._inmovie = True
        if self._inmovie and tag == 'a':
            d = dict(attrs)
            try:
                self._info = d['title']
            except KeyError:
                self._info = ''

    def handle_endtag(self, tag):
        if self._inmovie and tag == 'td':
            self._inmovie = False
        self._tags.pop()

    def handle_data(self, data):
        if self._inmovie:
            tag = self._tags[-1]
            if tag == 'a':
                # Movie name.
                self._moviename = data.strip()
            elif tag == 'span':
                # Movie year in format (\d{4})
                self._movies.append((self._moviename, int(data.strip(' ()')), self._info))
            #print("-{:8} {}".format(self._tags[-1], data.strip()))

    def __iter__(self):
        return iter(self._movies)
