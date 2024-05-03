class Edge:
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
    def __init__(self, link_to=None, ID=None, suffixID=None):
        self.id = ID
        self.link_to = link_to
        self.edges = {}
        self.sorted_edges = None
        self.suffixID = suffixID

    def __repr__(self):
        return f"Node {self.id}"
