from new_nodes import Node, Edge
import pprint


class SuffixTree:
    def get_node_id(self):
        self.node_id += 1
        return self.node_id

    def __init__(self, string, indices):
        self.node_id = -1
        self.root = Node(ID=self.get_node_id())
        self.root.link_to = self.root

        self.aNode = self.root
        self.aEdge = ""
        self.aLength = 0

        self.remainder = 0
        self.text = string
        self.end = -1

        ## Create hashmap of the indices that need to have their rank returnd
        self.ranks = {(item - 1): None for item in indices}
        self.currentRank = 0
        self.remainingIndices = len(self.ranks)

        self.last_internal_node = None  ## Holds the last created/modified internal node

    def _edge_insert(self, j):
        """
        Insert internal node at active point. x = aLength,

        PREVIOUS:    (A)---x---(B)  aNode = A, aEdge = AB, aLength = AB[0...x]

                          (D)
        NEW:               |
                    (A)---(C)---(B) aNode = A, aEdge = AC, aLength = AC[0...x]
        """
        # print("Edge Insert")
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

        self._suffix_link(C)  ## Resolve unresolved internal node if exists
        self.last_internal_node = C  # Mark C as the latest unresolved node

    def _node_insert(self, j):
        """
        Insert new leaf node at the active node. We never node insert from a leaf node.

        PREVIOUS:   (A)  aNode = A, aEdge = None, aLength = 0

        NEW:
                    (A)---(B) aNode = B, aEdge = None, aLength = 0
        """
        # print("Node Insert")
        ## Set internal node which we are inserting from to last_internal_node
        A = self.aNode
        B = Node(
            link_to=self.root, ID=self.get_node_id(), suffixID=(j - self.remainder + 1)
        )
        AB = Edge(head=A, tail=B, start=j, end=-1, value=self.text[j])

        A.edges[AB.value] = AB
        self.last_internal_node = A  ## Set node inserted from to last internal node

    def _check_or_insert(self, j):
        """
        Check if character string[j] exists at active point
        """
        currentCharacter = self.text[j]
        if self.aLength == 0:  ## If we are on a node

            ## If the character exists as an outgoing edge, it is implicitly represented, so return
            if currentCharacter in self.aNode.edges.keys():

                ## Update active edge and length to traverse to end of match
                self.aEdge = currentCharacter
                self.aLength = 1
                return False

            else:  ## If it doesn't exist, add the character as a new edge
                self._node_insert(j)
                return True

        else:  ## Else we are on an edge
            currentEdge = self.aNode.edges[self.aEdge]
            edgeLength = currentEdge.length(self.end)
            # print(f"On edge {currentEdge}")
            if self.aLength >= edgeLength:  ## If edgeLength <= aLength recurse deeper
                # print(self.aNode)
                self.aNode = currentEdge.tail
                # print(self.aNode)

                ## Calculate next character after fully matching current edge
                nextPosition = (
                    j - self.remainder + edgeLength + 1
                )  # currentEdge.start + edgeLength
                # print(
                #     f" nextPosition = j {j} - remainder {self.remainder} + edgeLength {edgeLength}"
                # )
                self.aEdge = (
                    self.text[nextPosition] if nextPosition < len(self.text) else None
                )
                # print(f"aEdge {self.aEdge}")
                self.aLength -= edgeLength
                # print(f"aLength {self.aLength}")
                return self._check_or_insert(j=j)

            else:  ## Else check/insert on current edge
                compareChar = currentEdge.start + self.aLength
                if self.text[compareChar] == currentCharacter:
                    self.aLength += 1
                    return False
                else:
                    self._edge_insert(j=j)
                    return True

    def _suffix_link(self, to_node):
        if self.last_internal_node is not None:
            self.last_internal_node.link_to = to_node
            print(f"Suffix link set from {self.last_internal_node} to {to_node}")
            self.last_internal_node = None

    def _perform_phase(self, j):
        """
        Performs a single phase of the suffix tree given. Extends the suffix tree from s[0...j-1] to s[0...j]
        """
        self.last_internal_node = None
        self.remainder += 1
        self.end += 1
        # print("\nRAPID LEAF EXPANSION TREE")
        # self.print_tree()
        i = 1
        while self.remainder > 0:
            # print(
            #     f"\n ITERATION {i} Inserting {self.text[j-self.remainder+1:j+1]}\naNode: {self.aNode} aEdge: {self.aEdge} aLength: {self.aLength} Remainder: {self.remainder}"
            # )
            i += 1

            ## Insert/check for remaining suffix at active point
            inserted = self._check_or_insert(j=j)

            if not inserted:  ## No insertion occured : skip to next phase
                ## If unresolved internal node exists : link to last node traversed when checking for remainder
                self._suffix_link(to_node=self.aNode)
                # self.print_tree()
                break

            else:  ## An insertion occured
                self.remainder -= 1

                ## Not at the root node : follow suffix link from active node
                if self.aNode != self.root:
                    # print(
                    #     f"\n Following suffix link from {self.aNode} to {self.aNode.link_to}"
                    # )

                    ## Traverse suffix link (back to root if no suffix link)
                    self.aNode = self.aNode.link_to
                    # print(self.aNode)
                ## At root node : stay at root node and decrement active length and increment active edge
                else:
                    self.aLength = max(0, self.aLength - 1)

                    ## Shift aEdge right to point to start of next remainder to insert
                    if self.aLength > 0:  ## only have to if aLength> 0
                        self.aEdge = self.text[j - self.remainder + 1]

                # self.print_tree()

    def build_suffix_tree(self):
        for j in range(len(self.text)):
            # print(f"\n\n\n\n--- Phase {j+1} for character '{self.text[j]}' ---")
            self._perform_phase(j)
            # print(
            #     f"\naNode: {self.aNode} aEdge: {self.aEdge} aLength: {self.aLength} Remainder: {self.remainder}"
            # )
            # print(f"FINAL TREE FOR PHASE {j+1}")
            self.print_tree()

    def _sort_edges(self, edges):
        # Return edges values based on their value, which presumes lexicographic order.
        return sorted(edges.values(), key=lambda e: e.value)

    def _dfs(self, node):  ## Returns True if all no remaining indices left
        if self.remainingIndices == 0:
            print(f" Terminating early at {self.currentRank}th smallest suffix")
            return True

        if not node.edges:  ## Base Case: If this is a leaf node
            self.currentRank += 1  ## Increment current rank each time encounter leaf
            # If this node is a wanted suffix
            if node.suffixID in self.ranks:
                self.ranks[node.suffixID] = self.currentRank
                self.remainingIndices -= 1  ## Accounting for 1 - indexing
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
        ## Starting from root
        self._dfs(node=self.root)
        print(self.ranks)
        pprint.pprint(list(self.ranks.values()))

    def print_tree(self, node=None, indent="", last=True):
        """Recursive function to print the tree"""
        if node is None:
            node = self.root
            print("Root")

        # Get a list of edges sorted by the edge's start for consistent output
        sorted_edges = sorted(node.edges.values(), key=lambda e: e.value)

        for i, edge in enumerate(sorted_edges):
            if last and i == len(sorted_edges) - 1:
                tree_icon = "└─"
                new_indent = indent + "  "
            else:
                tree_icon = "├─"
                new_indent = indent + "| "

            # Using the edge's own value method to get the representation of the substring
            edge_label = (
                f"{edge.full_value(self.text, self.end)}<{edge.start}:{edge.end}>"
            )

            # Displaying the edge and the node it points to
            node_label = f"({edge.tail.suffixID if edge.tail else 'None'})"  # Assuming the tail is the node the edge points to
            print(f"{indent}{tree_icon}{edge_label} ──> {node_label}")

            # Recursive call to print the subtree rooted at the tail node of the edge
            if edge.tail:  # Ensuring that there is a tail node to recurse into
                self.print_tree(
                    edge.tail, new_indent, last and i == len(sorted_edges) - 1
                )


# s = "xabcxacxabd$"
s = "mississippi$"
stree = SuffixTree(s, [3])  # , 6, 7])
stree.build_suffix_tree()
stree.get_sorted_suffixes()
