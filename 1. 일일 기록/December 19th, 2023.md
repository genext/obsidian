---
title: "December 19th, 2023"
created: 2023-12-19 05:18:49
updated: 2024-02-16 09:41:26
---
  * 08:27 오늘 너무 일찍 일어났다. 
    * 3시 넘어서 화장실 갔는데 너무 추워서 심하게 떨었더니 이후 잠에 쉽게 들지 못하고 엎치락 뒤치락하다가 결국 포기하고 일어나니 4시 넘은지 얼마 안 되었다.
    * 그냥 영어 공부나 하고 동영상 강의 보려다가 roam research에서 블록을 어떻게 쉽게 연결하는지 몰라서 roam research 강의 다시 보았다.
  * [x] 보고서 화면 연동 관련 메가 프롬프트 변경.
    * 메가 프롬프트에 활성화 여부 속성 추가.
    * 메가 프롬프트 등록/수정 화면에 활성화 radio 버튼 추가. 기본값은 비활성.
    * API 작성
      * reportType  값 조회 API
      * input, output 결정.
        * input
          * json
            * id값을 params에 넣어서 서버에게 요청
            * ```javascript
{
  action: 'report',
  gptModelType: ['public'],
  gptModelVersion: ['4.0'],
  reportType: ['interactive'],
  slideType: ['outline'],
  slideLayout: ['cover_1x1'],
}```
        * output
          * 서버는 조회 조건에 맞는 메가 프롬프트의 promptContent를 등록된 순서대로 json으로 돌려줌
            * ```javascript
{
  prompt1: ['암호화된 프롬프트', '...', '...'],
  prompt2: ['...', '...', '...'],
}```
  * [x] 권대영 부장에게 암호화 키, 원본, 암호화된 것 전달.