---
title: "IT 일반"
created: 2025-09-29 14:03:47
updated: 2025-10-04 13:04:24
---
## LSP(Language Server Protocol)
?
- **core: M x N 관계를 1 x N 관계로 decoupling**
- a standardized protocol that defines how development tools communicate with language servers.
- Most modern editors (VS Code, Neovim, Emacs, ...) already have LSP support
<!--SR:!2025-12-23,46,250-->
-
  
## frontend css framework
?
* Bootstrap, Tailwind
<!--SR:!2025-11-11,23,250-->
-

## REST API Generator
?
* OpenAPI Generator: Open-source tool that generates code from OpenAPI **specifications**:
* Client libraries (JavaScript, Python, Java, C#, etc.)
* Server stubs and boilerplate code
* API documentation in various formats
* Configuration files for API gateways
<!--SR:!2025-11-10,22,250-->
-

## variable/function naming style 4
?
* snake_case: buffer_max_size
* kebab-case: buffer-max-size
* camelCase: bufferMaxSize
* PascalCase: BufferMaxSize(upper camel case)
<!--SR:!2025-11-21,12,230-->
-

## uml 표기
?
![[100. media/image/Ced4rWfJ6b.png]]
Association:
1. 멤버변수에 객체가 보관되어 클래스 생명주기까지 유지
2. uml에서 실선으로 표시.
3. Directed Association은 직접 연관이라기보다는 방향 연관으로 이해. 화살표는 참조하는 방향을 의미.

Aggregation: has-a 관계로 각 클래스가 독립적인 관계. 예) 자동차와 바퀴
```java
class Department {
    private List<Employee> employees; // Employees exist independently
    public Department(List<Employee> employees) {
        this.employees = employees; // External objects passed in
    }
}
```

Composition: part-of 관계로 부분의 생명 주기가 전체 영향 받음. 예) 인간과 심장
```java
class House {
    private Room livingRoom;
    private Room bedroom;

    public House() 

    this.livingRoom = new Room("Living Room"); // Created internall
        this.bedroom = new Room("Bedroom");
    }
}
```
또는 이식이나 재사용이 불가능하고 아주 종속적인 것만 inner class로 구현하기도 함.
<!--SR:!2025-11-21,14,210-->
-

## sentinel value
?
* 참조자 타입이 아닌, 값 타입(value type)이면 nullable이 아니고 초기화값이 항상 있다. 이 때는 -1 또는 그 타입의 최대값을 sentinel value로 정해서 쓰면 굳이 그 타입을 nullable 참조자 타입으로 바꿔서 복잡하게 코딩할 필요 없다.
<!--SR:!2025-12-21,47,250-->
-

## 파일 타입 식별(magic numbers, file signature)
?
* 대부분 파일의 첫 4byte initial set of 4 bytes로 식별 가능. The term likely comes from the programming concept of "magic numbers" - hard-coded values in code whose meaning isn't immediately obvious.
	pdf : 25 50 44 46 (ASCII for %PDF)
	PNG : 89 50 4E 47(hex). linux->5089 474e
	JPEG : FF D8 FF e0. linux-> d8ff e0ff
	ZIP : 50 4B 03 04 -> 요즘 ms office 파일은 zip type으로 압축된 xml 파일. linux에서 docx는 4b50 0403으로 시작.

- 운영체제 구분
	Unix/linux: `file` -> /etc/magic, /usr/share/misc/magic
	Windows: file extension.
<!--SR:!2025-12-17,44,250-->
-

## 클럭/코어/쓰레드
?
* 클럭: CPU가 1초에 수행하는 연산 능력. 3.5GHz = 1초 35억번 연산.
	**Single-threaded Performance**
	Clock speed difference: 4.7 GHz ÷ 3.5 GHz = **1.34x faster (34% faster)**
* 코어: 한 CPU가 할 수 있는 병렬 연산 수. 6 core = 작업을 6개 동시에 처리 가능. GPU는 코어가 수천, 수만 개.
	**Core-limited workloads**
	For applications that scale with physical cores but not threads:
	CPU 1: 4.7 × 8 = 37.6 GHz-cores
	CPU 2: 3.5 × 6 = 21.0 GHz-cores
	Difference: 37.6 ÷ 21.0 = **1.79x faster (79% faster)**
* 쓰레드: 코어의 팔. 12 쓰레드. 한 코어마다 팔이 2개씩. GPU는 이보다 더...
	**Multi-threaded Performance (theoretical maximum)**

- Total compute capacity can be estimated by clock speed × thread count:
	CPU 1: 4.7 × 16 = 75.2 GHz-threads
	CPU 2: 3.5 × 12 = 42.0 GHz-threads
	Difference: 75.2 ÷ 42.0 = **1.79x faster (79% faster)**
* 거기에 RAM, SSD까지 성능 고려..
<!--SR:!2025-12-27,50,250-->
- 

#it일반