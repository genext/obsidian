---
title: "August 23rd, 2025"
created: 2025-08-23 09:46:12
updated: 2025-08-23 21:14:06
---
  * 할 일
    * 블록체인 개발 with Go
  * 명경지수 -> 명징한 생각
  * 계획: 총 20시간
    * introduction: 16분
    * tour of go: 61분
    * blockchain: 51분
    * explorer: 61분
    * rest api: 92분
    * cli: 30분
    * persistence: 110분
    * mining: 50분
    * transactions: 125분
    * wallets: 160분
    * p2p: 300분
    * bonus: 85분 
    * 일별 계획
      * 8/23 토:
        * introduction
        * tour of go
        * blockchain
        * explorer
        * rest api
        * cli
      * 8/24 일:
        * persistent
        * mining
        * transactions
      * 8/25 월:
        * wallets
        * p2p
      * 8/26 화:
        * p2p
        * bonus
  * 13:14 go 설치
    * 13:19 간단하다. tar.gz 압축 풀고 /usr/local에 go 디렉토리 복사 후 /usr/local/go/bin을 PATH에 추가.
  * 13:23 vsc go extension 설치. go nightly는 이전 버전이어서 설치할 필요 없음. 
  * 13:27 소스 다운.  https://github.com/nomadcoders/nomadcoin.git
  * 13:28 nomadcoder 프로젝트를 열고 main.go 열자마자 자동으로 vsc에서 필요한 도구들 내려받음.
    * ![[100. media/image/4ybC8jG8o3.png]]
  * 13:43 go 프로젝트 시작 명령어
    * ```shell
go mod init github.com/genext/mycoin```
    * go.mod 디렉토리 생성. 
      * go.mod는 node.js의 package.json나 python의 pyproject.md 같은 것.
  * 13:52 go 실행
    * ```shell
go run main.go```
  * 13:55 coding
    * 변수 선언
      * var 변수명 타입
      * ```go
# 타입 직접 지정 변수 생성
var name string = "name"

# 타입 자동 지정 변수 생성(함수 안에서만 가능)
name := "name"
age := 12

# 상수
const name string = "jkoh"

# 함수 정의
func main(a int, b int) 결과 타입 {
}
func plus( a, b int, name string) (int, string) {
  return a + b, name
}

func plus(a ...int) int {
  
}```
  * 14:19 zero day 시청 시작
  * 20:13 마감시한  ^_yzhYNaUi
    * 나는 마감시한을 꼭 지켜야 한다는 생각이 없었다. 마감 시간이 그렇게 절대적이라고 생각하지 않았다. 그런데 그렇지 생학하지 않는 사람들은 집중력을 발휘해서 어떻게든 일을 끝내려고 한다. 타인에 의해 강제된 것으리고 해도 마감시간을 지키려고 노력하는 행위는 그 자체로 가치가 있는 일이었던가? 절대적으로 어떤 것이 옳고 그르다는 것이 없을 때는 비록 내가 보기에 적절하게 보이지 않다고 해도, 불합리하게 보인다고 해도, 사회적으로 어느 정도 확립된 것이면 일단 지키고 보는 것이 순서였을까?
    * 더구나 여러 사람이 모여서 일할  때 주어진 마김시간은 그 중요성이 더 크다...
    * 마찬가지로 어떤 목표를 향해 만든 조직의 수장이 마감시한을 못 박으면 부당한 것이 아닌 한, 이에 반대하는 개인적인 의견을 내세우는 것은 신중한 주의가 필요하다.