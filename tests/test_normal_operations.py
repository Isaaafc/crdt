from crdt import CRDT, Operation, ADD, REMOVE, UPDATE, merge
from datetime import datetime
from . import ans, upd, slice_dict
import pytest

def test_add_one():
    crdt = CRDT()
    crdt.add('a', 1)

    assert len(crdt.log) == 1
    assert crdt.data == {'a': 1}
    assert crdt.log[0].op == ADD

def test_remove_one():
    crdt = CRDT()
    crdt.add('a', 1)
    crdt.remove('a')

    assert len(crdt.log) == 2
    assert len(crdt.data) == 0
    assert crdt.log[1].op == REMOVE

def test_update_one():
    crdt = CRDT()
    crdt.add('a', 1)
    crdt.update('a', 'b')

    assert len(crdt.log) == 2
    assert crdt.data == {'b': 1}
    assert crdt.log[1].op == UPDATE

def test_add_many(ans):
    crdt = CRDT()

    for k, v, in ans.items():
        crdt.add(k, v)

    assert len(crdt.log) == len(ans)
    assert crdt.data == ans

def test_remove_many(ans):
    crdt = CRDT()

    for k, v in ans.items():
        crdt.add(k, v)
    
    for k in ans:
        crdt.remove(k)
    
    # The same set of keys is added and removed, the length of the log should be twice that of the ans set
    assert len(crdt.log) == len(ans) * 2
    assert len(crdt.data) == 0

def test_update_many(ans, upd):
    crdt = CRDT()

    for k, v in ans.items():
        crdt.add(k, v)

    for k, v in upd.items():
        crdt.update(k, v)

    # The keys are added then updated, the length of the log should be the sum of the lengths of the ans and upd set
    assert len(crdt.log) == len(ans) + len(upd)
    assert crdt.data == {upd[k]:v for k, v in ans.items()}

def test_add_same_key_twice():
    crdt = CRDT()
    key = 'a'
    values = [1, 2, 3]

    for v in values:
        crdt.add(key, v)

    assert len(crdt.log) == len(values)

    # Only the updated value should be present
    assert crdt.data == {key: values[-1]}

def test_merge_add_only(ans):
    crdt_1, crdt_2 = CRDT(), CRDT()
    ans_1, ans_2 = slice_dict(ans, 0, len(ans) // 2), slice_dict(ans, len(ans) // 2, len(ans))

    for k, v in ans_1.items():
        crdt_1.add(k, v)
    
    for k, v in ans_2.items():
        crdt_2.add(k, v)

    merged = merge(crdt_1, crdt_2)

    assert len(merged.log) == len(crdt_1.log) + len(crdt_2.log)
    assert merged.data == ans

def test_merge_add_same_key_diff_values(ans):
    crdt_1, crdt_2 = CRDT(), CRDT()
    ans_alt = {k:v + 1 for k, v in ans.items()}

    for k, v in ans.items():
        crdt_1.add(k, v)
    
    for k, v in ans_alt.items():
        crdt_2.add(k, v)

    merged = merge(crdt_1, crdt_2)

    assert len(merged.log) == len(crdt_1.log) + len(crdt_2.log)

    # Only the values updated later should be present
    assert merged.data == ans_alt

def test_merge_add_remove(ans):
    crdt_1, crdt_2 = CRDT(), CRDT()
    ans_1, ans_2 = slice_dict(ans, 0, len(ans) // 2), slice_dict(ans, len(ans) // 2, len(ans))

    # Both CRDTs contain the same data initially
    for k, v in ans.items():
        crdt_1.add(k, v)
        crdt_2.add(k, v)

    # Remove second half of the ans set in crdt_2
    for k in ans_2:
        crdt_2.remove(k)
    
    merged = merge(crdt_1, crdt_2)

    # Only first half of the ans set should remain
    assert merged.data == ans_1

def test_merge_add_update(ans, upd):
    crdt_1, crdt_2 = CRDT(), CRDT()
    ans_1, ans_2 = slice_dict(ans, 0, len(ans) // 2), slice_dict(ans, len(ans) // 2, len(ans))

    for k, v in ans_1.items():
        crdt_1.add(k, v)
    
    for k, v in ans_2.items():
        crdt_2.add(k, v)

    for k in ans_2:
        crdt_2.update(k, upd[k])
    
    merged = merge(crdt_1, crdt_2)

    # Only keys in the second half of the ans set should be updated
    ans_1.update({upd[k]:v for k, v in ans_2.items()})
    assert merged.data == ans_1

def test_merge_add_remove_update(ans, upd):
    crdt_1, crdt_2 = CRDT(), CRDT()
    ans_1, ans_2 = slice_dict(ans, 0, len(ans) // 2), slice_dict(ans, len(ans) // 2, len(ans))

    for k, v in ans.items():
        crdt_1.add(k, v)
        crdt_2.add(k, v)

    # Remove the elements in the second half of the ans set in crdt_1
    for k in ans_2:
        crdt_1.remove(k)

    # Update same keys that are removed in crdt_1 in crdt_2
    for k in ans_2:
        crdt_2.update(k, upd[k])

    merged = merge(crdt_1, crdt_2)

    # Since this is a LWW set, the **updates** will overwrite the **removes** since they're executed later
    ans_1.update({upd[k]:v for k, v in ans_2.items()})
    assert merged.data == ans_1

def test_merge_add_update_remove(ans, upd):
    crdt_1, crdt_2 = CRDT(), CRDT()
    ans_1, ans_2 = slice_dict(ans, 0, len(ans) // 2), slice_dict(ans, len(ans) // 2, len(ans))

    for k, v in ans.items():
        crdt_1.add(k, v)
        crdt_2.add(k, v)

    # Update the elements in the second half of the ans set in crdt_1 (opposite of test_merge_add_remove_update())
    for k in ans_2:
        crdt_1.update(k, upd[k])

    # Remove old keys that are updated in crdt_1 in crdt_2 (opposite of test_merge_add_remove_update())
    for k in ans_2:
        crdt_2.remove(k)

    merged = merge(crdt_1, crdt_2)

    # Since this is a LWW set, the **removes** will overwrite the **updates** since they're executed later
    assert merged.data == ans_1
