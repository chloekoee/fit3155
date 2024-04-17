import sys

"""
###### Metadata #####
Author: Chloe Koe
Date: 30/03/2024
Purpose: A1 FIT3155
Student ID: 33109109

###### q1 File Structure #####
Terminal Usage Functions
- read_file (written by Arun, I take no ownership of this function)

Construction Functions
- calculate_z_array
- construct_bad_character_matrix
- construct_good_prefix_array
- construct_match_suffix_array

Auxillary Functions
- calculate_suffix_shift
- calculate_character_shift

Main Algorithm Function
- reverse_boyer_moore
"""


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def calculate_z_array(string):
    """
    Computes the Z-array for a given string. The Z-array is a list where Z[i] represents the length
    of the longest substring starting from S[i] that matches a prefix of S. Z[0] is defined as 0.

    Parameters:
    - string (str): The input string for which the Z-array is to be calculated.

    Returns:
    - list: The Z-array for the given string. Each element Z[i] contains the length of the longest
      substring starting at S[i] which is also a prefix of S.
    """
    S = list(string)
    Z = [0 for i in range(len(S))]
    L = R = 0
    ## take the z-value of the first character as 0
    Z[0] = 0

    for K in range(1, len(S)):
        ## outside current Z-box: calculate Z[K] by direct comparison
        if K > R:
            L = R = K
            while R < len(S) and S[R] == S[R - L]:
                ## while no mismatch, keep expanding z-box
                R += 1
            Z[K] = R - L
            R -= 1

        ## inside current Z-box: use previously calculated values
        else:
            kp = K - L  ## take the mirrored value position
            dist = R - K + 1  ## distance to right edge of z-box

            ## entire Z-box is within bounds
            if Z[kp] < dist:
                Z[K] = Z[kp]

            ## possible extension beyond current Z-box
            else:
                L = K
                while R < len(S) and S[R] == S[R - L]:
                    R += 1
                Z[K] = R - L
                R -= 1

    return Z


def construct_bad_character_matrix(pat, ascii_range=94):
    """
    Constructs the bad character matrix R using extended bad character rule such that
    R[i][j] = the leftmost occurrence of character "i" to the right of index "j"

    Parameters:
    - pat (str): The pattern for which the bad character shift matrix is constructed.
    - ascii_range (int): The range of ASCII values considered. Defaults to 94, covering the printable characters.

    Returns:
    - R (list of lists): A 2D list representing the bad character shift matrix. Each row corresponds to an ASCII
      character (offset by '!' to include only printable characters), and each column to a position in the pattern.
      The value at R[i][j] is the leftmost index of character i in the pattern, to the right of position j in the
      pattern, or -1 if the character does not occur to the right of j.

    The matrix is constructed by iterating through the pattern in reverse order, ensuring that for each character,
    the closest position to the right (i.e., towards the beginning of the pattern when processed in reverse) is recorded.
    """
    m = len(pat)
    ## initialise R to -1, indiciating no position exists
    R = [[-1 for _ in range(m)] for _ in range(ascii_range)]

    for i in range(m):
        ## adjust ASCII value to printable index range
        asci = ord(pat[i]) - ord("!")

        ## iterate in reverse to find leftmost occurence from the right
        for j in range(i - 1, -1, -1):
            # if not already set mark leftmost occurence
            if R[asci][j] == -1:
                R[asci][j] = i

            ## break if already set, optimizing for leftmost requirement
            else:
                break

    return R


def construct_good_prefix_array(pat):
    """
    Constructs the 'good prefix' array. The array, gp, is defined
    such that gp[i] contains the start position of the leftmost occurrence of the substring
    pat[0...i] that is immediately followed by a character different from pat[i+1].

    Parameters:
    - pat (str): The pattern for which the 'good prefix' array is to be calculated.

    Returns:
    - gp (list): The 'good prefix' array, where gp[i] holds the start position of the leftmost
    occurrence of pat[0...i] and is followed by a character not matching pat[i+1], or -1 if no such prefix exists.
    The last element, gp[-1], is specifically set to support the scenario where there is a mismatch on the first character (i = 0)
    and gp[1-1] = gp[-1] is taken to calculate the good prefix shift.
    """
    m = len(pat)
    zp = calculate_z_array(pat)
    gp = [-1 for i in range(m + 1)]

    ## iterate in reverse to construct gp based on Z-array findings
    for p in range(m - 1, -1, -1):
        ## if a prefix match exists starting at pat[p]
        if zp[p] > 0:
            ## calculate end position of the matching prefix
            j = zp[p] - 1
            ## update gp with the start position of this prefix
            gp[j] = p

    gp[-1] = 1  ## if the mismatch occurred at i = 0, shift to character on the right
    return gp


def construct_match_suffix_array(pat):
    """
    Computes the match suffix array for a given pattern such that ms[i]
    contains the length of the longest substring within pat[0...i] that is also a suffix of pat.

    First I use the Z-algorithm on the reversed pattern to determine these
    suffix lengths, then I iterate through the pattern to populate the match suffix array, ensuring
    each entry ms[i] holds the maximum value derived from either its own Z-value or the preceding
    value in ms, therefore capturing the longest relevant suffix at each step.

    Parameters:
    - pat (str): The pattern for which the match suffix array is to be calculated.

    Returns:
    - ms (list): The match suffix array where each element, ms[i], indicates the length of the largest
      substring within pat[0...i] that matches a suffix of pat. The last element, ms[len(pat) - 1],
      is explicitly set to the full length of pat as the entire pattern is a suffix of itself.
    """

    ## initialize to zeros
    ms = [0 for i in range(len(pat) + 1)]
    ## calculate Z-array for reversed pattern and reverse it back
    z_values = calculate_z_array(pat[::-1])[::-1]

    for i in range(len(pat)):
        ## take max of new value or previous value
        ms[i] = max(z_values[i], ms[i - 1])
    ms[len(pat) - 1] = len(pat)
    return ms


def calculate_suffix_shift(gp, ms, pat, previous):
    """
    Calculates the shift, start and stop value for the reversed implementation of Boyer-Moore.
    The function evaluates whether a "good prefix" exists at the given position and calculates the shift accordingly.
    If a good prefix is found, it shifts to this position, adjusting the search boundaries to skip over the matched
    portion. If no good prefix exists, it resorts to the longest matched suffix to determine the shift to maintain
    alignment with any shorter prefix matches or non-prefix occurrences of the pattern within itself.

    Parameters:
    - gp (list): The good prefix array, representing the start positions of leftmost occurrences of substrings.
    - ms (list): The match suffix array, containing lengths of the longest substrings that are suffixes of the pattern.
    - pat (str): The pattern being searched for in the text.
    - previous (int): The index representing the end position of the matched segment in the pattern (i - 1).

    Returns:
    - tuple: Contains the shift distance (int), and the start (int) and stop (int) boundaries within the pattern that
      have been matched and should not be rechecked.
    """
    good_prefix_start = gp[previous]
    matched_suffix_length = ms[previous]

    m = len(pat)

    ## if a good prefix exists, shift by good prefix start position to maintain alignment with good prefix
    if good_prefix_start > -1:
        shift = good_prefix_start
        start = good_prefix_start
        stop = good_prefix_start + previous

    ## no good prefix exists, use longest suffix to determine shift to maintain
    ## alignment with shorter prefix matches/non-prefix pattern occurences
    else:
        shift = m - matched_suffix_length
        start = 0
        stop = matched_suffix_length - 1
    return shift, start, stop


def calculate_character_shift(bcm, character, i):
    """
    Determines shift distance for a given character at a specific position based on the
    bad character matrix. The shift is based on the leftmost occurrence of the mismatched
    character to the right of the current position. If no such occurrence exists within
    the pattern, a default shift of 1 is applied to move the pattern past the mismatched character.

    Parameters:
    - bcm (list of lists): The bad character matrix precomputed for the pattern, where bcm[c][i]
      represents the leftmost position of character 'c' to the right of index 'i' in the pattern.
    - character (str): The mismatched character encountered in the text.
    - i (int): The current position in the pattern where the mismatch occurred.

    Returns:
    - int: The calculated shift distance based on the bad character rule. This is the difference
      between the leftmost position of the mismatched character to the right of 'i' and 'i' itself,
      or 1 if the character does not occur to the right.

    """
    ascii_base = ord("!")  ## ASCII value offset for printable characters
    char_index = ord(character) - ascii_base  ## Calculate index in bcm

    if bcm[char_index][i] > -1:
        # Calculate shift based on character's leftmost occurrence to the right of i
        return bcm[char_index][i] - i
    else:
        ## Default shift of 1 when character does not occur to the right or at
        return 1


def reverse_boyer_moore(txt, pat):
    """
    Implements the Reverse Boyer-Moore search algorithm to identify all instances
    of a pattern within text. The search proceeds right-to-left through the text,
    while pattern shifts are executed left-to-right. Mismatches trigger a
    comparison between shift distances derived from the good suffix (gs) and bad
    character (bcm) arrays, adopting the larger to advance the search. In cases
    of equal shift lengths, gs shifts are favored, utilizing 'start' and 'stop'
    optimization boundaries to prevent redundant comparisons.

    The algorithm uses three arrays for calculating shifting:
    1. gp (Good Prefix): Contains start positions of the leftmost occurrence of substrings followed by a character not matching pat[i+1].
    2. mp (Match Suffix): Holds lengths of the largest substrings within pat[0...i] that are suffixes of pat
    3. bcm (Bad Character Matrix): Tracks leftmost positions of characters right of position i

    Parameters:
    - txt (str): Target text for pattern search.
    - pat (str): Pattern sought within the text.

    Time Complexity:
    - Best case: O(n/m), where n is the length of the text and m is the length of the pattern
    - Average and Worst case: O(m*n), when many potential matches or overlaps.

    Space Complexity:
    - O(m*σ), where m is the length of the pattern and σ is the size of the alphabet (printable ASCII range).
    This space is required for storing the match suffix, good prefix arrays, and the bad character matrix.

    """
    mp = construct_match_suffix_array(pat)
    m, n = len(pat), len(txt)
    gs = construct_good_prefix_array(pat)
    bcm = construct_bad_character_matrix(pat)

    ## Initialise start and stop as -2 to always fail first optimisation condition
    start = stop = -2
    j = n - m  ## Initial alignment of pattern's end with txt's end

    ## While we have not traversed all of txt
    while j >= 0:
        i = 0  ## Current position in pat
        k = j  ## Current position in txt

        ## While a mismatch has not been found
        while i < m:
            ## If we are within the boundary of previous comparison, skip these characters (we previously made an MP or GS shift)
            if i <= stop and i >= start:
                i += 1
                k += 1

            ## Else perform the comparison between txt[k] and pat[i]
            elif pat[i] == txt[k]:
                i += 1
                k += 1

            ## If we have a mismatch at txt[k], break
            else:
                break

        ## Full match found if i has incremented to equal m. Output this match and shift by mp[1]
        if i == m:
            print((k - m) + 1)  ## Output the start position of this match in 1-indexing
            j = min((j - 1), (j - (m - mp[1])))  ## Apply the largest shift
            start = stop = -1  ## Reset optimisation boundaries

        ## Else we have had a mismatch, txt[k] != pat[i]. Shift accordingly
        else:

            ## Calculate both shifts
            gs_shift, gs_start, gs_stop = calculate_suffix_shift(gs, mp, pat, i - 1)
            bc_shift = calculate_character_shift(bcm, txt[k], i)

            ## Determine which shift to use, preferencing good suffix > bad character
            ## if both shifts are equal to leverage optimisation boundaries
            if gs_shift >= bc_shift:
                shift = gs_shift
                start, stop = gs_start, gs_stop
            else:
                shift = bc_shift
                start, stop = -1, -1  ## Reset optimisation boundaries

            ## Apply the calculated shift to j
            j -= shift


if __name__ == "__main__":
    _, filename1, filename2 = sys.argv
    txt = read_file(filename1)
    pat = read_file(filename2)
    reverse_boyer_moore(txt, pat)
