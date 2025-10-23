---
title: "vectorization"
created: 2024-02-23 14:21:04
updated: 2024-03-17 15:43:22
---
## **What is Vectorization ?**
to speed up the Python code without using loop
### example
#### - requirements.txt
```plain text
asttokens==2.4.1
colorama==0.4.6
comm==0.2.1
debugpy==1.8.1
decorator==5.1.1
exceptiongroup==1.2.0
executing==2.0.1
importlib-metadata==7.0.1
ipykernel==6.29.2
ipython==8.18.1
jedi==0.19.1
jupyter_client==8.6.0
jupyter_core==5.7.1
matplotlib-inline==0.1.6
nest-asyncio==1.6.0
numpy==1.26.4
packaging==23.2
parso==0.8.3
platformdirs==4.2.0
prompt-toolkit==3.0.43
psutil==5.9.8
pure-eval==0.2.2
Pygments==2.17.2
python-dateutil==2.8.2
pywin32==306
pyzmq==25.1.2
six==1.16.0
stack-data==0.6.3
tornado==6.4
traitlets==5.14.1
typing_extensions==4.9.0
wcwidth==0.2.13
zipp==3.17.0
```
#### - dot product
(inner product) of vectors: dot(a,b)
also known as *scalar product* as it produces single output
![[100. media/image/mROwNja9Xh.png]]
code sample
```python
import time
import numpy
import array

# 8 bytes size int
a = array.array('q')
for i in range(100000):
    a.append(i)

b = array.array('q')
for i in range(100000, 200000):
    b.append(i)
    
# classic dot product of vectors implementation
tic = time.process_time()
dot = 0.0

for i in range(len(a)):
    dot += a[i] * b[i]

toc = time.process_time()
print(f'1. Dot product: {dot}')
print('2. Dot product: ' + str(dot))
print('computation time: ' + str(1000*(toc - tic)) + 'ms')

n_tic = time.process_time()
n_dot_product = numpy.dot(a, b)
n_toc = time.process_time()

print("\nn_dot_product = "+str(n_dot_product)) 
print("Computation time = "+str(1000*(n_toc - n_tic ))+"ms")
```
	output
```shell
dot_product = 833323333350000.0
Computation time = 35.59449199999999ms

n_dot_product = 833323333350000
Computation time = 0.1559900000000225ms
```
#### - outer product: outer(a,b)
The *tensor product* of two **coordinate** vectors
results in square matrix of dimension equal to length X length of the vectors
![[100. media/image/7qowP_JAMW.png]]
code sample
```python
import time
import numpy
import array

a = array.array('i')
for i in range(200):
    a.append(i)

b = array.array('i')
for i in range(200, 400):
    b.append(i)

# classic outer product of vectors implementation
tic = time.process_time()
outer_product = numpy.zeros((200, 200))

for i in range(len(a)):
    for j in range(len(b)):
        outer_product[i][j] = a[i] * b[j]

toc = time.process_time()

print("outer_product = "+ str(outer_product)); 
print("Computation time = "+str(1000*(toc - tic ))+"ms") 

n_tic = time.process_time()
n_outer_product = numpy.outer(a, b)
n_toc = time.process_time()

print("outer_product = "+str(outer_product)); 
print("\nComputation time = "+str(1000*(n_toc - n_tic ))+"ms")
```
output
```shell
outer_product = [[     0.      0.      0. ...,      0.      0.      0.]
 [   200.    201.    202. ...,    397.    398.    399.]
 [   400.    402.    404. ...,    794.    796.    798.]
 ..., 
 [ 39400.  39597.  39794. ...,  78209.  78406.  78603.]
 [ 39600.  39798.  39996. ...,  78606.  78804.  79002.]
 [ 39800.  39999.  40198. ...,  79003.  79202.  79401.]]

Computation time = 39.821617ms

outer_product = [[    0     0     0 ...,     0     0     0]
 [  200   201   202 ...,   397   398   399]
 [  400   402   404 ...,   794   796   798]
 ..., 
 [39400 39597 39794 ..., 78209 78406 78603]
 [39600 39798 39996 ..., 78606 78804 79002]
 [39800 39999 40198 ..., 79003 79202 79401]]

Computation time = 0.2809480000000031ms
```
#### - Element wise multiplication
products the element of same indexes and dimension of the matrix remain unchanged
![[100. media/image/I4klqbQdmq.png]]
code sample
```python
import time
import numpy
import array

a = array.array('i')
for i in range(50000):
    a.append(i)

b = array.array('i')
for i in range(50000, 100000):
    b.append(i)

# classic element wise product of vectors implementation
vector = numpy.zeros((50000))

tic = time.process_time()
for i in range(50000):
    vector[i] = a[i] * b[i]

toc = time.process_time()

print("Element wise Product = "+ str(vector)); 
print("\nComputation time = "+str(1000*(toc - tic ))+"ms") 

n_tic = time.process_time()
n_vector = numpy.multiply(a, b)
n_toc = time.process_time()

print("Element wise Product = "+str(vector)); 
print("\nComputation time = "+str(1000*(n_toc - n_tic ))+"ms")
```
output
```shell
Element wise Product = [  0.00000000e+00   5.00010000e+04   1.00004000e+05 ...,   4.99955001e+09
   4.99970000e+09   4.99985000e+09]

Computation time = 23.516678000000013ms

Element wise Product = [        0     50001    100004 ..., 704582713 704732708 704882705]
Computation time = 0.2250640000000248ms
```
