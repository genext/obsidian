---
title: pydantic
---

# pydantic

provides runtime validation and type coercion

## 개요

데이터 유효성 library로 타입을 정의한 클래스 만들 수 있다.

## 리눅스 환경변수

WEB_APP1 어플리케이션이 사용하는 환경 변수 WEB_APP1_MY_VARIABLE을 읽어올 때

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    my_variable: str // .env에 있는 동일한 환경변수보다 우선.

    class Config:
        env_prefix = "WEB_APP1"
        env_file = ".env"

settings = Settings()

print("Value of WEB_APP1_MY_VARIABLE:", settings.my_variable)
```

### env_prefix

여러 어플리케이션이 한 시스템에서 돌고 모두 환경변수를 정의해서 쓴다면 접두어로 어떤 어플리케이션이 사용하는 환경변수인지 구분할 수 있음.

### Config class

해당 pydantic model 행동을 미리 정의

- env_file
- fields_ordered
- allow_extra
- anystr_strip_whitespace
- orm_mode
- schema_extra

## CRUD schema

pydantic을 이용해서 CRUD에 필요한 구조를 정의하는 일반적인 방법

```python
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True
```

## annotations

### @validate_call

```python
# Built-in Python (no runtime validation)
from typing import Iterable, Any

def show_all(iterable: Iterable[Any]) -> None:
    """
    This only provides type hints for static analysis tools like mypy
    No runtime validation occurs
    """
    for item in iterable:
        print(item)

# With Pydantic (runtime validation)
from pydantic import validate_call  # Third-party library
from typing import Iterable, Any

@validate_call  # This is from Pydantic, not built-in Python
def show_all(iterable: Iterable[Any]) -> None:
    """
    This provides runtime validation of arguments
    """
    for item in iterable:
        print(item)
```

## Pydantic best practice for performance

- **Use Pydantic at System Boundaries:** The most common and recommended approach is to use Pydantic for validation only when data enters your system, such as at an API endpoint.
- **`model_validate_json()`:** When working with JSON strings, use `Model.model_validate_json()` instead of the two-step `json.loads(data)` followed by `Model.model_validate(data)`. The single-step method is often more efficient as Pydantic's Rust core can handle the parsing and validation simultaneously.
- **Use `TypeAdapter`:** If you need to validate a single object or a simple collection (like a `List[int]`) without creating a full `BaseModel`, `TypeAdapter` is a lightweight, performant alternative.
