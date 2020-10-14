from collections import OrderedDict
import pytest

__ans__ = OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)])

def slice_dict(d, start, end):
    """
    Convenience function to slice an ordered dictionary. Returns the sliced dictionary

    Parameters
    ----------
    d:
        dict to slice
    start:
        start index of keys
    end:
        end index of keys
    """
    items = [(k, v) for k, v in d.items()]

    return {x[0]:x[1] for x in items[start:end]}

@pytest.fixture(scope='function')
def ans():
    return __ans__

@pytest.fixture(scope='function')
def upd():
    return {k:f'{k}_upd' for k in __ans__}
