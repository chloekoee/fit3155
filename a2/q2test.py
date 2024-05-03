from decoder import Decoder
from encoder import Encoder

text_filename = "tests.txt"
tests = open(text_filename).read().split("\n")
for test in tests:
    encoder = Encoder(test)
    bit_array = encoder.encode_bwt()
    encoded_string = bit_array.to01()
    decoder = Decoder(encoded_string)
    decoded_output = decoder.decode_bytestream()
    if test == decoded_output:
        print(True)
    else:
        print("FUUUCK")
        print(test, decoded_output)
        break
