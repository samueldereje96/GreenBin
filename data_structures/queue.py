# data_structures/queue.py

from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, item):
        """Add element to the back of the queue."""
        self.items.append(item)

    def dequeue(self):
        """Remove and return the element from the front of the queue."""
        if self.is_empty():
            return None
        return self.items.popleft()

    def peek(self):
        """Return the front element without removing it."""
        if self.is_empty():
            return None
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def __iter__(self):
        """Allow iteration through queue items (for displaying in UI)."""
        return iter(self.items)
