""" Compatability module for different Python versions. """

try:
    from ordereddict import OrderedDict  # NOQA
except ImportError:  # pragma: no cover
    from collections import OrderedDict  # NOQA
