class Command:

    def __init__(self, name, arg=None):
        self.name = name
        self.arg = NoArgument(name='default') if arg is None else arg

    def getoptions(self, string):
        return self.arg.getoptions(string)

    def getcommandargs(self, string):
        # Let the command handler worry about words validity.
        return self, self.arg.parse(string)

class CommandFunc(Command):

    def __init__(self, func, name=None, arg=None):
        super().__init__(name=name if name else func.__name__, arg=arg)
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class NoArgument:

    def __init__(self, name='noarg'):
        self.name = name

    def getoptions(self, string):
        return []

    def parse(self, string):
        if string is not None:
            stripped = string.strip()
            if stripped:
                raise ValueError()
        return None

class StringArgument:

    def __init__(self, name='string'):
        self.name = name

    def parse(self, string):
        if string is None:
            raise ValueError()
        return [string.strip()]

    def getoptions(self, string):
        if string == '':
            ret = []
        else:
            ret = [string]
        return ret

class EnumArgument:

    def __init__(self, name='enum', opts=None):
        self.name = name
        self.opts = [] if opts is None else opts

    def parse(self, string):
        try:
            stripped = string.strip()
        except AttributeError:
            pass
        else:
            if stripped in self.opts:
                return [stripped]
        raise ValueError()

    def getoptions(self, string):
        return [opt for opt in self.opts if opt.startswith(string)]

class RootMenu:
    """ A menu is a list of commands. """

    def __init__(self, name):
        self.name = name
        self.commands = []

    def additem(self, item):
        assert isinstance(item, (Command, RootMenu))
        self.commands.append(item)

    def delitem(self, item):
        assert isinstance(item, (Command, RootMenu))
        self.commands.remove(item)

    def __iter__(self):
        return (x.name for x in self.commands)

    def __getitem__(self, key):
        for x in self.commands:
            if x.name == key:
                return x
        raise KeyError()

    def _parse(self, string):
        if string == '':
            words = ['']
        else:
            words = string.split(None, maxsplit=1)
            if len(words) == 1 and string.endswith(' '):
                # Only want this if there's one word...... ie, no args.......
                words.append('')
        return words

    def getoptions(self, string):
        words = self._parse(string)
        if words[0] == '':
            # Return all options.
            opts = list(iter(self))
        else:
            if len(words) == 1:
                # Match every option starting with the first word.
                opts = [x for x in self if x.startswith(words[0])]
            else:
                opts = self._suboptions(words)
        return opts

    def _suboptions(self, words):
        # Get the exact subcommand and get it to return completions for the rest of the string.
        try:
            sub = self[words[0]]
        except KeyError:
            # No command matches first word, so return no valid options.
            opts = []
        else:
            # Handle Command/Argument types.
            try:
                opts = sub.getoptions(words[1])
            except AttributeError:
                opts = []
        return opts

    def getcommandargs(self, string):
        # Raises KeyError (Command not found) or IndexError (command name not provided).
        if string is None:
            # exec self.
            cmd, args = self, None
        else:
            words = string.split(None, maxsplit=1)
            subcmd = self[words[0]]
            try:
                subargs = words[1]
            except IndexError:
                subargs = None
            cmd, args = subcmd.getcommandargs(subargs)
        return cmd, args

class SubMenu(RootMenu):

    def __init__(self, name, rootmenu):
        super().__init__(name=name)
        self.rootmenu = rootmenu

    def back(self, *args, **kwargs):
        self.rootmenu.popmenu(self)
        # Remove 'back' menu command, assumes that popmenu is the last command.
        self.commands.pop()

    def __call__(self):
        self.rootmenu.pushmenu(self)
        # Add a 'back' menu command.
        self.additem(CommandFunc(func=self.back))

class Menu:

    def __init__(self, name):
        self._commandstack = [RootMenu(name=name)]

    def __iter__(self):
        return iter(self._commandstack[-1])

    def __getitem__(self, key):
        return self._commandstack[-1][key]

    def additem(self, item):
        return self._commandstack[-1].additem(item)

    def getoptions(self, string):
        return self._commandstack[-1].getoptions(string)

    def getcommandargs(self, string):
        return self._commandstack[-1].getcommandargs(string)

    def pushmenu(self, m):
        assert isinstance(m, RootMenu)
        assert m in self._commandstack[-1].commands
        self._commandstack.append(m)

    def popmenu(self, m):
        assert isinstance(m, RootMenu)
        assert m is self._commandstack[-1]
        self._commandstack.pop()
