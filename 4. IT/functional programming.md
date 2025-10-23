---
title: "functional programming"
created: 2023-09-14 20:16:02
updated: 2024-09-08 12:44:10
---
  * first-class function ^fQpSX_Nq4
    * functions are treated as "**first-class citizens.**"
      * Assigned to variables
      * Passed as arguments to other functions
        * allowing for higher-order functions.
      * Returned from functions
      * Stored in data structures
    * why matters?
      * Higher-order functions
        * Functions that take other functions as arguments or return them. ex: map, reduce, and filter.
      * Closure ^tXmxEJPe9
        * [x] The ability of inner functions to remember the environment in which they were created
        * example
          * ```javascript
function outerFunction() {
    let counter = 0;
    
    return function innerFunction() {
        counter++;
        return counter;
    };
}

const increment = outerFunction();  // innerFunction returned, and it "remembers" counter
console.log(increment());  // Output: 1
console.log(increment());  // Output: 2
console.log(increment());  // Output: 3```
          * In this example:
            * innerFunction is a closure because it has access to counter, even though outerFunction has finished executing.
            * The counter variable persists between calls to increment() because of the closure.
        * In C?
          * function pointers or static variables
          * ```c
#include <stdio.h>

void counter() {
    static int count = 0;
    count++;
    printf("Count: %d\n", count);
}

int main() {
    counter();  // Output: Count: 1
    counter();  // Output: Count: 2
    counter();  // Output: Count: 3
    return 0;
}
```
      * Currying and Partial Application
        * Breaking down a function that takes multiple arguments into a series of functions that each take a single argument, thereby enabling more reusable and composable code.
  * first-class citizen
    * an entity (such as a **value**, variable, or function) that can be treated as **any other value** in the language.
    * By treating functions, values, and data structures as first-class citizens, functional programming provides several benefits.
      * Composability
        * First-class functions enable you to break down complex operations into smaller, reusable components that can be combined in different ways. This makes your code more modular and easier to maintain.
      *  Purity
        * Functions that take input values and return output values without mutating any state are considered pure. Pure functions have several advantages, such as being easy to test, predictable, and composable.
      * Immutability
        * By avoiding mutation of data structures, functional programming promotes immutability, which helps prevent bugs and improve performance. Instead of modifying a data structure in place, you create a new copy with the desired changes and return it as a value.
      * Referential transparency
        * Functions that are pure and referentially transparent can be replaced by their output values without changing the behavior of the program. This makes your code easier to reason about and optimize.