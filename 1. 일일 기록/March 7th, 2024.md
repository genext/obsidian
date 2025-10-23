---
title: "March 7th, 2024"
created: 2024-03-07 07:57:40
updated: 2024-03-15 23:00:25
---
  * 07:57 어제 조금 일찍(?) 잠자리에 들어서 오늘 아침에 평소보다 약간 일찍 일어났다. 오늘은 그냥 스프링부트를 즐긴다고 생각하고 하자.
  * 09:37 some antivirus s/w can interfere with the IDE build process, causing **build** to run dramatically **slower**. change setup of Windows defender.
    * In windows security, click on "Virus and threat protection"
    * click on "Managing settings"
    * click on "Add or remove exclusions" --> add directories.
  * 10:02 spring boot demo application을 실행하면 8080 포트가 이미 사용 중이라고 나옴. ollama web ui가 그 포트를 사용. 그래서 [[docker]] run을 다시 실행하면서 8090으로 바꿨는데 이제는 ollama web이 에러.
    * 재부팅해도 안 돼서 포트를 다시 원래대로 8080으로 바꿨더니 된다. 그럼 [[docker]] 문제? 아니면 8090포트가 이미 사용 중?
      * docker run에서 앞 포트가 내 시스템 포트고 뒤 포트가 docker 포트다. 즉 [[ollama]] web ui가 docker 내에서 8080 쓰는 것으로 고정되어 있었음.
    * demo application을 처음에 실행할 때 바로 결과가 안 나와서 또 실행을 누른 바람에 뒤에 실행한 것이 에러를 나타낸 것임. 다시 하나만 실행하니 빌드 후에 제대로 실행함. intelliJ에서 빨간 색으로 jdk java.lang 오브젝트를 못 찾는다고 나온 것도 사라짐.
  * 10:17 국민연금
    * 총 243개월 납부해야 하는데 현재 나는 193개월 납부해서 50개월 모자란다.
    * 앞으로 4년 2개월 더 낸다면 243개월 채운다.
    * [x] 추후 납부로 추가 가능할까?
  * 12:38 demo application을 실행.
    * terminal에서 root 디렉토리로 가서 "gradlew bootRun" 실행 또는 실행 버튼 누르기.
  * 13:15 unit test를 하려는데 잘 안 된다. spring tutorial의 첫 번째 test 예제는 포기하고 두 번째 예제를 하는데
    * error: package org.junit.jupiter.api does not exist import org.junit.jupiter.api.Test;
    * 알고 보니 main 디렉토리가 아닌 test 디렉토리에 unit test 프로그램이 들어가 있어야 하는 것이었다. 
  * 15:00 공부 방향을 잡기가 힘들다...어떤 일이라도 할 수 있다고 해도 특급 엔지니어라고 할 수 있을까? 일단 개발 자체는 그렇게 중요하지 않은 듯...시스템 설계 측면에서 아는 것이 많아야 하지 않을까?
    * 또는 경력이 주는 이점 또는 경력이 많은 개발자에게 기대하는 것은 무엇일까?
      * 실수를 줄이는 것...시스템을 완성하는 데 필요한 수많은 요소들을 빠뜨리지 않는 것.
  * 16:35 업무 제안이 왔다. 블록체인 개발이다!! 그런데...정규직이다..젠장. 어쨌든 블록체인 공부할 동기가 생겼다. 일단 [[Golang]]를 다시 공부