""" Compatability module for different Python versions. """


try:
    from ordereddict import OrderedDict  # noqa
except ImportError:  # pragma: no cover
    from collections import OrderedDict  # noqa
