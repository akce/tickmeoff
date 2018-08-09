""" The Budge-Board Charts manager - main module. """

__version__ = '0.1'

import html.parser as hp
import os
import urllib.request as ur

class Imdb250Parser(hp.HTMLParser):

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
                self._movies.append((self._moviename, data.strip(' ()'), self._info))
            #print("-{:8} {}".format(self._tags[-1], data.strip()))

    def __iter__(self):
        return iter(self._movies)

def downloadurl(url):
    ## NOTE: the agent value usually affects the content format returned by the server!
    #agent = 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0'
    agent = 'Lynx/2.8.8rel.2 libwww-FM/2.14 SSL-MM/1.4.1'
    req = ur.Request(url, headers={'User-Agent': agent})
    return ur.urlopen(req).read()

def imdb250fileiter(filename='imdb250.html'):
    imdbstr = open(filename).read()
    parser = Imdb250Parser()
    parser.feed(imdbstr)
    yield from iter(parser)

def imdb250webiter(imdb250url='https://imdb.com/chart/top'):
    imdbstr = str(downloadurl(imdb250url), 'utf-8')
    parser = Imdb250Parser()
    parser.feed(imdbstr)
    yield from iter(parser)
