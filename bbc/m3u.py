"""
Playlist writing module.
Copyright (c) 2018 Acke, see LICENSE file for allowable usage.
"""

import os

def write(filename, movs):
    with open(filename, 'w+') as f:
        print('#EXTM3U', file=f)
        print('', file=f)
        destdir = os.path.dirname(filename)
        for label, fullpath in movs:
            # length/duration not supported yet so hardcode -1 for now.
            print('#EXTINF:-1,{}'.format(label), file=f)
            print(os.path.relpath(fullpath, destdir), file=f)
            print('', file=f)
