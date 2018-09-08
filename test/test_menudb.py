""" menudb.py unit tests """

# Module under test.
import tickmeoff.menudb as mdb

import tickmeoff.db as dbmod

import sqlite3
import unittest.mock as mock

import pytest

schema = '''
CREATE TABLE first (firstid INTEGER PRIMARY KEY, name TEXT, description TEXT);
CREATE TABLE second (secondid INTEGER PRIMARY KEY, name TEXT, firstid INTEGER REFERENCES first);

INSERT INTO first (name, description) VALUES ('hello', 'big greeting');
INSERT INTO first (name, description) VALUES ('world', 'for everyone');
INSERT INTO first (name, description) VALUES ('hello world', 'two word greeting');

INSERT INTO second (name, firstid) VALUES ('gday', 1);
INSERT INTO second (name, firstid) VALUES ('ahoj', 1);
'''

@pytest.fixture
def db():
    """ In-memory sqlite test db. """
    def altschema(self):
        return schema

    with mock.patch.object(dbmod.DB, '_loadschema', altschema) as m:
        dobj = dbmod.DB(':memory:')
    return dobj

gdb = db()

@pytest.mark.parametrize('db,tablename,columnname,expected', [
    (gdb, 'first', 'name', ['hello', 'world', 'hello world']),
    (gdb, 'first', 'description', ['big greeting', 'for everyone', 'two word greeting']),
    (gdb, 'second', 'name', ['gday', 'ahoj']),
    ])
def test_dbargs_init(db, tablename, columnname, expected):
    arg = mdb.TableArgument(db, tablename, columnname)
    assert arg.opts == expected

@pytest.mark.parametrize('db,tablename,columnname,search,expopts,exprem', [
    (gdb, 'first', 'name', '', ['hello', 'world', 'hello world'], None),
    (gdb, 'first', 'description', '', ['big greeting', 'for everyone', 'two word greeting'], None),
    (gdb, 'second', 'name', '', ['gday', 'ahoj'], None),

    # Partial search strings.
    (gdb, 'first', 'name', 'h', ['hello', 'hello world'], None),
    (gdb, 'first', 'name', 'he', ['hello', 'hello world'], None),
    (gdb, 'first', 'name', 'hel', ['hello', 'hello world'], None),
    (gdb, 'first', 'name', 'hello', ['hello', 'hello world'], None),
    (gdb, 'first', 'name', 'hello ', ['hello world'], None),
    (gdb, 'first', 'name', 'hello w', ['hello world'], None),
    # Exact match and remainder.
    (gdb, 'first', 'name', 'hello x', ['hello'], ' x'),
    ])
def test_dbargs_getoptions(db, tablename, columnname, search, expopts, exprem):
    arg = mdb.TableArgument(db, tablename, columnname)
    opts, rem = arg.getoptions(search)
    assert opts == expopts
    assert rem == exprem

def test_dbargs_refresh(db):
    """ db inserts are reflected in opts. """
    argname = mdb.TableArgument(db, 'first', 'name')
    assert argname.opts == ['hello', 'world', 'hello world']
    argdesc = mdb.TableArgument(db, 'first', 'description')
    assert argdesc.opts == ['big greeting', 'for everyone', 'two word greeting']
    with db as c:
        c.execute('''INSERT INTO first (name, description) VALUES ('cheesy', 'good bye')''')
    assert argname.opts == ['hello', 'world', 'hello world', 'cheesy']
    assert argdesc.opts == ['big greeting', 'for everyone', 'two word greeting', 'good bye']

@pytest.mark.parametrize('db,search,resrem', [
    (gdb, 'hello', None),
    (gdb, 'hello ', ' '),
    ])
def test_dbargs_getcommandargs(db, search, resrem):
    """ parse a good result """
    argname = mdb.TableArgument(db, 'first', 'name')
    # Test a good row.
    (result0,), remainder = argname.parse(search)
    assert isinstance(result0, sqlite3.Row)
    assert result0.keys() ==  ['firstid', 'name', 'description']
    assert result0['firstid'] == 1
    assert result0['name'] == 'hello'
    assert result0['description'] == 'big greeting'
    assert remainder == resrem

@pytest.mark.parametrize('db,search', [
    (gdb, ''),
    (gdb, 'h'),
    (gdb, 'hell'),
    (gdb, 'blah'),
    ])
def test_dbargs_getcommandargs_nonexist(db, search):
    """ non-existent rows """
    argname = mdb.TableArgument(db, 'first', 'name')
    with pytest.raises(ValueError):
        argname.parse(search)
