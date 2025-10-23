---
title: "callable"
created: 2023-09-12 11:12:05
updated: 2023-09-12 11:14:07
---
  * 파이썬에서 클래스 안에 \_\_call\_\_ 함수를 정의하면 해당 클래스의 객체를 함수처럼 호출해서 사용할 수 있게 한다.
    * ```python
class CallableClass:
    def *call*(self, x):
        return x * 2

# Create an instance of the class
callable_instance = CallableClass()

# Use the instance as if it were a function
result = callable_instance(5)  # This calls `*call*` with x=5
print(result)  # Output will be 10
```