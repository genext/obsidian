---
title: "AI"
created: 2023-12-24 17:05:37
updated: 2025-10-02 08:38:05
---
## 학습 과정
- [[AI의 학습, 훈련 과정 파헤치기]]

## 활용
- [Developers with AI assistants need to follow the pair programming model](https://stackoverflow.blog/2024/04/03/developers-with-ai-assistants-need-to-follow-the-pair-programming-model/?utm_campaign=the-overflow-newsletter&utm_medium=email&utm_source=iterable)
	- AI codegen tool을 pair programming의 driver로 두고 나는 navigator로 일하면 좋은 성과를 낼 수 있다.
	- It's the AI's job to be fast. It's my job to be good.
		- prompt에서 변수명, 사용할 패턴 등 기본 구상을 넣는다.
		- guardrail을 설정
		- 나온 결과를 테스트
  * [[June 20th, 2025#^8HPi2Gj4_|"AI is the new electricity" by Andrew Ng]]
  * [[June 13th, 2025#^HgyzD5h_M|12:28 무엇인가 학습하고자 할 때 반드시 잊지 말고 해야 할 것은 회상이다. 확실히 에너지가 많이 들어서 본능적으로 회피하려고 한다. 영어를 자유자재로 구사하지 못하기 때문에 문단을 읽을 때마다 요약할 때는 일단 핵심 단어 위주로 하자. 문장으로 요약하는 것은 AI에게 맡기자.]]
  * [[June 3rd, 2025#^PqcawfGL9|AI에게 코딩을 맡길 때 내가 감독자 입장이 되어야 한다. 감독자로서 꼭 알아야 할 것은?]]
  * [[1. 일일 기록/일기#^Jjnxtg_M1|AI는 시스템 중 일부 코드 작성에 유용할지 모르나 아키텍처를 설계하기에는 모자라니 개발자 업무는 아키텍처를 설계하고 코드가 아키텍처에 부합하는지를 검증하는 역할을 하게 될 거라고...흠..]]
  * [[April 6th, 2025#^HVzlU1aqf|AI 문답을 **반복**해서 보면서 기존 지식과 연결(**관계**)하고 결국 핵심을 잡으면서 큰 그림을 그려보기  ]]
  * [[April 6th, 2025#^LwMS6H6xA|위 세 가지 방법을 AI를 활용해서 효과적으로 할 수 있을까?]]
  * [[March 27th, 2025#^u28Jfv7Si|A frustration is present almost everywhere i've observed. 각 어린이에게 맞는 학습 환경...어려운 과제 -> AI로 가능할까?]]
  * AI 활용 개발 도구 - [[Claude code]]
  * How LLMS see the world ^cjrUZOKQA
    * Tokens are what rule the world of LLM. You send tokens to model, pay by the token, and models read, understand, and breathe tokens.
      * ![[100. media/image/N3ZtnH69cB.png]]
    * Why tokenization matters
      * vacabulary management: extraordinary -> extra + ordinary.
      * handling unknown words: biocatalyst -> bio + catalyst
      * Efficiency
      * Model performance
    * How tokens are read by LLM
      * transform symbolic tokens into something neural network can process: numerical representations. token ID.
      * embedding layer
        * tokens are converted to high dimensional vectors called "embeddings" through an embedding layer.
      * similarity search
    * Common tokenization methods
      * Byte Pair Encoding(BPE)
      * WordPiece
      * SentencePiece
      * Unigram
    * Tokens and context windows
      * The newer models, the higher limit of context windows.
      * Gemini 2.5 Pro: 1M+ tokens
    * Token counting
      * API costs
      * context window limits
      * Optimizing prompt desing
    * Tokenization quirks
      * Non-english language
      * Special chracters consume more tokens
      * Number and code in counter-intuitive ways -> more fragmentation -> harder to reason
    * How tokenization impacts LLM performance
      * Spelling and typos
      * Cross-language performance
      * Numerical and mathematical reasong
        * ![[100. media/image/VP3QvzD9QQ.png]]
    * Conclusion
      * understanding tokenization helps you write better prompts, .., grasp both the capabilities and fundamental limitations of AI.
- AI로 개발을 가속하기 ^upDgkstsd
    * 개발자 생산성은 코딩에서만 나오지 않는다. 아래 전과정에 AI가 적용될 수 있다면...
      * 관련 분야 조사
      * 문서 작성
        * 제품 규격 논의 - 회의
        * 아키텍처 설계 - 회의
      * 실제 구현 & 코드 검토
      * 테스트 및 디버깅
      * 모니터링 운영 장애 대응
    * 개발 프롬프트를 작성하기 위한 준비 - 저렴한 모델과 deep research 사용해서 만든다.
      * 정의가 엄밀하지 못하거나 빠진 부분을 AI에게 지적 요청
      * 분야별 지식 -> 지식기반.md로 미리 정리하고 항상 최신으로 유지 필요
    * 개발할 모든 내용을 정리한 거대 개발 프롬프트 - 고급 모델에게 만들게 하고 완성되면 이걸로 개발 시킨다.
      * 만들고자 하는 목표 지정하고 제품요구사항(PRD, System Requirement Specification) 작성을 요청.
        * 길고 풍부한 맥락으로 만들어주면 검토하면서 수정 반복
          * 아키텍처
          * 구조
          * 미래 변동 대비 등
        * 요구 사항 문서 완성 후, 시스템 개발 문서 작성
          * 쪼개기
          * 필요 시, 라이브러리 명시
          * 기간 명시 -> AI가 todo 목록 만듦.
        * 그 외 AI가 항상 주의해야 할 사항
          * 중복된 함수, 기능을 항상 사전에 조사하도록. 또는 내가 명시. <- chunk 때문에 찾지 못하고 중복 기능 개발. 가장 자주 발생.
          * 가장 단순한 해법이 가장 좋은 것
          * 시킨 것만 고치고 상관 없는 것 고치지 마라.
          * 구조 자체를 바꾸지 말라.
          * 주석이 정말 중요!
            * 기존 코드가 있으면, 개발자가 잘못 정한 이름, 급히 수정하면서 이상하게 된 것들이 있다.
          * sql은 자세하게 schema, 데이터, 예문 제공
          * 파이썬은 사용 도구 명시, 가상환경 항상 먼저 실행하라고 지시.
            * sqlalchemy 2
            * pandas 보여줄 때 tabluate와  CJK wide char 켜서 한글표도 예쁘게 보이게.
            * Diskcache 라이브러리와 데코레이터를 활용해 함수 내용 디스크에 캐시
            * json 다룰 때 기본 json 대신 orjson, msgspec 쓰라는 것.(이 때 indent 안 쓰기)
            * 로깅은 loguru 쓰라는 것.
    * 개발 도구
      * 공통: 대화가 너무 길어지면 안 된다.
      * Cursor
        * rule 설정
          * 필수: 모든 행동에서 위에 작성한 md 파일을 참조하라고 지시
          * 그 외는 각자 환경에 맞게.
          * AI 해결책을 잘 봐야 한다. 문제 해결 시, 우회하지 않도록 md에 추가.
        * glob
          * 소스와 관련 파일 다 포함하도록
        * 여기서도 영어로 쓰는 것이 좋다.
        * 너무 큰 파일이 인덱스 되지 않도록. ".cursorignore"에 추가
      * Claude code
        * agent이기 때문에 개발뿐 아니라 다른 일에도 활용 가능. 내 상상력만큼 가능?
        * 핵심은 CLAUDE.md
          * claude 삽질을 사전에 막기
            * 모델 버전을 낮춰서 시도
            * 학습한 오래된 코드, 문법을 쓸 때 -> context7 mcp로 방지
            * 금지 + 바른 방향 함께 기술
            * 바꿔야 할 것이 있으면 사용자에게 확인하도록 지시. # The golden rule: when unsure about implementation details, always ask the developer.
            * 테스트 코드 변경 금지 명시
              * 테스트 실패할 경우, 테스트를 없애거나 기준치를 낮추는 짓을 함.
              * 코드 변경하지 말고 테스트 코드만 만들게 한 후, 테스트 코드를 바꾸지 않도록 다시 명시.
              * API 이름과 인자도 함부로 바꾸지 마라고 해야 함.
              * 테스트 코드가 잘 확립되면 refactoring도 원활하게 됨. 
          * commit 시 CLAUDE.md로 자동으로 수정하도록 지시.  p92 참고
        * 병렬 설정 가능. Git [[Roam/genext-2025-10-05-02-18-30/git#^3dqYQkM6P|worktree #memo]] 이용
          * tmux로 여러 터미널 띄워서 실행 가능.
        * 모델 선택 https://github.com/musistudio/claude-code-router 참고

      * playwright로 화면 개발
        * 서버측에서 돌릴 때는 headless로 돌려라??
    * 개발할 동안 상기할 사항
      * 개발에 필요한 규칙이 생각날 때마다 수시로 md에 추가
        * 항상 테스트 코드도 같이 commit한다.
      * refactoring도 수시로 작은 단위로.
      * commit도 작은 단위로...
      * 결과를 확인하도록 항상 테스트 코드 작성하도록 지시. 그래야 결과를 보고 AI가 스스로 수정.
      * 이렇게 쌓인 규칙과 지식도 소스 코드처럼 저장소에 관리해야 한다.
      * AI 해결책을 잘 봐야 한다. 문제 해결 시, 우회하지 않도록 md에 추가.
    * 개발 중 관리
      * 수시로 LLM에게 상사 역할을 요청. 악플 요청이 가장 효과
    * voice dictation??
    * MCP는 사용자 단위로 설치. ~/.claude/settings.json 관리
      * context7은 원격 연결은 자주 끊어지므로 속편하게 자체 기동으로 설치.
  * RAG 시스템 개발 ^G-1FDuLTG
    * RAG 시스템 만들기 위한 준비
      * Define requirements and desing system architecture
        * 요건
          * 대상: What type of questions will your system answer?
          * 데이터: What data sources will you use (documents, PDFs, web pages, databases)?
            * 데이터 유지 정책: Do you need real-time updates or batch processing?
          * 비기능적 요소: What's your expected query volume and response time requirements?
        * architecture
          * Data flow: Source → Preprocessing → Embeddings → Vector DB → RAG Pipeline → fastAPI API
          * Choose your tech stack (which vector DB, embedding model, LLM)
          * Decide on deployment strategy
      * 개발
        * RAG pipeline
          * preprocessing
            * load - any format? or only PDF?
              * text unicode encoding
            * preprocessing
            * chunking
            * embedding generation
            * store vectorDB
          * RAG retrieval
            * Generate embeddings from query
            * Build the RAG retrieval logic
              * metadata from RDB
              * vector similarity search with metadata?
            * Create the API endpoints
            * Integrate everything into a complete pipeline
        * 사용자 질의 비동기 처리 by SSE?
  * Spring.ai ^0snqeJZpy
    * /src/main/resources/application.yml에 AI 관련 설정.
      * completion-path를 설정해야 한다고? default값이 /v1/chat/completions
    * build.gradle 내용 파악
      * 단순히 dependency만 추가하는 게 아닌 모양. repositories에 llm 관련 내용을 추가. -> spring boot 문서 참고
      * dependency에 모델 관련 의존성과 버전까지. 
    * start.spring.io(spring initializer)에서 AI 라이브러리 추가.
    * chatModel 핵심 컴포넌트. LLM과 기본적인 상호작용 담당하는 인터페이스
    * chatClient 함수형 인터페이스? deprecated? 문서 참조.
    * prompt 클래스
      * Roles: System, User, Assistant, Function
      * Message: List
      * ChatOptions
      * Prompt template
      * 프롬프트를 밖으로 빼내서 /src/main/reosurces/prompts에 *.st로 저장.
        * st: String Template
    * output parsing
      * json 문자열을 json 또는 클래스로?
      * chatResponse
    * version 1.0.0 최신 기능
      * MCP (Model Context Protocol)
      * Function Calling
      * Prompt Template
      * ETL framework
    * Fluent API
      * 메서드 체이닝에 기반한 API interface.
  * MCP(Model Context Protocol) ^lGUGfT_WU
    * 기본 개념
      * AI 모델이 다양한 외부 데이터와 시스템을 효과적으로 사용할 수 있도록 설계한 통신 규약. USB-C 포트에 비유.
      * 조대협의 MCP 10분만에 이해하기 영상
        * MCP는 Json RPC 사용하는데 SSE를 사용.
      * 서버와 클라이언트 사이 Interface 정할 때 조금 유연하게 정할 수 있다.
    * 인증 문제는?
    * Anthropic Model Context Protocol [문서](https://modelcontextprotocol.io/docs/getting-started/intro) 정리
      * architecture overview
        * mcp 서버가 AI 어플리케이션에게 어떻게 맥락을 제공하는지 설명하는 data layer protocol가 개발자에게 가장 유용하다. 
        * mcp는 맥락 교환을 위한 규약에 초점.
        * scope
          * mcp 규격: client/server 구현 요건 정의
          * mcp SDK
          * mcp 개발 도구: [MCP Inspector](https://github.com/modelcontextprotocol/inspector)를 포함한 개발 도구
          * mcp 서버 구현 참조사항
        * concept of mcp
          * 주요 참여자
            * MCP Host
            * MCP Client
            * MCP Server
            * ![[100. media/image/pCF22dDnN6.png]]
          * Layers
            * Data Layer
              * JSON-RPC 2.0 기반 규약 구현
              * 수명주기 관리
              * server feature
                * tools for AI action
                * resources for context data
                * prompts for interaction templates from and to client
              * client feature
                * Server can ask for sample from LLM
                * 사용자 입력을 유도?
                * log
              * 유용한 기능(Utilities)
                * 변경사항 실시간 반영
                * 과거 기록 추적
            * Transport Layer
              * 하부 통신 정의
              * stdio
              * Streamable HTTP 통신
                * SSE
                * bearer, API-key
                * MCP recommends OAuth for token
          *  Data Layer protocol: 여기서 실질적으로 개발자가 client/server 사이 맥락 교환 방식을 정의.
            * 수명 주기 관리: MCP is a stateful protocol
            * MCP는 클라이언트와 서버가 알려줄 수 있는 기본 기능을 정의
              * MCP 서버
                * tools: AI 어플리케이션이 어떤 일(파일 작업, API 호출, DB 질의)을 하기 위해 호출할 수 있는 함수.
                * resources: AI 어플리케이션에게 줄 수 있는 데이터(파일 내용, API 응답, DB 조회 결과)
                * prompt: LLM과 상호작용할 때 도움 되는 재사용 가능한 템플릿(시스템 프롬프트, 예제).
              * 서버 기능 호출 메소드:
                * 기능 탐색: */list
                * 얻기: */get
                * 실행: tools/call
              * MCP 클라이언트
                * sampling
                * elicitation
                * logging
        * examples. -> 문서 참조할 것.
      * Server Concepts: 문서 참조할 것.
      * Client Concepts
        * 클라이언트는 MCP 서버에게 다음 기능을 제공할 수 있고 이를 통해 서버는 사용자와 보다 다양한 상호작용이 가능하게 된다.
        * Sampling: MCP 서버가 LLM에게 어떤 요청(여러 데이터 중 최적 데이터 3건 추출해라)을 보내고 싶을 때 사용.
        * Elicitation: 
        * logging
    * gemini 답변 정리.
      * MCP specification for communication
      * MCP SDK
        * fastmcp(Python)
      * "tools": functions or methods that the server offers to clients
	  
##  Reference
- [[Langchain]]
- [[ollama]] AI를 offline에서 돌릴 수 있게 하는 도구