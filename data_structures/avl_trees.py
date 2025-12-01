class FacilityAVLTree:
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None
            self.height = 1

    def __init__(self, key=lambda f: f.id):
        self.root = None
        self.key = key

    # ---------------------------------------------------
    # Utility Functions
    # ---------------------------------------------------
    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    def rotate_right(self, y):
        x = y.left
        T2 = x.right

        # rotation
        x.right = y
        y.left = T2

        # update heights
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))

        return x

    def rotate_left(self, x):
        y = x.right
        T2 = y.left

        # rotation
        y.left = x
        x.right = T2

        # update heights
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    # ---------------------------------------------------
    # INSERT
    # ---------------------------------------------------
    def insert(self, value):
        self.root = self._insert(self.root, value)

    def _insert(self, node, value):
        if not node:
            return self.Node(value)

        if self.key(value) < self.key(node.value):
            node.left = self._insert(node.left, value)
        else:
            node.right = self._insert(node.right, value)

        # update height
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

        # balance
        balance = self.get_balance(node)

        # Left left
        if balance > 1 and self.key(value) < self.key(node.left.value):
            return self.rotate_right(node)

        # Right right
        if balance < -1 and self.key(value) > self.key(node.right.value):
            return self.rotate_left(node)

        # Left right
        if balance > 1 and self.key(value) > self.key(node.left.value):
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)

        # Right left
        if balance < -1 and self.key(value) < self.key(node.right.value):
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    # ---------------------------------------------------
    # DELETE
    # ---------------------------------------------------
    def delete(self, key_value):
        self.root = self._delete(self.root, key_value)

    def _delete(self, node, key_value):
        if not node:
            return None

        if key_value < self.key(node.value):
            node.left = self._delete(node.left, key_value)
        elif key_value > self.key(node.value):
            node.right = self._delete(node.right, key_value)
        else:
            # node to delete found
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            else:
                # smallest right subtree (inorder successor)
                successor = node.right
                while successor.left:
                    successor = successor.left

                node.value = successor.value
                node.right = self._delete(node.right, self.key(successor.value))

        # update height
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

        # balance
        balance = self.get_balance(node)

        # Left left
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.rotate_right(node)

        # Left right
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)

        # Right right
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.rotate_left(node)

        # Right left
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    # ---------------------------------------------------
    # SEARCH
    # ---------------------------------------------------
    def search(self, key_value):
        return self._search(self.root, key_value)

    def _search(self, node, key_value):
        if not node:
            return None
        if key_value == self.key(node.value):
            return node.value
        if key_value < self.key(node.value):
            return self._search(node.left, key_value)
        return self._search(node.right, key_value)

    # ---------------------------------------------------
    # INORDER TRAVERSAL
    # ---------------------------------------------------
    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.value)
            self._inorder(node.right, result)
