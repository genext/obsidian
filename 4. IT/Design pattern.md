---
title: "Design pattern"
created: 2023-10-26 12:08:32
updated: 2025-09-22 17:04:04
---
## 참고 사이트
- [ ] https://patterns-dev-kr.github.io/ <-- https://www.patterns.dev/ 이 사이트 정리
 - https://blog.carlosrojas.dev/quick-reference-guide-to-design-patterns-in-js-1ebeb1e1c605
## 그림
![[100. media/image/dVCwOMtguu.png]]
![[100. media/image/qeNPXcbJKF.png]]
## 1. Creational
### 1. 1 Singleton
#### javascript
- [source](https://blog.carlosrojas.dev/quick-reference-guide-to-design-patterns-in-js-1ebeb1e1c605)
- javascript는 java, c++과 달리 따로 instance 생성하는 것이 없다. 그냥 new 하면 알아서 오브젝트가 생성됨.
- javascript에서 전역 변수를 사용하는 것이 일반적이지 않고 React 같은 것은 전역 참조할 데이터는 상태 관리 라이브러리 redux나 react context를 사용해서 관리한다.
```javascript
// ES6
class Animal {
  constructor() {
    if (typeof Animal.instance === 'object') {
      return Animal.instance;
    }

    Animal.instance = this;

    return this;
  }
}

export default Animal;```
- 사용 예
```javascript
import Animal from './Animal'; // Assuming the Animal class is in a file named Animal.js

const animal1 = new Animal();
const animal2 = new Animal();

console.log(animal1 === animal2); // Should print true
```
#### java
- lazy initialization
```java
public class Singleton {
    // Private static variable to hold the single instance of Singleton
    private static Singleton instance;

    // Private constructor to prevent instantiation from outside the class
    private Singleton() {}

    // Public static method to get the instance of Singleton
    public static Singleton getInstance() {
        // Lazy initialization: create the instance only when needed
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }

    // Example method of the Singleton class
    public void doSomething() {
        System.out.println("Singleton is doing something!");
    }

    public static void main(String[] args) {
        // Get the instance of Singleton
        Singleton singleton = Singleton.getInstance();

        // Use the Singleton object
        singleton.doSomething();
    }
}
```
#### c++
- initialized before main
```c++
#include <iostream>

class Singleton {
public:
    // Static member function to get the instance of Singleton
    static Singleton& getInstance() {
        static Singleton instance; // Static instance of Singleton
        return instance;
    }

    // Delete the copy constructor and assignment operator
    Singleton(const Singleton&) = delete;
    void operator=(const Singleton&) = delete;

    // Example method of the Singleton class
    void doSomething() {
        std:cout << "Singleton is doing something!" << std::endl;
    }

private:
    // Private constructor to prevent instantiation
    Singleton() {}
};

int main() {
    // Get the instance of Singleton
    Singleton& singleton = Singleton::getInstance();

    // Use the Singleton object
    singleton.doSomething();

    return 0;
}
```
- lazy initialization
```c++
#include <iostream>

class Singleton {
public:
    // Public static method to get the instance of Singleton
    static Singleton& getInstance() {
        // Check if the instance has been initialized
        if (instance == nullptr) {
            // If not initialized, create a new instance
            instance = new Singleton();
        }
        // Return the instance
        return *instance;
    }

    // Example method of the Singleton class
    void doSomething() {
        std:cout << "Singleton is doing something!" << std::endl;
    }

private:
    // Private constructor to prevent instantiation
    Singleton() {}

    // Private static variable to hold the single instance of Singleton
    static Singleton* instance;
};

// Initialize the static member variable
Singleton* Singleton::instance = nullptr;

int main() {
    // Get the instance of Singleton
    Singleton& singleton = Singleton::getInstance();

    // Use the Singleton object
    singleton.doSomething();

    return 0;
}
```
### 1. 2 Prototype
#### javascript
[ ] Use this pattern when you only can instantiate classes in runtime. (*practical examples are needed*)
```javascript
class Fruit {
  constructor(name, weight) {
    this.name = name;
    this.weight = weight;
  }

  clone() {
    return new Fruit(this.name, this.weight);
  }
}

export default Fruit;
```
#### java
#### c++
### 1.3 Factory
#### javascript
Use this pattern when you want a subclass to decide what object to create???
![[100. media/image/YU_9kf2PRA.png]]
```javascript
class MovieFactory {
  create(genre) {
    if (genre == 'Adventure') return new Movie(genre, 10000);
    if (genre == 'Action') return Movie(genre, 11000)
  }
}

class Movie {
  constructor(type, price) {
    this.type = type;
    this.price = price;
  }
}

export default MovieFactory;
```
#### java
#### c++
### 1.4 Abstract Factory
#### javascript
![[100. media/image/vQv_RJuqMJ.png]]
```javascript
function foodProducer(kind) {
  if (kind == 'protein') return proteinPattern;
  if (kind == 'fat') return fatPattern;
  return carbohydratesPattern;
}

function proteinPattern() {
  return new Protein();
}

function fatPattern() {
  return new Fat();
}

function carbohydratesPattern() {
  return new Carbohydrates();
}

class Protein {
  info() {
    return 'I am Protein.';
  }
}

class Fat {
  info() {
    return 'I am Fat.';
  }
}

class Carbohydrates {
  info() {
    return 'I am carbohydrates';
  }
}

export default foodProducer;
```
#### java
#### c++
## 2. Structural
### 2.1 Adapter
- The Adapter Pattern allows **incompatible interfaces** to work together by creating a "wrapper" that translates one interface to another. It acts as a **bridge** between two incompatible interfaces.
- Classic Adapter Pattern Structure
```plain text
Client needs Interface A -> Adapter -> External code that only provides Interface B
```
#### go
- Go는 객체 지향 언어가 아니기 때문에 function type을 선언하고 그 function type이 대상 인터페이스를 구현하도록 했다. 결국 Adaptee를 그 function type으로 타입변환하면 바로 대상 인터페이스화 되는 것.
- 이 부분을 이해하는 것이 핵심
```go
// From Go's http package - this is the actual code:
type HandlerFunc func(ResponseWriter, *Request)

// This makes HandlerFunc implement the Handler interface:
func (f HandlerFunc) ServeHTTP(w ResponseWriter, r *Request) {
    f(w, r)  // Call the function that f holds
}
```
```go
package main

import (
    "fmt"
    "net/http"
    "log"
)

// Target interface that clients expect
type Logger interface {
    Log(message string)
}

// Adaptee - third-party logger with different interface
type ThirdPartyLogger struct {
    prefix string
}
func (l *ThirdPartyLogger) WriteLog(text string) {
    fmt.Printf("3rd party[%s]: %s\n", l.prefix, text)
}

// Object Adapter using composition
type LoggerAdapter struct {
    thirdPartyLogger *ThirdPartyLogger
}

func (a *LoggerAdapter) Log(message string) {
    a.thirdPartyLogger.WriteLog(message)
}

// Functional Adapter - leveraging Go's first-class functions
type LoggerFunc func(string)

func (f LoggerFunc) Log(message string) {
    f(message)
}

// Database adapter for external API integration
type UserStore interface {
    GetUser(id string) (*User, error)
    SaveUser(user *User) error
}

type User struct {
    ID   string
    Name string
}

// Third-party API client (adaptee)
type ExternalAPIClient struct {
    baseURL string
}

func (c *ExternalAPIClient) FetchUserData(userID string) (map[string]interface{}, error) {
    // Simulate API call returning different data structure
    return map[string]interface{}{
        "user_id":   userID,
        "full_name": "John Doe",
    }, nil
}

func (c *ExternalAPIClient) UpdateUser(data map[string]interface{}) error {
    fmt.Printf("Updating user via API: %+v\n", data)
    return nil
}

// Adapter that converts external API to our domain interface
type APIUserAdapter struct {
    client *ExternalAPIClient
}

func (a *APIUserAdapter) GetUser(id string) (*User, error) {
    data, err := a.client.FetchUserData(id)
    if err != nil {
        return nil, fmt.Errorf("API adapter: failed to fetch user: %w", err)
    }
    
    return &User{
        ID:   data["user_id"].(string),
        Name: data["full_name"].(string),
    }, nil
}

func (a *APIUserAdapter) SaveUser(user *User) error {
    data := map[string]interface{}{
        "user_id":   user.ID,
        "full_name": user.Name,
    }
    
    if err := a.client.UpdateUser(data); err != nil {
        return fmt.Errorf("API adapter: failed to save user: %w", err)
    }
    
    return nil
}

// Usage example demonstrating adapter flexibility
func main() {
    // Legacy system adapter
    thirdParty := &ThirdPartyLogger{prefix: "3rdParty"}
    adapter := &LoggerAdapter{thirdPartyLogger: thirdParty}
    
    // Functional adapter
    funcAdapter := LoggerFunc(func(msg string) {
        fmt.Printf("FUNC: %s\n", msg)
    })
    
    loggers := []Logger{adapter, funcAdapter}
    for _, logger := range loggers {
        logger.Log("Hello from adapted logger!")
    }
    
    // Database adapter example
    apiClient := &ExternalAPIClient{baseURL: "https://api.example.com"}
    userStore := &APIUserAdapter{client: apiClient}
    
    // Client code works with clean interface, unaware of external API complexity
    user, err := userStore.GetUser("123")
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Retrieved user: %+v\n", user)
    
    user.Name = "Jane Doe"
    if err := userStore.SaveUser(user); err != nil {
        log.Fatal(err)
    }
}
```
#### javascript
![[100. media/image/x9ao-HnAX1.png]]
```javascript
class Soldier {
  consturctor(level) {
    this.level = level;
  }

  attack() {
    console.log('attack with power ' + this.level);
  }
}

class SuperSoldier {  // Soldier와 상속관계가 있어야 할 텐데?
  constructor(level) {
    this.level = level;
  }

  attackwithShield() {
    console.log('attack with shield power ' + this.level * 10;)
  }
}

class SoldierAdapter {
  constructor(superSoldier) { // Interface 역할을 하려면 constructor 인자로 타입이 들어가야 할 텐데?
    this.superSoldier = superSoldier;
  }

  attack() {
    return this.superSoldier.attackWithShield();
  }
}

export {Soldier, SuperSoldier, SoldierAdapter};
```
#### java
- payment gateway integration
```java
package com.example.adapters;

import java.math.BigDecimal;
import java.util.Map;
import java.util.HashMap;

// Target interface that business logic expects
public interface PaymentProcessor {
    PaymentResult processPayment(PaymentRequest request);
    boolean supportsRefund();
    RefundResult refundPayment(String transactionId, BigDecimal amount);
}

// Common data structures
public class PaymentRequest {
    private final String customerId;
    private final BigDecimal amount;
    private final String currency;
    private final Map<String, Object> metadata;
    
    public PaymentRequest(String customerId, BigDecimal amount, String currency) {
        this.customerId = customerId;
        this.amount = amount;
        this.currency = currency;
        this.metadata = new HashMap<>();
    }
    
    // Getters and additional methods...
    public String getCustomerId() { return customerId; }
    public BigDecimal getAmount() { return amount; }
    public String getCurrency() { return currency; }
    public Map<String, Object> getMetadata() { return metadata; }
}

public class PaymentResult {
    private final boolean success;
    private final String transactionId;
    private final String message;
    
    public PaymentResult(boolean success, String transactionId, String message) {
        this.success = success;
        this.transactionId = transactionId;
        this.message = message;
    }
    
    public boolean isSuccess() { return success; }
    public String getTransactionId() { return transactionId; }
    public String getMessage() { return message; }
}

public class RefundResult {
    private final boolean success;
    private final String refundId;
    private final String message;
    
    public RefundResult(boolean success, String refundId, String message) {
        this.success = success;
        this.refundId = refundId;
        this.message = message;
    }
    
    public boolean isSuccess() { return success; }
    public String getRefundId() { return refundId; }
    public String getMessage() { return message; }
}

// Third-party PayPal SDK (Adaptee)
class PayPalGateway {
    public PayPalResponse charge(String customer, double amountUSD) {
        // PayPal-specific implementation
        System.out.println("Processing PayPal payment: $" + amountUSD + " for " + customer);
        return new PayPalResponse("pp_" + System.currentTimeMillis(), true);
    }
    
    public boolean processRefund(String paypalTransactionId, double amount) {
        System.out.println("Processing PayPal refund: $" + amount + " for " + paypalTransactionId);
        return true;
    }
}

class PayPalResponse {
    private final String transactionId;
    private final boolean successful;
    
    public PayPalResponse(String transactionId, boolean successful) {
        this.transactionId = transactionId;
        this.successful = successful;
    }
    
    public String getTransactionId() { return transactionId; }
    public boolean isSuccessful() { return successful; }
}

// Third-party Stripe SDK (Adaptee)
class StripeAPI {
    public StripeCharge createCharge(StripeChargeRequest request) {
        System.out.println("Processing Stripe payment: " + request.getAmountCents() + 
                          " cents for " + request.getCustomerId());
        return new StripeCharge("ch_" + System.currentTimeMillis(), "succeeded");
    }
    
    public StripeRefund createRefund(String chargeId, long amountCents) {
        System.out.println("Processing Stripe refund: " + amountCents + " cents for " + chargeId);
        return new StripeRefund("re_" + System.currentTimeMillis(), "succeeded");
    }
}

class StripeChargeRequest {
    private final String customerId;
    private final long amountCents;
    private final String currency;
    
    public StripeChargeRequest(String customerId, long amountCents, String currency) {
        this.customerId = customerId;
        this.amountCents = amountCents;
        this.currency = currency;
    }
    
    public String getCustomerId() { return customerId; }
    public long getAmountCents() { return amountCents; }
    public String getCurrency() { return currency; }
}

class StripeCharge {
    private final String id;
    private final String status;
    
    public StripeCharge(String id, String status) {
        this.id = id;
        this.status = status;
    }
    
    public String getId() { return id; }
    public String getStatus() { return status; }
}

class StripeRefund {
    private final String id;
    private final String status;
    
    public StripeRefund(String id, String status) {
        this.id = id;
        this.status = status;
    }
    
    public String getId() { return id; }
    public String getStatus() { return status; }
}

// PayPal Adapter implementing composition over inheritance
public class PayPalAdapter implements PaymentProcessor {
    private final PayPalGateway paypalGateway;
    
    public PayPalAdapter(PayPalGateway paypalGateway) {
        this.paypalGateway = paypalGateway;
    }
    
    @Override
    public PaymentResult processPayment(PaymentRequest request) {
        try {
            // Convert our domain request to PayPal format
            double amountUSD = convertToUSD(request.getAmount(), request.getCurrency());
            PayPalResponse response = paypalGateway.charge(request.getCustomerId(), amountUSD);
            
            return new PaymentResult(
                response.isSuccessful(),
                response.getTransactionId(),
                response.isSuccessful() ? "Payment successful" : "Payment failed"
            );
        } catch (Exception e) {
            return new PaymentResult(false, null, "PayPal processing error: " + e.getMessage());
        }
    }
    
    @Override
    public boolean supportsRefund() {
        return true;
    }
    
    @Override
    public RefundResult refundPayment(String transactionId, BigDecimal amount) {
        try {
            double amountUSD = convertToUSD(amount, "USD");
            boolean success = paypalGateway.processRefund(transactionId, amountUSD);
            
            return new RefundResult(
                success,
                success ? "ref_" + System.currentTimeMillis() : null,
                success ? "Refund processed" : "Refund failed"
            );
        } catch (Exception e) {
            return new RefundResult(false, null, "PayPal refund error: " + e.getMessage());
        }
    }
    
    private double convertToUSD(BigDecimal amount, String currency) {
        // Simplified currency conversion - in reality, would use exchange rate service
        return amount.doubleValue();
    }
}

// Stripe Adapter
public class StripeAdapter implements PaymentProcessor {
    private final StripeAPI stripeAPI;
    
    public StripeAdapter(StripeAPI stripeAPI) {
        this.stripeAPI = stripeAPI;
    }
    
    @Override
    public PaymentResult processPayment(PaymentRequest request) {
        try {
            // Convert BigDecimal to cents for Stripe API
            long amountCents = request.getAmount().multiply(BigDecimal.valueOf(100)).longValue();
            
            StripeChargeRequest chargeRequest = new StripeChargeRequest(
                request.getCustomerId(),
                amountCents,
                request.getCurrency().toLowerCase()
            );
            
            StripeCharge charge = stripeAPI.createCharge(chargeRequest);
            boolean success = "succeeded".equals(charge.getStatus());
            
            return new PaymentResult(
                success,
                charge.getId(),
                success ? "Charge successful" : "Charge failed"
            );
        } catch (Exception e) {
            return new PaymentResult(false, null, "Stripe processing error: " + e.getMessage());
        }
    }
    
    @Override
    public boolean supportsRefund() {
        return true;
    }
    
    @Override
    public RefundResult refundPayment(String transactionId, BigDecimal amount) {
        try {
            long amountCents = amount.multiply(BigDecimal.valueOf(100)).longValue();
            StripeRefund refund = stripeAPI.createRefund(transactionId, amountCents);
            boolean success = "succeeded".equals(refund.getStatus());
            
            return new RefundResult(
                success,
                refund.getId(),
                success ? "Refund processed" : "Refund failed"
            );
        } catch (Exception e) {
            return new RefundResult(false, null, "Stripe refund error: " + e.getMessage());
        }
    }
}

// Business service that works with any payment processor
public class PaymentService {
    private final PaymentProcessor processor;
    
    public PaymentService(PaymentProcessor processor) {
        this.processor = processor;
    }
    
    public String processOrder(String customerId, BigDecimal amount, String currency) {
        PaymentRequest request = new PaymentRequest(customerId, amount, currency);
        PaymentResult result = processor.processPayment(request);
        
        if (result.isSuccess()) {
            System.out.println("Order completed successfully. Transaction ID: " + result.getTransactionId());
            return result.getTransactionId();
        } else {
            System.out.println("Order failed: " + result.getMessage());
            throw new RuntimeException("Payment processing failed: " + result.getMessage());
        }
    }
    
    public void processRefund(String transactionId, BigDecimal amount) {
        if (!processor.supportsRefund()) {
            throw new UnsupportedOperationException("Refunds not supported by this payment processor");
        }
        
        RefundResult result = processor.refundPayment(transactionId, amount);
        
        if (result.isSuccess()) {
            System.out.println("Refund completed successfully. Refund ID: " + result.getRefundId());
        } else {
            throw new RuntimeException("Refund processing failed: " + result.getMessage());
        }
    }
}

// Demonstration of adapter pattern usage
public class PaymentProcessorDemo {
    public static void main(String[] args) {
        // Create different payment processor adapters
        PaymentProcessor paypalProcessor = new PayPalAdapter(new PayPalGateway());
        PaymentProcessor stripeProcessor = new StripeAdapter(new StripeAPI());
        
        // Business logic remains the same regardless of payment provider
        testPaymentProcessor("PayPal", paypalProcessor);
        System.out.println();
        testPaymentProcessor("Stripe", stripeProcessor);
    }
    
    private static void testPaymentProcessor(String providerName, PaymentProcessor processor) {
        System.out.println("Testing " + providerName + " payment processor:");
        
        PaymentService service = new PaymentService(processor);
        
        try {
            // Process a payment
            String transactionId = service.processOrder("customer123", 
                                                       BigDecimal.valueOf(99.99), 
                                                       "USD");
            
            // Process a refund
            service.processRefund(transactionId, BigDecimal.valueOf(99.99));
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
```
#### c++
### 2.2 Bridge
#### javascript
![[100. media/image/t22xlvqvsT.png]]
```javascript
class Soldier {
  constructor(weapon) {
    this.weapon = weapon;
  }
}

class SuperSoldier extends Soldier {
  constructor(weapon) {
    super(weapon);
  }

  attack() {
    return 'SuperSoldier, weapon:' + this.weapon.get();
  }
}

class IronMan extends Soldier {
  constructor(weapon) {
    super(weapon);
  }

  attack() {
    return 'Ironman, Weapon: ' + this.weapon.get();
  }
}

class Weapon {
  contructor(type) {
    this.type = type;
  }

  get() {
    return this.type;
  }
}

class Shield extends Weapon {
  constructor() {
    super('shield');
  }
}

class Rocket extends Weapon {
  constructor() {
    super('rocket');
  }
}

export {SuperSoldier, IronMan, Shield, Rocket};
```
#### java
#### c++
### 2.3 Composite
#### javascript
![[100. media/image/vawCp0fgCs.png]]
```javascript
// Equipment
class Equipment {
  getPrice() {
    return this.price || 0;
  }

  getName() {
    return this.name;
  }

  setName(name) {
    this.name = name;
  }
}

class Pattern extends Equipment {
  constructor() {
    super();
    this.equpments = [];
  }

  add(equipment) {
    this.equipments.push(equipment);
  }

  getPrice() {
    return this.equipments.map(equipment => {
      return equipment.getPrice();
    })
    .reduce((a, b) => {
      return a + b;
    });
  }
}

class Cabinet extends Pattern {
  constructor() {
    super();
    this.setName('cabinet');
  }
}

// --- leaves ---
class FloppyDisk extends Equipment {
  constructor() {
    super();
    this.setName('Floppy Disk');
    this.price = 70;
  }
}

class HardDrive extends Equipment {
  constructor() {
    super();
    this.setName('Hard Drive');
    this.price = 250;
  }
}

class Memory extends Equipment {
  constructor() {
    super();
    this.setName('Memory');
    this.price = 250;
  }
}

export {Cabinet, FloppyDisk, HardDrive, Memory};
```
#### java
#### c++
### 2.4 Decorator
#### javascript
![[100. media/image/a46Vx3Er-T.png]]
```javascript
class Notification {
  constructor(kind) {
    this.kind = kind || "Generic";
  }

  getInfo() {
    return `I'm a ${this.kind} Notification`;
  }
}

class FacebookNotification extends Notification {
  constructor() {
    super("Facebook");
  }

  setNotification(msg) {
    this.message = msg;
  }

  getInfo() {
    return `${super.getInfo()} with the message: ${this.message}`;
  }
}

class SMSNotification extends Notification {
  constructor() {
    super("SMS");
  }
  
  getInfo() {
    return super.getInfo();
  }
}

export { FacebookNotification, SMSNotification };
```
#### java
#### c++
### 2.5 Facade
### 2.6 Flyweight
### 2.7 Proxy
#### When to Use the Proxy Pattern
- **Lazy initialization**: When you have a resource-intensive object and you want to defer its creation until it's really needed.
- **Access control**: When you need to control access to sensitive or protected objects (e.g., protection proxies).
- **Remote control**: When objects are located in different address spaces (e.g., remote proxies).
- **Logging or auditing**: When you want to track the usage of a resource or operation.
#### javascript
![[100. media/audio/H1mvGlIjgT.mp4]]
![[100. media/image/w4R7kwzNrR.png]]
- access control
```javascript
class Plane {
  fly() {
    return 'flying';
  }
}

class PilotProxy {
  constructor(pilot) {
    this.pilot = pilot;
  }

  fly() {
    return this.pilot.age < 18 ? `too young to fly` : new Plane().fly();
  }
}

class Pilot {
  constructor(age) {
    this.age = age;
  }
}

export { Plane, PilotProxy, Pilot };
```
- check input validity
```javascript
const person = {
  name: "John Doe",
  age: 42,
  nationality: "American"
};

const personProxy = new Proxy(person, {
  get: (obj, prop) => {
    if (!obj[prop]) {
      console.log(`Hmm.. this property doesn't seem to exist`);
    } else {
      console.log(`The value of ${prop} is ${obj[prop]}`);
    }
  },
  set: (obj, prop, value) => {
    if (prop === "age" && typeof value !== "number") {
      console.log(`Sorry, you can only pass numeric values for age.`);
    } else if (prop === "name" && value.length < 2) {
      console.log(`You need to provide a valid name.`);
    } else {
      console.log(`Changed ${prop} from ${obj[prop]} to ${value}.`);
      obj[prop] = value;
    }
    return true;
  }
});

personProxy.nonExistentProperty;
personProxy.age = "44";
personProxy.name = "";
```
#### python: delays the creation of a resource-intensive object until it is actually needed
- Virtual proxy
```python
from abc import ABC, abstractmethod

# Subject Interface
class Image(ABC):
    @abstractmethod
    def display(self):
        pass

# Real Subject
class RealImage(Image):
    def *init*(self, filename):
        self.filename = filename
        self.load_image_from_disk()

    def load_image_from_disk(self):
        print(f"Loading image: {self.filename}")

    def display(self):
        print(f"Displaying image: {self.filename}")

# Proxy
class ProxyImage(Image):
    def *init*(self, filename):
        self.filename = filename
        self.real_image = None

    def display(self):
        if self.real_image is None:
            self.real_image = RealImage(self.filename)  # Load on demand
        self.real_image.display()

# Client code
if *name* == "*main*":
    # Image is loaded only when it is actually needed
    proxy_image = ProxyImage("test_image.png")
    print("Image object created. No loading yet.")
    
    # Display image (which loads it if necessary)
    proxy_image.display()
    print("Image displayed for the first time.")
    
    # Display image again (already loaded, so no need to load again)
    proxy_image.display()
```
#### java
### 3. Behavioral
### 3. 1 Chain of Responsibility
### 3. 2 Command
### 3. 3 Interpreter
### 3. 4 Iterator
### 3. 5 Mediator
### 3. 6 Memento
### 3. 7 Observer
### 3. 8 State
### 3. 9 Strategy
### 3. 10 Template
### 3. 11 Visitor