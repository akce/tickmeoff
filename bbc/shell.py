import operator
import os
import readline
import time
import traceback

from . import bbc
from . import config
from . import easter
from . import mediafile
from . import menu
from . import menudb
from . import menuls
from . import movie
from . import playlist

class App:

    def __init__(self, db):
        self.db = db
        self.menu = self._makemenu()

    def _makemenu(self):
        m = menu.Menu(name='bbc')
        m.additem(menu.CommandFunc(self.download))
        m.additem(menu.CommandFunc(self.history))
        m.additem(menu.CommandFunc(self.movies))
        patharg = menuls.DirectoryArgument(name='path')
        m.additem(menu.CommandFunc(self.addpath, patharg))
        m.additem(menu.CommandFunc(self.paths))
        m.additem(menu.CommandFunc(self.scan))
        m.additem(menu.CommandFunc(self.missing))
        m.additem(menu.CommandFunc(self.punted))
        m.additem(menu.CommandFunc(self.diffs))
        m.additem(menu.CommandFunc(self.rankings))
        m.additem(menu.CommandFunc(self.link))
        m.additem(menu.CommandFunc(self.write))
        cm = menu.SubMenu(name='config', rootmenu=m)
        ckeyarg = menudb.TableArgument(self.db, table='config', column='key')
        cgetargs = menu.CompositeArgument(ckeyarg, menu.NoArgument(name='getall'))
        cm.additem(menu.CommandFunc(self.configget, cgetargs, name='get'))
        cm.additem(menu.CommandFunc(self.configset, ckeyarg, menu.StringArgument(name='value'), name='set'))
        m.additem(cm)
        dm = menu.SubMenu(name='debug', rootmenu=m)
        dm.additem(menu.CommandFunc(self.commit))
        dm.additem(menu.CommandFunc(self.filedownload))
        dm.additem(menu.CommandFunc(self.fileimport))
        dm.additem(menu.CommandFunc(self.moviekeys))
        dm.additem(menu.CommandFunc(self.scanfile))
        m.additem(dm)
        return m

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

    def punted(self, *args, **kwargs):
        """ list movies that have been dropped from the rankings """
        for m in bbc.getpunted(self.db):
            print('{year} ({i:3}) {title}'.format(year=m['yearmade'], title=m['title'], i=m['indexnum']))

    def diffs(self, *args, **kwargs):
        """ list differences in movie rank position """
        for m in bbc.getdiffs(self.db):
            # Format the diff.
            if m['diff'] is None:
                # New entry
                diff = '*   '
            elif m['diff'] == 0:
                # Unchanged.
                diff = '    '
            else:
                # Diff is either positive or negative number.
                diff = '{:+4}'.format(m['diff'])
            print('{i:3}) {diff} {year} {title}'.format(diff=diff, year=m['yearmade'], title=m['title'], i=m['indexnum']))

    def rankings(self, *args, **kwargs):
        """ show latest movie rankings """
        self._printranks(bbc.getrankings(self.db))

    def configget(self, *args, **kwargs):
        """ show config settings """
        if args:
            # Print the requested config item.
            keyname = args[0]['key']
            row = config.getconfig(self.db, keyname)
            print('{:16} {}'.format(keyname, row['value']))
        else:
            # Print all.
            for row in config.getallconfig(self.db):
                print('{:16} {:16} {}'.format(row['key'], row['value'], row['description']))

    def configset(self, *args, **kwargs):
        """ set a config item """
        key, value = args[0].split()
        config.setconfig(self.db, key, value)
        self.db.commit()

    def link(self, *args, **kwargs):
        """ create soft links for media files """
        got = []
        for r, path in self._getrankedmedia():
            # Link the parent directory using label.
            label = '{rank}) {title} ({year})'.format(rank=r['indexnum'], title=r['title'], year=r['yearmade'], notes=r['notes'])
            got.append((label, os.path.dirname(path)))
        playlist.makesymlinks(config.getconfig(self.db, 'linkdir')['value'], got)

    def write(self, *args, **kwargs):
        """ write m3u playlist file """
        got = []
        for r, path in self._getrankedmedia():
            # m3u uses (label, path)
            label = '{rank}: {title}({year}) - {notes}'.format(rank=r['indexnum'], title=r['title'], year=r['yearmade'], notes=r['notes'])
            got.append((label, path))
        playlist.writem3u(config.getconfig(self.db, 'm3ufile')['value'], got)

    def _getrankedmedia(self):
        for r in bbc.getrankings(self.db):
            mf = mediafile.getmediafile(self.db, movieid=r['movieid'])
            if mf:
                path = os.path.expanduser(mediafile.getpathr(self.db, mf['locationid']))
                yield r, os.path.join(path, mf['filename'])

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

class DictReadlineCompleter:

    def __init__(self, menu):
        self._menu = menu

    def __call__(self, text, state):
        if state == 0:
            ## Build options list for text.
            # Grab the full line.
            line = readline.get_line_buffer()
            self.options = self._menu.getoptions(line)
        try:
            value = self.options[state]
        except IndexError:
            value = None
        return value

class Shell:

    def __init__(self, db):
        self.db = db
        self.app = App(db=db)
        # Initialise readline module.
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')
        readline.set_completer(DictReadlineCompleter(self.app.menu))

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
        try:
            func, args = self.app.menu.getcommandargs(line)
            return func(*args)
        except IndexError:
            print('bad input')
            # Small easter egg, print a funny saying inspired by Budge.
            print(easter.getcookie())
            traceback.print_exc()
        except KeyError:
            print('command {} not found'.format(line))
            traceback.print_exc()
        except ValueError:
            print('bad args')
            traceback.print_exc()
        except Exception:
            traceback.print_exc()

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
