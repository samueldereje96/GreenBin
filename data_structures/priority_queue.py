# # data_structures/priority_queue.py

# import heapq
# import itertools

# class MaxHeapPriorityQueue:
#     def __init__(self):
#         self._heap = []
#         self._counter = itertools.count()  # for stable ordering

#     def push(self, priority, item):
#         # Max heap => store negative priority
#         # Also store counter so equal priorities don't conflict
#         count = next(self._counter)
#         heapq.heappush(self._heap, (-priority, count, item))

#     def pop(self):
#         if not self._heap:
#             raise IndexError("pop from empty heap")
#         neg_priority, _, item = heapq.heappop(self._heap)
#         return -neg_priority, item  # return real priority

#     def peek(self):
#         if not self._heap:
#             return None
#         neg_priority, _, item = self._heap[0]
#         return -neg_priority, item

#     def __len__(self):
#         return len(self._heap)

#     def clear(self):
#         self._heap.clear()

import heapq

class MaxHeap:
    def __init__(self):
        self.heap = []

    def push(self, bin):
        heapq.heappush(self.heap, (-bin.fill_level, bin))

    def pop(self):
        if self.heap:
            return heapq.heappop(self.heap)[1]  # return bin object
        return None

    def is_empty(self):
        return len(self.heap) == 0
