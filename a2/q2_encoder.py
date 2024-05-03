from bitarray import bitarray
from q1 import SuffixTree
import sys
from collections import defaultdict
import heapq

"""
CHLOE KOE 
33109109
A2 FIT3155
Encoder Relevant Design Choices Made:

1. Reuse of Ukkonen's Algorithm:
   - The Encoder class leverages Ukkonen's algorithm not only to construct the suffix array but also to :
     - Calculate BWT directly from the suffix array which is constructed during the traversal of the suffix tree post its construction
     - Determine character frequencies and the number of unique characters, which is integrated into each phase of Ukkonen's algorithm

2. Memory Efficiency/Output:
   - A primary design goal of the encoder was to optimize memory usage. This is achieved through the following mechanisms:
     - 'add_to_output' Function: Manages output by writing data one byte at a time directly to the output file. 
     This approach ensures that the encoded string is never fully stored in memory
     - Bit Management: The encoder tracks the total number of bits processed modulo 8. This check allows for efficient padding 
     of the encoding to ensure the final output aligns to byte boundaries
"""


class HuffmanNode:
    """
    Represents a node in a Huffman Tree, used for Huffman encoding.

    Attributes:
        value (str): The character or combined characters this node represents.
        frequency (int): The frequency of occurrence for the node's value in the text.
        right (HuffmanNode): Right child in the Huffman Tree.
        left (HuffmanNode): Left child in the Huffman Tree.

    Methods:
        __lt__: Implements less than comparison based on frequency for priority queue operations.
        __str__: Provides a string representation of the node.
    """

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
    """
    Performs a depth-first search on the Huffman Tree to generate binary codes.

    Args:
        current (HuffmanNode): The current node in the DFS.
        codes (dict): Dictionary to store character codes.
        path (str): Current path (prefix) in binary code form.

    Returns:
        dict: Updated dictionary of character codes.
    """
    # Base case: we hit a leaf node
    if current.right is None and current.left is None:
        codes[current.value] = path
        return codes

    # Recursive DFS
    if current.left:
        codes = retrieve_codes(current=current.left, codes=codes, path=path + "0")
    if current.right:
        codes = retrieve_codes(current=current.right, codes=codes, path=path + "1")

    return codes


def get_huffman_encodings(str: str, character_frequencies):
    """
    Generates Huffman encodings for characters based on their frequencies.

    Args:
        string (str): The text from which to generate Huffman encodings.
        character_frequencies (dict): A dictionary mapping characters to their frequencies in the text.

    Returns:
        dict: A dictionary of characters mapped to their Huffman codes.

    Optimization:
        Utilizes a min-heap to efficiently build the Huffman tree by always merging the least frequent nodes first.
        Handles the special case of single-character strings by assigning a default code '0'.
    """
    if len(str) == 0:
        return

    chars = {}
    for char, freq in character_frequencies.items():
        chars[char] = HuffmanNode(value=char, frequency=freq)

    min_freq = list(chars.values())
    heapq.heapify(min_freq)

    # If there's only one type of character, assign it the code '0' (or '1')
    if len(min_freq) == 1:
        single_char = min_freq[0]
        return {single_char.value: "0"}
    ## coalesce elements until only one remains - the root node
    while len(min_freq) > 1:
        ## pop off two least frequent elements
        least = heapq.heappop(min_freq)
        second = heapq.heappop(min_freq)

        name = least.value + second.value
        freq = least.frequency + second.frequency
        combined = HuffmanNode(value=name, frequency=freq, left=least, right=second)

        heapq.heappush(min_freq, combined)

    root = min_freq.pop()

    codes = defaultdict(lambda: "")
    ## perfrom dfs from the root node to return all character encodings
    return dict(retrieve_codes(current=root, codes=codes, path=""))


def elias(n: int):
    """
    Generates an Elias omega encoding for a given integer.

    Args:
        n (int): The integer to encode.

    Returns:
        str: The Elias omega encoded string for the input integer.

    Optimization:
        Uses a recursive approach to prepend the binary lengths, reducing the computational overhead of iterative length calculation and bit manipulation.
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


class Encoder:
    """
    Encodes text from an input file using the Burrows-Wheeler Transform (BWT)
    combined with Huffman coding, and writes the encoded data to a binary output file.
    """

    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.bit_buffer = bitarray()
        self.bit_modulo = 0

        self.sTree = SuffixTree(
            stringFileName=input_file_path, positionsFileName=None, encoderMode=True
        )
        self.sTree.build_suffix_tree()
        self.bwt_string = self.sTree.get_bwt()
        self.frequencies = self.sTree.get_frequency_count()

    def read_input_file(self):
        """Reads the entire content of the input file as a single string."""
        with open(self.input_file_path, "r", encoding="utf-8") as file:
            return file.read()

    def add_to_output(self, data):
        """
        Adds data to the output buffer and writes to the output file when there's enough to form a byte.

        This method manages the buffer by adding data and checking if it contains enough bits to form one or more full bytes.
        If there are sufficient bits, they are written to the output file in binary mode and then removed from the buffer.

        Args:
            data (str or bitarray): The data to be added to the output buffer. If the data is a string, it's converted into a bitarray.
        """
        if isinstance(data, str):
            self.bit_buffer.extend(bitarray(data))
        else:
            self.bit_buffer.extend(data)
        self.bit_modulo = (self.bit_modulo + len(data)) % 8

        # write to file if have one full byte
        if len(self.bit_buffer) >= 8:
            # open file in append binary mode
            with open("q2_encoder_output.bin", "ab") as file:
                full_bytes = self.bit_buffer[: len(self.bit_buffer) // 8 * 8]
                file.write(full_bytes.tobytes())
                # clear buffer
                self.bit_buffer = self.bit_buffer[len(self.bit_buffer) // 8 * 8 :]

    def pad(self):
        """
        Pads the output buffer to ensure the total number of bits is a multiple of 8, and then writes the padded bits to the output file.

        This method calculates the number of bits needed to pad the buffer to make its length a multiple of 8.
        After padding, it writes the final bytes to the output file and clears the buffer.
        """
        if self.bit_modulo > 0:
            padding_length = 8 - self.bit_modulo
            self.bit_buffer.extend("0" * padding_length)

        with open("q2_encoder_output.bin", "ab") as file:
            file.write(self.bit_buffer.tobytes())
            self.bit_buffer.clear()

    def encode_bwt(self):
        """
        Encodes the Burrows-Wheeler Transform (BWT) of the input string using Huffman encoding and writes the encoded data to the output.

        This method processes the BWT string and encodes it using Huffman codes for each character. It handles:
        - Encoding the length of the BWT string using Elias coding.
        - Encoding each character's Huffman code and its length.
        - Handling runs of characters by encoding run lengths and appending them to the output.

        It follows the process of:
        1. Adding the encoded length of the BWT string.
        2. Adding encoded data for the number of unique characters.
        3. Iterating through the BWT string to handle consecutive characters and their run lengths.
        """
        n = len(self.bwt_string)
        self.add_to_output(elias(n))  ## string length

        hCodes = get_huffman_encodings(self.bwt_string, self.frequencies)
        self.add_to_output(elias(len(hCodes)))  ## num unique characters

        for char, hCode in hCodes.items():
            self.add_to_output(bin(ord(char))[2:].zfill(7))
            self.add_to_output(elias(len(hCode)))
            self.add_to_output(hCode)

        current_char = self.bwt_string[0]
        count = 1

        for char in self.bwt_string[1:]:
            if char == current_char:
                count += 1
            else:
                binary_count = elias(count)
                self.add_to_output(hCodes[current_char] + binary_count)
                current_char = char
                count = 1

        binary_count = elias(count)
        self.add_to_output(hCodes[current_char] + binary_count)

    def run(self):
        self.encode_bwt()
        self.pad()


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


if __name__ == "__main__":
    # Clear the output file before starting the encoding process
    output_file_name = "q2_encoder_output.bin"
    open(output_file_name, "wb").close()
    _, input_file_name = sys.argv
    encoder = Encoder(input_file_path=input_file_name)
    encoder.run()
