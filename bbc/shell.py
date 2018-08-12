import operator
import os
import readline
import shlex
import time

from . import bbc
from . import easter
from . import m3u
from . import mediafile
from . import menufuncs
from . import movie

class Menu:

    def __init__(self, db):
        self.db = db
        self._debug = False
        self._menu = [
            self.help,
            self.download,
            self.history,
            self.movies,
            self.addpath,
            self.paths,
            self.scan,
            self.missing,
            self.rankings,
            self.write,
            ]
        self._debugmenu = [
            self.filedownload,
            self.fileimport,
            self.moviekeys,
            self.scanfile,
            ]

    def help(self, *args, **kwargs):
        """ list command help """
        for m in self:
            print('{:10} {}'.format(m, self[m].__doc__))

    def download(self, *args, **kwargs):
        """ download and import listing """
        self._import(bbc.download)
        self.db.commit()

    def history(self, *args, **kwargs):
        """ list download history """
        for h in bbc.gethistory(self.db):
            print('{:<3} {}'.format(h['syncid'], formatsync(h)))

    def movies(self, *args, **kwargs):
        """ show movie listing """
        movs = movie.getmovies(self.db)
        for m in sorted(movs, key=operator.itemgetter('title', 'yearmade')):
            print('({year}): {title} - {notes}'.format(title=m['title'], year=m['yearmade'], notes=m['notes']))
        print('{} in total'.format(len(movs)))

    def addpath(self, *args, **kwargs):
        """ add given path to list of dirs to scan """
        if len(args) == 1:
            p = args[0]
            if mediafile.getlocation(self.db, p):
                print('already have that one')
            else:
                mediafile.addlocation(self.db, p)
                self.db.commit()
        else:
            print('need path')

    def paths(self, *args, **kwargs):
        """ list media paths """
        for p in mediafile.getpaths(self.db):
            print(p['pathname'])

    def scan(self, *args, **kwargs):
        """ scan known paths for media """
        new = mediafile.scanpaths(self.db)
        for f in new:
            print(f)
        print('{} new media files added'.format(len(new)))

    def _printranks(self, movs):
        for m in movs:
            print('{rank}: {title}({year}) - {notes}'.format(rank=m['indexnum'], title=m['title'], year=m['yearmade'], notes=m['notes']))

    def missing(self, *args, **kwargs):
        """ list missing media from the latest ranking """
        miss = []
        for r in bbc.getrankings(self.db):
            mf = mediafile.getmediafile(self.db, movieid=r['movieid'])
            if mf is None:
                miss.append(r)
        self._printranks(miss)

    def rankings(self, *args, **kwargs):
        """ show latest movie rankings """
        self._printranks(bbc.getrankings(self.db))

    def write(self, *args, **kwargs):
        """ write m3u playlist file """
        got = []
        for r in bbc.getrankings(self.db):
            mf = mediafile.getmediafile(self.db, movieid=r['movieid'])
            if mf:
                # m3u uses (label, path)
                label = '{rank}: {title}({year}) - {notes}'.format(rank=r['indexnum'], title=r['title'], year=r['yearmade'], notes=r['notes'])
                path = os.path.expanduser(mediafile.getpathr(self.db, mf['locationid']))
                got.append((label, os.path.join(path, mf['filename'])))
        m3u.write(args[0], got)

    def x(self, *args, **kwargs):
        """ toggle expert/debug mode """
        self._debug = not self._debug
        print('debug = {}'.format(self._debug))


    def commit(self, *args, **kwargs):
        """ DEBUG: save changes to database. """
        # Adding check (in addition to the options listing above) as the command can be manually typed in as well.
        if self.db.dirty:
            self.db.commit()

    def filedownload(self, *args, **kwargs):
        """ DEBUG: download chart file and save to chart.html """
        bbc.dlchart(self.db)

    def fileimport(self, *args, **kwargs):
        """ DEBUG: import (only) rankings from local file. Use commit to save changes. """
        self._import(bbc.fileimport)

    def moviekeys(self, *args, **kwargs):
        """ DEBUG: List internal movie keys for movies list. """
        movs = movie.getmovies(self.db)
        for m in sorted(movs, key=operator.itemgetter('title', 'yearmade')):
            print('({year}): {title} -> {key}'.format(title=m['title'], year=m['yearmade'], key=m['mkey']))
        print('{} in total'.format(len(movs)))

    def scanfile(self, *args, **kwargs):
        """ DEBUG: Scan media files from filelist.txt as if it was a filesystem. """
        for key, filename, location in mediafile.scanfiles(self.db, 'filelist.txt'):
            print('{} {}'.format(key, filename))

    def _import(self, func):
        """ Internal func for downloading/importing etc. """
        newmovies, rankings = func(self.db)
        if len(rankings):
            self._printranks(newmovies)
            print('Chart successfully imported: {} new movies'.format(len(newmovies)))
        else:
            print('Big problem, nothing new found - contact tech support!')

    def __iter__(self):
        if self._debug:
            menu = self._menu + self._debugmenu
            # Only display commit if there are unsaved changes.
            if self.db.dirty:
                menu.append(self.commit)
        else:
            menu = self._menu
        return (m.__name__ for m in menu)

    def __getitem__(self, key):
        return getattr(self, key)

class DictReadlineCompleter:

    def __init__(self, menu):
        self._menu = menu

    def __call__(self, text, state):
        if state == 0:
            ## Build options list for text.
            # Grab list of completions for text.
            parts = shlex.split(readline.get_line_buffer())
            # Append a space char saving user from having to add it for single completions.
            self.options = ['{} '.format(x) for x in menufuncs.getoptions(self._menu, parts)]
        try:
            value = self.options[state]
        except IndexError:
            value = None
        return value

class Shell:

    def __init__(self, db):
        self.db = db
        self.menu = Menu(db=db)
        # Initialise readline module.
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')
        readline.set_completer(DictReadlineCompleter(self.menu))

    @property
    def prompt(self):
        return '* ' if self.db.dirty else '> '

    def inputloop(self):
        keepgoing = True
        while keepgoing:
            try:
                line = input(self.prompt)
            except (EOFError, KeyboardInterrupt):
                keepgoing = False
            else:
                # Process completed line/command.
                self.action(line)

    def action(self, line):
        parts = shlex.split(line)
        func, args = menufuncs.getmenuitem(self.menu, parts)
        try:
            return func(*args)
        except TypeError:
            # Small easter egg, print a funny saying inspired by Budge.
            print(easter.getcookie())

def formatsync(lastsync):
    if lastsync is None:
        lastsyncstr = 'Never'
    else:
        lastsyncstr = time.strftime('%c', time.localtime(lastsync['whensynced']))
    return lastsyncstr

def motd(db):
    """ Prints out the message of the day """
    print('Welcome to The Budge-Board Charts v{}'.format(bbc.__version__))
    print('Chart last synced {}'.format(formatsync(bbc.getlastsync(db))))
    print("Type 'help' for more information.")

def run(db):
    shell = Shell(db=db)
    motd(db)
    shell.inputloop()
