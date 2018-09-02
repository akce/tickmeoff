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
def test_menuls_getoptions(cls, path, expected):
    with mockfs:
        arg = cls()
        opts, _ = arg.getoptions(path)
        assert opts == expected

@pytest.mark.parametrize('cls,path,expected,remainder', [
    (mls.DirectoryArgument,	'/',			[sep], None),
    (mls.FileArgument,		'/',			ValueError, None),
    (mls.ListArgument,		'/',			[sep], None),
    (mls.DirectoryArgument,	'dir1/',		['dir1' + sep], None),
    (mls.DirectoryArgument,	'/dir1/',		['/dir1' + sep], None),
    (mls.FileArgument,		'dir1',			ValueError, None),
    (mls.FileArgument,		'/dir1',		ValueError, None),
    (mls.ListArgument,		'dir1',			['dir1'], None),
    (mls.ListArgument,		'/dir1',		['/dir1'], None),
    (mls.DirectoryArgument,	'/dir2',		['/dir2'], None),
    # Partial search string.
    (mls.DirectoryArgument,	'/dir2/s',		ValueError, None),
    (mls.DirectoryArgument,	'/dir2/su',		ValueError, None),
    (mls.DirectoryArgument,	'/dir2/x',		ValueError, None),

    (mls.FileArgument,		'/dir2',		ValueError, None),
    (mls.ListArgument,		'/dir2',		['/dir2'], None),

    (mls.DirectoryArgument,	'/dir2/subdir1',	['/dir2/subdir1'], None),
    (mls.FileArgument,		'/dir2/subdir1',	ValueError, None),
    (mls.ListArgument,		'/dir2/subdir1',	['/dir2/subdir1'], None),
    (mls.DirectoryArgument,	'dir2/subdir1',		['dir2/subdir1'], None),
    (mls.FileArgument,		'dir2/subdir1',		ValueError, None),
    (mls.ListArgument,		'dir2/subdir1',		['dir2/subdir1'], None),
    (mls.DirectoryArgument,	'/dir3',		['/dir3'], None),
    (mls.FileArgument,		'/dir3',		ValueError, None),
    (mls.ListArgument,		'/dir3',		['/dir3'], None),
    (mls.ListArgument,		'',			ValueError, None),

    # Home dir expansion.
    (mls.DirectoryArgument,	'~',			['~'], None),
    (mls.FileArgument,		'~',			ValueError, None),
    (mls.ListArgument,		'~',			['~'], None),
    (mls.DirectoryArgument,	'~/',			['~/'], None),
    (mls.FileArgument,		'~/',			ValueError, None),
    (mls.ListArgument,		'~/',			['~/'], None),
    (mls.DirectoryArgument,	'~/subdir1',		['~/subdir1'], None),
    (mls.FileArgument,		'~/subdir1',		ValueError, None),
    (mls.ListArgument,		'~/subdir1',		['~/subdir1'], None),
    # Partial search string.
    (mls.DirectoryArgument,	'~/s',		ValueError, None),
    (mls.DirectoryArgument,	'~/su',		ValueError, None),
    ])
def test_menuls_parse(cls, path, expected, remainder):
    with mockfs:
        arg = cls()
        if expected is ValueError:
            with pytest.raises(ValueError):
                arg.parse(path)
        else:
            opts, rem = arg.parse(path)
            assert opts == expected
            assert rem == remainder
