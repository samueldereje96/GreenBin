class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = new_node
        self.size += 1

    def remove(self, condition_fn):
        """Remove first node where condition_fn(node.data) == True"""
        curr = self.head
        prev = None
        while curr:
            if condition_fn(curr.data):
                if prev:
                    prev.next = curr.next
                else:
                    self.head = curr.next
                self.size -= 1
                return True
            prev = curr
            curr = curr.next
        return False

    def find(self, condition_fn):
        """Return first matching data node"""
        curr = self.head
        while curr:
            if condition_fn(curr.data):
                return curr.data
            curr = curr.next
        return None

    def __iter__(self):
        curr = self.head
        while curr:
            yield curr.data
            curr = curr.next

    def __len__(self):
        return self.size
