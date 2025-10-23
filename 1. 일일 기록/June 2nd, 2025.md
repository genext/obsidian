---
title: "June 2nd, 2025"
created: 2025-06-02 09:12:14
updated: 2025-06-03 09:26:35
---
  * 09:12 어제 react 설치할 때 왜 node.js가 필요한지 물음.
    * node.js 없이 바로 HTML에 script 태그를 써서 브라우저에 페이지 표현 가능하지만 불편.
    * react는 HTML처럼 보이는 소스를 양산하는데 이를 JSX라고 이것을 자바스크립트로 컴파일하기 위해서 node.js에 포함된 Babel(JSX -> React.createElement call) 필요.
    * **node.js는 개발서버(3000 포트)를 제공.**
  * 11:19 HTTP 보안 요약
    * TCP 3 way handshake
    * client가 서버로부터 인증서 구조(server-intermediate-root) 수신 -> client가 디지털 서명 검증
      * client는 인증서의 디지털 서명을 해당 인증서에 있는 공개키(브라우저에 저장된 값)로 복호화하면 해시값이 나옴.
      * client는 서버가 보낸 인증서 내용을 해시 돌려서 나온 값과 비교.
    * client가 pre-master-secret 생성해서 인증서에 있는 공개키로 암호화해서 서버에서 전달하면 서버는 개인키로 복호화. 이후, 양쪽에서 session key 생성.
    * 이후 session key를 대칭키로 사용해서 암호화.