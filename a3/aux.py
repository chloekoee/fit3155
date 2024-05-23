def print_tree(node, indent="", is_last=True):
    # Create the current level line
    line = indent
    if is_last:
        line += "└── "
        new_indent = indent + "    "
    else:
        line += "├── "
        new_indent = indent + "│   "

    # Print the node keys
    print(line + " ".join(map(str, node.keys)))

    # Calculate the width for child alignment
    if node.child:
        for i, child in enumerate(node.child):
            print_tree(child, new_indent, i == len(node.child) - 1)
