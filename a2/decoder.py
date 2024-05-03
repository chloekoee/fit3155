from bitarray import bitarray
from collections import defaultdict


class Decoder:

    def __init__(self, encoded_input):
        self.encoded_input = encoded_input
        self.cursor = 0  # Cursor to track the current read position in the bitarray
        self.output = []
        self.huffman_root = {}

    def add_huffman_code(self, char, code):
        node = self.huffman_root
        for bit in code:
            if bit not in node:
                node[bit] = {}  # Create a new node if the path doesn't exist
            node = node[bit]
        node["char"] = char  # Mark the end of the code path with the character

    def get_char(self):
        node = self.huffman_root
        for _ in range(len(self.encoded_input)):  # Safer than a while loop
            if len(node) == 1:  ## This is leaf note : {'char':'a'}
                return node["char"]
            else:
                bit = self.read_bits(1, isBitarray=False)
                node = node.get(bit, None)
                # if not node:
                #     print("Error Decoding")

    def read_bits(self, num_bits, isBitarray=True):
        """Reads num_bits from the encoded_input starting from the cursor."""
        bits = self.encoded_input[self.cursor : self.cursor + num_bits]
        self.cursor += num_bits
        if isBitarray:
            return bitarray(bits)
        else:
            return bits

    def peek_bits(self, num_bits, isBitarray=True):
        """Reads next bits from the encoded_input without moving cursor"""
        bits = self.encoded_input[self.cursor : self.cursor + num_bits]
        if isBitarray:
            return bitarray(bits)
        else:
            return bits

    def decode_elias_omega(self):
        """
        Decodes an Elias omega encoded number from the current position.
        """

        def recursive_decode(i, length):
            if self.peek_bits(1)[0] == 1:
                return int(self.read_bits(length, isBitarray=False), 2)

            next_length_binary = self.read_bits(length)
            next_length_binary[0] = 1
            next_length = int("".join(map(str, next_length_binary)), 2)
            next_length += 1

            next_i = i + length
            return recursive_decode(i=next_i, length=next_length)

        return recursive_decode(i=0, length=1)

    def construct_huffman_tree(self, num_chars):
        """Directly constructs the Huffman decoding tree from the encoded input."""
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
        ## Constructing cumulative char count
        sorted_chars = sorted(char_count.keys())  # O(1)
        total = 0
        first_occurrence = {}
        for char in sorted_chars:
            first_occurrence[char] = total
            total += char_count[char]

        ## Construct mapping first to last column
        T = [0] * len(bwt)
        count = {char: 0 for char in char_count}
        for i in range(len(bwt)):
            char = bwt[i]
            T[first_occurrence[char] + count[char]] = i
            count[char] += 1

        # Step 4: Reconstruct the original string by following the map
        row = T[first_occurrence["$"]]
        row = T[row]
        for _ in range(len(bwt)):
            self.output.append(bwt[row])
            row = T[row]

    def decode_bytestream(self):
        """Main method to decode the entire byte stream."""
        length_of_string = self.decode_elias_omega()
        number_of_unique_chars = self.decode_elias_omega()
        self.construct_huffman_tree(number_of_unique_chars)
        bwt, char_count = self.decode_bwt_string(length_of_string)
        self.invert_bwt_string(bwt, char_count)
        # TODO: Stream these bits out
        return "".join(self.output)


if __name__ == "__main__":
    encoded_string = "000000101010011011110111100010000000100100000100000111011100001000010110011100010000111100010011010111001101101111010010111001100101011101111010001111011000110001001110110100000010011110110100000111001011110100011110011110010000110100101101001011010101000101011000"
    decoder = Decoder(encoded_string)
    decoded_output = decoder.decode_bytestream()
    print("Decoded Output:", decoded_output)
