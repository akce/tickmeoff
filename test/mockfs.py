import os
import unittest.mock as mock

class Filesystem:

    def __init__(self, fsdict, home='/'):
        self._fsdict = fsdict
        self._home = home
        self._mocklistdir = mock.patch.object(os, 'listdir', self.listdir)
        self._mockabspath = mock.patch.object(os.path, 'abspath', self.abspath)
        self._mockexpanduser = mock.patch.object(os.path, 'expanduser', self.expanduser)
        self._mockisdir = mock.patch.object(os.path, 'isdir', self.isdir)
        self._mockisfile = mock.patch.object(os.path, 'isfile', self.isfile)
        self._mockexists = mock.patch.object(os.path, 'exists', self.exists)

    def _get_path(self, path):
        fs = self._fsdict
        if path != os.path.sep:
            for _dir in (x for x in path.split(os.path.sep) if x):
                fs = fs[_dir]
        return fs

    def abspath(self, path):
        if path == '.':
            ap = '/'
        else:
            ap = path
        return ap

    def expanduser(self, path):
        # expanduser only works with ~ at the start of the path.
        # NOTE: this implementation does not support ~username expansion.
        if path.startswith('~'):
            res = path.replace('~', self._home)
        else:
            res = path
        return res

    def listdir(self, path):
        try:
            d = self._get_path(path)
            res = list(sorted(d.keys()))
        except KeyError:
            raise FileNotFoundError(path) from None
        return res

    def isdir(self, path):
        # path is a dir if it contains a dict.
        try:
            d = self._get_path(path)
            res = d is not None
        except KeyError:
            res = False
        return res

    def isfile(self, path):
        try:
            d = self._get_path(path)
            res = d is None
        except KeyError:
            res = False
        return res

    def exists(self, path):
        try:
            d = self._get_path(path)
            res = True
        except KeyError:
            res = False
        return res

    def __enter__(self):
        self._mocklistdir.start()
        self._mockabspath.start()
        self._mockexpanduser.start()
        self._mockexists.start()
        self._mockisdir.start()
        self._mockisfile.start()

    def __exit__(self, *args, **kwargs):
        self._mocklistdir.stop()
        self._mockabspath.stop()
        self._mockexpanduser.stop()
        self._mockexists.stop()
        self._mockisdir.stop()
        self._mockisfile.stop()
