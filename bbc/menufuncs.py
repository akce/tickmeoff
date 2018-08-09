""" Menu utility functions. """

def menumatches(menudict, searchstr):
    """ Return the dict of menu strings that match or begin with searchstr. """
    return {x: menudict[x] for x in menudict if x.startswith(searchstr)}

def getoptions(menudict, pathlist):
    try:
        cmd = pathlist[0]
    except IndexError:
        # Nothing in pathlist, return all possible options.
        ret = menudict
    else:
        matches = menumatches(menudict, cmd)
        args = pathlist[1:]
        if args:
            # Having args implies that there's already a command.
            # Find the command and pass it the args for completion.
            # Return nothing if the command does not exist.
            try:
                child = matches[cmd]
            except KeyError:
                # Exact cmd is not found.
                ret = {}
            else:
                ret = getoptions(child, args)
        else:
            # No args, return matches for cmd.
            ret = matches
    return ret

def getmenuitem(menudict, pathlist):
    item = menudict
    args = pathlist
    for path in pathlist:
        try:
            item = item[path]
            args = args[1:]
        except (KeyError, TypeError):
            # path is not found, or item is not subscriptable. End search and return.
            break
    return item, args
