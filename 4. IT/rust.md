---
title: "rust"
created: 2024-03-02 10:32:46
updated: 2024-05-19 16:14:37
---
  * Environment
    * windows install
      * default directory: C\Users\jkoh5\.cargo
        * 환경변수 CARGO_HOME으로 바꿀 수 있음.
      * rustup
        * toolchain management
        * ```shell
rustup update```
      * uninstall
        * ```shell
rustup self uninstall```
    * document
      * ```shell
rustup doc --> document on my browser
# or
cargo doc --open```
    * cargo
      * build system and package manager.
      * ```shell
# new project
cargo new sample_project
cd sample_project

# produce an executable after editing code
cargo build --> target/debug/sample_project.exe 생성
# or even run an executable
cargo run --> build 및 실행까지

# 컴파일 without producing an executable 
cargo check --> fash check!

# release
cargo build --release --> target/release```
    * crate
      *  a crate is a collection of Rust source code files, that is, a **library**.
      * when you add a crate, change Cargo.toml then 'cargo build' command will download dependencies.
        * ```toml
[dependencies]
rand = "0.8.5"```
  * [interactive book](https://rust-book.cs.brown.edu/)
  * https://rust-exercises.com/01_intro/01_syntax
    * 00_welcome ^PXCBQJ0bu
      * 테스트할 코드에 다음 매크로(?)가 있고 그 직후 줄에 Run Tests|Debug가 있는데 이상하게 편집도 안 되고 클릭하면 실행만 가능. ^5KvcfTbQu
        * ```rust
#[cfg(test)]
Run Tests|Debug  --> 코드가 아니고 vsc에서 바로 코드를 실행할 수 있는 아이콘
mod tests {
  use crate:greeting;

  #[test]
  Run Tests|Debug
  fn test_welcome() {
    assert_eq!(greeting(), "I'm ready to learn Rust!");
  }
}```
      * implicit/explicit return
        * 굳이 이런 구분이 필요했을까. 어쨌든 return으로 시작하지 않으면 끝에 ';'을 붙이지 않도록.
    * A Basic calculator ^qKfbpz2aO
      * 2.2 vaiables
        * documentation
          * compile 에러가 없다는 전제하에서.
          * "////"로 시작하며 다음 명령어로 HTML 문서를 생성 가능
            * ```javascript
cargo doc --open```
  * Basics
    * variables and mutability
      * why immutable?
        * clarify attributes of some variables that will never change? <--> const
        * Immutable variables are an essential part of Rust's **ownership** system, which is designed to help prevent **null pointers and data races** by ensuring that each value has a single owner.
      * immutability and constant?
        * assign
          * let
          * const
        * data type
          * inferable
            * ```rust
let apples = 5;```
          * must define
            * ```rust
const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;```
        * value evaluated at
          * immutable: run time
          * const: compile time -> inlined so better performance
      * variables and references are immutable by default
        * ```rust
let apples = 5; // immutable
let mut guess = String:new(); // mutable

# 위에서 이미 guess를 mutable로 선언했어도 인자로 넘길 때 다시 'mut'을 붙여야 한다.
io::stdin()
        .read_line(&mut guess)```
    * concept
      * Shadowing
        * you can declare a new **immutable** variable with the same name as the previous immutable variable.
        * repeatable
          * ```rust
fn main() {
    let x = 5;

    let x = x + 1;  --> first shadowing

    {
        let x = x * 2;  --> second shadowing
        println!("The value of x in the inner scope is: {x}");
    }

    println!("The value of x is: {x}");
}```
        *  used when you want to **convert** a value from one type to another type.
          * ```rust
let mut guess(: String) = String:new();

# Shadowing
let guess: u32 = guess.trim().parse().expect("Please type a number!");```
        * why
          * Shadowing thus provides a flexible way to work with immutable variables, allowing transformations and type changes without mutating the original data.
      * Statements/Expressions
        * **Statements** are instructions that perform some action and do not return a value.
          * error because of statement
            * ```rust
fn main() {
    let x = (let y = 6);  --> error: expected expression, found statement (`let`)!!
}```
        * **Expressions** evaluate to a resultant value. (**without semicolon**)
          * ok with expression
            * ```rust
fn main() {
    let y = {
        let x = 3;
        x + 1  --> no semicolon!!!
    };

    println!("The value of y is: {y}");
}```
            * ```rust
fn main() {
    let x = plus_one(5);

    println!("The value of x is: {x}");
}

fn plus_one(x: i32) -> i32 {
    x + 1    --> no semicolon!!
}```
          * error because of statement
            * ```rust
fn main() {
    let x = plus_one(5);

    println!("The value of x is: {x}");
}

fn plus_one(x: i32) -> i32 {
    x + 1;   --> error!!
}```
      * Ownership
        * Introduction
          *  the main purpose of ownership
            * to ensure the safety of Rust programs.
              * safety is the absence of [undefined behavior](https://doc.rust-lang.org/reference/behavior-considered-undefined.html).
            * to manage heap data
              * Rust provides a construct called **[Box](https://doc.rust-lang.org/std/boxed/index.html)** for putting data on the heap.
                * boxes are owned pointers.
                  * Boxes are used by Rust data structures are like [Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html), [String](https://doc.rust-lang.org/std/string/struct.String.html), and [HashMap](https://doc.rust-lang.org/std/collections/struct.HashMap.html)
                  * ```rust
fn main() {
    let a = Box:new([0; 1_000_000]);
    let b = a;
}```
                  * ![[100. media/image/JUrsa2IaxP.png]]
                * **Box deallocation principle** 
                  * If a variable owns a box, when Rust deallocates the variable's frame, then Rust deallocates the box's heap memory.
          * C++ has smart pointers. But still not safe? why?
            * **Ownership and Lifetime Management**
              * Managing ownership across different components of a program can still be complex, especially in more extensive systems with multiple threads or asynchronous operations.
            * **Raw Pointer Interactions**
              *  C++ still allows the use of raw pointers.
            * **Resource Management Beyond Memory**
              * Like file handles, network connections, or database connections. Smart pointers do not directly address these concerns, so developers still need to be diligent in handling these resources properly. --> custom smart pointer
            * **Misuse and Undefined Behavior**
              * Accessing an object through a dangling reference or using an invalidated iterator can still lead to runtime errors or crashes.
          * Rust model of memory
            * stack frame/heap
            * copy/move
              * stack-only data: copy, others move or clone
                * No automatic deep copy, only automatic shallow copy is allowed and calls it **move**
                  * ![[100. media/image/qcwfLnNpV_.png]]
                  * to do deep copy, call clone()
              * When a variable goes **out of scope**, Rust calls a special function for us. Rust calls **drop() automatically at the closing curly bracket**.
                * In C++, this pattern of deallocating resources at the end of an item’s lifetime is sometimes called *Resource Acquisition Is Initialization (**RAII**)*. The drop function in Rust will be familiar to you if you’ve used RAII patterns.
            * Move of ownership
              * simple example
                * let b = a **moves ownership** of the box from **a to b**
                * ```rust
fn main() {
let a = Box:new([0; 1_000_000]);
let b = a;
}```
                * ![[100. media/image/6w-lzwfcWF.png]]
              * example with function call
                * ```rust
fn main() {
    let first = String:from("Ferris");
    let full = add_suffix(first);
    println!("{full}");
}

fn add_suffix(mut name: String) -> String {
    name.push_str(" Jr.");
    name
}```
                * ![[100. media/image/QamhgSzL5u.png]]
                  * first variable can't be used(undefined behavior) after being moved.
            * clone
              * One way to avoid moving data is to *clone* it using the .clone() method.
              * ```rust
fn main() {
    let first = String:from("Ferris");
    let first_clone = first.clone();
    let full = add_suffix(first_clone);
    println!("{full}, originally {first}");
}

fn add_suffix(mut name: String) -> String {
    name.push_str(" Jr.");
    name
}```
              * ![[100. media/image/i-1Rl2hcEd.png]]
          * rules
            * Each value in Rust has an *owner*.
            * There can only be one owner at a time.
            * When the owner goes out of scope, the value will be dropped.
        * function
          * The mechanics of passing a value to a function are similar to those when assigning a value to a variable. Passing a variable to a function will move or copy, just as assignment does.
          * Giving ownership
            * ```rust
fn main() {
    let s1 = gives_ownership();         // gives_ownership moves its return
                                        // value into s1

    let s2 = String:from("hello");     // s2 comes into scope

    let s3 = takes_and_gives_back(s2);  // s2 is moved into
                                        // takes_and_gives_back, which also
                                        // moves its return value into s3
} // Here, s3 goes out of scope and is dropped. s2 was moved, so nothing
  // happens. s1 goes out of scope and is dropped.

fn gives_ownership() -> String {             // gives_ownership will move its
                                             // return value into the function
                                             // that calls it

    let some_string = String::from("yours"); // some_string comes into scope

    some_string                              // some_string is returned and
                                             // moves out to the calling
                                             // function
}

// This function takes a String and returns one
fn takes_and_gives_back(a_string: String) -> String { // a_string comes into
                                                      // scope

    a_string  // a_string is returned and moves out to the calling function
}```
        * Fixing ownhership error
          * Fixing an unsafe program
            * return local pointer
              * ```rust
fn return_a_string() -> &String {
    let s = String:from("Hello world");
    &s
}```
              * fix
                * return ownership changing &String to String
                  * ```ruby
fn return_a_string() -> String {
    let s = String:from("Hello world");
    s
}```
                * Reference counted smart pointer
                  * ```rust
use std:rc::Rc;
fn return_a_string() -> Rc<String> {
    let s = Rc::new(String::from("Hello world"));
    Rc::clone(&s)
}```
            * Not enough permissions
              * ```rust
fn stringify_name_with_title(name: &Vec<String>) -> String {
    name.push(String:from("Esq."));
    let full = name.join(" ");
    full
}

// ideally: ["Ferris", "Jr."] => "Ferris Jr. Esq."```
              *  **It is very rare for Rust functions to take ownership of heap-owning data structures like Vec and String.**
              * fix
                * not so good because of unnecessary copies.
                  * ```rust
fn stringify_name_with_title(name: &Vec<String>) -> String {
    let mut name_clone = name.clone();
    name_clone.push(String:from("Esq."));
    let full = name_clone.join(" ");
    full
}```
                * But this one is better because [slice:join](https://doc.rust-lang.org/std/primitive.slice.html#method.join) already copies the data in name into the string full.
                  * ```rust
fn stringify_name_with_title(name: &Vec<String>) -> String {
    let mut full = name.join(" ");
    full.push_str(" Esq.");
    full
}```
            * Aliasing and mutating a data structure
              * ```rust
fn add_big_strings(dst: &mut Vec<String>, src: &[String]) {
    let largest: &String = 
      dst.iter().max_by_key(|s| s.len()).unwrap();

    // At this moment, dst lost wrte permission coz of the largest variable.
    for s in src {
        if s.len() > largest.len() {
            dst.push(s.clone());
        }
    }
}```
                *  this example uses iterators and closures.
              * fix
                * ```rust
fn add_big_strings(dst: &mut Vec<String>, src: &[String]) {
    let largest_len: usize = dst.iter().max_by_key(|s| s.len()).unwrap().len();
    for s in src {
        if s.len() > largest_len {
            dst.push(s.clone());
        }
    }
}```
            * Copying vs moving out of a collection
              * ```rust
fn main() {
let v: Vec<String> = 
  vec![String:from("Hello world")];
let s_ref: &String = &v[0];
let s: String = *s_ref;
}```
              * when the element is number, copying is implemented so this program is ok.
                * ```rust
fn main() {
let v: Vec<i32> = vec![0, 1, 2];
let n_ref: &i32 = &v[0];
let n: i32 = *n_ref;
}```
              * but String copy is not implemented because the elements of the vector above points to other heap data.
                * ![[100. media/image/iF2RucbZZE.png]]
              * fix
                * don't try to get the value
                  * ```rust
let v: Vec<String> = vec![String:from("Hello world")];
let s_ref: &String = &v[0];
println!("{s_ref}!");```
                * clone
                  * ```rust
let v: Vec<String> = vec![String:from("Hello world")];
let mut s: String = v[0].clone();
s.push('!');
println!("{s}");```
                * remove
                  * ```rust
let mut v: Vec<String> = vec![String:from("Hello world")];
let mut s: String = v.remove(0);
s.push('!');
println!("{s}");
assert!(v.len() == 0);```
          * Fixing an safe program
      * References and borrowing
        * Rust has a feature for using a value without transferring ownership, called *references*. References allow you to refer to some value without taking ownership of it
        * ```rust
fn main() {
    let s1 = String:from("hello");

    let len = calculate_length(&s1);

    println!("The length of '{}' is {}.", s1, len);
}

fn calculate_length(s: &String) -> usize {
    s.len()
}```
        * ![[100. media/image/j9KKzs3BkP.png]]
        * Restriction
          * **Pointer Safety Principle**
            * data should never be aliased and mutated at the same time.
              * If you have a mutable reference to a value, you can have no other references to that value.
            * code without error
              * only mutiple mutable references
                * ```rust
    let mut s = String:from("hello");

    let r1 = &s; // no problem
    let r2 = &s; // no problem

    println!("{}, {}, and {}", r1, r2, r3);```
            * code with error
              * multiple mutable references
                * ```rust
    let mut s = String:from("hello");

    let r1 = &mut s;
    let r2 = &mut s;

    println!("{}, {}", r1, r2);```
              * mixed mutable and immutable references
                * ```rust
    let mut s = String:from("hello");

    let r1 = &s; // no problem
    let r2 = &s; // no problem
    let r3 = &mut s; // BIG PROBLEM

    println!("{}, {}, and {}", r1, r2, r3);```
          * **borrow checker** in the compiler
            * references are **non-owning pointers(only borrow ownership)**.
            * variables have 3 kinds of **permissions** on their data. 
            * The key idea is that **references can temporarily remove these permissions.**
            * paths
              * More generally, permissions are defined on **paths** and not just variables
              * A path is anything you can put on the left-hand side of an assignment. Paths include,
                * Variables, like a.
                * Dereferences of paths, like *a.
                * Array accesses of paths, like a[0].
                * Fields of paths, like a.0 for tuples or a.field for structs (discussed next chapter).
                * Any combination of the above, like *((*a)[0].1).
            * **mutable references**(**unique references**)
              * immutable reference(**shared references**)
                * ![[100. media/image/vaxvKtAi3-.png]]
              * mutable reference
                *  is created with the **&mut** operator
                * ![[100. media/image/TrBSe0qhwK.png]]
            * F permission
              * Another enforcement mechanism  when it doesn't know how long a reference lives. Specifically, when references are either input to a function, or output from a function.
              * lifetime parameters
          * prevent data races at compile time.
            * data race: A *data race* is similar to a race condition and happens when these three behaviors occur:
              * Two or more pointers access the same data at the same time.
              * At least one of the pointers is being used to write to the data.
              * There’s no mechanism being used to synchronize access to the data.
      * Slice Type
        * String slice range indices must occur at **valid UTF-8 character** boundaries.
        * let you reference a **contiguous sequence** of elements in a collection rather than the whole collection. A slice is a kind of reference, it does have **no ownership**.
        * ```rust
    let s = String:from("hello world");

    let hello = &s[0..5];
    let world = &s[6..11];```
        * ![[100. media/image/hAFcF8EAoI.svg]]
      * Struct: 세세한 내용은 생략
      * Enums and Pattern Matching
        * C++처럼 enum 타입 내 필드를 구할 때 범위 지정자 "\:\:" 사용
        * Option enum and advantage over null value
          * enum defined by the standard library and include null
            * ```rust
enum Option<T> {
    None,
    Some(T),
}```
          * you can use Some and None directly without the Option\:\: prefix
            * ```rust
    let some_number = Some(5);
    let some_char = Some('e');

    let absent_number: Option<i32> = None;```
              * The type of some_number is Option<i32>
              * The type of some_char is Option<char>
              * For absent_number, Rust requires us to annotate the overall Option type because the type is not inferable unlike some_number, some_char.
          * Option 이외의 type은 null값이 없음을 compiler가 보장. 하지만 null도 가질 수 있는 타입의 변수를 쓰려면 Option<T>를 정의해야 한다. --> null exception 에러 안 나게.
            * Option<T>의 메소드를 잘 알아야 rust 코딩 원활.
        * match
          * The match expression is a **control flow construct**
          * arm: "조건(패턴) => 실행문" 으로 구성
          * Option<t>와 찰떡궁합
    * coding
      * 2 types in processing return
        * expect
          * fail일 때 에러 메시지 표시하고 종료
          * ```rust
let guess: u32 = guess.trim().parse().expect("Please type a number!");```
        * match
          * Return enum을 처리
          * ```rust
let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };```
      * indent
        * only 4 spaces, not a tab
      * loop
      * source zip
        * ![[100. media/archives/LZ_0H0swgx.zip]]