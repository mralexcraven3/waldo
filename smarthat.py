import heapq
from operator import attrgetter


class SmartHat:
    def __init__(self, iterable):
        heapq.heapify(iterable)
        self.heap = iterable

    def pop(self):
        """Pop off the smallest object. """
        return heapq.heappop(self.heap)

    def push(self, elem):
        heapq.heappush(self.heap, elem)

    def __len__(self):
        return len(self.heap)

    def __iter__(self):
        for obj in self.heap:
            yield(obj)
        raise StopIteration()


import random
if __name__ == '__test__':
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
