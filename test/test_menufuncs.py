# Module under test.
import bbc.menufuncs as mfuncs

import pytest

smallmenu = {
    'item1': 1,
    'item2': 2,
    'sub1': {
        'item1': 3,
        'item2': 4,
        },
    }

# Menu with one item a substring of another.
similarmenu = {
    'sub1': {
        'item1': 3,
        'item2': 4,
        },
    'sub10': {
        'item101': 101,
        'item102': 102,
        }
    }

@pytest.mark.parametrize('menu,search,expected', [
    (smallmenu, '', smallmenu),
    (smallmenu, 'i', {'item1': 1, 'item2': 2}),
    (smallmenu, 'it', {'item1': 1, 'item2': 2}),
    (smallmenu, 'item1', {'item1': 1}),
    (smallmenu, 'item2', {'item2': 2}),
    (smallmenu, 's', {'sub1': smallmenu['sub1']}),
    (smallmenu, 'x', {}),
    (smallmenu, 'xy', {}),
    (similarmenu, 'sub1', similarmenu),
    (similarmenu, 'sub10', {'sub10': similarmenu['sub10']}),
    (similarmenu, 'sub10x', {}),
    ])
def test_menumatches(menu, search, expected):
    """ Test menu item string matcher. """
    res = mfuncs.menumatches(menu, search)
    assert res == expected

@pytest.mark.parametrize('menu,search,expected', [
    (smallmenu, [], smallmenu),
    (smallmenu, [''], smallmenu),
    (smallmenu, ['i'], {'item1': 1, 'item2': 2}),
    (smallmenu, ['it'], {'item1': 1, 'item2': 2}),
    (smallmenu, ['item1'], {'item1': 1}),
    (smallmenu, ['item2'], {'item2': 2}),
    (smallmenu, ['s'], {'sub1': smallmenu['sub1']}),
    (smallmenu, ['sub1'], {'sub1': smallmenu['sub1']}),
    (smallmenu, ['s', ''], {}),
    (smallmenu, ['sub1', 'i'], smallmenu['sub1']),
    (smallmenu, ['x'], {}),
    (smallmenu, ['xy'], {}),
    (smallmenu, ['x', 'item1'], {}),
    (similarmenu, ['sub1', ''], similarmenu['sub1']),
    (similarmenu, ['sub1', 'i'], similarmenu['sub1']),
    (similarmenu, ['sub10'], {'sub10': similarmenu['sub10']}),
    (similarmenu, ['sub10', ''], similarmenu['sub10']),
    (similarmenu, ['sub10', 'i'], similarmenu['sub10']),
    (similarmenu, ['sub10', 'x'], {}),
    ])
def test_getoptions(menu, search, expected):
    """ Test get menu options based on command line input. """
    res = mfuncs.getoptions(menu, search)
    assert res == expected

@pytest.mark.parametrize('menu,search,expitem,expargs', [
    (smallmenu, [], smallmenu, []),
    (smallmenu, [''], smallmenu, ['']),
    (smallmenu, ['x'], smallmenu, ['x']),
    (smallmenu, ['item1'], smallmenu['item1'], []),
    (similarmenu, ['sub1'], similarmenu['sub1'], []),
    (similarmenu, ['sub1', 'item1'], similarmenu['sub1']['item1'], []),
    (similarmenu, ['sub10', 'item102', 'arg1'], similarmenu['sub10']['item102'], ['arg1']),
    (similarmenu, ['sub10', 'item102', 'arg1', 'arg2'], similarmenu['sub10']['item102'], ['arg1', 'arg2']),
    ])
def test_getmenuitem(menu, search, expitem, expargs):
    """ Test getting menu item and args based on command line. """
    resitem, resargs = mfuncs.getmenuitem(menu, search)
    assert resitem == expitem
    assert resargs == expargs
