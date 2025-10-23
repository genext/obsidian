---
title: "December 7th, 2023"
created: 2023-12-07 08:18:29
updated: 2023-12-08 10:22:04
---
  * 08:18 삭제 구현까지 모두 완료. 이제 테스트 반복.
  * 11:32 테스트 데이터 생성 완료 및 테스트 시작.
    * 버그
      * promptModule
        * 페이지 화살표 이동 x
          * totalRecords를 사용
          * 화면에서 currentItems로 전체 데이터를 받아온 다음 페이지별로 보여주는 식으로 로직이 구성되어 있는 것을 삭제하고 서버에서 페이지당 갯수만 돌려주는 식으로 변경.
        * 상단 검색 조건 중 유형에서 system 선택하고 조회
          * ```plain text
query:  {
  '': '',
  promptType: 'system',
  gptModelType: '',    
  gptModelVersion: '', 
  page: '1',
  limit: '20'
}
BSONError: Argument passed in must be a string of 12 bytes or a string of 24 hex characters or an integer
    at new ObjectId (C:\genai\tokaireport\node_modules\bson\lib\bson.cjs:2006:23)
    at buildQueryCondition (webpack-internal:///(api)/./pages/api/v1/report/prompt-management/prompt-module/index.js:309:46)
    at eval (webpack-internal:///(api)/./pages/api/v1/report/prompt-management/prompt-module/index.js:329:43)
    at Array.forEach (<anonymous>)
    at handler (webpack-internal:///(api)/./pages/api/v1/report/prompt-management/prompt-module/index.js:328:28)
    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)
2023-12-07 11:33:51 [error] An error occurred: Argument passed in must be a string of 12 bytes or a string of 24 hex characters or an integer```
  * [x] const promptCodes = promptContent.split('\n');에서 새로 등록할 때 어떻게 처리할지 고민. [[December 8th, 2023]]