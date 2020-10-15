from collections import OrderedDict, namedtuple
from datetime import datetime

# Operation entry
Operation = namedtuple('Operation', ['ts', 'key', 'value', 'op'])

# Operation types
ADD = 0
REMOVE = 1
UPDATE = 3

class CRDT():
    """
    CRDT dict variant. This class keeps a log of all operations performed in sequence.
    """
    def __init__(self):
        self.log = []
        self.data = OrderedDict()

    def add(self, key, value):
        """
        Add operation
        """
        operation = Operation(ts=datetime.utcnow().timestamp(), key=key, value=value, op=ADD)
        self.append(operation)

    def remove(self, key):
        """
        Remove operation
        """
        operation = Operation(ts=datetime.utcnow().timestamp(), key=key, value=None, op=REMOVE)
        self.append(operation)

    def update(self, key, new_key):
        """
        Update the key of the resulting dict. Essentially the same steps as add
        """
        operation = Operation(ts=datetime.utcnow().timestamp(), key=key, value=new_key, op=UPDATE)
        self.append(operation)

    def append(self, operation):
        assert operation.op in [ADD, REMOVE, UPDATE], 'Invalid operation'

        if operation.op == ADD:
            self.data[operation.key] = operation.value
        elif operation.op == REMOVE:
            # If the key does not exist, an exception is thrown
            self.data.pop(operation.key)
        else:
            # If the key does not exist, an exception is thrown
            self.data[operation.value] = self.data.pop(operation.key)

        self.log.append(operation)

def merge(crdt, other):
    """
    Merge two CRDTs. Returns a new CRDT with the merged sequence of logs. The data in this class will not be affected
    When the timestamps of two operations are the same, the operation of this class will be taken first
    An important input assumption is both crdt and other must contain valid logs produced by only CRDT.add(), CRDT.remove(), CRDT.update(), and merge() functions

    Parameters
    ----------
    crdt, other:
        CRDTs to be merged
    """
    def append_LWW(operation):
        """
        Append operation with Last-Write-Wins mechanism to res

        Parameters
        ----------
        operation:
            Operation to be appended
        """
        if operation.op == ADD:
            res.append(operation)
        elif operation.op == REMOVE:
            rm_val = res.data.get(operation.key)

            if not rm_val:
                if operation.key in removed:
                    # Ignore the remove operation if it has already been removed
                    return

                # If the key does not exist in both the current dict and the updated dict, an exception is thrown
                rm_key = updated.pop(operation.key)
                rm_val = res.data[rm_key]

                # Treat the remove operation as removing the updated key such that validity of the log is preserved
                new_op = Operation(ts=operation.ts, key=rm_key, value=None, op=REMOVE)
                res.append(new_op)
                removed[rm_key] = rm_val
            else:
                res.append(operation)
                removed[operation.key] = rm_val
        else:
            old = res.data.get(operation.key)

            if not old:
                # If the key is in the current set, it must either be updated or removed
                if operation.key in updated:
                    # Since neither set can use the old key now, remove it from the updated dict
                    old = updated.pop(operation.key)
                    new_op = Operation(ts=operation.ts, key=old, value=operation.value, op=UPDATE)
                    res.append(new_op)
                else:
                    # If the key does not exist in both the current dict and the removed dict, an exception is thrown
                    old = removed.pop(operation.key)
                    
                    # Treat the update as add since the key is removed such that validity of the log is preserved
                    new_op = Operation(ts=operation.ts, key=operation.value, value=old, op=ADD)
                    res.append(new_op)
            else:
                res.append(operation)
                updated[operation.key] = operation.value

    i, j = 0, 0
    res = CRDT()

    removed = OrderedDict()
    updated = OrderedDict()

    while i < len(crdt.log) and j < len(other.log):
        if crdt.log[i].ts <= other.log[j].ts:
            operation = crdt.log[i]
            i += 1
        else:
            operation = other.log[j]
            j += 1

        append_LWW(operation)

    if i < len(crdt.log):
        for operation in crdt.log[i:]:
            append_LWW(operation)
    else:
        for operation in other.log[j:]:
            append_LWW(operation)

    return res
