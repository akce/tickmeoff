""" menuls unit tests. """

# Module under test.
import bbc.menuls as mls

import unittest.mock as mock
import pytest

import os

import test.mockfs

fsdict = {
    'dir1': {
        'file1': None,
    },
    'dir2': {
        'subdir1': {
            'file2': None,
            'file3': None,
        },
    },
    'dir3': {},
}
mockfs = test.mockfs.Filesystem(fsdict, home='/dir2')

sep = os.path.sep

@pytest.mark.parametrize('cls,path,expected', [
    (mls.DirectoryArgument,	'/',	['dir1' + sep, 'dir2' + sep, 'dir3' + sep]),
    (mls.FileArgument,		'/',	[]),
    (mls.ListArgument,		'/',	['dir1' + sep, 'dir2' + sep, 'dir3' + sep]),
    (mls.DirectoryArgument,	'dir1/',		[]),
    (mls.DirectoryArgument,	'/dir1/',		[]),
    (mls.FileArgument,		'dir1',			['file1']),
    (mls.FileArgument,		'/dir1',		['file1']),
    (mls.ListArgument,		'dir1',			['file1']),
    (mls.ListArgument,		'/dir1',		['file1']),
    (mls.DirectoryArgument,	'/dir2',		['subdir1' + sep]),
    # Partial search string.
    (mls.DirectoryArgument,	'/dir2/s',		['subdir1' + sep]),
    (mls.DirectoryArgument,	'/dir2/su',		['subdir1' + sep]),
    (mls.DirectoryArgument,	'/dir2/x',		[]),

    (mls.FileArgument,		'/dir2',		[]),
    (mls.ListArgument,		'/dir2',		['subdir1' + sep]),

    (mls.DirectoryArgument,	'/dir2/subdir1',	[]),
    (mls.FileArgument,		'/dir2/subdir1',	['file2', 'file3']),
    (mls.ListArgument,		'/dir2/subdir1',	['file2', 'file3']),
    (mls.DirectoryArgument,	'dir2/subdir1',		[]),
    (mls.FileArgument,		'dir2/subdir1',		['file2', 'file3']),
    (mls.ListArgument,		'dir2/subdir1',		['file2', 'file3']),
    (mls.DirectoryArgument,	'/dir3',		[]),
    (mls.FileArgument,		'/dir3',		[]),
    (mls.ListArgument,		'/dir3',		[]),
    (mls.ListArgument,		'',		['dir1' + sep, 'dir2' + sep, 'dir3' + sep]),

    # Home dir expansion.
    (mls.DirectoryArgument,	'~',		['subdir1' + sep]),
    (mls.FileArgument,		'~',		[]),
    (mls.ListArgument,		'~',		['subdir1' + sep]),
    (mls.DirectoryArgument,	'~/',		['subdir1' + sep]),
    (mls.FileArgument,		'~/',		[]),
    (mls.ListArgument,		'~/',		['subdir1' + sep]),
    (mls.DirectoryArgument,	'~/subdir1',		[]),
    (mls.FileArgument,		'~/subdir1',		['file2', 'file3']),
    (mls.ListArgument,		'~/subdir1',		['file2', 'file3']),
    # Partial search string.
    (mls.DirectoryArgument,	'~/s',		['subdir1' + sep]),
    (mls.DirectoryArgument,	'~/su',		['subdir1' + sep]),
    ])
def test_menuls(cls, path, expected):
    with mockfs:
        arg = cls()
        opts, _ = arg.getoptions(path)
        assert opts == expected
