---
title: typing
---
정적 타입 정의로 타입 관련 에러를 방지하기 위해  typing을 사용한다.
## sample code
```python
from typing import List, Dict, Union, Optional

def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> None:
    print(f"Hello, {name}!")

def get_student_scores(name: str) -> Dict[str, Union[int, float]]:
    # Simulated database query result
    return {
        "math": 90,
        "science": 85.5
    }

def find_max(numbers: Optional[List[int]]) -> Optional[int]:
    if not numbers:
        return None
    return max(numbers)
```

## Optional
데이터 타입이 있을 수도 있고 None일 수도 있을 때 사용.

- These two are equivalent:  
	- Optional[List[int]]  
	- Union[List[int], None]

- 일반적 사용례
1. Function parameters that might not be provided:
```python   
from typing import Optional, List

def create_user(name: str, favorite_numbers: Optional[List[int]] = None):
	if favorite_numbers is None:
		favorite_numbers = []
		# Process user creation

```
2. Return values that might fail:
```python
def find_even_numbers(data: List[int]) -> Optional[List[int]]:
	evens = [x for x in data if x % 2 == 0]
	return evens if evens else None
```
3. Class attributes that might not be initialized:
```python
class Student:
	def __init__(self, name: str):
		self.name = name
		self.grades: Optional[List[int]] = None
```
- Best Practices
	When working with Optional types, **always check for None** before using the value:
```python
def calculate_average(scores: Optional[List[int]]) -> float:
	if scores is None or len(scores) == 0:
		return 0.0
	return sum(scores) / len(scores)
```

## 검증
mypy로 코드 타입을 검증할 수 있다.
