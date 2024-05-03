from nodes import Node, Edge


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

        self.ranks = {(item - 1): None for item in indices}
        self.currentRank = 0
        self.remainingIndices = len(self.ranks)

        self.last_internal_node = None

    def _edge_insert(self, j):
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
        A = self.aNode
        B = Node(
            link_to=self.root, ID=self.get_node_id(), suffixID=(j - self.remainder + 1)
        )
        AB = Edge(head=A, tail=B, start=j, end=-1, value=self.text[j])

        A.edges[AB.value] = AB
        self._suffix_link(A)
        self.last_internal_node = A

    def _check_or_insert(self, j):
        currentCharacter = self.text[j]
        if self.aLength == 0:
            if currentCharacter in self.aNode.edges.keys():
                self.aEdge = currentCharacter
                self.aLength = 1
                return False

            else:
                self._node_insert(j)
                return True

        else:
            currentEdge = self.aNode.edges[self.aEdge]
            edgeLength = currentEdge.length(self.end)

            if self.aLength >= edgeLength:
                self.aNode = currentEdge.tail
                nextPosition = j - self.aLength + edgeLength
                self.aEdge = (
                    self.text[nextPosition] if nextPosition < len(self.text) else None
                )

                self.aLength -= edgeLength
                return self._check_or_insert(j=j)

            else:
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
            self.last_internal_node = None

    def _perform_phase(self, j):
        self.last_internal_node = None
        self.remainder += 1
        self.end += 1

        i = 1
        while self.remainder > 0:

            inserted = self._check_or_insert(j=j)

            if not inserted:
                self._suffix_link(to_node=self.aNode)
                break

            else:
                self.remainder -= 1

                if self.aNode != self.root:
                    self.aNode = self.aNode.link_to
                else:
                    self.aLength = max(0, self.aLength - 1)
                    if self.aLength > 0:
                        self.aEdge = self.text[j - self.remainder + 1]

    def build_suffix_tree(self):
        for j in range(len(self.text)):
            self._perform_phase(j)

    def _sort_edges(self, edges):
        return sorted(edges.values(), key=lambda e: e.value)

    def _dfs(self, node):
        if self.remainingIndices == 0:
            return True

        if not node.edges:
            self.currentRank += 1
            if node.suffixID in self.ranks:
                self.ranks[node.suffixID] = self.currentRank
                self.remainingIndices -= 1
            return

        if not node.sorted_edges:
            node.sorted_edges = self._sort_edges(node.edges)

        for childEdge in node.sorted_edges:
            if self._dfs(node=childEdge.tail):
                return True

        return False

    def get_sorted_suffixes(self):
        self._dfs(node=self.root)
        return list(self.ranks.values())


s = "wadzmiavvanypqppunuiiqcihmhylwxkzyqlxbaecwjrjpmrpmiqxwyzrrclnlttrwilurykvccxyagmhznziccwnyfqgzttxtmqkqfnqghskniqvfnxlnylbndnezsojtqqfypmavbhvmkwpeikyzuaawjuozqgccgxtffoofhpvsqjlphrztkzupknnpqfsudwjkfffhhzgnjcighnkygqhramcbczbbrmyaqywrnqgxjhsqvjthpqkzfxjzkbrvtnyjncxrwjuvbdlqxcjncmwhubfmpzbvpcctrpqqewadzmiavvanypqppunuiiqcihmhylwxkzyqlxbaecwjrjpmrpmiqxwyzrrclnlttrwilurykvccxyagmhznziccwnyfqgzttxtmqkqfnqghskniqvfnxlnylbndnezsojtqqfypmavbhvmkwpeikyzuaawjuozqgccgxtffoofhpvsqjlphrztkzupknnpqfsudwjkfffhhzgnjcighnkygqhramcbczbbrmyaqywrnqgxjhsqvjthpqkzfxjzkbrvtnyjncxrwjuvbdlqxcjncmwhubfmpzbvpcctrpqqewadzmiavvanypqppunuiiqcihmhylwxkzyqlxbaecwjrjpmrpmiqxwyzrrclnlttrwilurykvccxyagmhznziccwnyfqgzttxtmqkqfnqghskniqvfnxlnylbndnezsojtqqfypmavbhvmkwpeikyzuaawjuozqgccgxtffoofhpvsqjlphrztkzupknnpqfsudwjkfffhhzgnjcighnkygqhramcbczbbrmyaqywrnqgxjhsqvjthpqkzfxjzkbrvtnyjncxrwjuvbdlqxcjncmwhubfmpzbvpcctrpqqewadzmiavvanypqppunuiiqcihmhylwxkzyqlxbaecwjrjpmrpmiqxwyzrrclnlttrwilurykvccxyagmhznziccwnyfqgzttxtmqkqfnqghskniqvfnxlnylbndnezsojtqqfypmavbhvmkwpeikyzuaawjuozqgccgxtffoofhpvsqjlphrztkzupknnpqfsudwjkfffhhzgnjcighnkygqhramcbczbbrmyaqywrnqgxjhsqvjthpqkzfxjzkbrvtnyjncxrwjuvbdlqxcjncmwhubfmpzbvpcctrpqqe"

s = s + s + "$"
s = "##$"
s = "mississippi$"
## mishap with teh $$ signs
stree = SuffixTree(s, [i for i in range(1, len(s) + 1)])
stree.build_suffix_tree()
print(stree.get_sorted_suffixes())
