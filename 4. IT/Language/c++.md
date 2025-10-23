---
title: "c/c++"
created: 2024-02-26 11:40:05
updated: 2025-09-17 12:53:28
---
  * interview question [source](https://www.geeksforgeeks.org/cpp-interview-questions/)
    * reference
      * basics
        * an alias of the already existing variable.
        * changes made in the reference variable will be reflected in the already existing variable.
        * ```c++
int GFG = 10;

// reference variable
int& ref = GFG;```
      * reference/pointer
        * {{table}}
          * Reference
            * Pointer
          * The value of a reference cannot be reassigned
            * The value of a pointer can be reassigned
          * It can never hold a *null *value as it needs an existing value to become an alias of
            * It can hold or point at a *null* value and be termed as a *nullptr* or *null pointer*
          * It cannot work with arrays
            * It can work with arrays
          * To access the members of class/struct it uses a ‘ **. **‘
            * To access the members of class/struct it uses a ‘ **-> **‘
          * The memory location of reference can be accessed easily or it can be used directly
            * The memory location of a pointer cannot be accessed easily as we have to use a dereference ‘ *** **‘
    * prefix/postfix
      * {{table}}
        * prefix
          * postfix
        * It executes itself before **‘; ‘ **
          *  It executes itself after **‘; ‘ **
        * Associativity of prefix ++ is right to left
          * Associativity of postfix ++ is left to right
    * new/malloc
      * {{table}}
        * new
          * malloc
        * new is an operator which performs an operation
          * malloc is a function that returns and accepts values
        * new calls the constructors
          * malloc cannot call a constructor
        * new is faster than malloc as it is an operator
          * malloc is slower than new as it is a function
        * new returns the exact data type
          * malloc returns void*
    * virtual function/pure virtual function
      * related to polymorphism
      * keyword 'virtual' before function name.
      * {{table}}
        * virtual function
          * pure virtual function
        * virtual void myFunction() {...}
          * virtual void myFunction() = 0;
        * A Virtual Function is a member function of a base class that can be redefined in another derived class.
          * A Pure Virtual Function is a member function of a base class that is only declared in a base class and **requires to be defined** in a derived class to prevent it from becoming an abstract class
        * A virtual Function has its definition in its respective base class.
          * There is no definition in Pure Virtual Function and is initialized with a pure specifier **(= 0).**
        * The base class has a virtual function that can be represented or instanced; In simple words, its object can be made.
          * A base class having pure virtual function becomes abstract that **cannot be represented or instanced**; In simple words, it means its object cannot be made.
    * polymorphism
      * {{table}}
        * compile time polymorphism(static binding)
          * runtime polymorphism(late binding)
        * function/operator overloading
          * function overriding, virtual function
    * constructor
      * {{table}}
        * default
          * parameterized
            * copy
            * takes a reference to an object of the same class as an argument.
            * ```c++
Sample(Sample& t)
{ 
  id = t.id; 
}```
    * virtual destructor
      * When destroying instances or objects of a derived class **using a base class pointer object**, a virtual destructor is invoked to free up memory space allocated by the derived class object or instance.
      * It is advised to make your destructor virtual whenever your class is polymorphic.
    * delete
      * basics
        * it destroys or deallocates array and non-array(pointer) objects which are created by new expressions.
        * ```c++
int GFG = new int[100]; 
   // uses GFG for deletion 
   delete [] GFG;```
      * delete[]
        * {{table}}
          * delete[]
            * delete
          * a whole array
            * only one single pointer
          * **new[]** --> **delete[]**
            * **new** --> **delete**
    * friend
      * class
        * a class that can access both the protected and private variables of the classes where it is declared as a friend.
        * ```c++
class Class_1st { 
  // ClassB is a friend class of ClassA 
  friend class Class_2nd; 
  statements; 
} 

class Class_2nd { 
  statements; 
}```
      * function
        * a function used to access the private, protected, and public data members or member functions of other classes.
    * STL
      * ![[100. media/image/fXBskQhD2V.png]]
    * volatile
      * to inform the compiler that the value may change anytime.
      * to prevents the compiler from performing optimization
    * storage class
      * ![[100. media/image/CtMa8deXhq.png]]
    * keyword "mutable"
      * used only on a class data member to make it modifiable even though the member is part of an object declared as const.
    * keyword "auto"
      * use "type inference capabilities"
  * 복잡한 선언 이해
    * [geeksforgeeks](https://www.geeksforgeeks.org/complicated-declarations-in-c/)