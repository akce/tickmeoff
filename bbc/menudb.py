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
        return self._makeopts()

    @opts.setter
    def opts(self, lst):
        # Ignored, only here for compatibility with EnumArgument.__init__.
        pass

    def _makeopts(self):
        self._data = dbutil.getall(self.db, 'SELECT * FROM {}'.format(self.table))
        return [r[self.column] for r in self._data]
