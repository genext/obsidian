# Andrew Ng 수업 - DeepLearning.AI

[강의 소스](https://github.com/jkoh-AI/agenticAI)

## 1. 들어가기
AI agent를 효과적으로 개발하려면 평가와 에러 분석을 제대로 해야 한다.
- AI agent를 적용할 수 있는 분야가 눈에 보인다. 결과가 좀 느리게 나오더라도 기다릴 수 있는 분야가 AI agent가 비집고 들어갈 수 있다. 신속하게 바로 결과가 나와야 하는 곳에 AI agent를 적용할 수 없다.
- 여기서도 상식적으로 생각해봄직한 것이 복잡한 일을 잘 쪼개서 단위 일도 잘 나누는 능력이 에이전트 개발에서 중요하다.

### Degrees of autonomy
the degree to which agentic workflows can be autonomous.
Debating about what true agent is looks unnecessary, which is why Andrew Ng started using term "agentic". If we use it as an adjective rather than a binary, it's either an agent or not, then we're going to have to acknowledge that systems can be agentic to different degrees.

- 기존 어플리케이션과 agentic AI의 차이와 agentic AI의 이점?
	- 기존에 할 수 없었던 일을 AI로 구현할 수 있다?
	- LLM에게 단순히 단발성으로 코딩 시키는 것보다 agentic workflow를 만들어서 코딩 시키면 훨씬 나은 성능을 보인다. 
	- 일을 잘 나눠서 업무 흐름을 잘 짜면 병렬 실행이 가능해서 인간보다 빨리 결과를 낼 수 있다. 하지만 컴퓨터보다는 빠르게 못한다.
![[Pasted image 20251105090325.png]]	
---
## 2. 개발
### Decomposition and building blocks for agentic workflow
![[Pasted image 20251105092235.png]]

### Disciplined Evaluation
객관적으로 수치로 평가할 수 있는 것은 프로그램 코딩해서 수행하고 그렇지 않은 주관적인 것은 평가지표를 만들어서 생산물을 만든 것이 아닌 다른 LLM에게 평가하도록 할 수 있다.
![[Pasted image 20251105093917.png]]

### Agentic design patterns
![[Pasted image 20251105094050.png]]

### Reflection
![[Pasted image 20251105095202.png]]
![[Pasted image 20251105095253.png]]
**실행 결과 등, LLM 외부 의견이 보다 효과적이다.

아래 각 단계를 함수로 만든다. utils에 AI 모델에게 prompt를 전송하는 함수가 있다.
- draft 생성 요청 prompt를 AI model에게 보내서 draft 받음.
- 생성된 draft를 검사, 비판하도록 요청하는 prompt 작성해서 draft와 함께 AI model에게 전송해서 결과 받음.
- 검사 결과를 draft와 함께 보내면서 개선을 요청하는 prompt를 AI model에게 전송하여 최종 개선된 결과 받음.
![[Pasted image 20251105103031.png]]

- [ ] aisuite 모듈 분석 중요! LLM이 내 함수를 호출할 수 있는 기전이 여기에 있다.

## Eval
일단 만들어 놓고 평가를 반복하면서 결과를 보고 계속 개선하는 것이 최선. 
AI 처리 결과는 기본적으로 불확실하다. 그래서 평가를 통해 이러한 불확실성을 최소한도로 해야 한다.
평가할 때 객관적 기준과 주관적 기준, 결과를 검증하는 예가 있는지 등이 중요한 고려사항. 평가 자체도 일이고 양이 많아질 수 있기 때문에 이것도 프로그램뿐 아니라 AI(특히 주관적 평가)를 활용해서 자동화하는 것도 빠질 수 없다.

## disciplined error analysis
agentic ai workflow에서 각 단계별 결과를 보고 어디서 가장 불만족스러운지를 엑셀 형식으로 기록하면 어디를 집중적으로 개선해야 할 지 알 수 있을 것 이다.

- [ ] 다른 사람의 prompt를 많이 읽는 것도 도움이 될까? 어디서 확인하지?

### Tools
#### - protocol
현재는 LLM이 외부 도구를 호출할 수 있도록 훈련되어 있지만 예전에는...
![[Pasted image 20251105104845.png]]
현재 대부분 이런 식으로 구현...
![[Pasted image 20251105105714.png]]
#### - code execution tool
python exec() or docker environment.

### Latency, cost
좋은 에이전트는 응답이 적절한 시간 내에 나오면서도 비용이 많이 들지 않는 것.

### 아. 이렇게 활용할 수 있는 거구나...
DB 데이터 조회할 때 제품 설명 따로 조회한 후, 재고 확인, 가격 확인을 각각 따로 기능 함수로 제공하면 AI가 이 중에서 문맥에 따라 필요한 것을 조합하게 하는 것이구나...
AI의 불확실성이 오히려 장점이 되겠구나...그런데 DB 질의에 특화된 AI가 있다면 이런 에이전트를 만들어도 곧 쓸모가 없어지게 되겠네...

변화를 간단하게 표현하면,
1. SQL에 모든 상황, 사업 맥락, 필요 조건 등을 때려넣어서 한 업무 영역을 운영하는 관련 모든 지식을 모두 SQL에 때려넣었던 시절이 있었는데...
2. 사업 운영계층과 데이터 계층을 분리해서 비교적 정제된 sql문과 정해진 업무 규칙을 담은 서버 코드로 분리된 시절에 이어,
3. AI가 주어진 업무 규칙에 따라 알아서 sql을 호출해서 결과를 보여주는 시대로 온 것 같다. 즉 불확실한 상황에 유연하게 대응할 수 있는 에이전트를 만드는 시대다.

### multi agent
## communication patterns
