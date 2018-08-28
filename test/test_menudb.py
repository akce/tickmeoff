""" menudb.py unit tests """

# Module under test.
import bbc.menudb as mdb

import bbc.db as dbmod

import unittest.mock as mock
import pytest

schema = '''
CREATE TABLE first (firstid INTEGER PRIMARY KEY, name TEXT, description TEXT);
CREATE TABLE second (secondid INTEGER PRIMARY KEY, name TEXT, firstid INTEGER REFERENCES first);

INSERT INTO first (name, description) VALUES ('hello', 'big greeting');
INSERT INTO first (name, description) VALUES ('world', 'for everyone');

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
    (gdb, 'first', 'name', ['hello', 'world']),
    (gdb, 'first', 'description', ['big greeting', 'for everyone']),
    (gdb, 'second', 'name', ['gday', 'ahoj']),
    ])
def test_dbargs_init(db, tablename, columnname, expected):
    arg = mdb.TableArgument(db, tablename, columnname)
    assert arg.opts == expected

def test_dbargs_refresh(db):
    """ db inserts are reflected in opts. """
    argname = mdb.TableArgument(db, 'first', 'name')
    assert argname.opts == ['hello', 'world']
    argdesc = mdb.TableArgument(db, 'first', 'description')
    assert argdesc.opts == ['big greeting', 'for everyone']
    with db as c:
        c.execute('''INSERT INTO first (name, description) VALUES ('cheesy', 'good bye')''')
    assert argname.opts == ['hello', 'world', 'cheesy']
    assert argdesc.opts == ['big greeting', 'for everyone', 'good bye']
