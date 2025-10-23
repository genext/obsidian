---
title: "February 22nd, 2024"
created: 2024-02-22 09:46:39
updated: 2025-03-23 17:12:37
---
  * Good code
    * coding convention
      * 명명규칙
        * Use business domain terminology(userId -> payerId)
        * Avoid exposing implementation details(sendPaymentToExternalChannel() -> startPayment())
    * [x] builder pattern
    * The Benefits of Immutable Data
      * [x] advantage of immutability
      * If we use a modern IDE, it generates getters and setters for a class by default. While convenient, this enables modifying data whenever we want, which can lead to bugs from seemingly small changes. Martin Fowler includes mutable data as one of the code smells in Refactoring.
      * In functional programming, an object's state cannot change after creation. To update values, we copy them into a new object (deep copy). Immutable data structures allow parallelism by letting multiple processes access and manipulate data without risk of conflicts.