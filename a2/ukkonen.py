class Edge:
    def __init__(self, start, string, end=-1):
        self.start = start
        self.end = end
        self.start_value = string[start]  # character at the start of the edge

    def value(self, string, global_end):
        """Return the substring this edge represents."""
        if self.end == -1:
            return string[self.start : global_end + 1]
        else:
            return string[self.start : self.end + 1]

    def length(self, global_end):
        """Return the length of the edge."""
        return (global_end if self.end == -1 else self.end) - self.start

    def __hash__(self):
        """Hash based on the start character of the edge."""
        return hash(self.start_value)

    def __eq__(self, other):
        """Equality based on the start character of the edge."""
        return (
            self.start_value == other.start_value if isinstance(other, Edge) else False
        )

    def __repr__(self):
        """String representation assuming a fixed global_end for simplification."""
        return f"Edge({self.start_value}: start={self.start}, end={self.end})"


class Node:
    def __init__(self, incoming_edge=None, link_to=None):
        self.incoming_edge = incoming_edge
        self.link_to = link_to
        self.children = {}  ## HashMap<Edge: Node>


class RootNode(Node):
    def __init__(self, incoming_edge=None, link_to=None):
        self.incoming_edge = incoming_edge
        self.link_to = link_to
        self.children = {}  ## HashMap<Edge: Node>

        ## HashMap mapping characters to their Edges
        self.char_to_edge = {}  ## HashMap<Char: Edge>


class SuffixTree:
    def __init__(self, string):
        self.root = RootNode()
        self.root.link_to = self.root

        ## Triple representing the active point
        self.aNode = self.root
        self.aEdge = None
        self.aLength = 0

        self.remainder = 0
        self.text = string
        self.end = -1

        ## Holds the last created internal node
        self.new_internal_node = None

    def _edge_insert(self, j):
        """
        Insert a new node at the active point which lies along an edge

        PREVIOUS:    (A)---x---(B)  aNode = A, aEdge = AB, aLength = AB[0...x]

                          (D)
        NEW:               |
                    (A)---(C)---(B) aNode = A, aEdge = AC, aLength = AC[0...x]
        """
        x = self.aLength
        A = self.aNode
        AB = self.aEdge  ## This becomes the edge AC when new end is defined

        B = A.children.pop(AB.start_value)  # Remove and get the original node B

        # Create new internal node C
        C = Node(link_to=self.root)

        # Update the active edge to end at x-1 (split the edge)
        AB.end = x - 1

        # Create new edge CB from the split point to existing node B
        CB = Edge(start=x, end=AB.end, string=self.text)

        # Create new edge CD from C to new leaf node D
        CD = Edge(start=x, end=-1, string=self.text)
        D = Node(incoming_edge=CD, link_to=self.root)

        # Assign new edges to internal node C
        C.children[self.text[CB.start]] = B
        C.children[self.text[CD.start]] = D

        # Update B's incoming edge to the new edge CB
        B.incoming_edge = CB

        # Reattach C under A using the start character of the original AB
        A.children[self.text[AB.start]] = C

        # Set new_internal_node to C for potential suffix link updates
        self.new_internal_node = C

    def _node_insert(self, position):
        """
        Insert a new node at the active node
        """
        new_edge = Edge(start=position, string=self.text)
        new_leaf_node = Node(incoming_edge=new_edge, link_to=self.root)
        self.aNode.children[new_edge] = new_leaf_node

        ## If this node in the root node, add the edge_value : edge into the char_to_edge hashmap for O(1)
        ## lookup when "incrementing" active edge after an intertion at the root node : [start_character] = new_edge
        if self.aNode == self.root:
            self.aNode.char_to_edge[self.text[new_edge.start]] = new_edge

    def _check_or_insert(self, position):
        """
        Check if character at position exists at current active point, and insert if not.
        Position calculates as s[j-k] for current phase j and k from remainder.
        """
        ## If we are on a node
        if self.aLength == 0:

            ## If the character exists as a child node, it is implicitly represented, so return
            if self.text[position] in self.aNode.children:

                ## Update active edge and length to traverse to end of match
                self.aEdge = self.aNode.children[self.text[position]]
                self.aLength = 1
                return False

            ## If it doesn't exist, add the character as a new edge and node
            else:
                self._node_insert(position)
                return True

        ## Else we are on an edge
        else:
            edge_length = self.aEdge.length(self.end)

            ## If length of the edge <= the remaining length we must traverse (aLength), then recurse deeper into tree
            if self.aLength >= edge_length:
                self.aNode = self.aNode.children[
                    self.aEdge
                ]  ## Traverse down aEdge to connecting aNode
                self.aEdge = None  ## Reset edge as now we are at new aNode
                self.aLength -= edge_length  ## Decrement aLength to be remaining length after traversing aEdge
                return self._check_or_insert(position)

            ## Else we don't need to recurse deeper, so check/insert on the current edge
            else:
                # Determine character to compare at the edge
                edge_char_index = self.aEdge.start + self.aLength
                if self.text[edge_char_index] == self.text[position]:
                    self.aLength += 1
                    return False
                else:
                    self._edge_insert(position)
                    return True

    def _suffix_link(self, from_node, to_node):
        from_node.link_to = to_node

    def _perform_phase(self, j):
        """
        Performs a single phase of the suffix tree given. Extends the suffix tree from s[0...j-1] to s[0...j]
        """
        self.remainder += 1  # Increment `remainder` for each new character
        self.end += 1  # Increment end denoter to execute rapid lead expansion
        unresolved = None  # Holds the last internal node inserted

        ## Deal with remaining suffixes
        while self.remainder > 0:

            ## Attempt to insert the remaining suffix at the active point
            inserted = self._check_or_insert(j - self.remainder + 1)

            ## No insertion occured : skip to next phase
            if not inserted:
                ## Unresolved internal node exists : link it to last node traversed to when checking for remainder
                if unresolved:
                    self._suffix_link(from_node=unresolved, to_node=self.aNode)
                break

            ## An insertion occured
            else:
                self.remainder -= 1

                ## Not at the root node : follow suffix link from active node
                if self.aNode != self.root:
                    self.aNode = (
                        self.aNode.link_to
                    )  # Links to another internal node, or root node if no alternative suffix link was set

                ## At room node : stay at root node and decrement active length and increment active edge
                else:
                    self.aLength = max(0, self.aLength - 1)

                    ## Shift aEdge right to point to start of next remainder to insert
                    if self.aLength > 0:
                        self.aEdge = self.root.char_to_edge[
                            self.text[j - self.remainder + 1]
                        ]

                ## Resolve suffix link for previously created internal node
                if unresolved is not None:
                    self._suffix_link(
                        from_node=unresolved,
                        to_node=self.new_internal_node,
                    )

                unresolved = self.new_internal_node
                self.new_internal_node = None

    def build_suffix_tree(self):
        for j in range(len(self.text)):
            self._perform_phase(j)


s = "abcabxabcd"
stree = SuffixTree(s)
stree.build_suffix_tree()
