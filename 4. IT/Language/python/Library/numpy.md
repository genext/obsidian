---
title: NumPy
---
## array-processing library
- [source](https://github.com/genext/numpy)
- [Document](https://numpy.org/doc/)
- NumPy arrays are **memory efficient** as it stores the homogenous data in contiguous blocks of memory,
## Basic concept/terms
- **axes(axis)**: dimensions
- **rank**: number of axes
- **shape**: A tuple of integers giving the size of the array along each dimension
## Broadcasting
- Broadcasting allows us to perform operations between arrays of different shapes.
- automatically expand the dimensions of the smaller array to match the dimensions of the larger array, **without actually copying data**
### Broadcasting rule

#### Rule 1: If the two arrays differ in their number of dimensions, the shape of the one with fewer dimensions is padded with ones on its leading (left) side.
**example**
```python
import numpy as np

# A larger array
a = np.array([[1, 2, 3, 4, 5, 6]])

# A smaller array
b = np.array([1, 2, 3])

# Broadcasting happens here; 'b' is automatically expanded
# to match the shape of 'a' during addition, as if it were
# np.array([[1, 2, 3, 1, 2, 3]]).
print(a + b)
```
**output**
```shell
[[2 4 6]
 [5 7 9]]
```
#### Rule 2: If the shape of the two arrays does not match in any dimension, the array with shape equal to 1 in that dimension is stretched to match the other shape.
**example1**
```python
import numpy as np

# 2D array
a = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

print('shape of a: ', a.shape)
# Column vector
b = np.array([[1, 2, 3]])
print('shape of b: ', b.shape)

# Broadcasting b onto a
result = a + b

print("Result of Broadcasting:\n", result)
```
**output**
b 변형
```shell
b
[[1, 2, 3]]

after broadcasting
b
[[1,1,1, 2,2,2, 3,3,3]]
```

```shell
shape of a:  (3, 3)
shape of b:  (3, 1)
Result of Broadcasting:
 [[ 2  3  4]
 [ 6  7  8]
 [10 11 12]]
```
**example2**
```python
import numpy as np

# 2D array
a = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

# Row vector
b = np.array([1, 0, -1])

# Broadcasting b onto a
result = a + b

print("Result of Broadcasting:\n", result)
```
**output**
b 변형
```shell
[[ 1,  0, -1],
 [ 1,  0, -1],
 [ 1,  0, -1]]
```

```shell
Result of Broadcasting:
 [[2 2 2]
 [5 5 5]
 [8 8 8]]
```
#### Rule 3: If in any dimension the sizes disagree and neither is equal to 1, a ValueError (indicating that the arrays have incompatible shapes) is raised.
**example**
```python
import numpy as np

# 1D array with 3 elements
a = np.array([1, 2, 3])
print('shape of a: ', a.shape)

# 1D array with 4 elements
b = np.array([1, 2, 3, 4])
print('shape of b: ', b.shape)

# This will raise a ValueError due to incompatible shapes
try:
    result = a + b
    print("Result:", result)
except ValueError as e:
    print("Error:", e)

import numpy as np

#-------------------------------
# 2D array with shape (2, 3)
a = np.array([[1, 2, 3],
              [4, 5, 6]])

# 2D array with shape (3, 3)
b = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

# This will raise a ValueError due to incompatible shapes
try:
    result = a + b
    print("Result:", result)
except ValueError as e:
    print("Error:", e)
```
**output**
```shell
shape of a:  (3,)
shape of b:  (4,)
Error: operands could not be broadcast together with shapes (3,) (4,)
Error: operands could not be broadcast together with shapes (2,3) (3,3)
```
## Arrays in NumPy
**example**
```python
# In this example, we are creating a two-dimensional array that has the rank of 2 as it has 2 axes.
# The first axis(dimension) is of length 2, i.e., the number of rows,
# and the second axis(dimension) is of length 3, i.e., the number of columns.
# The overall shape of the array can be represented as (2, 3)

import numpy as np

arr = np.array([[1,2,3, 4,2,5]])

# Printing type of arr object
print('Array is of type: ', type(arr))

# Printing array dimensions (axes)
print('No. of dimensions: ', arr.ndim)

# Printing shape of array
print('Shape of array: ', arr.shape)

# Printing size (total number of elements) of array
print('Size of array: ', arr.size)

# Printing type of elements in array
print('Array stores elements of type: ', arr.dtype)
```
**output**
```shell
Array is of type:  <class 'numpy.ndarray'>
No. of dimensions:  2
Shape of array:  (2, 3)
Size of array:  6
Array stores elements of type:  int64
```
## NumPy Array Creation
### From list, tuple

```python
import numpy as np

# Creating array from list with type float
a = np.array([[1, 2, 4, 5, 8, 7]], dtype = 'float')
print ("Array created using passed list:\n", a)

# Creating array from tuple
b = np.array((1 , 3, 2))
print ("\nArray created using passed tuple:\n", b)
```

**output**
```shell
Array created using passed list:
 [[1. 2. 4.]
 [5. 8. 7.]]

Array created using passed tuple:
 [1 3 2]
```

### Fixed size

- np.zeros, np.ones, np.full, np.empty, etc.

#### arrange

```python
# Create a sequence of integers
# from 0 to 30 with steps of 5
f = np.arange(0, 30, 5)
print ("A sequential array with steps of 5:\n", f)
```

**output**
```shell
A sequential array with steps of 5:
[ 0  5 10 15 20 25]
```

#### linspace

### etc

#### reshaping array

#### flatten array

```python
# Flatten array
arr = np.array([[1, 2, 3, 4, 5, 6]])
flat_arr = arr.flatten()

print ("Original array:\n", arr)
print ("Fattened array:\n", flat_arr)
```

**output**
```shell
Original array:
 [[1 2 3]
 [4 5 6]]
Fattened array:
 [1 2 3 4 5 6]
```

## NumPy Array Indexing

### Slicing

### Integer array indexing

- lists are passed for indexing for each dimension.

### Boolean array indexing

**example**
```python
# indexing in numpy
import numpy as np

arr = np.array([[-1, 2, 0, 4],
                [4, -0.5, 6, 0],
                [2.6, 0, 7, 8],
                [3, -7, 4, 2.0]])

# Slicing array
temp = arr[:2, :2]
print ("Array with first 2 rows and alternate"
                    "columns(0 and 2):\n", temp)

# Integer array indexing example
temp = arr[[0, 1, 2, 3, 3, 2, 1, 0]]
print ("\nElements at indices (0, 3), (1, 2), (2, 1),"
                                    "(3, 0):\n", temp)

# boolean array indexing example
cond = arr > 0 # cond is a boolean array
temp = arr[cond]
print ("\nElements greater than 0:\n", temp)
```

**output**
```shell
Array with first 2 rows and alternatecolumns(0 and 2):
 [[-1.  0.]
 [ 4.  6.]]

Elements at indices (0, 3), (1, 2), (2, 1),(3, 0):
 [ 4.  6.  0.  3.]

Elements greater than 0:
 [ 2.   4.   4.   6.   2.6  7.   8.   3.   4.   2. ]
```

## NumPy Basic Operations

### Operations on a single NumPy array

We can use overloaded arithmetic operators to do element-wise operations on the array to create a new array.

**example**
```python
##############################################################################################
# basic operations on single array
##############################################################################################
import numpy as np

a = np.array([1, 2, 5, 3])

# add 1 to every element
b = a + 1
print ("Adding 1 to every element:", b)

# subtract 3 from each element
b = a - 3  # b = a - np.array([3, 3, 3, 3])
print ("Subtracting 3 from each element:", b)

# multiply each element by 10
print ("Multiplying each element by 10:", a*10)

# square each element
print ("Squaring each element:", a**2)

# modify existing array
a *= 2
print ("Doubled each element of original array:", a)

# transpose of array
a = np.array([[1, 2, 3, 3, 4, 5, 9, 6, 0]])

print ("\nOriginal array:\n", a)
print ("Transpose of array:\n", a.T)
```

**output**
```shell
Adding 1 to every element: [2 3 6 4]
Subtracting 3 from each element: [-2 -1  2  0]
Multiplying each element by 10: [10 20 50 30]
Squaring each element: [ 1  4 25  9]
Doubled each element of original array: [ 2  4 10  6]

Original array:
 [[1 2 3]
 [3 4 5]
 [9 6 0]]
Transpose of array:
 [[1 3 9]
 [2 4 6]
 [3 5 0]]
```

### Unary Operators

- sum, min, max, etc.
- These functions can also be applied row-wise or column-wise by setting an axis parameter.

**example**
```python
##############################################################################################
# unary operators in numpy
##############################################################################################
import numpy as np

arr = np.array([[1, 5, 6],
                [4, 7, 2],
                [3, 1, 9]])

# maximum element of array
print ("Largest element is:", arr.max())
print ("Row-wise maximum elements:",
                    arr.max(axis = 1))

# minimum element of array
print ("Column-wise minimum elements:",
                        arr.min(axis = 0))

# sum of array elements
print ("Sum of all array elements:",
                            arr.sum())

# cumulative sum along each row
print ("Cumulative sum along each row:\n",
                        arr.cumsum(axis = 1))
```

**output**
```shell
Largest element is: 9
Row-wise maximum elements: [6 7 9]
Column-wise minimum elements: [1 1 2]
Sum of all array elements: 38
Cumulative sum along each row:
[[ 1  6 12]
 [ 4 11 13]
 [ 3  4 13]]
```

### Binary Operators

**example**
```python
##############################################################################################
# binary operators in numpy
##############################################################################################
import numpy as np

a = np.array([[1,2, 3,4]])
b = np.array([[4,3, 2,1]])

# add arrays
print ("Array sum:\n", a + b)

# multiply arrays (elementwise multiplication)
print ("Array multiplication:\n", a*b)

# matrix multiplication
print ("Matrix multiplication:\n", a.dot(b))
```

**output**
```shell
Array sum:
[[5 5]
 [5 5]]
Array multiplication:
[[4 6]
 [6 4]]
Matrix multiplication:
[[ 8  5]
 [20 13]]
```

### etc

- sin, cos, exp, sort

## numpy function

### where

조건 만족 인덱스 반환

### transpose

swap the rows and columns of a dataframe or a series.

**useful scenario**
- reorientation data for visualization purposes.
- for machine learning
- compare series or dataframe structure
- pivot table post-processing

**example**
```python
import pandas as pd

# Create a sample DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'Los Angeles', 'Chicago']}

df = pd.DataFrame(data)

# Transpose the DataFrame
df_transposed = df.transpose()

print(df_transposed)
```

**output**
```shell
      Name  Age         City
0    Alice   25     New York
1      Bob   30  Los Angeles
2  Charlie   35      Chicago
---------------------
             0            1        2
Name     Alice          Bob  Charlie
Age         25           30       35
City  New York  Los Angeles  Chicago
```
