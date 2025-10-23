---
title: "Golang"
created: 2024-03-07 17:07:15
updated: 2025-10-03 07:22:48
---
## 1. 모듈 관리
### go mod init "project identifier"
- hello 디렉토리를 만들고 나서 "go mod init C:\Temp\hello"를 하면 에러
- "go mod init hello"로 해야.
- 모듈 내 함수를 export하고 싶으면 첫 글자를 **대문자**로, 그렇지 않으면 private.
## 2. framework
### 2. 1 To develop CLI, we can use go standard library(flag) but what framework can we use?
![[100. media/image/LR68-KpyQ6.png|300]]

github, kubernetes cli도 이걸로 만들어졌음.
### 2. 2 go package for url router and dispatcher
gorilla-mux
## 3. nomadcoin 강의 정리
### 3. 1 type
Inside function definition, we can use ":=" to assign a value to a variable with type. The type of the variable is defined by the value.
### 3. 2 Argument type that accept all types in goLang
Go's equivalent to `Object` in Java or `any` in typescript.
`any` is newer version of `i interface{}`
```go
func HandleValue(i any) {
    switch v := i.(type) {
    case string:
        fmt.Println("Got string:", v)
    case int:
        fmt.Println("Got int:", v)
    default:
        fmt.Println("Unknown type")
    }
}

func PrintAnything(i interface{}) {
    fmt.Println(i)
}

// You can call it with any type:
PrintAnything(42)           // int
PrintAnything("hello")      // string  
PrintAnything([]int{1,2,3}) // slice
PrintAnything(struct{}{})   // struct
```
### 3. 3 function
#### - 여러 다른 타입 값 return 가능.
```go
package main

import (
	"fmt"
	"strings"
)

func main() {
	len, upper := lenAndUpper("Hello")
    # or
    len, _ := lenAndUpper("Hello") --> '_'는 무시한다는 뜻.
	fmt.Println(len, upper)
}

func lenAndUpper(name string) (int, string) {
	return len(name), strings.ToUpper(name)
}
```
#### - "..."
여러 값이 반복될 때 간편하게 "..."으로 표시
```go
func repeat(names ...String) {...}

repeat("A", "B", "C", "D")
```
#### - naked return
 함수 정의할 때 return 변수까지 다 정의할 수 있고 마지막에 그냥 return만 넣은다.
 we can define return variables in a function signature
```go
func lenAndUpper(name string) (length int, Upper string) {
	length = len(name)
    Upper = strings.Upper(name)
    return
}
```
#### - defer
after a function returns, something can be done more like resource close, etc.
```go
func lenAndUpper(name string) (length int, Upper string) {
    defer fmt.PrintLn("I'm done!")
  
	length = len(name)
    Upper = strings.Upper(name)
    return
}
```
#### - variable expression in if-else statement or switch.
```go
if koreanAge := age + 2; koreanAge < 18 {
  return false
}
return true
```
### 3. 4 pointer
 c와 동일한 포인터 표기 사용. &, *
### 3. 5 slice
array without length so we use slice more often than array in Go.
append(slice, value) returns new slice the value appended.
```go
names := []string{"A", "B", "C"}
names = append(names, "D")
```
### 3. 6 map
python의 dictionary, javascript의 object와 비슷하게 key:value 쌍.
```go
jay = map[string]string{"name":"jay", "age":"55"}
for _, value := range jay {
  fmt.Println(value)
}
jay["new_key"] = "new_value"
```
### 3. 7 struct
Go는 class가 없음.
c 구조체와 동일하지만 go는 ';'를 쓰지 않기 때문에 주의.
```go
type Account struct {  --> 다른 모듈에서 사용할 수 있게.
  owner string
  balance int
}

func NewAccount(owner string) *account {
  account := account{owner: owner, balance: 0}
  return &account
}
```
### 3. 8 Stringer Interface of fmt package
java의 toString()과 비슷.
```plain text
type Stringer interface {
    String() string
}

// Implementing the Stringer interface
func (p Person) String() string {
    return fmt.Sprintf("Person{Name: %s, Age: %d}", p.Name, p.Age)
}
```
 ❌ DON'T use %s or %v on the receiver itself
✅ DO use %+v or %#v for the receiver itself
✅ DO use %s or %v freely for individual fields/members
### 3. 9 method
#### - 사용자 정의 struct method
struct에 constructor 같은 method 추가 가능.
func signature에 receiver를 추가하여 특정 struct에 속한다는 것을 표시.
struct를 변경할 때는 인자를 포인터로 받도록.
```go
func (a *account) Deposit(amount: int) {
  a.balance += amount
}
```
#### - built-in struct method
#### - type method
- 기존 데이터 타입을 struct 선언할 때 쓰는 "type"을 사용해 다른 이름(alias)을 부여할 수 있음.
```go
package mydict
// map을 dictionary라는 이름으로 정의
type Dictionary map[string]string 

다른 모듈에서
dictionary := mydict.Dictionary{}
dictionary["key"] = "value"```
 - 재정의한 타입의 사용자 정의 method
```go
func (d Dictionary) Search(word string) (string, error) {
  value, exists := d[word]
  ...
}
```
### 3. 10 c style error-handling
try-except(python), try-catch(javascript) 없음.
```go
var errNoMoney = errors.New("Can't withdraw")
func (a *account) Withdraw(amount int) error {
  if a.balance < amount {
    return errNoMoney
  }
  a.balance -= amount
  return nil
}
```
### 3. 11 Goroutine
- 함수 호출할 때 go를 앞에 추가.
- 유닉스 시스템에서 네트웍 연결을 fork해서 처리하듯이 go에서는 네트웍 연결 요청을  go routine으로 처리.
- channel: higer-order function과 go로 실행하는 function 사이 통로
	default channel은 blocking -> 받는 쪽이 안 받으면 보내는 쪽도 blocking
	단순히 go를 함수 앞에 추가할 뿐 아니라 병렬실행 함수의 signature에 channel 타입과 결과를 추가
```go
func main() {
	c := make(chan int)
    go countToTen(c)
	go receive(c)
}

# 읽기 전용 채널
func receive(c <-chan int) {
	for {
		a, ok := <-c
		if !ok {
			fmt.Printf("Done\n")
            break;
		}
    	fmt.Println("received from channel")
	}
}

# 쓰기 전용 채널
func countToTen(c chan int) {
	for i := 1; i <= 10; i++ {
		c <- i
		time.Sleep(200 * time.Millisecond)
	}
    close(c)
}
```
### 3. 12 multiplexor & web server
#### - a multiplexor (often abbreviated as "mux") is a fundamental digital circuit component. It's a selector switch that takes multiple input signals and route one of them to a single output based on control signals.
#### - HTTP/2 Multiplexing:
- HTTP/2 introduced stream multiplexing, which allows multiple HTTP requests and responses to be sent concurrently over a single TCP connection. HTTP/2 can:
	- Send multiple requests simultaneously
	- Interleave response data from different requests
	- Prioritize certain streams over others
	- Avoid head-of-line blocking that plagued HTTP/1.1
#### - HTTP/3 and QUIC:
	- HTTP/3 takes this further with QUIC protocol.
#### - http.DefaultServeMux 대신 http.NewServeMux 쓰면 보다 유연한 route 기능.
```go
func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/api/", apiHandler)
    mux.HandleFunc("/static/", staticHandler)
    
    // Still only listens on ONE port
    http.ListenAndServe(":8080", mux)
}
```
### 3. 13 middleware
#### - Go Middleware is an Adapter pattern. Refer to [[4. IT/Design pattern#2.1 Adapter]]
```plain text
http.Handler -> Middleware -> http.Handler
```
#### - Go middleware pattern is a pattern that allows you to wrap HTTP handlers with additional functionality.
#### - Target Interface
```go
// Handler interface - the contract
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}
```
#### - **Functional** adapter with http.Handler Interface
```go

// The HandlerFunc type is an adapter to allow the use of
// ordinary functions as HTTP handlers. If f is a function
// with the appropriate signature, HandlerFunc(f) is a
// [Handler] that calls f.
type HandlerFunc func(ResponseWriter, *Request)

// ServeHTTP calls f(w, r).
func (f HandlerFunc) ServeHTTP(w ResponseWriter, r *Request) {
	f(w, r)
}

//
func middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Middleware before logic here.  It wraps the existing handler with additional behavior
        next.ServeHTTP(w, r)
        // Middleware after logic here.  It wraps the existing handler with additional behavior
    })
}
```
#### - **Object** adapter with the same http.Handler Interface
```go
// Object Adapter version - more verbose but clearer structure
type MiddlewareAdapter struct {
    next http.Handler  // This is the adaptee
}

func (m *MiddlewareAdapter) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Middleware logic here
    m.next.ServeHTTP(w, r)  // Delegate to adaptee
}

func middleware(next http.Handler) http.Handler {
    return &MiddlewareAdapter{next: next}  // Return adapter struct
}
```
#### - Complete example of multiple middleware 1
```go
package main

import (
    "fmt"
    "net/http"
    "log"
)

// Target interface that clients expect
type ModernLogger interface {
    Log(message string)
}

// Adaptee - legacy logging system with different interface
type LegacyLogger struct {
    prefix string
}

func (l *LegacyLogger) WriteLog(text string) {
    fmt.Printf("[%s] %s\n", l.prefix, text)
}

// Object Adapter using composition
type LoggerAdapter struct {
    legacy *LegacyLogger
}

func (a *LoggerAdapter) Log(message string) {
    a.legacy.WriteLog(message)
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
    legacy := &LegacyLogger{prefix: "LEGACY"}
    adapter := &LoggerAdapter{legacy: legacy}
    
    // Functional adapter
    funcAdapter := LoggerFunc(func(msg string) {
        fmt.Printf("FUNC: %s\n", msg)
    })
    
    // Use both adapters through same interface
    loggers := []ModernLogger{adapter, funcAdapter}
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
#### - Complete example of multiple middleware 2
```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "time"
)

// Logging middleware
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

// Authentication middleware
func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token != "Bearer valid-token" {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        next.ServeHTTP(w, r)
    })
}

// CORS middleware
func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
        
        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }
        
        next.ServeHTTP(w, r)
    })
}

// Main handler
func homeHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, World!")
}

func main() {
    mux := http.NewServeMux()
    
    // Chain middleware
    handler := corsMiddleware(loggingMiddleware(authMiddleware(http.HandlerFunc(homeHandler))))
    mux.Handle("/", handler)
    
    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", mux))
}
```
#### - Using popular router library
- gorilla mux
```go
import "github.com/gorilla/mux"

r := mux.NewRouter()
r.Use(loggingMiddleware)
r.Use(authMiddleware)
r.HandleFunc("/", homeHandler)
```
#### - Custom middleware Chain Helper
```go
func chainMiddleware(h http.Handler, middleware ...func(http.Handler) http.Handler) http.Handler {
    for i := len(middleware) - 1; i >= 0; i-- {
        h = middleware[i](h)
    }
    return h
}

// Usage
handler := chainMiddleware(
    http.HandlerFunc(homeHandler),
    corsMiddleware,
    loggingMiddleware,
    authMiddleware,
)
```
#### - Context based middleware
```go
func contextMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Add values to context
        ctx := context.WithValue(r.Context(), "userID", "12345")
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// In your handler, retrieve the value
func handler(w http.ResponseWriter, r *http.Request) {
    userID := r.Context().Value("userID").(string)
    fmt.Fprintf(w, "User ID: %s", userID)
}
```
### 3. 14 storage: bolt
#### - bucket(table in RDB) 2개 만들기
- 블록 저장
- 메타데이터 저장
### 3. 15 defer
#### - for ensuring cleanup code runs even if the function exits early due to an error or panic
```go
func readFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close() // Ensures file is closed when function exits
    
    // ... work with file
    return nil
}

func safeFunction() {
    mu.Lock()
    defer mu.Unlock() // Ensures mutex is unlocked
    
    // ... critical section
}

func example() {
    defer fmt.Println("first")
    defer fmt.Println("second") 
    defer fmt.Println("third")
    fmt.Println("main")
}
// Output:
// main
// third
// second
// first
```
### 3. 16 runtime.Goexit()
#### os.Exit() 참고
#### 사용예
- 1. Testing frameworks: Test libraries often use Goexit() to stop test execution
```go
func TestSomething(t *testing.T) {
    if someCondition {
        t.Fatal("Test failed") // internally calls runtime.Goexit()
    }
}
```
- 2. HTTP handlers with early termination: When you need to stop processing without returning an error
```go
func handler(w http.ResponseWriter, r *http.Request) {
    defer log.Println("Handler cleanup")
    
    if !authorized {
        w.WriteHeader(http.StatusUnauthorized)
        runtime.Goexit() // Stop processing but run deferred functions
    }
    // ... rest of handler
}
```
- 3. Worker goroutines with complex cleanup: When normal return isn't sufficient
```go
func complexWorker() {
    defer closeConnections()
    defer saveState()
    defer notifyManager()
    
    for {
        if fatalError {
            runtime.Goexit() // Ensures all cleanup runs
        }
        // ... work
    }
}
```
### 3. 17 iota ([[Enum]])
#### predeclared identifier that's used to create sequences of related constants.
#### example
```go
const (
    Sunday = iota    // 0
    Monday           // 1
    Tuesday          // 2
    Wednesday        // 3
    Thursday         // 4
    Friday           // 5
    Saturday         // 6
)

const (
    a, b = iota + 1, iota + 2  // a=1, b=2
    c, d                       // c=2, d=3
    e, f                       // e=3, d=4
)

const (
    BitFlag1 = 1 << iota  // 1 (1 << 0)
    BitFlag2              // 2 (1 << 1)
    BitFlag3              // 4 (1 << 2)
    BitFlag4              // 8 (1 << 3)
)
```
### 3. 18 transaction은 Blockchain의 [[Blockchain(블록체인)#^8ovx_gFJ1|transaction]] 참고
### 3. 19 websocket
- 표준 라이브러리 대신 gorilla/websocket 이용
- http 연결을 websocket으로 upgrade하고 origin allow 설정(authentication)하는 것이 필요.
### 3. 20 race detector
- "go run -race *.go"
- 데이터 경합 조건을 미리 탐지.
```shell
# Run with race detection
go run -race main.go

# Build with race detection
go build -race myprogram.go

# Test with race detection (very common)
go test -race ./...

```
### 3.21 scraper source directory zip
- [goquery](https://pkg.go.dev/github.com/PuerkitoBio/goquery#section-readme) 사용해서 html 파일 읽고 파싱
- source zip

### 3. 22 test 패키지가 좋다. 참고 영상은 nomadcoder의 nomadcoin을 보면 된다.
### 3.23 메모리 할당 함수 차이

|        | make()                                              | new()                                                    |
| ------ | --------------------------------------------------- | -------------------------------------------------------- |
| 반환타입   | 슬라이스, 맵, 채널의 초기화된 값 자체를 반환                          | 해당 타입의 포인터(pointer)를 반환                                  |
| 초기화 대상 | slice/map/channel과 같이 런타임에 초기화가 필요한 복합 자료구조를 생성<br> | 모든 타입의 포인터를 반환, `make()`와 달리 런타임 초기화가 필요 없는 기본 타입에도 사용.  |
**주의!!** slice/map/channel에 new를 쓰면 안 된다.
