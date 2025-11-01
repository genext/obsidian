# Andrew Ng 수업 - DeepLearning.AI

[강의 소스](https://github.com/jkoh-AI/agenticAI)

# Reflection
아래 각 단계를 함수로 만든다. utils에 AI 모델에게 prompt를 전송하는 함수가 있다.
- draft 생성 요청 prompt를 AI model에게 보내서 draft 받음.
- 생성된 draft를 검사, 비판하도록 요청하는 prompt 작성해서 draft와 함께 AI model에게 전송해서 결과 받음.
- 검사 결과를 draft와 함께 보내면서 개선을 요청하는 prompt를 AI model에게 전송하여 최종 개선된 결과 받음.

- [ ] aisuite 모듈 분석 중요! LLM이 내 함수를 호출할 수 있는 기전이 여기에 있다.