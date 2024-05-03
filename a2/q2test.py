from q2_decoder import Decoder
from q2_encoder import Encoder

text_filename = "tests.txt"
with open(text_filename, "r") as file:
    tests = file.read().strip().split("\n")


# for index, test in enumerate(tests):
for index, test in enumerate(tests):
    input_file_name = f"test_input.txt"
    encoding_file_path = f"q2_encoder_output.bin"
    output_file_name = f"q2_decoder_output.txt"

    # Refresh
    open(encoding_file_path, "wb").close()
    open(output_file_name, "wb").close()

    # Write test case to a temporary input file
    with open(input_file_name, "w") as file:
        file.write(test)

    # Run encoder
    encoder = Encoder(input_file_path=input_file_name)
    encoder.run()  # Assuming `run` method encompasses encoding and writing to output file

    # Clear the decoder output file
    with open(output_file_name, "wb") as file:
        pass  # Just to clear/ensure the file is created

    # Run decoder
    decoder = Decoder(encoding_file_path)
    decoded_output = (
        decoder.run()
    )  # Assuming `run` method encompasses decoding and returning the output

    # Read decoded output from file
    with open(output_file_name, "r") as file:
        decoded_output = file.read().strip()

    if test == decoded_output:
        pass
        # print(f"Test {index + 1}: Pass")
    else:
        print(f"Test {index + 1}: FAIL")
        print(f"Expected: {test}, Got: {decoded_output}")
        break  # Exit on first failure


text_filename = "hamlet.txt"
with open(text_filename, "r") as file:
    test = file.read()
input_file_name = f"test_input.txt"
encoding_file_path = f"q2_encoder_output.bin"
output_file_name = f"q2_decoder_output.txt"

# Refresh
open(encoding_file_path, "wb").close()
open(output_file_name, "wb").close()

# Write test case to a temporary input file
with open(input_file_name, "w") as file:
    file.write(test)

# Run encoder
encoder = Encoder(input_file_path=input_file_name)
encoder.run()  # Assuming `run` method encompasses encoding and writing to output file

# Clear the decoder output file
with open(output_file_name, "wb") as file:
    pass  # Just to clear/ensure the file is created

# Run decoder
decoder = Decoder(encoding_file_path)
decoded_output = (
    decoder.run()
)  # Assuming `run` method encompasses decoding and returning the output

# Read decoded output from file
with open(output_file_name, "r") as file:
    decoded_output = file.read().strip()

if test == decoded_output:
    print(f"Test Pass")
else:
    print(f"Test FAIL")
