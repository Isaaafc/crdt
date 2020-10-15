from crdt import CRDT, merge, Operation, INVALID_OP, INVALID_TS
from datetime import timedelta, datetime
import pytest

def test_out_of_order_append():
    crdt = CRDT()

    crdt.add('a', 1)
    inserted = crdt.log[-1]

    operation = Operation(ts=inserted.ts - 1, key=inserted.key, value=inserted.value, op=inserted.op)

    # Append should fail if the timestamp of the operation is earlier than the last inserted operation
    try:
        crdt.append(operation)
        assert False
    except AssertionError as e:
        assert str(e) == INVALID_TS

def test_invalid_op():
    crdt = CRDT()

    operation = Operation(ts=datetime.utcnow().timestamp(), key='a', value=1, op=-1)

    # Append should fail if the operation is invalid
    try:
        crdt.append(operation)
        assert False
    except AssertionError as e:
        assert str(e) == INVALID_OP

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
    crdt = CRDT()

    crdt.add('a', 1)
    crdt.add('b', 2)

    crdt.update('a', 'b')

    # In this implementation of LWW the update should overwrite the original key if the key already exists
    assert crdt.data == {'b': 1}

def test_merge_update_key_collision():
    crdt_1, crdt_2 = CRDT(), CRDT()

    crdt_1.add('a', 1)
    crdt_2.add('b', 2)

    crdt_1.update('a', 'b')

    merged = merge(crdt_1, crdt_2)

    # In this implementation of LWW the update should overwrite the original key if the key already exists
    assert merged.data == {'b': 1}
