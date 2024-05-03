from itertools import zip_longest, islice

from archive.q12 import SuffixTree


def to_int_keys_best(list):
    """
    l: iterable of keys
    returns: a list with integer keys
    """
    seen = set()
    ls = []
    for e in list:
        if e not in seen:
            ls.append(e)
            seen.add(e)
    ls.sort()
    index = {v: i for i, v in enumerate(ls)}
    return [index[v] for v in list]


def suffix_array_best(s):
    """
    suffix array of s
    O(n * log(n)^2)
    """
    n = len(s)
    k = 1
    line = to_int_keys_best(s)
    while max(line) < n - 1:
        line = to_int_keys_best(
            [
                a * (n + 1) + b + 1
                for (a, b) in zip_longest(line, islice(line, k, None), fillvalue=-1)
            ]
        )
        k <<= 1
    return line


text_filename = "tests.txt"
tests = open(text_filename).read().split("\n")


count = 0
total_run = 0
smallest_fail = ""
for test in tests:

    t = SuffixTree(test, [i for i in range(1, len(test) + 1)])
    try:
        t.build_suffix_tree()
    except:
        pass
    s_arr = t.get_sorted_suffixes()
    # ordered_rank = [-1] * len(t.text)
    # for i in range(len(t.text)):
    #     try:
    #         rank = s_arr[i]
    #     except IndexError:
    #         pass
    #     ordered_rank[rank] = i

    s_arr2 = suffix_array_best(test)
    s_arr2 = [i + 1 for i in s_arr2]

    if s_arr == s_arr2:
        # print(count)
        count += 1

    # Uncomment if you want to be given a test case to solve
    else:
        if smallest_fail == "":
            smallest_fail = test
        if len(test) <= len(smallest_fail):
            smallest_fail = test
            print(s_arr)
            print(s_arr2)
            print(smallest_fail)
print(smallest_fail)
print(count / len(tests) * 100)
