""" menu database arguments. """

from . import menu
from . import dbutil

class TableArgument(menu.EnumArgument):

    def __init__(self, db, table, column):
        self.db = db
        self.table = table
        self.column = column
        super().__init__(name=table)

    @property
    def opts(self):
        return [r[self.column] for r in self._get()]

    @opts.setter
    def opts(self, lst):
        # Ignored, only here for compatibility with EnumArgument.__init__.
        pass

    def longmatch(self, string):
        """ overridden so a sqlite.Row is returned. """
        matches = []
        for x in self._get():
            val = x[self.column]
            if string.startswith(val):
                matches.append((x, string[len(val):]))
        return matches

    def _get(self):
        return dbutil.getall(self.db, 'SELECT * FROM {}'.format(self.table))
