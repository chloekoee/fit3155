from bitarray import bitarray
from encoder_auxiliary import get_huffman_encodings, elias
from ukkonen import SuffixTree


class Encoder:
    def __init__(self, inputString):
        self.sTree = SuffixTree(string=inputString, encoderMode=True)
        self.sTree.build_suffix_tree()
        self.bwt_string = self.sTree.get_bwt()
        self.frequencies = self.sTree.get_frequency_count()

        self.output_bits = (
            bitarray()
        )  ## TODO : Remove this after testing, convert to streaming
        self.bit_modulo = 0

    def add_to_output(self, data):
        if isinstance(data, str):
            self.output_bits.extend(bitarray(data))
        else:
            self.output_bits.extend(data)
        self.bit_modulo = (self.bit_modulo + len(data)) % 8

    def encode_bwt(self):
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

        if self.bit_modulo > 0:
            padding_length = 8 - self.bit_modulo
            self.output_bits.extend("0" * padding_length)

        return self.output_bits


if __name__ == "__main__":
    bwt_string = "$"
    encoder = Encoder(bwt_string)
    bit_array = encoder.encode_bwt()
    print("Binary Stream:", bit_array.to01())
    print("Total Length of Bit Array:", len(bit_array))
