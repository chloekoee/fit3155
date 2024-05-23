from aux import print_tree


class Node:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []  # Holds keys: []
        self.children = []


class BTree:
    def __init__(self, t):
        self.root = Node(True)
        #'t' is order of B Tree
        self.t = t

    def search(self, k, node=None):
        """Recursively searches for key 'k' from node 'node'.
        If 'node' is not specified, then search occurs from root.

        Returns 'None' if 'k' is not found.
        Otherwise returns a tuple of node and index at which the key was found.

        Arguments:
                k -- key to be searched
                node -- node to search from
        """

        ## If a start node has been specified, search from node
        if node != None:
            i = 0  # Current index checking at/cursor

            # Increment while i within bounds and k greater than current key
            while i < len(node.keys) and k > node.keys[i]:
                i += 1

            # If no overflow and match, return
            if i < len(node.keys) and k == node.keys[i]:
                return (node, i)

            # Base case
            elif node.leaf:
                return None
            else:  # Recursive Case: Search in children
                return self.search(k, node.children[i])

        ## Search entire tree as node not provided
        else:
            return self.search(k, self.root)

    def insert(self, k):
        """Calls helper functions to insert key 'k' in the B-Tree
        Recursively inserts key 'k' in B-Tree
        If traverses upon a node at capacity, then splits it

        Arguments:
                k -- key to be inserted
        """
        root = self.root  ## why does it work if this is always set to root

        # Encountered full node
        if len(root.keys) == (2 * self.t) - 1:
            temp = Node()
            self.root = temp

            # Former root becomes 0th child of new root 'temp'
            temp.children.insert(0, root)
            self._split_child(temp, 0)
            self._insert_nonfull(temp, k)

        else:
            self._insert_nonfull(root, k)

    def _insert_nonfull(self, x, k):
        """Insert key 'k' at position 'x' in a non-full node

        Arguments:
                x -- Position in node
                k -- key to be inserted
        """
        i = len(x.keys) - 1  # Upper bound (start from right)
        if x.leaf:  # If non - full leaf then insert
            x.keys.append((None, None))  # Create temporary position
            while i >= 0 and k < x.keys[i]:  #  Until at left bound
                x.keys[i + 1] = x.keys[i]  # Shift everyting rightward
                i -= 1  # Decrement index to insert at
            x.keys[i + 1] = k  # Insert (+1 offsets last decrement)

        else:  # If internal node, traverse
            while i >= 0 and k < x.keys[i]:  # Search correct key
                i -= 1
            i += 1

            # If traverse onto a full node, split
            if len(x.children[i].keys) == (2 * self.t) - 1:
                self._split_child(x, i)
                if k > x.keys[i]:
                    i += 1  # ??
            self._insert_nonfull(x.children[i], k)  # recursive call

    def _split_child(self, x, i):
        """Splits the child of node at 'x' from index 'i'
        This differs from Cormen as rather than taking in `y`, the child node
        `y`s position in x.children is taken in instead, as `i`
        Arguments:
                x -- parent node of the node to be split
                i -- index value of the child
        """
        t = self.t
        y = x.children[i]

        ## New node z holds keys greater than median - made a child of x
        z = Node(y.leaf)
        x.children.insert(pos=i + 1, elmt=z)
        x.keys.insert(pos=i, elmt=y.keys[t - 1])

        z.keys = y.keys[t : (2 * t) - 1]
        y.keys = y.keys[0 : t - 1]

        if not y.leaf:
            z.children = y.children[t : 2 * t]
            y.children = y.children[0 : t - 1]

    def delete(self, x, k):
        """Calls helper functions to delete key 'k' after searching from node 'x'

        Arguments:
                x -- node, according to whose relative position, helper functions are called
                k -- key to be deleted
        """
        t = self.t
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        # Deleting the key if the node is a leaf
        if x.leaf:
            if i < len(x.keys) and x.keys[i] == k:
                x.keys.pop(i)
                return
            return

        # Calling '_delete_internal_node' when x is an internal node and contains the key 'k'
        if i < len(x.keys) and x.keys[i] == k:
            return self._delete_internal_node(x, k, i)
        # Recursively calling 'delete' on x's child
        elif len(x.children[i].keys) >= t:
            self.delete(x.children[i], k)
        # Ensuring that a child always has atleast 't' keys
        else:
            if i != 0 and i + 2 < len(x.children):
                if len(x.children[i - 1].keys) >= t:
                    self._delete_sibling(x, i, i - 1)
                elif len(x.children[i + 1].keys) >= t:
                    self._delete_sibling(x, i, i + 1)
                else:
                    self._del_merge(x, i, i + 1)
            elif i == 0:
                if len(x.children[i + 1].keys) >= t:
                    self._delete_sibling(x, i, i + 1)
                else:
                    self._del_merge(x, i, i + 1)
            elif i + 1 == len(x.children):
                if len(x.children[i - 1].keys) >= t:
                    self._delete_sibling(x, i, i - 1)
                else:
                    self._del_merge(x, i, i - 1)
            self.delete(x.children[i], k)

    def _delete_internal_node(self, x, k, i):
        """Deletes internal node

        Arguments:
                x -- internal node in which key 'k' is present
                k -- key to be deleted
                i -- index position of key in the list

        """
        t = self.t
        # Deleting the key if the node is a leaf
        if x.leaf:
            if x.keys[i] == k:
                x.keys.pop(i)
                return
            return

        # Replacing the key with its predecessor and deleting predecessor
        if len(x.children[i].keys) >= t:
            x.keys[i] = self._delete_predecessor(x.children[i])
            return
        # Replacing the key with its successor and deleting successor
        elif len(x.children[i + 1].keys) >= t:
            x.keys[i] = self._delete_successor(x.children[i + 1])
            return
        # Merging the child, its left sibling and the key 'k'
        else:
            self._del_merge(x, i, i + 1)
            self._delete_internal_node(x.children[i], k, self.t - 1)

    def _delete_predecessor(self, x):
        """Returns and deletes predecessor of key 'k' which is to be deleted

        Arguments:
                x -- node
        """
        if x.leaf:
            return x
        n = len(x.keys) - 1
        if len(x.children[n].keys) >= self.t:
            self._delete_sibling(x, n + 1, n)
        else:
            self._del_merge(x, n, n + 1)
        self._delete_predecessor(x.children[n])

    def _delete_successor(self, x):
        """Returns and deletes successor of key 'k' which is to be deleted

        Arguments:
                x -- node
        """
        if x.leaf:
            return x.keys.pop(0)
        if len(x.children[1].keys) >= self.t:
            self._delete_sibling(x, 0, 1)
        else:
            self._del_merge(x, 0, 1)
        self._delete_successor(x.children[0])

    def _del_merge(self, x, i, j):
        """Merges the children of x and one of its own keys

        Arguments:
                x -- parent node
                i -- index of one of the children
                j -- index of one of the children
        """
        cnode = x.children[i]

        # Merging the x.children[i], x.children[j] and x.keys[i]
        if j > i:
            rsnode = x.children[j]
            cnode.keys.append(x.keys[i])
            # Assigning keys of right sibling node to child node
            for k in range(len(rsnode.keys)):
                cnode.keys.append(rsnode.keys[k])
                if len(rsnode.children) > 0:
                    cnode.children.append(rsnode.children[k])
            if len(rsnode.children) > 0:
                cnode.children.append(rsnode.children.pop())
            new = cnode
            x.keys.pop(i)
            x.children.pop(j)
        # Merging the x.children[i], x.children[j] and x.keys[i]
        else:
            lsnode = x.children[j]
            lsnode.keys.append(x.keys[j])
            # Assigning keys of left sibling node to child node
            for i in range(len(cnode.keys)):
                lsnode.keys.append(cnode.keys[i])
                if len(lsnode.children) > 0:
                    lsnode.children.append(cnode.children[i])
            if len(lsnode.children) > 0:
                lsnode.children.append(cnode.children.pop())
            new = lsnode
            x.keys.pop(j)
            x.children.pop(i)

        # If x is root and is empty, then re-assign root
        if x == self.root and len(x.keys) == 0:
            self.root = new

    def _delete_sibling(self, x, i, j):
        """Borrows a key from jth child of x and appends it to ith child of x

        Arguments:
                x -- parent node
                i -- index of one of the children
                j -- index of one of the children
        """
        cnode = x.children[i]
        if i < j:
            # Borrowing key from right sibling of the child
            rsnode = x.children[j]
            cnode.keys.append(x.keys[i])
            x.keys[i] = rsnode.keys[0]
            if len(rsnode.children) > 0:
                cnode.children.append(rsnode.children[0])
                rsnode.children.pop(0)
            rsnode.keys.pop(0)
        else:
            # Borrowing key from left sibling of the child
            lsnode = x.children[j]
            cnode.keys.insert(0, x.keys[i - 1])
            x.keys[i - 1] = lsnode.keys.pop()
            if len(lsnode.children) > 0:
                cnode.children.insert(0, lsnode.children.pop())


def main():
    B = BTree(3)
    entries = [chr(ord("a") + i) for i in range(10)]
    B.root = Node()
    B.root.keys = ["g", "m", "p", "x"]
    children = [
        ["a", "c", "d", "e"],
        ["j", "k"],
        ["n", "o"],
        ["r", "s", "t", "u", "v"],
        ["y", "z"],
    ]
    for child in children:
        newChild = Node(leaf=True)
        newChild.keys = child
        B.root.children.append(newChild)
    print_tree(B.root)
    entries = ["b", "q", "l", "f"]
    for i in entries:
        B.insert(i)
        print_tree(B.root)
        print("\n")
    B.delete(B.root, ("m"))
    # if B.search(54) != None:
    #     (x, i) = B.search(54)
    # else:
    #     print("Element not found!")
    print("\n")
    print_tree(B.root)


if __name__ == "__main__":
    main()
