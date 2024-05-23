from bitarray import bitarray
from collections import defaultdict
import sys

"""
CHLOE KOE 
33109109
A2 FIT3155

Decoder Design Summary:

1. Cursor Management:
   - Efficiency in the decoder is primarily achieved through the use of a cursor, which tracks the current position within the encoded string.
   - Two key functions manage the cursor's position:
     - 'read_bits': Advances the cursor as bits are read.
     - 'peek_bits': Peeks at up to one bit without advancing the cursor, allowing for conditional reads without consuming the bit.

2. Memory Optimization:
   - To optimize memory usage, the BWT is inverted in forward order, contrary to the backward order shown in the lectures. 
   This approach allows for direct output to a file, reducing the memory overhead by avoiding the storage of the entire decoded string in memory.

3. Huffman Tree Reconstruction:
   - The Huffman tree is reconstructed in a hash map format, utilizing the prefix-free nature of Huffman codes. 
   As Huffman codes are read, the tree is traversed until a leaf node (decoded character) is reached, 
   at which point the character is returned and no further bits are read for that character.

Decoder Process Outline:
1. Decode the initial parameters from the encoded data:
   - Length of the original string (n).
   - Number of unique characters (x).

2. Construct the Huffman Encoding HashMap:
   - For each of the x characters, perform the following:
     - Read 7 bits to obtain the ASCII representation of the character.
     - Decode an Elias codeword to determine the length of the Huffman code for the character.
     - Read the Huffman code based on the length determined.

3. Decode the BWT string:
   - For each of the n characters in the BWT, decode and construct a frequency hash map for characters. 
   This is achieved without storing the entire BWT string by leveraging the Huffman Encoding Hash Map to store frequency data alongside the Huffman codes.

4. Invert the BWT:
   - Create a mapping vector where each index i in the BWT string maps to an index in the first column of the transformed array. 
   This mapping is done using a forward approach, not the conventional backward method, to allow direct output.
   - Construct a frequency hash map ('nOc') during the BWT inversion.
   - Reconstruct the original string by following the mapping vector and output the result directly to the file
"""


class Decoder:
    def __init__(self, file_path):
        self.encoded_input = self.read_file_to_bitarray(file_path)
        self.cursor = 0
        self.huffman_root = {}

    def read_file_to_bitarray(self, file_path):
        """Reads the binary file content into a bitarray."""
        bitarr = bitarray()
        with open(file_path, "rb") as file:
            bitarr.fromfile(file)
        return bitarr

    def add_huffman_code(self, char, code):
        """
        Adds a Huffman code to the Huffman tree for a specified character.

        This method constructs the tree by traversing the code bit by bit, creating new nodes as needed. The character
        is stored at the leaf node, which represents the end of the code path for that character.

        Args:
            char (str): The character to which the Huffman code corresponds.
            code (str): The Huffman code as a binary string, where each character ('0' or '1') represents a bit.
        """
        node = self.huffman_root
        for bit in code:
            if bit not in node:
                node[bit] = {}  # Create a new node if the path doesn't exist
            node = node[bit]
        node["char"] = char  # Mark the end of the code path with the character

    def get_char(self):
        """
        Decodes a single character from the Huffman tree based on the encoded input.

        This method traverses the Huffman tree from the root based on the bits read from the encoded input.
        It continues until it reaches a leaf node, which contains the character represented by the sequence of bits read.

        Returns:
            str: The decoded character.

        Note:
            If there is only one character in the Huffman tree (a single node tree), this function immediately returns
            that character without reading any bits, as all bits would decode to this single character.
        """
        node = self.huffman_root

        if len(node) == 1:  # Single character in the tree
            return next(iter(node.values()))["char"]
        for _ in range(len(self.encoded_input)):  # Safer than a while loop
            if len(node) == 1:  ## This is leaf note : {'char':'a'}
                return node["char"]
            else:
                bit = self.read_bits(1, isBitarray=False)
                node = node.get(bit, None)

    def read_bits(self, num_bits, isBitarray=True):
        """Reads num_bits from the encoded_input starting from the cursor."""
        bits = self.encoded_input[self.cursor : self.cursor + num_bits]
        self.cursor += num_bits
        return bits if isBitarray else bits.to01()

    def peek_bits(self, num_bits, isBitarray=True):
        """Reads next bits from the encoded_input without moving cursor"""
        bits = self.encoded_input[self.cursor : self.cursor + num_bits]
        if isBitarray:
            return bitarray(bits)
        else:
            return bits

    def decode_elias_omega(self):
        """
        Decodes an Elias omega encoded number using a recursive approach from the current bit position.

        This function interprets the bit stream as Elias omega encoded integers, where each integer
        represents the length of the next integer until a '1' bit indicates the termination of recursion.

        Returns:
            int: The decoded integer from the Elias omega encoded bit stream.
        """

        def recursive_decode(i, length):
            try:
                if self.peek_bits(1)[0] == 1:
                    return int(self.read_bits(length, isBitarray=False), 2)
            except:
                print(self.cursor)
            next_length_binary = self.read_bits(length)
            next_length_binary[0] = 1
            next_length = int("".join(map(str, next_length_binary)), 2)
            next_length += 1

            next_i = i + length
            return recursive_decode(i=next_i, length=next_length)

        return recursive_decode(i=0, length=1)

    def construct_huffman_tree(self, num_chars):
        """
        Constructs a Huffman tree from encoded input by reading character codes and their frequencies.

        Args:
            num_chars (int): Number of unique characters for which Huffman codes are to be read and constructed.

        This method reads the ASCII representation of each character, decodes its associated Huffman code length using
        Elias omega, and constructs the tree directly by adding nodes for each character.
        """
        for _ in range(num_chars):
            char_bits = self.read_bits(7, isBitarray=False)  # Read ASCII bits
            char = chr(int(char_bits, 2))  # Convert bits to character

            ## Decode the length of the Huffman code using Elias Omega
            code_length = self.decode_elias_omega()

            ## Read the Huffman code
            huffman_code = self.read_bits(code_length, isBitarray=False)
            self.add_huffman_code(
                char, huffman_code
            )  # Add code directly to the Huffman tree

    def decode_bwt_string(self, length):
        """
        Decodes a Burrows-Wheeler Transformed (BWT) string based on encoded input.

        Args:
            length (int): The number of characters in the BWT string to decode.

        Processes the BWT string to reconstruct the original string by tracking character frequencies and
        calculating run lengths using Elias omega decoding. Results are stored in a character count dictionary.

        Returns:
            tuple: A tuple containing the reconstructed BWT string and the character count dictionary.
        """
        bwt = []
        char_count = defaultdict(lambda: 0)
        while length > 0:  ## To avoid decoding padded bits
            char = self.get_char()
            run_length = self.decode_elias_omega()
            char_count[char] += run_length
            bwt.extend([char] * run_length)
            length -= run_length
        return bwt, char_count

    def invert_bwt_string(self, bwt, char_count):
        """
        Inverts a Burrows-Wheeler Transform (BWT) string to reconstruct the original text and writes it to an output file.

        Args:
            bwt (list): The BWT string as a list of characters.
            char_count (dict): A dictionary mapping each character to its frequency in the BWT.

        This function constructs and utilizes the LF-mapping to reconstruct the original string by following the last-to-first column mapping.
        The result is directly written to 'q2_decoder_output.txt'.
        """
        with open("q2_decoder_output.txt", "w") as output_file:
            # Constructing cumulative char count
            sorted_chars = sorted(
                char_count.keys()
            )  # Sorting the characters (constant time bounded by ASCII range)
            total = 0
            first_occurrence = {}
            for char in sorted_chars:
                first_occurrence[char] = total
                total += char_count[char]

            # Construct mapping from first to last column
            T = [0] * len(bwt)
            count = {char: 0 for char in char_count}
            for i in range(len(bwt)):
                char = bwt[i]
                T[first_occurrence[char] + count[char]] = i
                count[char] += 1

            # Reconstruct the original string by following the map
            row = T[first_occurrence["$"]]
            row = T[row]
            for _ in range(len(bwt)):
                output_file.write(bwt[row])  # Write each character to the file
                row = T[row]

    def run(self):
        """Main method to decode the entire byte stream."""
        length_of_string = self.decode_elias_omega()
        number_of_unique_chars = self.decode_elias_omega()
        self.construct_huffman_tree(number_of_unique_chars)
        bwt, char_count = self.decode_bwt_string(length_of_string)
        self.invert_bwt_string(bwt, char_count)
        return


if __name__ == "__main__":
    # Clear the output file before starting the encoding process
    output_file_name = "q2_decoder_output.txt"
    open(output_file_name, "wb").close()
    _, encoding_file_path = sys.argv
    encoder = Decoder(file_path=encoding_file_path)
    encoder.run()
