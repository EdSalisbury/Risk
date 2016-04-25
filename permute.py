import itertools
from itertools import chain, combinations

def powerset(iterable):
  xs = list(iterable)
  # note we return an iterator rather than a list
  return chain.from_iterable( combinations(xs,n) for n in range(len(xs)+1) )


# def total_subsets_matching_sum(numbers, sum):
#     subsets = list()
#     array = [1] + [0] * (sum)
#     for current_number in numbers:
#         for num in xrange(sum - current_number, -1, -1):
#             if array[num]:
#                 subsets[sum].append(array)
#     return subsets

def total_subsets_matching_sum(numbers, sum):
    array = [1] + [0] * (sum)
    for current_number in numbers:
        print array
        for num in xrange(sum - current_number, -1, -1):
            if array[num]:
                array[num + current_number] += array[num]
    return array[sum]


def f(r, n, t, acc=[]):
    if t == 0:
        if n >= 0:
            yield acc
        return
    for x in r:
        if x > n:  # <---- do not recurse if sum is larger than `n`
            break
        for lst in f(r, n-x, t-1, acc + [x]):
            yield lst

# def subsets_matching_sum(numbers, sum):

# assert(total_subsets_matching_sum(range(1, 10), 9)       == 8)
# assert(total_subsets_matching_sum({1, 3, 2, 5, 4, 9}, 9) == 4)

# print list(itertools.permutations([1, 2, 3], 3))

#print list(itertools.combinations([1, 2, 3], 5))

#print list(powerset(set([1,2,3])))

# print total_subsets_matching_sum({1, 3, 2, 5, 4, 9}, 9)

count = 0
num_troops = 10
num_territories = 10
for xs in f(range(num_troops+1), num_troops, num_territories):
     if sum(xs) == num_troops:
        count += 1
        # print xs
        #print xs

print count

# http://stackoverflow.com/questions/27586404/how-to-efficiently-get-all-combinations-where-the-sum-is-10-or-below-in-python


import numpy as np
from itertools import product

t = 3
n = 3
# r = range(n+1)

# Create the product numpy array
# prod = np.fromiter(product(r, repeat=t), np.dtype('u1,' * t))
# prod = prod.view('u1').reshape(-1, t)

# Extract only permutations that satisfy a condition
# prod[prod.sum(axis=1) < n]