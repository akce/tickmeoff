""" menu filesystem arguments. """

import itertools
import os

from . import menu

def dirs(path):
    yield from (x + os.path.sep for x in os.listdir(path) if os.path.isdir(x))

def files(path):
    yield from (x for x in os.listdir(path) if os.path.isfile(x))

def ls(path):
    yield from (x for x in itertools.chain(dirs(path), files(path)))

class BaseListerArgument(menu.EnumArgument):

    def __init__(self, listfunc, name, cwd=None):
        super().__init__(name=name)
        self.cwd = os.path.abspath(os.curdir) if cwd is None else cwd
        self.listfunc = listfunc

    @property
    def opts(self):
        return list(self.listfunc(self.cwd))

    @opts.setter
    def opts(self, lst):
        # Ignored, only here for compatibility with EnumArgument.__init__.
        pass

class DirectoryArgument(BaseListerArgument):

    def __init__(self, name='dir', cwd=None):
        super().__init__(listfunc=dirs, name=name, cwd=cwd)

class FileArgument(BaseListerArgument):

    def __init__(self, name='file', cwd=None):
        super().__init__(listfunc=files, name=name, cwd=cwd)

class ListArgument(BaseListerArgument):

    def __init__(self, name='ls', cwd=None):
        super().__init__(listfunc=ls, name=name, cwd=cwd)
