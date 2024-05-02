import secrets
import string

tests = []
for i in range(1):

    for n in range(6, 300):

        res = "".join(secrets.choice(string.ascii_lowercase) for _ in range(n)) + "$"
        tests.append(res)

ranks_str = "\n".join(tests)
with open("tests.txt", "w") as output_file:
    output_file.write(f"{ranks_str}")
