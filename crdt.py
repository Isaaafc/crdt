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
        # TODO try OrderedDict
        self.log = []

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
        # TODO Check if key is removed?
        operation = Operation(ts=datetime.utcnow().timestamp(), key=key, value=None, op=REMOVE)
        self.append(operation)

    def update(self, key, new_key):
        """
        Update the key of the resulting dict. Essentially the same steps as add
        """
        operation = Operation(ts=datetime.utcnow().timestamp(), key=key, value=new_key, op=UPDATE)
        self.append(operation)

    def append(self, operation):
        """
        Validate and append an operation to the log
        """
        self.log.append(operation)
        # TODO validation

    def data(self):
        """
        Get the result dict from the CRDT after all of the ops. Returns an ordered dictionary ordered by the sequence of operations
        """
        res = OrderedDict()

        for operation in self.log:
            if operation.op == ADD:
                res[operation.key] = operation.value
            elif operation.op == REMOVE:
                res.pop(operation.key, None)
            elif operation.op == UPDATE:
                # If the key does not exist, an exception is thrown
                old = res.pop(operation.key)
                res[operation.value] = old

        return res

def merge(crdt, other):
    """
    Merge two CRDTs. Returns a new CRDT with the merged sequence of logs. The data in this class will not be affected.
    When the timestamps of two operations are the same, the operation of this class will be taken first
    """
    i, j = 0, 0
    res = CRDT()

    while i < len(crdt.log) and j < len(other.log):
        if crdt.log[i].ts <= other.log[j].ts:
            res.append(crdt.log[i])
            i += 1
            continue

        res.append(other.log[j])
        j += 1

    if i < len(crdt.log):
        for operation in crdt.log[i:]:
            res.append(operation)
    else:
        for operation in other.log[j:]:
            res.append(operation)

    return res
