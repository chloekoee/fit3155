def mobius(n):
    if n == 1:
        return 1
    p = 0  # number of prime factors
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            if n // i % i == 0:  # squared prime factor
                return 0
            while n % i == 0:
                n //= i
            p += 1
    if n > 1:
        p += 1  # n is prime now
    return -1 if p % 2 else 1


def count_primitive_strings(N, A_size):
    count = 0
    for d in range(1, N + 1):
        if N % d == 0:
            count += mobius(d) * (A_size ** (N // d))
    return count


# Example usage
N = 6
A_size = 3

primitive_count = count_primitive_strings(N, A_size)
print(
    f"Number of primitive strings of length {N} over an alphabet of size {A_size}: {primitive_count}"
)


def count_primitive_strings(N, A_size):
    count = 0
    for d in range(1, N + 1):
        if N % d == 0:
            count += mobius(d) * (A_size ** (N // d))
    return count


def cyclic_permutations(N, A_size):
    total_strings = A_size**N
    strings_with_one_rotation = A_size

    strings_with_ge_two_rotations = total_strings - strings_with_one_rotation
    strings_with_exactly_n_rotations = count_primitive_strings(N, A_size)

    return (
        strings_with_ge_two_rotations,
        strings_with_exactly_n_rotations,
        strings_with_one_rotation,
    )


def is_multiple_of_N(N, A_size):
    strings_with_ge_two_rotations, _, _ = cyclic_permutations(N, A_size)
    return (strings_with_ge_two_rotations % N) == 0


# Example usage
N = 2
A_size = 100

ge_two_rotations, exactly_n_rotations, one_rotation = cyclic_permutations(N, A_size)
print(f"Strings with ≥ 2 distinct cyclic rotations: {ge_two_rotations}")
print(f"Strings with exactly N distinct cyclic rotations: {exactly_n_rotations}")
print(f"Strings with exactly 1 distinct cyclic rotation: {one_rotation}")
print(f"Is multiple of N: {is_multiple_of_N(N, A_size)}")
