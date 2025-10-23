---
title: "August 18th, 2024"
created: 2024-08-18 07:17:24
updated: 2024-10-23 16:24:07
---
  * 07:15 출근
  * 오늘 할 일
    * 업무 메일 확인
    * fnReadDetail 데이터 모두 확인 및 엑셀 다운로드 업로드 구현

  * 명경지수
  * 07:22 fnReadDetail 데이터 항목 연결 확인.
  * 08:37 아이고 엉뚱한 데서 헤맸다. 단지 vouchId가 잘못 선택된 것인데...chatGPT가 헤매는 것도 당연하다. 문제가 없는 것을 보여주면서 문제를 찾으라 했으니..ㅋㅋ
  * 09:09 이용자 사용처 목록 하단 조회 표시 시작
  * [x]  fnReadApplcntList("/applcnt/" + selectId!).then((response: Array<IfTbVcApplcnt>) => {...}이 에러가 나는 이유를 getApi에서 확인. Promise<V | null> 이것 때문인 것 같은데..
    * error message
      * ```plain text
TS2345: Argument of type '(response: Array<IfTbVcApplcnt>) => void' is not assignable to parameter of type '(value: IfTbVcApplcnt[] | null) => void | PromiseLike<void>'.
  Types of parameters 'response' and 'value' are incompatible.
    Type 'IfTbVcApplcnt[] | null' is not assignable to type 'IfTbVcApplcnt[]'.
      Type 'null' is not assignable to type 'IfTbVcApplcnt[]'.```