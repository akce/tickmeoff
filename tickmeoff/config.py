from . import dbutil

def getallconfig(db):
    return dbutil.getall(db, 'SELECT * FROM config')

def getconfig(db, field):
    return dbutil.getone(db, 'SELECT value, description FROM config WHERE key = ?', field)

def setconfig(db, field, value):
    with db as conn:
        curs = conn.execute('UPDATE config SET value = ? WHERE key = ?', (value, field,))
