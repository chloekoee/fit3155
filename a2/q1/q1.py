from collections import defaultdict
import sys

"""
CHLOE KOE 
33109109
A2 FIT3155

Suffix Tree Design Summary:
The implementation for constructing and utilizing my suffix tree can be broken down into distinct phases:

Part 1: Suffix Tree Construction

1. Suffix Tree Construction Using Ukkonen's Algorithm
    - The suffix tree is built using Ukkonen's algorithm ensuring the tree is constructed in O(n) time complexity,
      where n is the length of the input string.

2. Depth-First Search (DFS) in Lexicographic Order
    - A DFS is performed on the suffix tree in lexicographic order. Each node processes its children based on their 
      lexicographical order, and since the maximum number of children a node can have is limited by the size of the ASCII character set,
      the sorting operation is effectively constant time. Note that for the construction of the tree, a hash map is used to 
      access children in constant time, the sorted children array is only constructed and used in the DFS.
    - The DFS terminates early if all requested positions have been found, optimizing the traversal process.

Part 2: Extension for Encoding (Question 2)

To adapt the suffix tree construction for encoding purposes (Part 2), the implementation incorporates an 'encoder mode'. 
This mode adds specific operations that are performed concurrently with the suffix tree construction and DFS traversal:

1. Character Frequency Map Construction:
    - During each phase of the suffix tree construction, the frequency of the current character processed 
    (denoted by `str[j]` in phase j) is updated. This is used to construct a character frequency hashmap that is for the Huffman encoding.

2. Burrows-Wheeler Transform Construction:
    - As the DFS visits each suffix `i`, the Burrows-Wheeler Transform is constructed by appending `string[(i-1) % n]` to the BWT array. 
    This operation is integrated into the DFS to eliminate the need for a separate pass over the data.
"""


class Edge:
    """
    Represents an edge in a Suffix Tree, which is a substring or a portion of the input string.

    Attributes:
        head (Node): The starting node of the edge.
        tail (Node): The ending node of the edge.
        start (int): The starting index in the string for this edge's label.
        end (int): The ending index in the string for this edge's label, can be -1 indicating current position.
        value (any): Additional value that can be used to store any specific data related to the edge.

    Methods:
        full_value: Retrieves the full string value represented by this edge.
        length: Calculates the length of the substring represented by this edge.
    """

    def __init__(self, head, tail, start, end, value):
        self.head = head
        self.tail = tail
        self.start = start
        self.end = end
        self.value = value

    def full_value(self, string, global_end):
        if self.end == -1:
            return string[self.start : global_end + 1]
        else:
            return string[self.start : self.end + 1]

    def length(self, global_end):
        return (global_end if self.end == -1 else self.end) - self.start + 1

    def __repr__(self):
        return f"{self.value}|{self.start}:{self.end}"


class Node:
    """
    Represents a node in a Suffix Tree.

    Attributes:
        id (int): Identifier for the node.
        link_to (Node): Suffix link to another node.
        edges (dict): Dictionary of edges emanating from the node.
        sorted_edges (list): Cached list of edges sorted based on some criteria, used for traversal.
        suffixID (int): Identifier for a suffix starting at this node.

    Methods:
        __repr__: Returns a string representation of the node.
    """

    def __init__(self, link_to=None, ID=None, suffixID=None):
        self.id = ID
        self.link_to = link_to
        self.edges = {}
        self.sorted_edges = None
        self.suffixID = suffixID

    def __repr__(self):
        return f"Node {self.id}"


class SuffixTree:
    """
    Suffix tree implementation
    """

    def get_node_id(self):
        self.node_id += 1
        return self.node_id

    def __init__(self, stringFileName, positionsFileName, encoderMode=False):
        self.text = read_file(stringFileName)
        self.encoderMode = encoderMode

        # Encoder mode specifics
        if self.encoderMode:
            self.positions = {
                (int(position)): None for position in range(len(self.text))
            }
            self.frequencies = defaultdict(lambda: 0)
            self.bwt = []
        else:
            self.positions = {
                (int(position) - 1): None
                for position in read_positions(positionsFileName)
            }

        self.node_id = -1
        self.root = Node(ID=self.get_node_id())
        self.root.link_to = self.root

        # for representing the active point
        self.aNode = self.root
        self.aEdge = ""
        self.aLength = 0

        self.remainder = 0
        self.end = -1

        ## for use in the traversal and early termination
        self.currentRank = 0
        self.remainingIndices = len(self.positions)

        self.last_internal_node = None

    def _edge_insert(self, j):
        """
        Insert internal node at active point. x = aLength,

        PREVIOUS:    (A)---x---(B)  aNode = A, aEdge = AB, aLength = AB[0...x]

                          (D)
        NEW:               |
                    (A)---(C)---(B) aNode = A, aEdge = AC, aLength = AC[0...x]
        """

        AB = self.aNode.edges[self.aEdge]

        splitStart = AB.start + self.aLength - 1
        splitEnd = AB.start + self.aLength

        B = AB.tail

        C = Node(link_to=self.root, ID=self.get_node_id())
        D = Node(
            link_to=self.root, ID=self.get_node_id(), suffixID=j - self.remainder + 1
        )

        CB = Edge(start=splitEnd, end=AB.end, head=C, tail=B, value=self.text[splitEnd])
        CD = Edge(start=j, end=-1, head=C, tail=D, value=self.text[j])

        C.edges[CB.value] = CB
        C.edges[CD.value] = CD

        AB.tail = C
        AB.end = splitStart

        self._suffix_link(C)
        self.last_internal_node = C

    def _node_insert(self, j):
        """
        Insert new leaf node at the active node. We never node insert from a leaf node.

        PREVIOUS:   (A)  aNode = A, aEdge = None, aLength = 0

        NEW:
                    (A)---(B) aNode = B, aEdge = None, aLength = 0
        """
        A = self.aNode
        B = Node(
            link_to=self.root, ID=self.get_node_id(), suffixID=(j - self.remainder + 1)
        )
        AB = Edge(head=A, tail=B, start=j, end=-1, value=self.text[j])

        A.edges[AB.value] = AB
        self._suffix_link(A)
        self.last_internal_node = A

    def _check_or_insert(self, j):
        """
        Check if character string[j] exists at active point. If it does not, insert it
        """
        currentCharacter = self.text[j]
        if self.aLength == 0:
            ## If the character exists as an outgoing edge, it is implicitly represented, so return
            if currentCharacter in self.aNode.edges.keys():
                ## Update active edge and length to traverse to end of match
                self.aEdge = currentCharacter
                self.aLength = 1
                return False

            else:  ## If it doesn't exist, add the character as a new edge
                self._node_insert(j)
                return True

        else:  ## Else we are on an edge. Perform skip counting
            currentEdge = self.aNode.edges[self.aEdge]
            edgeLength = currentEdge.length(self.end)

            ## If edgeLength <= aLength recurse deeper
            if self.aLength >= edgeLength:
                self.aNode = currentEdge.tail

                ## Calculate next character after fully matching current edge
                nextPosition = j - self.aLength + edgeLength
                self.aEdge = (
                    self.text[nextPosition] if nextPosition < len(self.text) else None
                )

                self.aLength -= edgeLength
                return self._check_or_insert(j=j)

            ## Else check/insert on current edge
            else:
                compareChar = currentEdge.start + self.aLength
                if self.text[compareChar] == currentCharacter:
                    self.aLength += 1
                    return False
                else:
                    self._edge_insert(j=j)
                    return True

    def _suffix_link(self, to_node):
        """
        Resolves unresolved internal node if one exists, via a suffix link
        """
        if self.last_internal_node is not None:
            self.last_internal_node.link_to = to_node
            self.last_internal_node = None

    def _perform_phase(self, j):
        """
        Performs a single phase of the suffix tree given. Extends the suffix tree from s[0...j-1] to s[0...j]
        """
        self.last_internal_node = None
        self.remainder += 1
        self.end += 1  # rapid leaf expansion

        i = 1

        ## Performs extensions of a phase, while remainder exists
        while self.remainder > 0:
            ## Insert/check for remaining suffix at active point
            inserted = self._check_or_insert(j=j)

            if not inserted:
                ## No insertion occured : skip to next phase
                ## If unresolved internal node exists : link to last node traversed when checking for remainder
                self._suffix_link(to_node=self.aNode)
                break

            else:  ## An insertion occured
                self.remainder -= 1

                ## Not at the root node : follow suffix link from active node
                if self.aNode != self.root:
                    ## Traverse suffix link (back to root if no suffix link)
                    self.aNode = self.aNode.link_to

                ## At root node : stay at root node and decrement active length and increment active edge
                else:
                    ## Shift aEdge right to point to start of next remainder to insert
                    self.aLength = max(0, self.aLength - 1)
                    if self.aLength > 0:
                        self.aEdge = self.text[j - self.remainder + 1]

    def build_suffix_tree(self):
        """
        Performs all phases in Ukkonens
        """
        for j in range(len(self.text)):
            self._perform_phase(j)
            if self.encoderMode:
                self.frequencies[self.text[j]] += 1

    def _sort_edges(self, edges):
        """Return edges values based on their value, which presumes lexicographic order. Constant time
        as number of edges outgoing from a node is bounded by ASCII range"""
        return sorted(edges.values(), key=lambda e: e.value)

    def _dfs(self, node):
        """
        Performs a depth-first search (DFS) on the suffix tree starting from the given node.
        This method is used to traverse the tree lexicographically and to perform specific actions based on the node type and encoder mode.

        The DFS terminates early if all required positions are processed, and it handles different tasks:
        - In non-encoder mode, it simply assigns ranks to nodes based on their lexicographic order.
        - In encoder mode, it also constructs the Burrows-Wheeler Transform (BWT) by appending the character found at the position (suffixID - 1) % len(text).

        Parameters:
            node (Node): The current node from which the DFS starts or continues.

        Returns:
            bool: True if the DFS has processed all required indices and can terminate early; otherwise, False.

        Notes:
            - The method modifies `self.positions` to store ranks of required suffix positions.
            - The method updates `self.bwt` if in encoder mode.
            - The method adjusts `self.remainingIndices` to track the number of remaining indices that need processing.
        """
        if self.remainingIndices == 0:
            return True

        ## Base Case: If this is a leaf node
        if not node.edges:
            self.currentRank += 1

            # If this node is a wanted suffix
            if node.suffixID in self.positions:

                self.positions[node.suffixID] = self.currentRank

                ## If in encoderMode, construct the BWT concurrently
                if self.encoderMode:
                    self.bwt.append(self.text[(node.suffixID - 1) % len(self.text)])
                self.remainingIndices -= 1
            return
        ## No chance of node having been visited already
        ## If this node has not yet had its edges sorted, then sort and visit edges
        if not node.sorted_edges:
            node.sorted_edges = self._sort_edges(node.edges)

        ## Recursive Case: visit outgoing edges lexicographically
        for childEdge in node.sorted_edges:
            if self._dfs(node=childEdge.tail):
                return True

        return False

    def get_sorted_suffixes(self):
        """
        Calculates ranks of each position in the input
        """
        self._dfs(node=self.root)
        with open("output_q1.txt", "a") as file:
            for index, rank in self.positions.items():
                file.write(f"{rank}\n")

    def get_bwt(self):
        self._dfs(node=self.root)
        return self.bwt

    def get_frequency_count(self):
        return self.frequencies

    def run(self):
        self.build_suffix_tree()
        return self.get_sorted_suffixes()


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def read_positions(positionsFileName):
    with open(positionsFileName, "r") as file:
        positions = file.read().strip().split("\n")
    return positions


if __name__ == "__main__":
    output_file_name = "output_q1.txt"
    open(output_file_name, "wb").close()
    _, stringFileName, positionsFileName = sys.argv
    sTree = SuffixTree(stringFileName, positionsFileName, encoderMode=False)
    sTree.run()
