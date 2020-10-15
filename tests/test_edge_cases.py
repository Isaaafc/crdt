from crdt import CRDT

def test_remove_same_key_twice():
    pass

def test_update_after_remove():
    # In the same instance, this operation should fail
    pass

def test_merge_remove_same_key_twice():
    pass

def test_merge_remove_old_key_after_update():
    # Should retain the updated key (deleting the updated key is an option but is not chosen)
    pass

def test_out_of_order_append():
    pass

def test_update_key_collision():
    pass

def test_merge_update_key_collision():
    # LWW behaviour: the newer value is retained
    pass
