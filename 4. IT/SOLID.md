---
title: "SOLID"
created: 2025-03-28 11:08:20
updated: 2025-06-13 09:20:39
---
  * S: Single Responsibility Principle(SRP)
  * O: Open to change, closed to modification
    * Abstraction and base classes -> class hierarchy
    * 결제 방식이 새로 나올 수 있으면 interface 메소드로 정의. 기존 결제 코드는 바뀌지 않고 새 클래스가 그 interface 를 구현하면 된다.
  * L: Liskov Substitution
    * polymorphism + well defined class(interface) hierarchy
    * 자식 클래스 자리에 부모 클래스가  쓰여도 문제 없어야 한다. interface를 타입처럼 사용.
  * I: Interface Segregation
    * 관련 기능을 구분, 분리
  * D: Dependency Inversion
    * 프린터 드라이버 interface 예.