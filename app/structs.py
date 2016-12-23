import collections
import copy


def deep_update(d, u):
    """
    Taken from: http://stackoverflow.com/a/3233356/721519
    :param d:
    :param u:
    :return:
    """
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = deep_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


class FrozenDict(dict):
    """
    A recursively frozen dictionary
    http://code.activestate.com/recipes/414283-frozen-dictionaries/#c7
    """

    def _blocked_attribute(self):
        raise AttributeError("A FrozenDict cannot be modified.")

    _blocked_attribute = property(_blocked_attribute)

    __delitem__ = __setitem__ = clear = _blocked_attribute
    pop = popitem = setdefault = update = _blocked_attribute

    def __new__(cls, *args, **kw):
        new = dict.__new__(cls)

        args_ = []
        for arg in args:
            if isinstance(arg, dict):
                arg = copy.copy(arg)
                for k, v in arg.items():
                    if isinstance(v, dict):
                        arg[k] = FrozenDict(v)
                    elif isinstance(v, list):
                        v_ = list()
                        for elm in v:
                            if isinstance(elm, dict):
                                v_.append(FrozenDict(elm))
                            else:
                                v_.append(elm)
                        arg[k] = tuple(v_)
                args_.append(arg)
            else:
                args_.append(arg)

        dict.__init__(new, *args_, **kw)
        return new

    def __init__(self, *args, **kw):
        pass

    def __hash__(self):
        try:
            return self._cached_hash
        except AttributeError:
            h = self._cached_hash = hash(tuple(sorted(self.items())))
            return h

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __missing__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __repr__(self):
        return "FrozenDict(%s)" % dict.__repr__(self)


class UserPrefs(FrozenDict):
    """
    Read only user prefs dict with defaults
    """

    DEFAULTS = {
        # Tags that mean we can use the image or cannot use the image
        'whitelist': [],
        'blacklist': [],
    }

    def __new__(cls, prefs):
        prefs = deep_update(UserPrefs.DEFAULTS.copy(), prefs)
        return FrozenDict.__new__(cls, prefs)
