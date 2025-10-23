---
title: "OOP"
created: 2024-10-24 13:35:35
updated: 2025-06-13 09:43:32
---
  * oop(Object Oriented Programming, 객체 지향 설계) 4대 핵심 원칙
    * encapsulation 
    * abstraction 
    * inheritance
      * 상속이 복잡해질 경우, composition이 나을 때가 있다.
    * polymorphism
  * 일급 컬렉션(First Class Collection)
    * 정의: 컬렉션을 포함한 클래스이지만 다른 멤버 변수가 없다. 
    * 만드는 방법
      * 기본 타입 예제
        * 기본 타입으로 만든 것
          * ```java
Map<String, String> map = new HashMap<>();
map.put("1", "A");
map.put("2", "B");
map.put("3", "C");```
        * 일급 컬렉션으로 만든 것
          * ```java
public class GameRanking {
  private Map<String, String> ranks;

  public GameRanking(Map<String, String> ranks) {
    this.ranks = ranks;
  }
}```
      * 클래스 예제
        * 기본 클래스로 만든 것
          * ```java
public class Car {
    private String name;
    private String oil;
    // ...
}```
        * 일급 컬렉션으로 만든 것
          * ```java
// List<Car> cars를 Wrapping
// 일급 컬렉션
public class Cars {
    // 멤버변수가 하나 밖에 없다!!
    private List<Car> cars;
    // ...
}```
    * 이점
      * 업무(business/domain) 종속성을 보장.
        * 예제
          * 6자리 로또 복권: 단순히 List<Integer> lottoNumbersi만 선언하고 여기에 값을 넣으면 끝?
          * LottoTicket이라는 클래스에 6자리 한계와 중복 제거 기능을 넣으면 자체적으로 LottoTicket을 설명한다.
            * ```java
package kr.or.cbdc.application.voucherManage.vc.manage.controller;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class LottoTicket {
    private static final int LOTTO_NUMBER_COUNT = 6;

    private final List<Integer> lottoNumbers;     // Now wrapped collection

    public LottoTicket(List<Integer> lottoNumbers) {
        validateCount(lottoNumbers);
        validateDuplicate(lottoNumbers);
        this.lottoNumbers = lottoNumbers;
    }

    public getLottoTicket() {
      return lottoNumbers;
    }
  
    private void validateCount(List<Integer> lottoNumbers) {
        if (lottoNumbers.size() != LOTTO_NUMBER_COUNT) {
            throw new IllegalArgumentException("로또 번호는 6개만 가능합니다.");
        }
    }
    
    private void validateDuplicate(List<Integer> lottoNumbers) {
        Set<Integer> nonDuplicateNumbers = new HashSet<>(lottoNumbers);
        if (nonDuplicateNumbers.size() != LOTTO_NUMBER_COUNT) {
            throw new IllegalArgumentException("로또 번호는 중복될 수 없습니다.");
        }
    }
}```
        * 편의점에서 파는 각 상품마다 상태와 행위를 묶어서 클래스 정의하면 상품 갯수 제한 확인 작업이 필요할 때 각 상품이 자체적으로 갯수 제한 기능을 갖추기 때문에 편의점이 모든 상품의 갯수를 일일 확인하는 중복을 줄일 수 있다.
      * VO처럼 컬렉션도 immutable 보장하고 싶다면
        * 위 LottoTicket 객체는 완전 불변이 아니다. final은 재할당만 금지할 뿐 lottoNumbers.add(...)를 막지 못한다.
        * 1차 수정: 새 메모리 생성(깊은 복사)
          * ```java
package kr.or.cbdc.application.voucherManage.vc.manage.controller;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class LottoTicket {
    private static final int LOTTO_NUMBER_COUNT = 6;

    private final List<Integer> lottoNumbers;     // Now wrapped collection

    public LottoTicket(List<Integer> lottoNumbers) {
        validateCount(lottoNumbers);
        validateDuplicate(lottoNumbers);
        this.lottoNumbers = new ArrayList<>(lottoNumbers);  // 할당을 한 번 한다. 깊은 복사 원리와 비슷.
    }
    ...    
}```
        * 2차 수정: getter return 값 변경
          * ```java
package kr.or.cbdc.application.voucherManage.vc.manage.controller;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class LottoTicket {
    private static final int LOTTO_NUMBER_COUNT = 6;

    private final List<Integer> lottoNumbers;     // Now wrapped collection

    public LottoTicket(List<Integer> lottoNumbers) {
        validateCount(lottoNumbers);
        validateDuplicate(lottoNumbers);
        this.lottoNumbers = new ArrayList<>(lottoNumbers);  // 할당을 한 번 한다. 깊은 복사 원리와 비슷.
    }

    // reference를 그냥 돌려ㅇ주지 않도록 한다.
    public getLottoTicket() {
      return Collections.unmodifiable(lottoNumbers);
    }
    ...    
}```
      * 상태와 행위를 한 클래스에서 관리
      * 이름이 있는 컬렉션: 컬렉션 클래스 만들 때 업무 상 의미있는 이름으로 컬렉션 명을 쓰면 동일한 구조라도 이름으로 구분할 수 있다.
  * VO(Value Object)
    * 속성들을 묶어서 특정값을 나타내는 객체로 기본키로 식별되는 Entity와 구별된다.
    * **equals & hash code** 메서드를 재정의해야 한다
      * 객체 변수 자체는 객체가 저장된 메모리 주소로 동일한 속성값을 가져도 "=="로 비교하면 다르다고 나온다. --> 속성값을 기준으로 비교해야 할 때는?
      * ```java
public class AAA {
...
    @Override
    public boolean equals(final Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        final Point point = (Point) o;
        return x == point.x &&
                y == point.y;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }
...
}```
    * 수정자(setter)가 없는 불변 객체(immutable)여야 한다 --> 위 일급 컬렉션 참고.
      * 두 사람이 동일한 주문을 했다고 첫 번째 주문을 복사해서 두 번째 주문을 만들면 안 된다.(얕은 복사)
      * ```java
public class Order {
  private String restaurant;
  private String food;
  private int quantity;
  
  public Order(String restaurant, String food, int quantity) {
    this.restaurant = restaurant;
    this.food = food;
    this.quantity = quantity;
  }
  
  // only getter..
}

public static void main(String[] args) {

  Order 첫번째주문 = new Order("황제떡볶이", "매운떡볶이", 2);
  // 첫번째주문 = {restaurant='황제떡볶이', food='매운떡볶이', quantity=2}

  Order 두번째주문 = new Order("황제떡볶이", "매운떡볶이", 2)
  // 두번째주문 = {restaurant='황제떡볶이', food='매운떡볶이', quantity=2}

  두번째주문 = new Order("황제떡볶이", "안매운떡볶이", 3)  //** 주문 변경
  // 첫번째주문 = {restaurant='황제떡볶이', food='매운떡볶이', quantity=2}
  // 두번째주문 = {restaurant='황제떡볶이', food='안매운떡볶이', quantity=3}
  
}```