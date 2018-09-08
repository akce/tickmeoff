""" Simple case db utility functions. """

def getone(db, query, *values):
    with db as cur:
        res = cur.execute(query, values)
        row = res.fetchone()
    return row

def getall(db, query, *values):
    with db as cur:
        res = cur.execute(query, values)
        rows = res.fetchall()
    return rows

def getlast(db, table):
    return getone(db, 'SELECT * from {t} ORDER BY {t}id DESC LIMIT 1'.format(t=table))

def wherelike(**kwargs):
    wl = []
    value = []
    for k, v in kwargs.items():
        if v is not None:
            wl.append('{} LIKE ?'.format(k))
            value.append('%{}%'.format(v))
    if wl:
        where = ' WHERE ' + ' OR '.join(wl)
    else:
        where = ''
    return where, value

def insert(db, query, *values):
    with db as cur:
        res = cur.execute(query, values)
        if res.rowcount == 0:
            # Assume we've hit a duplicate entry.
            newid = None
        else:
            newid = res.lastrowid
    return newid
