import heapq

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
