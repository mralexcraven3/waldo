"""
A smart data structure that lets you draw random elements from a set with a
probability distribution weighted on likelihood of success.
"""
import heapq
from operator import attrgetter

class HeapObj:
    def __init__(self, obj, alpha=0, beta=0):
        """
        Create a new heap object.

        alpha = the number of successes
        beta = the number of failures
        """
        self.obj = obj
        self.alpha = alpha
        self.beta = beta

    def __lt__(self, other):
        return self.beta < other.beta

    def success(self):
        self.alpha += 1

    def fail(self):
        self.beta += 1

    def __repr__(self):
        return "<HeapObj: %s, alpha=%s, beta=%s>" % (self.obj, self.alpha,
                self.beta)

    @classmethod
    def convert(cls, obj, *args, **kwargs):
        return HeapObj(obj=obj, *args, **kwargs)


class SmartHat:
    def __init__(self, iterable):
        _data = [HeapObj.convert(obj) for obj in iterable]
        heapq.heapify(_data)
        self.heap = _data

    def pop(self):
        """Pop off the smallest object. """
        return heapq.heappop(self.heap)

    def push(self, elem):
        heapq.heappush(self.heap, elem)

    def __len__(self):
        return len(self.heap)

import random
if __name__ == '__main__':
    test_list = [
        '127.0.0.1:1230',
        '127.0.0.1:1231',
        '127.0.0.1:1232',
        '127.0.0.1:1233',
        '127.0.0.1:1234',
    ]
    sh = SmartHat(test_list)
    for i in range(100):
        elem = sh.pop()
        if random.random() > .5:
            elem.success()
        else:
            elem.fail()
        sh.push(elem)

