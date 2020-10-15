from crdt import CRDT, Operation, ADD, REMOVE, UPDATE, merge
from datetime import datetime
from . import ans, upd, slice_dict
import pytest

def test_remove_same_key_twice():
    crdt = CRDT()

    crdt.add('a', 1)

    try:
        crdt.remove('a')
        crdt.remove('a')
        
        # In the same instance, this operation should fail
        assert False
    except KeyError:
        pass

def test_update_after_remove():
    crdt = CRDT()

    crdt.add('a', 1)

    try:
        crdt.update('a', 'b')
        crdt.remove('a')

        # In the same instance, this operation should fail
        assert False
    except KeyError:
        pass

def test_merge_remove_same_key_twice():
    crdt_1, crdt_2 = CRDT(), CRDT()

    crdt_1.add('a', 1)
    crdt_2.add('a', 1)

    crdt_1.remove('a')
    crdt_2.remove('a')

    # In a merged set, since the key is removed before, the later remove should be ignored
    merged = merge(crdt_1, crdt_2)

    assert len(merged.data) == 0

def test_merge_update_same_key_twice():
    crdt_1, crdt_2 = CRDT(), CRDT()

    crdt_1.add('a', 1)
    crdt_2.add('a', 2)

    crdt_1.update('a', 'b')
    crdt_2.update('a', 'c')

    merged = merge(crdt_1, crdt_2)

    # In a LWW merge, only the latest update should be present
    assert merged.data == {'c': 2}

def test_update_key_collision():
    pass

def test_merge_update_key_collision():
    # LWW behaviour: the newer value is retained
    pass
