---
title: pandas vs numpy
---

# pandas vs numpy

## performance of a operation that can be vectorized

```python
import pandas as pd
import numpy as np
import time

# Creating a large Series
s = pd.Series(np.random.randn(1000000))

# Using apply() to compute the square of each element
start_time = time.time()
squared_apply = s.apply(lambda x: x**2)
end_time = time.time()
print(f"Using apply(): {end_time - start_time} seconds")

# Extracting to a NumPy array and computing the square
start_time = time.time()
squared_np = np.square(s.values)
end_time = time.time()
print(f"Using NumPy: {end_time - start_time} seconds")
```

### output

```shell
Using apply(): 0.15290331840515137 seconds
Using NumPy: 0.0 seconds
```
