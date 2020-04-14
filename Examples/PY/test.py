

import numpy as np
"""
size = (3, 4)

A = np.zeros(size)
print(A)

# AI shape = (2, 3, 4) # (indices , real x, real y)
AI = np.indices(size)
print("AI")
print(AI)
#  AIT shape = (4, 3, 2)
AIT = np.transpose(AI)
print("AIT")
print(AIT)


# desired shape = (3,4,2) # (real x, real y, indices)
AIT_test = np.transpose(AI, (1, 2, 0)) 
print("correct AIT")
print(AIT_test)

dim = 3
#order = np.array([(d + 1) % (dim + 1) for d in range(dim + 1)])

order = np.arange(dim + 1)
shift = 1
new_order = np.roll(order, shift)
print(order)
print(new_order)


order = np.arange(16).reshape(4, 4)
shifts = [[0, 0],
          [0, 1],
          [0, -1],
          [1, 0],
          [-1, 0]]

neighbours = [np.roll(order, shift, (0, 1)).ravel() for shift in shifts]
print(np.stack(neighbours, axis=-1))

import compas

print(compas.__version__)
"""

# from . import volpy 

# print(volpy.draft.hello())