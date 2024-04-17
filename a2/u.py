class Edge:
    def __init__(self, start, string, end=-1):
        self.start = start
        self.end = end
        self.start_value = string[start]

    def value(self, string, global_end):
        """Return the substring this edge represents."""
        if self.end == -1:
            return string[self.start : global_end + 1]
        else:
            return string[self.start : self.end + 1]

    def length(self, global_end):
        """Return the length of the edge."""
        return (global_end if self.end == -1 else self.end) - self.start + 1

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
    def __init__(self, incoming_edge=None, link_to=None, ID=None):
        self.id = ID
        self.incoming_edge = incoming_edge
        self.link_to = link_to
        self.children = {}  ## HashMap<Edge: Node>

    def __repr__(self):
        return f"Node {self.id}"


class RootNode(Node):
    def __init__(self, incoming_edge=None, link_to=None, ID=None):
        self.id = ID
        self.incoming_edge = incoming_edge
        self.link_to = link_to
        self.children = {}  ## HashMap<Edge: Node>

        ## HashMap mapping characters to their Edges
        self.char_to_edge = {}  ## HashMap<Char: Edge>


class SuffixTree:
    def get_node_id(self):
        self.node_id += 1
        return self.node_id

    def __init__(self, string):
        self.node_id = -1
        self.root = RootNode(ID=self.get_node_id())
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
        Insert a new node at the active point which lies along an edge.
        Position is the character attempting to insert -> j

        PREVIOUS:    (A)---x---(B)  aNode = A, aEdge = AB, aLength = AB[0...x]

                          (D)
        NEW:               |
                    (A)---(C)---(B) aNode = A, aEdge = AC, aLength = AC[0...x]
        """
        print("Edge Insert")
        x = self.aLength
        A = self.aNode
        AB = self.aEdge  ## This becomes the edge AC when new end is defined

        B = A.children.pop(AB.start_value)  # Remove and get the original node B

        # Update the active edge to end at x-1 (split the edge)
        AB.end = AB.start + (x - 1)  # TODO: ADD -1 BACK IN
        # Create new internal node C
        C = Node(incoming_edge=AB, link_to=self.root, ID=self.get_node_id())

        # Create new edge CB from the split point to existing node B
        CB = Edge(start=(AB.start + x), end=-1, string=self.text)

        # Create new edge CD from C to new leaf node D
        CD = Edge(start=j, end=-1, string=self.text)
        D = Node(incoming_edge=CD, link_to=self.root, ID=self.get_node_id())

        # Assign new edges to internal node C
        C.children[CB.start_value] = B
        C.children[CD.start_value] = D

        # Update B's incoming edge to the new edge CB
        B.incoming_edge = CB

        # Reattach C under A using the start character of the original AB
        A.children[AB.start_value] = C

        # Set new_internal_node to C for potential suffix link updates
        self.new_internal_node = C

    def _node_insert(self, j):
        """
        Insert a new leaf node at the active node


        PREVIOUS:   (A)---(B)  aNode = B, aEdge = None, aLength = 0    B is leaf node, AB.end = -1

                          (C)
        NEW:               |
                    (A)---(B) aNode = A, aEdge = None, aLength = 0     B is internal node, AB.end = position

        """
        print("Node Insert")
        ## Set internal node which we are inserting from to new_internal_node
        self.new_internal_node = self.aNode
        B = self.aNode
        BC = Edge(start=j, end=-1, string=self.text)
        C = Node(incoming_edge=BC, link_to=self.root, ID=self.get_node_id())
        self.aNode.children[BC.start_value] = C

        ## If this node in the root node, add the edge_value : edge into the char_to_edge hashmap for O(1)
        ## lookup when "incrementing" active edge after an intertion at the root node : [start_character] = new_edge
        if B == self.root:
            self.root.char_to_edge[self.text[BC.start]] = BC
        else:  ## If B was a leaf node, freeze the range of its incoming edge
            if B.incoming_edge.end == -1:
                print(f"LEAF {self.end}")
                B.incoming_edge.end = self.end

    def _check_or_insert(self, j):
        """

        Check if character string[j] exists at active point

        """
        ## If we are on a node
        if self.aLength == 0:

            ## If the character exists as a child node, it is implicitly represented, so return
            char = self.text[j]
            if char in self.aNode.children.keys():

                ## Update active edge and length to traverse to end of match
                self.aEdge = self.aNode.children[self.text[j]].incoming_edge
                self.aLength = 1
                return False

            ## If it doesn't exist, add the character as a new edge and node
            else:
                self._node_insert(j)
                return True

        ## Else we are on an edge
        else:
            edge_length = self.aEdge.length(self.end)

            ## If length of the edge <= the remaining length we must traverse (aLength), then recurse deeper into tree
            if self.aLength >= edge_length:
                self.aNode = self.aNode.children[
                    self.aEdge.start_value
                ]  ## Traverse down aEdge to connecting aNode

                ## Calculate next character position after fully matching current edge
                next_char_position = self.aEdge.start + edge_length
                next_char = (
                    self.text[next_char_position]
                    if next_char_position < len(self.text)
                    else None
                )  # May be none if the correct check/insertion is at a node
                self.aEdge = (
                    self.aNode.children[next_char].incoming_edge
                    if next_char and next_char in self.aNode.children
                    else None
                )

                self.aLength -= edge_length  ## Decrement aLength to be remaining length after traversing aEdge
                return self._check_or_insert(j=j)

            ## Else we don't need to recurse deeper, so check/insert on the current edge
            else:
                # Determine character to compare at the edge
                edge_char_index = self.aEdge.start + self.aLength
                if self.text[edge_char_index] == self.text[j]:
                    self.aLength += 1
                    return False
                else:
                    self._edge_insert(j)
                    return True

    def _suffix_link(self, from_node, to_node):
        from_node.link_to = to_node

    def _perform_phase(self, j):
        """
        Performs a single phase of the suffix tree given. Extends the suffix tree from s[0...j-1] to s[0...j]
        """
        print(f"\n\n\n\n--- Phase {j+1} for character '{self.text[j]}' ---")
        self.remainder += 1  # Increment `remainder` for each new character
        self.end += 1  # Increment end denoter to execute rapid lead expansion
        unresolved = None  # Holds the last internal node inserted

        ## Deal with remaining suffixes
        while self.remainder > 0:
            print(
                f"\nAttempting to insert j: {j} at active point {self.aNode}, {self.aEdge}, {self.aLength} with remainder {self.remainder}"
            )
            ## Attempt to insert the remaining suffix at the active point
            inserted = self._check_or_insert(j=j)

            ## No insertion occured : skip to next phase
            if not inserted:
                ## Unresolved internal node exists : link it to last node traversed to when checking for remainder
                if unresolved is not None:
                    self._suffix_link(from_node=unresolved, to_node=self.aNode)
                    print(f"Suffix link set from {unresolved} to {self.aNode}")
                break

            ## An insertion occured
            else:
                self.remainder -= 1

                ## Not at the root node : follow suffix link from active node
                if self.aNode != self.root:
                    print(f"\n Following suffix link to Node {self.aNode.link_to}")
                    self.aNode = (
                        self.aNode.link_to
                    )  # Links to another internal node, or root node if no alternative suffix link was set

                ## At root node : stay at root node and decrement active length and increment active edge
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
                    print(
                        f"Suffix link set from {unresolved} to {self.new_internal_node}"
                    )

                unresolved = self.new_internal_node
                self.new_internal_node = None

                self.print_tree()

    def build_suffix_tree(self):
        for j in range(len(self.text)):
            # if j > 3:
            #     break
            self._perform_phase(j)
            print(f"\nTree structure after phase:{j+1}")
            self.print_tree()
            print(
                f"\nActive Node: {self.aNode} Active Edge: {self.aEdge} Active Length: {self.aLength}"
            )

    def print_tree(self, node=None, indent="", last=True):
        """Recursive function to print the tree"""
        if node is None:
            node = self.root
            print("Root")

        # Get a list of children sorted by edge start value for consistent output
        sorted_children = sorted(node.children.items(), key=lambda x: x)

        for i, (edge, child) in enumerate(sorted_children):
            if last and i == len(sorted_children) - 1:
                tree_icon = "└─"
                new_indent = indent + "  "
            else:
                tree_icon = "└─"  # "├─"
                new_indent = indent + "| "

            e = child.incoming_edge
            edge_label = f" {e.value(self.text, self.end)} ({e.start}:{e.end}) "

            # Check if the node has an incoming edge and display it appropriately
            node_label = f"Node({child.id})"  # {child.incoming_edge.start}:{child.incoming_edge.end})"  # f"Node({child.incoming_edge.value(self.text, self.end)})"
            print(f"{indent}{tree_icon}{edge_label} ---> {node_label}")
            self.print_tree(child, new_indent, last and i == len(sorted_children) - 1)


# s = "abcabxabcd$"
s = "abcabxabcd$"
stree = SuffixTree(s)
stree.build_suffix_tree()
