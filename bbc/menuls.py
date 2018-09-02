""" menu filesystem arguments. """

import itertools
import os
import shlex

from . import menu

def dirs(path):
    yield from (x + os.path.sep for x in os.listdir(path) if os.path.isdir(os.path.join(path, x)))

def files(path):
    yield from (x for x in os.listdir(path) if os.path.isfile(os.path.join(path, x)))

def ls(path):
    yield from (x for x in itertools.chain(dirs(path), files(path)))

def resolvepath(*paths):
    # expanduser only works with ~ at the start of the path, so call for each component
    # before joining.
    return os.path.abspath(os.path.join(*(os.path.expanduser(x) for x in paths)))

class BaseListerArgument(menu.EnumArgument):

    def __init__(self, listfunc, name, cwd=None):
        super().__init__(name=name)
        self.basedir = os.path.abspath(os.path.expanduser(cwd or os.curdir))
        self.extradir = ''
        self.listfunc = listfunc

    @property
    def cwd(self):
        return resolvepath(self.basedir, self.extradir)

    @property
    def opts(self):
        return list(self.listfunc(self.cwd))

    @opts.setter
    def opts(self, lst):
        # Ignored, only here for compatibility with EnumArgument.__init__.
        pass

    def _config(self, string):
        try:
            path = shlex.split(string)[0]
            remainder = string[len(path):]
            # Check if cwd exists.
            # Split to get directory/fileparts.
            fullpath = resolvepath(self.basedir, path)
            if os.path.isdir(fullpath):
                self.extradir = path
                filepart = ''
            else:
                # XXX spliting the fullpath -> self.extradir....
                self.extradir, filepart = os.path.split(fullpath)
        except IndexError:
            self.extradir = ''
            filepart = ''
            remainder = ''
        return filepart, remainder

    def getoptions(self, string):
        filepart, _ = self._config(string)
        return super().getoptions(filepart)

    def parse(self, string):
        filepart, remainder = self._config(string)
        args, _ = super().parse(filepart)
        return args, remainder

class DirectoryArgument(BaseListerArgument):

    def __init__(self, name='dir', cwd=None):
        super().__init__(listfunc=dirs, name=name, cwd=cwd)

class FileArgument(BaseListerArgument):

    def __init__(self, name='file', cwd=None):
        super().__init__(listfunc=files, name=name, cwd=cwd)

class ListArgument(BaseListerArgument):

    def __init__(self, name='ls', cwd=None):
        super().__init__(listfunc=ls, name=name, cwd=cwd)
