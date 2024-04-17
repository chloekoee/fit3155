from bitarray import bitarray
import sys

"""
###### Metadata #####
Author: Chloe Koe
Date: 30/03/2024
Purpose: A1 FIT3155
Student ID: 33109109

###### q2 File Structure #####
Terminal Usage Functions
- read_file (written by Arun, I take no ownership of this function)

Main Algorithm Function
- bitvector_match
"""


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def bitvector_match(txt, pat):
    """
    Implements pattern matching utilizing bit vectors. This approach identifies all occurrences
    of a pattern within a text by updating bit vectors to track matching positions as the
    pattern is shifted from left to right under the text.

    The bit vector update mechanism uses the relationship between the bit vectors of
    successive text positions. Bit vector delta_j is generated for each text
    position j, indicating mismatches between txt[j] and each character in pat. The
    bit vector for j, bitvector_j, is then obtained by left-shifting the previous bit vector
    and performing a logical or with delta_j.

    The matrix r holds bit vectors for each text position, where r[i] represents the
    bitvector corresponding to prefix matches of pat at position txt[i]. A value of r[i][j] = 1
    indicates a mismatch for the prefix pat[0...i] against txt[j-i...j], otherwise 0 for a match.
    (Please note that I indexed the bitvector in reverse to what is in the spec sheet)
    Full matches are identified where r[i][0] = 0 for any i, indicating a complete prefix match.

    Parameters:
    - txt (str): The text in which to search for the pattern.
    - pat (str): The pattern to search for within the text.

    Time Complexity: O(mn), where m is the length of the pattern and n is the length of the text.
    Due to iterating through all of n without skips, and comparing each new character at txt[j], m<=j<n
    to each character in pat

    Space Complexity: O(m + n), due to dimensions of r.
    """
    n = len(txt)
    m = len(pat)

    ## Return empty if text is shorter than pattern
    if n < m:
        return []

    ## Initialise r as a matrix of None
    r = [None for i in range(n)]

    ## Construct initial bit vector by direct comparison
    first_bit = [1 if pat[0:i] != txt[m - i : m] else 0 for i in range(m, 0, -1)]
    first_bit = bitarray(first_bit)

    # Check if a pattern match exists starting at first position
    if first_bit[0] == 0:
        print(1)  ## 1-indexing

    r[m - 1] = first_bit

    ## Shift pat under text from left to right
    ## Start at m as a full pattern match cannot fit in txt[0...(<m)]
    for j in range(m, n):
        previous = r[j - 1]
        delta = bitarray(m)

        ## Populate delta with mismatches between pat and txt[j]
        for i in range(m):
            delta[i] = pat[m - i - 1] != txt[j]

        ## Shift previous bit vector left and combine with delta
        shift_left = previous[1:] + bitarray("0")
        bitvector_j = shift_left | delta

        r[j] = bitvector_j

        # If the current bitvector[0] is 0, then the prefix[0...(m-0)] or the full pattern matched
        # the txt at txt[j-m+1...j]
        if bitvector_j[0] == 0:
            print(j - m + 2)  ## 1 -indexing


if __name__ == "__main__":
    _, filename1, filename2 = sys.argv
    txt = read_file(filename1)
    pat = read_file(filename2)
    bitvector_match(txt, pat)
