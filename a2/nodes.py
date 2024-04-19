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
        # return f"Edge({self.start_value}: start={self.start}, end={self.end})"
        return f"{self.start_value}"


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
