""" Compatability module for different Python versions. """


try:
    from ordereddict import OrderedDict
except ImportError:  # pragma: no cover
    from collections import OrderedDict

# Linting purposes, no other use
OrderedDict
