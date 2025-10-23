---
title: "java"
created: 2024-02-27 14:55:21
updated: 2025-10-04 13:06:43
---
## interview questions [source](https://www.geeksforgeeks.org/core-java-interview-questions-for-freshers/?ref=shm)
### 1. instance variable/[[static#1. class variable|class variable]]
- ```java
class Employee { 
	int empNo; 
	String empName, department; 
	double salary; 
	static int officePhone;  --> class variable
} 

Employee empObj1 = new Employee();  --> instance variable

# access to instance variables
empObj1.empNo

# access to class variables
Employee.officePhone
```
### 2. [[static#2. static class|static class]]
### 3. types of variables
- local
- instance
- static
### 4. String
#### 4. 1. String/StringBuilder/StringBuffer

| String                                                                                                                             | StringBuilder                        | StringBuffer                         |
| ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------------ |
| immutable                                                                                                                          | mutable                              | mutable                              |
|                                                                                                                                    | not thread-safe                      | thread-safe                          |
| Whenever we alter the content of a String object, it creates a new string and refers to that, it does not modify the existing one. | so performance is better than String | so performance is better than String |
#### 4. 2. **Current best practices:**
- Use `StringBuilder` for single-threaded string building
- Use `String.join()`, `String.format()`, or text blocks for many concatenation scenarios
- Use `StringBuffer` only when you specifically need thread-safe mutable strings
- For building/modifying strings
```java
// Inefficient - creates many String objects
String result = "";
for(int i = 0; i < 1000; i++) {
    result += "data" + i; // Creates new String each time!
}

// Efficient - modifies internal buffer
StringBuffer buffer = new StringBuffer();
for(int i = 0; i < 1000; i++) {
    buffer.append("data" + i); // Modifies existing buffer
}
```
### 5. [5- ways of object creation](https://www.geeksforgeeks.org/java/different-ways-create-objects-java/)
- new
- clone()
- deserialization
-  Using Constructor.newInstance() from Reflection API
- Using Class.forName().newInstance()
### 6. HashMap/HashTable

| HashMap                            | HashTable                        |
| ---------------------------------- | -------------------------------- |
| non-synchronized - not thread-safe | synchronized - thread-safe       |
| allow null key, null values        | not allow any null key or values |
### 7 thread safe Map
- `ConcurrentHashMap`
- `Collections.synchronizedMap()`
- Proper caching solutions like `@Cacheable`
- Bad example of shared Map
	- cache with HashMap
```java
@RestController
@RequestMapping("/api/cache")
public class BadCacheController {
    
    // BAD: Shared HashMap across all requests - NOT thread-safe!
    private Map<String, Object> cache = new HashMap<>();
    private int hitCount = 0;
    
    @GetMapping("/data/{key}")
    public ResponseEntity<?> getData(@PathVariable String key) {
        // Multiple threads accessing shared HashMap - DANGEROUS!
        Object cachedValue = cache.get(key);
        
        if (cachedValue != null) {
            hitCount++; // Race condition here too!
            return ResponseEntity.ok(cachedValue);
        }
        
        // Simulate expensive operation
        String newValue = "Computed value for " + key;
        
        // Multiple threads modifying shared HashMap - DATA CORRUPTION RISK!
        cache.put(key, newValue);
        
        return ResponseEntity.ok(newValue);
    }
    
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("cacheSize", cache.size()); // Unreliable due to race conditions
        stats.put("hitCount", hitCount);
        return ResponseEntity.ok(stats);
    }
    
    @DeleteMapping("/clear")
    public ResponseEntity<Void> clearCache() {
        // Multiple threads could be reading while this clears - CRASH RISK!
        cache.clear();
        hitCount = 0;
        return ResponseEntity.ok().build();
    }
}
```
- Good example of shared Map
	- ConcurrentHashMap
		- In RestController
```java
@RestController
@RequestMapping("/api/cache")
public class GoodCacheControllerV1 {
    
    // GOOD: Thread-safe map
    private final ConcurrentHashMap<String, Object> cache = new ConcurrentHashMap<>();
    private final AtomicInteger hitCount = new AtomicInteger(0);
    
    @GetMapping("/data/{key}")
    public ResponseEntity<?> getData(@PathVariable String key) {
        Object cachedValue = cache.get(key);
        
        if (cachedValue != null) {
            hitCount.incrementAndGet(); // Thread-safe increment
            return ResponseEntity.ok(cachedValue);
        }
        
        String newValue = "Computed value for " + key;
        
        // Thread-safe put operation
        cache.put(key, newValue);
        
        return ResponseEntity.ok(newValue);
    }
    
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        Map<String, Object> stats = new HashMap<>(); // Local variable - safe
        stats.put("cacheSize", cache.size());
        stats.put("hitCount", hitCount.get());
        return ResponseEntity.ok(stats);
    }
    
    @DeleteMapping("/clear")
    public ResponseEntity<Void> clearCache() {
        cache.clear(); // Thread-safe clear
        hitCount.set(0);
        return ResponseEntity.ok().build();
    }
}
```
		- In Service layer
```java
@RestController
@RequestMapping("/api/cache")
public class GoodCacheControllerV3 {
    
    @Autowired
    private CacheService cacheService; // State moved to service
    
    @GetMapping("/data/{key}")
    public ResponseEntity<?> getData(@PathVariable String key) {
        Object value = cacheService.getValue(key);
        return ResponseEntity.ok(value);
    }
    
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        return ResponseEntity.ok(cacheService.getStats());
    }
}

@Service
public class CacheService {
    private final ConcurrentHashMap<String, Object> cache = new ConcurrentHashMap<>();
    private final AtomicInteger hitCount = new AtomicInteger(0);
    
    public Object getValue(String key) {
        Object cachedValue = cache.get(key);
        if (cachedValue != null) {
            hitCount.incrementAndGet();
            return cachedValue;
        }
        
        String newValue = "Computed value for " + key;
        cache.put(key, newValue);
        return newValue;
    }
    
    public Map<String, Object> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("cacheSize", cache.size());
        stats.put("hitCount", hitCount.get());
        return stats;
    }
}
```
		- @Cacheable
```java
@RestController
@RequestMapping("/api/data")
public class GoodCacheControllerV2 {
    
    @Autowired
    private DataService dataService;
    
    @GetMapping("/{key}")
    public ResponseEntity<?> getData(@PathVariable String key) {
        // Spring handles caching thread-safety automatically
        String value = dataService.getComputedValue(key);
        return ResponseEntity.ok(value);
    }
    
    @DeleteMapping("/cache/clear")
    public ResponseEntity<Void> clearCache() {
        dataService.clearCache();
        return ResponseEntity.ok().build();
    }
}

@Service
public class DataService {
    
    @Cacheable("dataCache")
    public String getComputedValue(String key) {
        // Simulate expensive operation
        return "Computed value for " + key;
    }
    
    @CacheEvict(value = "dataCache", allEntries = true)
    public void clearCache() {
        // Spring handles thread-safe cache clearing
    }
}
```
### 8. wrapper classes
Wrapper classes convert the Java primitives into reference types (objects). Every primitive data type has a class dedicated to it.
### 9. Collections
java util package
used for following operations
- Searching
- Sorting
- Manipulation
- Insertion
- Deletion
### 10. Synchronization
- makes only one thread access a block of code at a time.
- keyword **synchronized**
	- a thread needs a key to access synchronized code
- object's lock
	- Every Java object has a lock. A lock has only one key.
## Collections Interview questions [source](https://www.geeksforgeeks.org/java-collections-interview-questions/?ref=shm)
### 1. For freshers
#### 1. Introduction of Collection
##### 1. 1. 2 main "root" interfaces
- java.util.Collection
- java.util.Map
- class hierachy
	![[100. media/image/DdCqh21B6l.png|800]]
##### 1. 2. Collection framework
equivalent of STL in C++
##### 1. 3. Collection Interface
- A class’s interface specifies what it should do, not how.
- This interface provides the most common methods for all collection objects that are part of the Collection Framework.
##### 1. 4. Collection class
A member of Collection Framework.
#### 2. ArrayList
        * dynamic
        * ![[100. media/image/p8EJ1buXGV.png]]
#### 3. ArrayList/Vector
![[100. media/image/EwPaWxkNs2.png]]

| ArrayList                   | Vector                   |
| --------------------------- | ------------------------ |
| Not synchronized --> faster | synchronized --> slower  |
| iterator                    | iterator and enumeration |
#### 4. the difference between iterator and enumeration
- iterator: we can apply it to any Collection object. By using an Iterator, we can perform both read and remove operations.
- enumeration: Enumeration (or enum) is a user-defined data type. It is mainly used to assign names to integral constants, the names make a program easy to read and maintain.
```java
// A simple enum example where enum is declared 
// outside any class (Note enum keyword instead of 
// class keyword) 
enum Color 
{ 
    RED, GREEN, BLUE; 
}
```
### 2. For experienced
#### 1. The difference between comparable and comparator
- two interfaces to sort objects using data members of the class

| comparable                                                   | comparator                                                    |
| ------------------------------------------------------------ | ------------------------------------------------------------- |
| The Comparable interface provides a single sorting sequence. | The Comparator interface provides multiple sorting sequences. |
| The actual class is modified by a comparable interface       | The actual class is not modified by the Comparator interface. |
| compareTo() method is used to sort elements.                 | compare() method is used to sort elements.                    |
| Comparable is present in the package java.lang               | Comparator is present in the package java.util                |
#### 2. fail-fast/fail-safe iterator
## Framework
### Spring
      * 스프링 이전에는 EJB 컨테이너(Oracle Weblogic, IBM WebSphere 등) 사용하여 구현. 
      * 배포하기 위해서는 War 파일을 생성해서 별도 웹 서버 Tomcat 등에 배포해야 해서 불편.
      * IoC Container
        * Spring IoC is achieved through Dependency Injection.
        * It gets the information about the bean(objects) from 
          * a configuration file(XML)
          * Java Code
          * Java Annotations and Java POJO class.
        * 2 types of IoC Container
          * ![[100. media/image/ueTFLNQh6Y.png]]
          * BeanFactory(**org.springframework.beans**)
            * *BeanFactory is **deprecated** from Spring 3.0.*
            * BeanFactory represents a basic ** IoC container** which is a parent interface of **ApplicationContext.**
            * BeanFactory does not support Annotation-based configuration whereas ApplicationContext does.
            * ![[100. media/image/wD06Pna7_Y.png]]
          * ApplicationContext(**org.springframework.context**)
            * ApplicationContext extends the capabilities of BeanFactory by providing additional features suitable for enterprise-level applications.
        * Main features of Spring IoC
          * creating bean(object)
          * Managing beans(objects)
          * Helping an application to be configurable
          * Managing dependencies
      * AOP ^B8_I075qT
        * [Aspect-Oriented Programming](https://www.geeksforgeeks.org/aspect-oriented-programming-and-aop-in-spring-framework/) is one way to implement Inversion of Control.
          * can be defined as the breaking of code into different modules, also known as **modularization**
            * For example- **Security** is a crosscutting concern, in many methods in an application, security rules can be applied, therefore repeating the code at every method
            * So define the functionality in **a common class and control** were to apply that functionality in the whole application.
          * Aspect
            * The class which implements the JEE application cross-cutting concerns(transaction, logger etc)
            * is a specialized class annotated with @Aspect (or configured via XML) that contains advice methods and pointcut expressions to implement cross-cutting concerns.
```java
@Aspect  // Special annotation
@Component
public class LoggingAspect {  // Specialized class
    
    @Before("execution(* com.example.*.*(..))") // Pointcut + Advice
    public void logBefore(JoinPoint joinPoint) {
        // This runs automatically, not called directly
    }
}
```
  * Weaving
            * The process of linking Aspects with an Advised Object. Spring AOP does weaving at runtime.
          * Advice
            * the action taken by the Aspect at a particular time
            * ![[100. media/image/hFxs4yZDqF.png]]
          * JointPoints
            * An application has thousands of opportunities or points to apply Advice.
          * PointCut
            * selected join point
            * specify using explicit class/method name or through regular expressions.
          * diagram
            * ![[100. media/image/8sKD94vZVs.png]]
### Springboot
      * Spring의 복잡한 설정을 자동화
      * 의존성 관리 간소화
        * 3rd party 의존성 관리를 용이하게 하기 위한 ‘starter’ 의존성 통합 모듈을 제공하여 Maven/Gradel 설정 시 버전 관리가 간편하다. 이를 통해 개발자는 버전 충돌이나 복잡한 의존성 설정에 대해 걱정하지 않고 필요한 의존성을 쉽게 지정할 수 있다.
      * 자체 웹 서버 내장(Tomcat, Jetty, Undertow) --> 독립적으로 실행 가능한 jar로 프로젝트 빌드 가능 --> 배포 용이
      * [[Spring boot]]
## JPA
    * ORM 기술 표준으로 사용되는 인터페이스 모음.
    * JPA 구현 예시
      * Entiry 정의
        * ```javascript
@Entity // 엔티티 클래스임을 선언.
@Table(name = "users") // 해당 엔티티 클래스와 매핑될 데이터베이스 테이블 이름을 지정.
public class User {

    @Id // 엔티티 클래스의 주요 식별자(primary key)임을 선언
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 엔티티의 식별자 값을 자동으로 생성
    private Long id;

    // 해당 엔티티 클래스의 필드가 데이터베이스의 칼럼으로 매핑될 때,
    // 해당 칼럼의 제약 조건을 설정하는 어노테이션입니다. (널허용 = x 등)
    @Column(nullable = false, unique = true) 
    private String username;

    @Column(nullable = false)
    private String password;

    // getters and setters
}```
      * Repository Interface 정의
        * JPARepository 상속 받아 사용.
        * ```javascript
// 해당 인터페이스가 스프링의 데이터 접근 계층(Data Access Layer)의 컴포넌트임을 선언
// 간단하게 말 하자면 "레파지토리"를 의미
@Repository
// JpaRepository<User, Long> 인터페이스 : 스프링 데이터 JPA에서 제공하는 CRUD 메서드를 상속받아 사용할 수 있는 인터페이스입니다.
public interface UserRepository extends JpaRepository<User, Long> {
	
    // 데이터베이스에서 username 필드 값이 일치하는 User 엔티티 객체를 반환하는 메서드입니다.
    Optional<User> findByUsername(String username);

}```
      * 설정
```plain
# H2 인-메모리 데이터베이스를 사용하기 위한 데이터 소스 설정(application.yml)
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA를 사용하기 위한 설정
spring.jpa.hibernate.ddl-auto=create # 애플리케이션 실행 시 엔티티를 대상으로 DDL 실행
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.H2Dialect # H2 데이터베이스 방언 지정
```
      * Service 정의
        * Repository interface를 주입 받아 사용.
```java
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    /**
     * 새로운 사용자를 생성하고, 생성된 사용자를 반환.
     * param : user 새로 생성할 사용자 정보
     * return : 생성된 사용자 정보
     */
    public User createUser(User user) {
        return userRepository.save(user);
    }

    /**
     * 주어진 사용자명(username)에 해당하는 사용자 정보를 조회.
     * param : username 조회할 사용자명
     * return 사용자 정보가 존재하는 경우 해당 정보를, 그렇지 않은 경우 null을 반환.
     */
    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    // other methods
}
```
      * Controller 정의
```java
@RestController
@RequestMapping("/users")
public class UserController {

    @Autowired
    private UserService userService;

    /**
     * 새로운 사용자를 생성하고, 생성된 사용자 정보를 반환.
     * param : user 생성할 사용자 정보
     * return : 생성된 사용자 정보
     */
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.createUser(user);
    }

    /**
     * 주어진 사용자명(username)에 해당하는 사용자 정보를 조회.
     * param : username 조회할 사용자명
     * return : 사용자 정보가 존재하는 경우 해당 정보를, 그렇지 않은 경우 null을 반환.
     */
    @GetMapping("/{username}")
    public User getUser(@PathVariable String username) {
        Optional<User> user = userService.findByUsername(username);
        if (user.isPresent()) {
            return user.get();
        } else {
            throw new UserNotFoundException(username);
        }
    }

    // other methods
}
```

## [[Enum]]
## [[record]]
## Wildcard in generic
- String이 Object를 상속하더라도 generic에서 Box\<Object>와 Box\<String>은 상속관계 형성 X
- 제네릭 메소드와 와일드카드 기반 메소드는 상호 대체 가능하지만 와일드카드 기반 메소드가 간결하기 때문에 선호.
```java
// generic method
public static <T> void peekBox(Box<T> box) {
  System.out.println(box);
}

// wildcard based method
public static void peekBox(Box<?> box) {
  System.out.println(box);
}
```
- 상한 제한(Upper-Bounded)
	- box는 Box\<T> 인스턴스를 참조하는 참조변수
	- Box\<T>의 T는 Number 또는 이를 상속하는 하위 클래스
```java
Box <? extends Number> box
```
- 하한 제한(Low-Bounded)
	- Box\<Integer>, Box\<Number>, Box\<Object>만 가능.
```java
Box <? super Integer> box
```

## Inner class - Static? Non Static?
    * Static
      * logically grouped but maintain independence.
      * When an Inner class doesn't need to access outer class instance and exist independently.
      * helper, builders, factories.
      * Builder Pattern
        * private constructor + public static Builder inner class + 두 클래스 둘 다 동일한 속성 소유.
```java
public class Car {
    private final String brand;
    private final String model;
    private final int year;
    private final String color;
    private final boolean isElectric;
    
    // Private constructor
    private Car(CarBuilder builder) {
        this.brand = builder.brand;
        this.model = builder.model;
        this.year = builder.year;
        this.color = builder.color;
        this.isElectric = builder.isElectric;
    }
    
    // Static inner class - Builder
    public static class CarBuilder {
        private String brand;
        private String model;
        private int year;
        private String color = "White"; // default
        private boolean isElectric = false; // default
        
        public CarBuilder(String brand, String model, int year) {
            this.brand = brand;
            this.model = model;
            this.year = year;
        }
        
        public CarBuilder color(String color) {
            this.color = color;
            return this;
        }
        
        public CarBuilder electric(boolean isElectric) {
            this.isElectric = isElectric;
            return this;
        }
        
        public Car build() {
            return new Car(this);
        }
    }
}

// Usage:
Car tesla = new Car.CarBuilder("Tesla", "Model 3", 2023)
    .color("Red")
    .electric(true)
    .build();
```
      * HTTP Response with Status code
```java
public class HttpResponse {
    private final StatusCode status;
    private final String body;
    private final Map<String, String> headers;
    
    public HttpResponse(StatusCode status, String body) {
        this.status = status;
        this.body = body;
        this.headers = new HashMap<>();
    }
    
    // Static inner class for HTTP Status Codes
    public static class StatusCode {
        public static final StatusCode OK = new StatusCode(200, "OK");
        public static final StatusCode CREATED = new StatusCode(201, "Created");
        public static final StatusCode BAD_REQUEST = new StatusCode(400, "Bad Request");
        public static final StatusCode UNAUTHORIZED = new StatusCode(401, "Unauthorized");
        public static final StatusCode FORBIDDEN = new StatusCode(403, "Forbidden");
        public static final StatusCode NOT_FOUND = new StatusCode(404, "Not Found");
        public static final StatusCode INTERNAL_ERROR = new StatusCode(500, "Internal Server Error");
        
        private final int code;
        private final String message;
        
        private StatusCode(int code, String message) {
            this.code = code;
            this.message = message;
        }
        
        public int getCode() { return code; }
        public String getMessage() { return message; }
        
        public boolean isSuccess() { return code >= 200 && code < 300; }
        public boolean isClientError() { return code >= 400 && code < 500; }
        public boolean isServerError() { return code >= 500 && code < 600; }
        
        @Override
        public String toString() {
            return code + " " + message;
        }
    }
    
    public StatusCode getStatus() { return status; }
    public String getBody() { return body; }
    
    public void addHeader(String key, String value) {
        headers.put(key, value);
    }
}

// Usage:
HttpResponse response = new HttpResponse(HttpResponse.StatusCode.OK, "Success!");

if (response.getStatus().isSuccess()) {
    System.out.println("Request successful: " + response.getStatus());
} else {
    System.out.println("Request failed: " + response.getStatus());
}

// You can use status codes independently
HttpResponse.StatusCode notFound = HttpResponse.StatusCode.NOT_FOUND;
System.out.println("Error code: " + notFound.getCode());
```
      * Orders with Status code
```java
public class Order {
    private final String orderId;
    private final String customerId;
    private final List<OrderItem> items;
    private final OrderStatus status;
    private final PaymentInfo payment;
    private final ShippingAddress address;
    
    public Order(String customerId, PaymentInfo payment, ShippingAddress address) {
        this.orderId = generateOrderId();
        this.customerId = customerId;
        this.items = new ArrayList<>();
        this.status = OrderStatus.PENDING;
        this.payment = payment;
        this.address = address;
    }
    
    // Static inner class - Order Status
    public static class OrderStatus {
        public static final OrderStatus PENDING = new OrderStatus("PENDING", "Order received, processing payment");
        public static final OrderStatus CONFIRMED = new OrderStatus("CONFIRMED", "Payment confirmed, preparing items");
        public static final OrderStatus SHIPPED = new OrderStatus("SHIPPED", "Order shipped to customer");
        public static final OrderStatus DELIVERED = new OrderStatus("DELIVERED", "Order delivered successfully");
        public static final OrderStatus CANCELLED = new OrderStatus("CANCELLED", "Order cancelled by customer or system");
        public static final OrderStatus REFUNDED = new OrderStatus("REFUNDED", "Order refunded to customer");
        
        private final String code;
        private final String description;
        
        private OrderStatus(String code, String description) {
            this.code = code;
            this.description = description;
        }
        
        public String getCode() { return code; }
        public String getDescription() { return description; }
        
        public boolean canBeCancelled() {
            return this == PENDING || this == CONFIRMED;
        }
        
        public boolean isCompleted() {
            return this == DELIVERED || this == CANCELLED || this == REFUNDED;
        }
    }
    
    // Static inner class - Payment Information
    public static class PaymentInfo {
        private final String paymentMethod; // "CREDIT_CARD", "PAYPAL", "BANK_TRANSFER"
        private final String paymentId;
        private final double amount;
        private final String currency;
        
        public PaymentInfo(String paymentMethod, String paymentId, double amount, String currency) {
            this.paymentMethod = paymentMethod;
            this.paymentId = paymentId;
            this.amount = amount;
            this.currency = currency;
        }
        
        // Getters...
        public String getPaymentMethod() { return paymentMethod; }
        public double getAmount() { return amount; }
        public String getCurrency() { return currency; }
    }
    
    // Static inner class - Shipping Address
    public static class ShippingAddress {
        private final String recipientName;
        private final String street;
        private final String city;
        private final String zipCode;
        private final String country;
        
        public ShippingAddress(String recipientName, String street, String city, String zipCode, String country) {
            this.recipientName = recipientName;
            this.street = street;
            this.city = city;
            this.zipCode = zipCode;
            this.country = country;
        }
        
        // Getters...
    }
}

// Usage in business context:
Order.PaymentInfo payment = new Order.PaymentInfo("CREDIT_CARD", "pay_12345", 299.99, "USD");
Order.ShippingAddress address = new Order.ShippingAddress(
    "John Smith", "123 Main St", "New York", "10001", "USA");

Order customerOrder = new Order("customer_789", payment, address);

// Check order status
if (customerOrder.getStatus().canBeCancelled()) {
    System.out.println("Customer can still cancel this order");
}
```
      * Employee with Department
```java
public class Employee {
    private final String employeeId;
    private final String firstName;
    private final String lastName;
    private final Department department;
    private final Position position;
    private final ContactInfo contact;
    private double salary;
    
    public Employee(String firstName, String lastName, Department department, Position position) {
        this.employeeId = generateEmployeeId();
        this.firstName = firstName;
        this.lastName = lastName;
        this.department = department;
        this.position = position;
    }
    
    // Static inner class - Department
    public static class Department {
        public static final Department SALES = new Department("SALES", "Sales & Marketing", "John Manager");
        public static final Department ENGINEERING = new Department("ENG", "Engineering", "Sarah CTO");
        public static final Department HR = new Department("HR", "Human Resources", "Mike Director");
        public static final Department FINANCE = new Department("FIN", "Finance & Accounting", "Lisa CFO");
        
        private final String code;
        private final String fullName;
        private final String manager;
        
        private Department(String code, String fullName, String manager) {
            this.code = code;
            this.fullName = fullName;
            this.manager = manager;
        }
        
        public String getCode() { return code; }
        public String getFullName() { return fullName; }
        public String getManager() { return manager; }
    }
    
    // Static inner class - Job Position
    public static class Position {
        public static final Position INTERN = new Position("Intern", 1, 25000, 40000);
        public static final Position JUNIOR = new Position("Junior", 2, 40000, 65000);
        public static final Position SENIOR = new Position("Senior", 3, 65000, 100000);
        public static final Position LEAD = new Position("Lead", 4, 90000, 130000);
        public static final Position MANAGER = new Position("Manager", 5, 100000, 150000);
        
        private final String title;
        private final int level;
        private final double minSalary;
        private final double maxSalary;
        
        private Position(String title, int level, double minSalary, double maxSalary) {
            this.title = title;
            this.level = level;
            this.minSalary = minSalary;
            this.maxSalary = maxSalary;
        }
        
        public boolean isEligibleForPromotion(Position targetPosition) {
            return targetPosition.level == this.level + 1;
        }
        
        public boolean isSalaryInRange(double salary) {
            return salary >= minSalary && salary <= maxSalary;
        }
        
        // Getters...
    }
    
    // Static inner class - Contact Information  
    public static class ContactInfo {
        private final String email;
        private final String phoneNumber;
        private final String emergencyContact;
        
        public ContactInfo(String email, String phoneNumber, String emergencyContact) {
            this.email = email;
            this.phoneNumber = phoneNumber;
            this.emergencyContact = emergencyContact;
        }
        
        // Getters...
    }
}

// Business usage:
Employee developer = new Employee("Alice", "Johnson", 
    Employee.Department.ENGINEERING, Employee.Position.SENIOR);

// HR can check salary ranges
if (Employee.Position.SENIOR.isSalaryInRange(75000)) {
    System.out.println("Salary is within range for Senior position");
}

// Check promotion eligibility
if (developer.getPosition().isEligibleForPromotion(Employee.Position.LEAD)) {
    System.out.println("Alice is eligible for promotion to Lead");
}
```
      * Configuration classes
```java
public class DatabaseConnection {
    private final Config config;
    private Connection connection;
    
    public DatabaseConnection(Config config) {
        this.config = config;
    }
    
    // Static inner class for configuration
    public static class Config {
        private String host = "localhost";
        private int port = 5432;
        private String database;
        private String username;
        private String password;
        private int maxConnections = 10;
        private int timeoutSeconds = 30;
        
        public Config(String database, String username, String password) {
            this.database = database;
            this.username = username;
            this.password = password;
        }
        
        public Config host(String host) {
            this.host = host;
            return this;
        }
        
        public Config port(int port) {
            this.port = port;
            return this;
        }
        
        public Config maxConnections(int maxConnections) {
            this.maxConnections = maxConnections;
            return this;
        }
        
        public Config timeout(int timeoutSeconds) {
            this.timeoutSeconds = timeoutSeconds;
            return this;
        }
        
        // Getters
        public String getHost() { return host; }
        public int getPort() { return port; }
        public String getDatabase() { return database; }
        public String getUsername() { return username; }
        public String getPassword() { return password; }
        public int getMaxConnections() { return maxConnections; }
        public int getTimeoutSeconds() { return timeoutSeconds; }
    }
    
    public void connect() {
        String url = String.format("jdbc:postgresql://%s:%d/%s", 
            config.getHost(), config.getPort(), config.getDatabase());
        // Connection logic here
        System.out.println("Connecting to: " + url);
    }
}

// Usage:
DatabaseConnection.Config config = new DatabaseConnection.Config(
    "myapp_db", "admin", "password123")
    .host("db.company.com")
    .port(5433)
    .maxConnections(20)
    .timeout(60);

DatabaseConnection db = new DatabaseConnection(config);
db.connect();
```
      * Bank account and Transactions
```java
public class BankAccount {
    private double balance;
    private String accountNumber;
    
    // Non-static - needs access to outer class fields
    public class Transaction {
        private double amount;
        private String type;
        
        public void execute() {
            // Can directly access outer class fields!
            balance += amount;  // This is why it's non-static
            System.out.println("Account " + accountNumber + " balance: " + balance);
        }
    }
    
    public Transaction createDeposit(double amount) {
        Transaction t = new Transaction();
        t.amount = amount;
        t.type = "DEPOSIT";
        return t;
    }
}
```
      * helper: Calculator
```java
public class Calculator {
    
    // Static - just a helper class, doesn't need Calculator's fields
    public static class MathUtils {
        public static double square(double x) {
            return x * x;
        }
    }
}

// Usage:
Calculator.MathUtils.square(5); // Can use without Calculator instance
```
    * Non Static
      * When an Inner class needs direct access to the outer class' instance variables.
      * potential memory leak if not careful.
      * Iterator Pattern
```java
public class CustomArrayList<T> {
    private Object[] elements;
    private int size = 0;
    private static final int DEFAULT_CAPACITY = 10;
    
    public CustomArrayList() {
        elements = new Object[DEFAULT_CAPACITY];
    }
    
    public void add(T element) {
        if (size >= elements.length) {
            resize();
        }
        elements[size++] = element;
    }
    
    @SuppressWarnings("unchecked")
    public T get(int index) {
        if (index >= size) throw new IndexOutOfBoundsException();
        return (T) elements[index];
    }
    
    public int size() {
        return size;
    }
    
    // Non-static inner class - Iterator
    public class ArrayListIterator implements Iterator<T> {
        private int currentIndex = 0;
        
        @Override
        public boolean hasNext() {
            return currentIndex < size; // Accessing outer class's 'size' field
        }
        
        @Override
        @SuppressWarnings("unchecked")
        public T next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            return (T) elements[currentIndex++]; // Accessing outer class's 'elements'
        }
    }
    
    public Iterator<T> iterator() {
        return new ArrayListIterator();
    }
    
    private void resize() {
        elements = Arrays.copyOf(elements, elements.length * 2);
    }
}

// Usage:
CustomArrayList<String> list = new CustomArrayList<>();
list.add("Hello");
list.add("World");

Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    System.out.println(iter.next());
}
```

## programming skill
    * Utility pattern #memo ^Y86uDWxo_
      * Utility, Math, StringUtils, etc.
      * Similar to `Math.max()`, `Collections.sort()`, etc.
      * 구현
        * 1. `private` 생성자 선언: `public` 클래스의 생성자를 `private`으로 선언
        * 2. `static` 메서드 사용: 모든 유틸리티 기능을 `static` 메서드로 정의.
        * 3. `final` 클래스 선언:
```java
public final class StringUtils {
    private StringUtils() {
        // This prevents instantiation even through reflection, making the restriction more robust.
        throw new UnsupportedOperationException("Utility class");
    }

    public static boolean isNullOrBlank(String str) {
        return str == null || str.trim().isEmpty();
    }
}
```
      * 실제코드
        * ErrorAssert.java
```java
package kr.or.cbdc.infrastructure.framework.core.foundation.exception;

import org.springframework.lang.Nullable;
import org.springframework.util.CollectionUtils;
import org.springframework.util.ObjectUtils;
import org.springframework.util.StringUtils;
import java.util.Collection;
import java.util.Objects;

public final class ErrorAssert {

    private ErrorAssert() {
        // 유틸리티 클래스는 인스턴스화할 수 없음
    }

    /**
     * 조건이 참이 아니면 BizException을 던짐
     *
     * @param expression 검증할 조건
     * @param errorCode  실패 시 던질 ErrorCode 객체
     */
    public static void isTrue(boolean expression, ErrorCode errorCode, Object... args) {
        if (!expression) {
            throw new InputParamException(errorCode, null,args);
        }
    }

    /**
     * 객체가 null이 아니어야 함. null이면 InputParamException 던짐
     *
     * @param object    검증할 객체
     * @param errorCode 실패 시 던질 ErrorCode 객체
     */
    public static void notNull(Object object, ErrorCode errorCode, Object... args) {
        if (object == null) {
            throw new InputParamException(errorCode,null, args);
        }
    }

    /**
     * Assert that an object is {@code null}.
     *
     */
    public static void isNull(@Nullable Object object, ErrorCode errorCode, Object... args) {
        if (object != null) {
            throw new InputParamException(errorCode,null, args);
        }
    }

    public static void hasLength(@Nullable String text, ErrorCode errorCode, Object... args) {
        if (!StringUtils.hasLength(text)) {
            throw new InputParamException(errorCode,null, args);
        }
    }

    /**
     * 문자열이 비어있으면 InputParamException 던짐
     *
     * @param text      검증할 문자열
     * @param errorCode 실패 시 던질 ErrorCode 객체
     */
    public static void notEmpty(String text, ErrorCode errorCode, Object... args) {
        if (text == null || text.trim().isEmpty()) {
            throw new InputParamException(errorCode,null, args);
        }
    }

    public static void notEmpty(@Nullable Object[] array, ErrorCode errorCode, Object... args) {
        if (ObjectUtils.isEmpty(array)) {
            throw new InputParamException(errorCode,null,args);
        }
    }

    public static void notEmpty(@Nullable Collection<?> collection,ErrorCode errorCode, Object... args) {
        if (CollectionUtils.isEmpty(collection)) {
            throw new InputParamException(errorCode,null,args);
        }
    }

    /**
     * 두 객체가 동일한지 확인합니다. 다르면 BizException을 던집니다.
     *
     * @param expected 기대되는 값
     * @param actual 실제 값
     * @param errorCode 에러 코드
     * @param args 메시지 포맷에 필요한 인수 (필요 없는 경우 제공하지 않음)
     */
    public static void equals(Object expected, Object actual, ErrorCode errorCode, Object... args) {
        if (!Objects.equals(expected, actual)) {
            throw new BizException(errorCode,null, args);
        }
    }

    /**
     * 숫자가 0 이상이어야 함. 그렇지 않으면 BizException을 던짐
     *
     * @param number    검증할 숫자
     * @param errorCode 실패 시 던질 ErrorCode 객체
     */
    public static void isPositive(int number, ErrorCode errorCode) {
        if (number <= 0) {
            throw new BizException(errorCode);
        }
    }

}
```
    * validate input by annotation #memo ^qDyBo0wo0
      * RULE 1: Data classes (User, Address) don't need @Validated
        * They just define what constraints exist
        * @Valid on fields enables nested validation
      * RULE 2: Service/Controller classes need @Validated to enable validation infrastructure
        * Without @Validated: parameter constraints are ignored
      * RULE 3: @Valid works everywhere for object validation
        * Validates the entire object and its nested objects
        * Works whether the class has @Validated or not
      * RULE 4: Parameter validation (like @NotNull @Positive Long id) only works if:
        * The containing class has @Validated annotation
        * Spring AOP can intercept the method call
      * PRACTICAL DECISION TREE:
        * Validating an entire object? → Use @Valid
        * Validating individual parameters (primitives)? → Use @Validated on class + constraints on parameters
        * Need validation groups? → Use @Validated
        * Need nested object validation? → Use @Valid on the field/paramete__