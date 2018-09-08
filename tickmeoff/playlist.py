"""
Playlist writing module.
Copyright (c) 2018 Acke, see LICENSE file for allowable usage.
"""

import os

def writem3u(filename, movs):
    fp = os.path.expanduser(filename)
    destdir = os.path.dirname(fp)
    # Ensure basedir exists.
    os.makedirs(destdir, exist_ok=True)
    with open(fp, 'w+') as f:
        print('#EXTM3U', file=f)
        print('', file=f)
        for label, fullpath in movs:
            # length/duration not supported yet so hardcode -1 for now.
            print('#EXTINF:-1,{}'.format(label), file=f)
            print(os.path.relpath(fullpath, destdir), file=f)
            print('', file=f)

def makesymlinks(basedir, movs):
    fp = os.path.expanduser(basedir)
    # Ensure basedir exists.
    os.makedirs(fp, exist_ok=True)
    # Remove all existing symlinks (ONLY).
    for f in os.listdir(fp):
        path = os.path.join(fp, f)
        if os.path.islink(path):
            os.unlink(path)
    # Link items.
    for label, dirpath in movs:
        os.symlink(dirpath, os.path.join(os.path.relpath(fp, dirpath), label))
