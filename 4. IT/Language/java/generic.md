## generic 기반 클래스 정의
?

| 타입 매개변수(Type parameter)                     | T           | 인스턴스 생성 시 자료형을 결정하는 표식                                         |
| ------------------------------------------- | ----------- | -------------------------------------------------------------- |
| 타입 인자(Type argument)                        | Apple       | 기본 자료형 int는 안 되지만 Integer는 가능                                  |
| 매개변수화 타입(Parameterized Type) - Generic Type | Box\<Apple> | Box\<Apple>이라는 새로운 자료형이 완성. 이후 이것도 **타입**이기 때문에 일반 타입처럼 이용 가능. |

### 클래스 이름 뒤에 \<T>를  붙인다.
```java
class Box<T> {
	private T ob;
	public void set(T o) {
		ob = o;
	}
	public T get() {
		return ob;
	}
}
or
@Data
class Box<T> {
	private T item; // or 'contents' -> generates getItem()/setItem()
}

Box<Apple> aBox = new Box<Apple>(); 
Box<Apple> aBox = new Box<>();       # 참조변수 선언에서 유추
```
위 코드는 상자에 무엇을 담는다는 개념을 함수명과 변수명을 명확히 표현하지 않아서 사과가 마치 상자의 속성처럼 보임. 아래 코드는 이를 개선했지만 lombok을 포기해야 하는 문제가 있지만 요즘 AI의 autocomplete를 쓰면 간단히 해결된다. -> 따라서 요즘은 lombok을 안 써도 되긴 하다.
```java
class Box<T> {
	private T contents;
	public void put(T item) {
		contents = item;
	}
	public T take() {
		return contents;
	}
}
Box<Apple> aBox = new Box<Apple>();
aBox.put(new Apple());
Apple apple = aBox.take();
```
<!--SR:!2025-11-16,13,230-->
-

## generic and lombok
일반적으로 lombok은 제네릭 클래스에 대해서 큰 문제는 없다. 
- 다만, "@Builder" 또는 "@SuperBuilder"를 이용할 때나 
- chained method call에서 type inference가 제대로 안 될 수도 있다는 것을 유념해야.

## generic 클래스 타입 인자 제한(지정, 한정)
?
### 1. class 상속으로 제한
제네릭 클래스 정의 시, 타입 인자(parameter)가 클래스 상속
```java
class Box<T extends Number> {
...
}
```
### 2. interface 상속으로 제한
제네릭 클래스 정의 시, 타입 인자(parameter)가 인터페이스 상속
```java
class Box<T extends Eatable> {
	T ob;
	
	public T get() {
		System.out.println(ob.eat())
		retur ob;
	}
}

interface Eatable {
	public String eat();
}

class Apple implements Eatable {
	@Override
	public String eat() {
		return "I eat Apple";
	}
}
```
### 3. 복합 상속
```java
class Box<T extends Number & Eatable> {...}
```
<!--SR:!2025-11-06,3,210-->
-

## generic 메소드 정의
?
### static 유무에 상관없이 인스턴스, 클래스 메소드 정의 가능
```java
class BoxFactory {
	public static <T> Box<T> makeBox(T o) {
		Box<T> box = new Box<T>(); // 상자 생성
		box.set(o);                // 전달된 인자 인스턴스를 상자에 담기
		return box;                // 상자 반환
	}
}

class Unboxer {
	public static <T> T openBox(Box<T> box) {
		return box.get();
	}
}
```
### 호출
메소드 호출 시, 자료형 결정.
```java
Box<String> sBox = BoxFactory.<String>makeBox("Sweet");
```
- 생각할 것
	- 단순화한 호출 -> BoxFactory.makeBox("Sweet") 참조 변수 타입으로 유추 가능. 즉 target type으로 input type 유추.
	- 클래스처럼 타입 인자 제한 가능
		- public static \<T extends Number> T openBox(Box\<T> box) {...}
<!--SR:!2025-11-16,13,230-->
-

## generic class 상속
?
```java
class SteelBox<T> extends Box<T> {...}
```
- 생각할 것
	- 상속 관계 덕분에 Box\<T> 타입 참조변수에  SteelBox\<T> 인스턴스 저장 가능.
<!--SR:!2025-11-06,3,210-->
-

## wild card 기반 메소드 정의
?
서로 동일하지만 wildcard 사용하는 것이 간결.
```java
public static <T> void peekBox(<Box<T> box) {...}

public static void peekBox(<Box<?> box) {...}
```
<!--SR:!2025-11-06,3,210-->
-

## 상한 제한(Upper-Bounded) wildcard
?
### 1. 가능 범위
	Box\<? extends Number> Box: T는 Number 또는 이를 상속하는 하위 클래스만 가능
	--> Number, Integer, Double 등.
### 2. 언제 도입?
	- **get형 메소드 정의**할 때 사용. 꺼내는 작업만 허용 즉, get 메소드 안에서 set 메소드를 호출할 수 없게
```java
public static void outBox(Box<? extends Toy> box) {
	Toy t = box.get();
	// box.set(new Toy()) 컴파일 에러!
}

# Real product code
// Real scenario: A pet shop system
public class PetShop {
    public void feedAllPets(List<? extends Animal> animals) {
        for (Animal animal : animals) {
            animal.eat();  // Can call Animal methods safely
        }
    }
}

// Usage - same method works with different lists
PetShop shop = new PetShop();
shop.feedAllPets(Arrays.asList(new Dog(), new Cat()));
shop.feedAllPets(Arrays.asList(new Bird(), new Fish()));
shop.feedAllPets(Arrays.asList(new Animal(), new Animal()));
```
### 3. 의미
Toy를 상속한 Car는 Toy 타입에 저장 가능하지만, 반대 방향으로, Car에 Toy 타입 저장하는 것은 불가
<!--SR:!2025-11-16,13,230-->
-

## 하한 제한(Lower-Bounded) wildcard
?
### 1. 가능 범위
	Box\<?  super Integer> box -> T는 Integer 또는 Integer가 상속하는 상위 클래스
	--> Integer, Number, Object
### 2. 언제 도입?
	- **set형 메소드 정의**할 때 사용. 저장만 허용 즉, set 메소드 안에서 get 메소드를 호출할 수 없게
```java
public static void inBox(Box<? super Toy> box, Toy n) {
	box.set(n)
	//Toy myToy = box.get() 컴파일 에러!
}

# Event manager
// Real scenario: Event system that accepts different listener types
public class EventManager {
    private List<EventListener> listeners = new ArrayList<>();
    
    // Lower bound: accepts EventListener or ANY supertype of EventListener
    public void addListener(List<? super EventListener> listenerList) {
        listeners.addAll(listenerList);
    }
    
    public void fireEvent(Event event) {
        for (EventListener listener : listeners) {
            listener.onEvent(event);
        }
    }
}

// Usage - you can pass lists of parent types
EventManager manager = new EventManager();
List<Object> generalList = new ArrayList<>();
generalList.add(new EventListener() {
    public void onEvent(Event e) { /* ... */ }
});
manager.addListener(generalList);  // Works! Object is supertype of EventListener
```
### 3. 의미
Toy가 상속하는 플라스틱에 Toy 타입 저장 가능하지만, 반대 방향으로, Toy 타입에 플라스틱 저장하는 것은 불가
<!--SR:!2025-11-16,13,230-->
-

## 타입 매개변수 T를 상속, overloading을 위해?
?
generic 이전 버전과 호환을 위해 컴파일러는 generic과 와일드카드 정보 지움.(Type Erasure)
```java
public static void outBox(Box<? extends Toy> box) {...}
public static void outBox(Box<? extends Robot> box) {...}
# 위 overloading된 두 함수는 컴파일 후 동일할 함수로 바뀜. overloading이 인정되지 않는다.
-->
public static <T> void outBox(Box<? extends T> box) {...}
```

하지만, 다음은 overloading 인정. 2번째 인자 타입 때문.
```java
public static void inBox(Box<? super Toy> box, Toy n) {...}
public static void inBox(Box<? super Robot> box, robot n) {...}
```

inBox만 오버로딩된다고 해결되는 것이 아니기 때문에 다음과 같이 Box\<Toy> 인스턴스와 Box\<Robot> 인스턴스가 동시에 허용되는 정의를 사용.
```java
public static <T> void outBox(Box<? extends T> box) {...}
public static <T> void inBox(Box<? super T> box, T n) {...}
```
<!--SR:!2025-11-06,3,210-->
-

## generic 인터페이스
?
```java
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
<!--SR:!2025-11-07,2,190-->
-

#java