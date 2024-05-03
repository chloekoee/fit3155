from a2.encoder_auxiliary import get_huffman_encodings, elias
from collections import defaultdict
from bitarray import bitarray
import sys


def encode_bwt(bwt_string):
    n = len(bwt_string)
    output_bits = bitarray()  # Initialize bitarray to collect output
    bit_modulo = 0  # To track the number of bits mod 8

    # Function to add bits to the output and update the modulo counter
    def add_to_output(data):
        nonlocal bit_modulo
        if isinstance(data, str):
            output_bits.extend(bitarray(data))
        else:
            output_bits.extend(data)
        bit_modulo = (bit_modulo + len(data)) % 8

    # Stream Elias encoding of the string length
    add_to_output(elias(n))
    print(f"string length: {elias(n)}")

    # Get Huffman Encodings
    hCodes = get_huffman_encodings(bwt_string)
    add_to_output(elias(len(hCodes)))  # Stream number of unique characters
    print(f"unique characters {len(hCodes)}: {elias(len(hCodes))}\n")

    # Stream each huffman code and its details
    for char, hCode in sorted(hCodes.items()):
        if char == "$":
            continue  # for debugging
        print(f"char: {char}, binary: {bin(ord(char))[2:]}")
        print(f"length: {len(hCode)}, binary: {elias(len(hCode))}")
        print(f"hCode: {hCode}, binary: {hCode}\n")
        add_to_output(bin(ord(char))[2:].zfill(7))
        add_to_output(elias(len(hCode)))
        add_to_output(hCode)
    ## Ensure that ASCII codes are padded with leading zeros to be of length 7

    add_to_output(bin(ord("$"))[2:].zfill(7))
    add_to_output(elias(len(hCodes["$"])))
    add_to_output(hCodes["$"])
    print(f"char: $, binary: {bin(ord('$'))[2:]}")
    print(f"length: {len( hCodes['$'])}, binary: {elias(len( hCodes['$']))}")
    print(f"hCode: { hCodes['$']}, binary: { hCodes['$']}\n")

    current_char = bwt_string[0]
    count = 1
    # Iterate over the BWT string starting from the second character
    for char in bwt_string[1:]:
        if char == current_char:
            count += 1
        else:
            add_to_output(hCodes[current_char])
            add_to_output(elias(count))
            print(f"hCode for '{current_char}': {hCodes[current_char]}")
            print(f"length: {count}, binary: {elias(count)}\n")

            current_char = char
            count = 1

    add_to_output(hCodes[current_char] + elias(count))
    print(f"hCode for '{current_char}': {hCodes[current_char]}")
    print(f"length: {count}, binary: {elias(count)}\n")

    # If there are leftover bits that don't make a full byte, pad with zeros
    if bit_modulo > 0:

        padding_length = 8 - bit_modulo
        output_bits.extend("0" * padding_length)
        print(f"padding {bit_modulo}: {padding_length}")
    return output_bits


# Initialize bit buffer
bit_buffer = bitarray()
answer = (
    "00011100010011000011011000100111101101110010100100100011111011001011011111001000"
)
print(len(answer))

# Example usage
bwt_string = "annb$aa"
result_bits = encode_bwt(bwt_string)
print(result_bits.to01())
print(answer)
print(len(result_bits))

assert result_bits.to01() == answer
