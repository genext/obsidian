---
title: "September 27th, 2023"
created: 2023-09-27 05:14:45
updated: 2023-09-27 14:52:56
---
  * 어제 11시쯤에 잠들어서 3:45분에 깼는데 느낌상 잠을 더 잘 수 없을 것 같아서 일어남.
  * 영어 단어 외우기, react hook[[React#^dbBOkDWe7|Hooks]], [[Elasticsearch]]를 정리.
  * fetch와 axios의 에러 처리 방식 차이.
    * axios는  then/catch로 하면 catch에서 모든 에러를 처리할 수 있다. 다만 네트웍 에러는 응답 결과가 조금 다르니 주의.
      * axios는 HTTP 코드값이 에러여도 promise를 reject하지 않으므로 then 블록에서 처리 가능하지만 catch 절에서 모든 에러 처리 가능하기도 하다. 
    * fetch는 HTTP 에러 코드와 네트웍 에러를 따로 처리.  