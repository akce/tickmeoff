""" menuls unit tests. """

# Module under test.
import bbc.menuls as mls

import unittest.mock as mock
import pytest

import os

rootpath = '/testhome'
mockdirs = ['dir1', 'dir2']
mockfiles = ['file1']

def mocklistdir(path):
    return iter(mockdirs + mockfiles)

def mockisdir(path):
    return path in mockdirs

def mockisfile(path):
    return path in mockfiles

def mockabspath(path):
    return rootpath

@mock.patch.object(os, 'listdir', mocklistdir)
@mock.patch.object(os.path, 'abspath', mockabspath)
@mock.patch.object(os.path, 'isdir', mockisdir)
@mock.patch.object(os.path, 'isfile', mockisfile)
@pytest.mark.parametrize('cls,expected', [
    (mls.DirectoryArgument, ['dir1/', 'dir2/']),
    (mls.FileArgument, ['file1']),
    (mls.ListArgument, ['dir1/', 'dir2/', 'file1']),
    ])
def test_menuls(cls, expected):
    arg = cls()
    assert arg.opts == expected
