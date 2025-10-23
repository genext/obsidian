---
title: "September 8th, 2024"
created: 2024-09-08 07:05:44
updated: 2024-09-09 09:21:30
---
  * 일요일
  * 06:49
  * 07:44 오라클 관리에서 상태변경(update)은 상태만 바꾸는 것으로 가정하고 그 칼럼만 갱신하고 나머지 abi_info처럼 not null 조건인 칼럼은 update sql에 넣지 말아야 한다. 안 그러면 xml sql에서 abi_info가 자동으로 null이 된다.
    * 만약 선택적으로 넣고 싶다면 다음과 같이 수정.
    * ```sql
 <if test="abiInfo != null">
            , abi_info = #{abiInfo}
 </if>```
  * 08:15 xml에서 update sql 수정.완료
  * [x] 이정주 팀장에게 문의
    * 이건 기관 등록이 아니고 오라클 사용 권한 부여가 아닌가?
    * tb_ca_oracle_grant_bank에 wallte_id는 무엇? 필요한가?
    * transaction_hash는 무엇?
    * 바우처 배포 실행할 때 constructor param 순서 문제
  * vsc에서 neovim 사용
    * 09:24 neovim 최신 버전이 0.10.0으로 바뀌었다. 내 컴퓨터에 설치된 것은 0.9.0이어서 재설치 필요
    * Neovim enable/disable은 Ctrl+Shift+X
    * Ctrl+A 설정하는 대신 ggvG를 하는 것이 낫겠다.
  * [ ] Notion 메모를 Roam으로 옮기기
  * 11:42 향미 식사 신한카드 ^c5Yp3kqNQ