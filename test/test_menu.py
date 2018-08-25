# Module under test.
from bbc.menu import *

import pytest

m = Menu(name='root')
m.additem(Command(name='exec1'))	# arg defaults to NoArgument.
m.additem(Command(name='exec2', arg=StringArgument()))
m.additem(Command(name='exec22'))
enumargs = Command(name='enumargs', arg=EnumArgument(opts=['one', 'two']))
m.additem(enumargs)
s1 = Menu(name='submenu1')
s1.additem(Command(name='exec3', arg=NoArgument()))
m.additem(s1)

@pytest.mark.parametrize('menu,search,expected', [
    (m, '', list(m)),
    (m, 'exec1', ['exec1']),
    (m, 'exec1 ', []),			# Trailing whitespace, match subcommand/args.
    (m, 'exec2', ['exec2', 'exec22']),
    (m, 'exec2 ', []),			# Trailing whitespace, match subcommand/args.
    (m, 'exec22', ['exec22']),
    (m, 'exec22 ', []),			# Trailing whitespace, match subcommand/args.
    (m, 'no-match', []),
    # With submenu on its own.
    (s1, '', list(s1)),
    (s1, 'exec3', ['exec3']),
    (s1, 'exec3 ', []),			# Trailing whitespace, match subcommand/args.
    (s1, 'no-match', []),
    # Now submenu via main menu.
    (m, 'submenu1 ', ['exec3']),
    (m, 'submenu1 e', ['exec3']),
    (m, 'submenu1 exec3', ['exec3']),
    (m, 'submenu1 exec3 ', []),		# Trailing whitespace, match subcommand/args.
    (m, 'submenu1 no-match', []),
    (m, 'exec1 no-match', []),
    (m, 'no-match arg', []),
    # With args.
    (m, 'enumargs', ['enumargs']),
    (m, 'enumargs ', ['one', 'two']),
    (m, 'enumargs o', ['one']),
    (m, 'enumargs x', []),
    ])
def test_getopts(menu, search, expected):
    results = menu.getoptions(search)
    assert results == expected

@pytest.mark.parametrize('menu,search,ecmd,eargs', [
    # exec1 defaults to no arguments.
    (m, 'exec1', m['exec1'], None),
    (m, 'exec1 ', m['exec1'], None),
    # exec2 needs a string.
    (m, 'exec2 x', m['exec2'], ['x']),
    (m, 'exec2 xxxx', m['exec2'], ['xxxx']),
    (m, 'exec2 xxxx yyyy', m['exec2'], ['xxxx yyyy']),	# A string with spaces.
    # Play with extra whitespaces.
    (m, 'exec2  xxxx', m['exec2'], ['xxxx']),
    (m, 'exec2  xxxx ', m['exec2'], ['xxxx']),
    (m, 'exec2  xxxx  yyyy ', m['exec2'], ['xxxx  yyyy']),	# A string with spaces.
    # exec22 (as opposed to exec2). Takes no args.
    (m, 'exec22', m['exec22'], None),
    (m, 'exec22 ', m['exec22'], None),
    # enum args.
    (m, 'enumargs one', m['enumargs'], ['one']),
    (m, 'enumargs one ', m['enumargs'], ['one']),
    (m, 'enumargs  one', m['enumargs'], ['one']),
    (m, 'enumargs  one ', m['enumargs'], ['one']),
    (m, 'enumargs two', m['enumargs'], ['two']),
    (m, 'enumargs two ', m['enumargs'], ['two']),
    (m, 'enumargs  two', m['enumargs'], ['two']),
    (m, 'enumargs  two ', m['enumargs'], ['two']),
    # submenu1 -> exec3
    (m, 'submenu1', m['submenu1'], None),
    (m, 'submenu1 exec3', m['submenu1']['exec3'], None),
    (m, 'submenu1 exec3 ', m['submenu1']['exec3'], None),
    (m, 'submenu1  exec3 ', m['submenu1']['exec3'], None),
    ])
def test_getcommandargs(menu, search, ecmd, eargs):
    rcmd, rargs = menu.getcommandargs(search)
    assert rcmd == ecmd
    assert rargs == eargs

@pytest.mark.parametrize('menu,search,expected', [
    (m, '', IndexError),
    (m, 'blah', KeyError),
    # exec1 takes no arguments.
    (m, 'exec1 arg1', ValueError),
    (m, 'exec1   arg1', ValueError),
    (m, 'exec1 arg1  ', ValueError),
    (m, 'exec1  arg1  ', ValueError),
    # exec2 takes a string argument.
    (m, 'exec2', ValueError),
    (m, 'exec2 ', ValueError),
    # enums must fully match.
    (m, 'enumargs', ValueError),
    (m, 'enumargs ', ValueError),
    (m, 'enumargs  ', ValueError),
    (m, 'enumargs o', ValueError),
    (m, 'enumargs on', ValueError),
    (m, 'enumargs t', ValueError),
    (m, 'enumargs tw', ValueError),
    # submenu1 -> exec3, menus raise KeyError..
    (m, 'submenu1 blah', KeyError),
    # exec3 takes no args.
    (m, 'submenu1 exec3 x', ValueError),
    (m, 'submenu1  exec3 x', ValueError),
    ])
def test_getcommandargs_errors(menu, search, expected):
    with pytest.raises(expected):
        menu.getcommandargs(search)
