## generic 기반 클래스 정의
?

| 타입 매개변수(Type parameter)                     | T           | 인스턴스 생성 시 자료형을 결정하는 표식                                     |
| ------------------------------------------- | ----------- | ---------------------------------------------------------- |
| 타입 인자(Type argument)                        | Apple       | 기본 자료형 int는 안 되지만 Integer는 가능                              |
| 매개변수화 타입(Parameterized Type) - Generic Type | Box\<Apple> | Box\<Apple>이라는 새로운 자료형이 완성. 이후 이것도 타입이기 때문에 일반 타입처럼 이용 가능. |

### 클래스 이름 뒤에 \<T>를  붙인다.
```
class Box<T> {
	private T ob;
	public void set(T o) {
		ob = o;
	}
	public T get() {
		return ob;
	}
}

Box<Apple> aBox = new Box<Apple>(); 
Box<Apple> aBox = new Box<>();       # 참조변수 선언에서 유추
```
- 생각할 것
	- 새로운 타입 생성
<!--SR:!2025-10-27,3,250-->
-

## generic 클래스 타입 인자 제한
?
### 1. class 상속으로 제한
```
class Box<T extends Number> {
...
}
```
### 2. interface 상속으로 제한
```
interface Eatable {
	public String eat();
}

class Apple implements Eatable {
	@Override
	public String eat() {
		return "I eat Apple";
	}
}

class Box<T extends Eatable> {
	T ob;
	
	public T get() {
		System.out.println(ob.eat())
		retur ob;
	}
}
```
### 3. 복합 상속
```
class Box<T extends Number & Eatable> {...}
```
- 생각할 것
	- 상속함으로써 얻는 효과
<!--SR:!2025-10-27,3,250-->
-

## generic 메소드 정의
?
### static 유무에 상관없이 정의 가능
```
class BoxFactory {
	public static <T> Box<T> makeBox(T o) {
		Box<T> box = new Box<T>(); // 상자 생성
		box.set(o);                // 전달된 인자 인스턴스를 상자에 담기
		return box;                // 상자 반환
	}
}
```
### 호출
```
Box<String> sBox = BoxFactory.<String>makeBox("Sweet");
```
- 생각할 것
	- 단순화한 호출 -> BoxFactory.makeBox("Sweet") 참조 변수 타입으로 유추 가능. 즉 target type으로 input type 유추.
	- 클래스처럼 타입 인자 제한 가능
		- public static \<T extends Number> T openBox(Box\<T> box) {...}
<!--SR:!2025-10-27,3,250-->
-

## generic class 상속
?
```
class SteelBox<T> extends Box<T> {...}
```
- 생각할 것
	- 상속 관계 덕분에 Box\<T> 타입 참조변수에  SteelBox\<T> 인스턴스 저장 가능.
<!--SR:!2025-10-27,3,250-->
-

## wild card 기반 메소드 정의
?
서로 동일하지만 wildcard 사용하는 것이 간결.
```
public static <T> void peekBox(<Box<T> box) {...}

public static void peekBox(<Box<?> box) {...}
```
<!--SR:!2025-10-27,3,250-->
-

## 상한 제한(Upper-Bounded) wildcard
?
### 1. 가능 범위
	Box\<? extends Number> Box: T는 Number 또는 이를 상속하는 하위 클래스만 가능
	--> Number, Integer, Double 등.
### 2. 언제 도입?
	- **get형 메소드 정의**할 때 사용. 꺼내는 작업만 허용 즉, get 메소드 안에서 set 메소드를 호출할 수 없게
```
public static void outBox(Box<? extends Toy> box) {
	Toy t = box.get();
	// box.set(new Toy()) 컴파일 에러!
}
```
### 3. 의미
Toy를 상속한 Car는 Toy 타입에 저장 가능하지만, 반대 방향으로, Car에 Toy 타입 저장하는 것은 불가
<!--SR:!2025-10-27,3,250-->
-

## 하한 제한(Lower-Bounded) wildcard
?
### 1. 가능 범위
	Box\<?  super Integer> Box -> T는 Integer 또는 Integer가 상속하는 상위 클래스
	--> Integer, Number, Object
### 2. 언제 도입?
	- **set형 메소드 정의**할 때 사용. 저장만 허용 즉, set 메소드 안에서 get 메소드를 호출할 수 없게
```
public static void inBox(Box<? super Toy> box, Toy n) {
	box.set(n)
	//Toy myToy = box.get() 컴파일 에러!
}
```
### 3. 의미
Toy가 상속하는 플라스틱에 Toy 타입 저장 가능하지만, 반대 방향으로, Toy 타입에 플라스틱 저장하는 것은 불가
<!--SR:!2025-10-27,3,250-->
-

## 타입 매개변수 T를 상속?
?
generic 이전 버전과 호환을 위해 컴파일러는 generic과 와이드카드 정보 지움.(Type Erasure)
```
public static void outBox(Box<? extends Toy> box) {...}
public static void outBox(Box<? extends Robot> box) {...}
# 위 overloading된 두 함수는 컴파일 후 동일할 함수로 바뀜.
```

이를 해결하기 위해 제네릭 메소드 정의 이용
```
public static <T> void outBox(Box<? extends T> box) {...}
public static <T> void inBox(Box<? super T> box) {...}
```
<!--SR:!2025-10-27,3,250-->
-

## generic 인터페이스
?
```
interface Getable<T> {
	public T get();
}

class Box<T> implements Getable<T> {

	@Override
	public T get() {
		return ob;
	}
}
```
<!--SR:!2025-10-27,3,250-->
-

#java