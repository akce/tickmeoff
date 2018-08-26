# Module under test.
from bbc.menu import *

import pytest

import contextlib
import io

m = Menu(name='root')
m.additem(Command(name='exec1'))	# arg defaults to NoArgument.
m.additem(Command(name='exec2', arg=StringArgument()))
m.additem(Command(name='exec22'))
enumargs = Command(name='enumargs', arg=EnumArgument(opts=['one', 'two']))
m.additem(enumargs)
s1 = SubMenu(name='submenu1', rootmenu=m)
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
    (m, 'submenu1 ', ['help', 'exec3']),
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
    (m, 'exec1', m['exec1'], []),
    (m, 'exec1 ', m['exec1'], []),
    # exec2 needs a string.
    (m, 'exec2 x', m['exec2'], ['x']),
    (m, 'exec2 xxxx', m['exec2'], ['xxxx']),
    (m, 'exec2 xxxx yyyy', m['exec2'], ['xxxx yyyy']),	# A string with spaces.
    # Play with extra whitespaces.
    (m, 'exec2  xxxx', m['exec2'], ['xxxx']),
    (m, 'exec2  xxxx ', m['exec2'], ['xxxx']),
    (m, 'exec2  xxxx  yyyy ', m['exec2'], ['xxxx  yyyy']),	# A string with spaces.
    # exec22 (as opposed to exec2). Takes no args.
    (m, 'exec22', m['exec22'], []),
    (m, 'exec22 ', m['exec22'], []),
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
    (m, 'submenu1', m['submenu1'], []),
    (m, 'submenu1 exec3', m['submenu1']['exec3'], []),
    (m, 'submenu1 exec3 ', m['submenu1']['exec3'], []),
    (m, 'submenu1  exec3 ', m['submenu1']['exec3'], []),
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

def test_menulist():
    assert list(m) == ['help', 'exec1', 'exec2', 'exec22', 'enumargs', 'submenu1']

def test_commandfuncdefaultname():
    cf = CommandFunc(func=bool)
    assert isinstance(cf, Command)
    assert cf.name == 'bool'
    assert isinstance(cf.arg, NoArgument)
    assert cf.func is bool

def test_commandfuncsetname():
    cf = CommandFunc(func=bool, name='myname')
    assert isinstance(cf, Command)
    assert cf.name == 'myname'
    assert isinstance(cf.arg, NoArgument)
    assert cf.func is bool

@pytest.fixture
def menu():
    root = Menu(name='xyzzy')
    root.additem(CommandFunc(name='test1', func=any))
    submenu = SubMenu(name='sub1', rootmenu=root)
    root.additem(submenu)
    def nodoc():
        pass
    root.additem(CommandFunc(name='test3', func=nodoc))
    return root

def test_pushpopmenu(menu):
    # Check the original menu.
    assert menu.name == 'xyzzy'
    assert list(menu) == ['help', 'test1', 'sub1', 'test3']
    cmd, args = menu.getcommandargs('sub1')
    cmd(*args)
    assert menu.name == 'sub1'
    assert list(menu) == ['help', 'back']
    assert menu.getoptions('') == ['help', 'back']
    assert menu.getoptions('b') == ['back']
    assert menu.getoptions('back') == ['back']
    assert menu.getoptions('blah') == []
    backcmd, backargs = menu.getcommandargs('back')
    backcmd(*args)
    assert list(menu) == ['help', 'test1', 'sub1', 'test3']
    # Make sure that 'back' command has been removed from sub1 menu.
    assert list(menu['sub1']) == ['help']

def test_helprootcommand(menu):
    # Get the help command.
    h, a = menu.getcommandargs('help')
    # HACK! Capture and compare expected stdout, only because I can't patch ''.format().
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        h(*a)
    assert stdout.getvalue() == '''help       list command help
test1      Return True if bool(x) is True for any x in the iterable.
sub1       stick menu sub1
test3      no documentation available
'''

def test_helpsubmenucommand(menu):
    # Select submenu.
    cmd, args = menu.getcommandargs('sub1')
    cmd(*args)
    # Get the help command.
    h, a = menu.getcommandargs('help')
    # HACK! Capture and compare expected stdout, only because I can't patch ''.format().
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        h(*a)
    print(stdout.getvalue())
    assert stdout.getvalue() == '''help       list command help
back       jump back to parent menu
'''
