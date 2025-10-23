## 인증방법
github은 비밀번호 인증을 더는 사용하지 않는다.

두 가지 인증 방법이 있지만 굳이 사용하지 않아도 개인 PC서는 잘 된다. 회사에서 보안 정책 상 쓰기는 한다.

### access token
github에서 access token을 만들어서 매번 로그인할 때마다 사용. -> 불편!!

### ssh
```shell
ssh-keygen -t ed25519 -C "your-email@example.com"
```
-t 옵션에 rsa 등 다른 것도 있지만 ed25519가 가장 최근 것.
