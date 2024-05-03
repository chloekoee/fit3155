import typing
import heapq
from collections import defaultdict
from bitarray import bitarray
import typing
from bitarray import bitarray


## Finish type hints
class HuffmanNode:
    def __init__(self, value: str = None, frequency: int = 0, right=None, left=None):
        self.value = value
        self.frequency = frequency
        self.right = right
        self.left = left

    def __lt__(self, other):
        """Compare nodes based on frequency for heapq."""
        return self.frequency < other.frequency

    def __str__(self) -> str:
        # return f" Value: {self.value} Frequency: {self.frequency}"
        return f" Value: {self.value} \nFrequency: {self.frequency}\nRight: {self.right}\nLeft: {self.left}"


def retrieve_codes(current, codes, path: str):
    """Conducts DFS on a HuffmanNode returning the stack (binary encoding) and leaf value
    As no cycles exist in a tree, no need for a visited data structure"""
    ## base case have hit a leaf
    if (
        not current.right
    ):  ## can just check for right child, as all nodes will either have no children or both left and right
        codes[current.value] = path
        return codes

    ## traverse the children
    codes = retrieve_codes(current=current.left, codes=codes, path=path + "0")
    codes = retrieve_codes(current=current.right, codes=codes, path=path + "1")
    return codes


def get_huffman_encodings(str: str, character_frequencies):
    if len(str) == 0:
        return
    # Create a hashmap in order to find all unique ASCII characters in str, ensure each
    # new character has a new Huffman node
    # chars = defaultdict(
    #     lambda: HuffmanNode(value=None)
    # )  ## Maps characters to huffman nodes

    # for c in str:
    #     if chars[c].value is None:
    #         chars[c].value = c
    #     chars[c].frequency += 1  ## Increment the frequency of the given entry

    chars = {}
    for char, freq in character_frequencies.items():
        chars[char] = HuffmanNode(value=char, frequency=freq)

    min_freq = list(chars.values())
    heapq.heapify(min_freq)

    ## Coalesce elements until only one remains - the root node
    while len(min_freq) > 1:  ## potentially inefficient o(n)
        ## pop off two least frequent elements
        least = heapq.heappop(min_freq)
        second = heapq.heappop(min_freq)

        name = least.value + second.value
        freq = least.frequency + second.frequency
        combined = HuffmanNode(value=name, frequency=freq, left=least, right=second)

        heapq.heappush(min_freq, combined)

    root = min_freq.pop()

    ## potentially can make a predecessor array to backtrack
    codes = defaultdict(lambda: "")
    ## perfrom dfs from the root node to return all character encodings
    return dict(retrieve_codes(current=root, codes=codes, path=""))


def elias(n: int):
    """
    elias returns elias encoding for a given decimal integer
    """

    ## recursive function
    def add_code(l: bitarray) -> bitarray:
        ## If the length component is equal to 1, return
        if len(l) == 1:
            return l

        ## Recursive case, calculate the next smallest length component to be prepended
        l_length: int = len(l) - 1

        ## Convert it to binary and flip the leading bit
        next_l: bitarray = bitarray(bin(l_length)[2:])
        next_l[0] = 0
        return add_code(next_l) + l

    ## Convert n to binary (removing '0f' prefix)
    n_binary: bitarray = bitarray(bin(n)[2:])
    return add_code(n_binary).to01()  ## Converts it to string form
