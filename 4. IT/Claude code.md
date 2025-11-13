---
title: "Claude code"
created: 2025-06-27 17:22:51
updated: 2025-10-04 18:14:55
---
## 역할: 맥락을 설계한다. software engineering이 아니라 context engineering을 하는 것이다.

## 초보 개발자에게 지시하는 것처럼 배경, 목적, 범위, 원하는 결과를 정리해서 알려야 한다.

## 주의사항
분할 단위: 업무 목적 위주. 기능 단위. 너무 잘게 쪼개지 말자
범위: 리팩토링 여부, 수정 가능한 파일 등 명시
결과: 목적, 성공 기준, 예외 조건 등 명시하여 테스트 프로그램으로 결과를 확인 가능하게.

## Claude code in action 교육
### What is a coding assistant?

claude code는 사용자와 LLM 사이에 있다.

- LLM은 기본적으로 직접 읽고 쓸 수 있는 능력이 없다. 단지 글로 된 내용을 읽고 글로 답할 뿐.
- 에러 메시지 주면서 디버그하라는 사용자 요구를 받으면 claude code는 LLM에게 요청을 보내지만, 동시에 자신에게 있는 **도구**를 알려주면서 "어떤 일(읽기)을 하려면 이런 도구를 쓴다고 알려줌".
- claude code와 LLM 사이 대화는 아주 정형되된 전문(system prompt + instructions + user prompt)들로 구성되었음.
- 사용자가 요청한 일을 처리하기 위해 LLM은 무엇을 해야 할지 파악한 후, 맥락을 파악하고 소스 코드를 읽기 위해 도구 사용 요청(read a file)을 claude code에게 하면 그제서야 claude code가 내부 도구를 써서 파일 내용을 읽어서 보내줌.
- LLM에게 전체 코드를 보내주는 것 아님.

결국 claude code는 다른 시각에서 보면 LLM 능력을 확장할 수 있는 도구 집합이고 계속 새로운 도구(MCP 등)를 추가함으로써 능력을 확장할 수 있다.

### Claude code in action - React Component Generator

실제 사용사례:

- benchmark 테스트 통한 성능 향상
- jupyter notebook을 활용한 파일 분석
- Playwright MCP를 통한 웹 UI 개선
- github action을 통한 배포 전 문제점 포착 
### Project setup

- uigen.zip을 받아서 하려는데 API_KEY 필요하다고...이상한데...그럼 전에 어떻게 claude code로 개발했지? 아무튼 그거 없이도 되지만 진짜로 제대로 쓰려면 필요한 듯.
- 10:55 그런데 api key 예전 것이 있는데 어디에 보관했는지 기억이 나지 않아서 지우고 다시 만들려고 하는데 에러가 나네. "cannot create api keys in the claude code workspace"
- 11:10 내가 원하는 claude code workspace가 아닌 default에서 api key 생성해서 .env에 저장.
- 11:19 일단 npm run dev로 웹 서버를 띄웠다. localhost:3000

![[100. media/image/nn-G9xHI_0.png]]

- 11:32 uigen을 vsc로 열었는데 vsc update가 떴다. .deb 파일을 받아서 그냥 실행하면 install 화면이 뜬다. 그대로 하면 어디에 설치되었는지 모르겠지만 아무튼 version-up 된 것 확인.
### Adding Context

- 11:38 어떻게 이렇게 자꾸 발목이 잡히냐. claude가 왜 갑자기 실행되지 않지? 전에도 그랬는데.
  - vsc를 업그레이드한 후 발생해서...혹시?
  - https://github.com/anthropics/claude-code/issues/1682에 누군가 이미 버그 신고. npm update 때문이라고.  거기 나온 방법대로 하니까 claude 다시 실행 가능.
    ```shell
      rm -rf ~/.npm-global/lib/node_modules/@anthropic-ai/claude-code
      npm install -g @anthropic-ai/claude-code
    ```
    - npm 방식이 아닌 다른 방식으로 설치하는 것을 개발 중이라고...
- AI가 제대로 일하기 위해서 맥락이 필요. 이 때 적절한 지침이 중요. 
- /init 하니까 CLAUDE.md 파일 생성됨.
- CLAUDE.mp 파일 종류
  - project 단위: /init로 성된 것으로 git에도 올라감.
  - local: CLAUDE.local.md: git에 올라가지 않고 공유되지 않음.
  - machine: ~/.claude/CLAUDE.md: 내 pc 전체에 적용되는 것.
- "#"를 쓰면 기억 상태로 들어가며 내 명령을 내가 원하는 CLAUDE.md에 저장하게 할 수 있다. 
- "@"를 쓰면 특정 파일이나 디렉토리를 지정한다.
- "#"와 "@"를 사용한 예.
```plain
# The database schema is defined in the @prisma/schema.prisma. Reference it when ...
```
  - 그럼 CLAUDE.md에 위 내용이 저장.

### Making changes

- 화면을 담아서 UI를 바꾸는 방법.
- 복잡한 일을 시킬 때는,
  - claude code가 계획을 짜서 일하도록 하고 싶을 때
    - =="plan mode"==로 바꿔서 할 수 있다. shift+tab 두 번 누른다. --> wide understanding + 여러 단계가 있을 때
    - 또는 "/model"을 쳐서 나오는 여러 모델 중 "plan mode"가 있는 것을 선택해도 된다.
  - 또는 문장에 **"think [more, hard, a lot, longer]" 또는 "ultrahink"**를 넣으면 된다. 오른쪽으로 갈수록 더 많은 생각을 요구한다.--> 보다 어려운 로직이나 고치기 어려운 버그가 있을 때

### uigen을 다시 처음부터 압축 풀어서 claude code in action 재시작.

- github에 uigen 저장소 만듦.
- github 저장소 만든 후 나오는 안내를 따라 터미널 환경에서 git init부터 시작해서 진행하는데 이상하게 git push할 때 인증 단계가 뜬다.
- vsc를 띄우고 거기 터미널에서 "git add ."으로 모든 소스를 stage에 올리고 commit한 후, push 하면 인증과정없이 바로 push 된다.
### Controlling context
- ESC: 중단
  - 내가 알려줘야 할 것을 빠뜨렸을 때 "#"와 "@"를 사용해서 기억하도록 한 후 "continue" 치면 중단한 지점에서부터 다시 시작.
- double ESC: 이전 대화 목록 표시
  - Claude가 작업한 내용 중 쓸데없는 것(debugging해서 해결했을 경우)이 있을 때 해당 맥락을 안 쓰기 위해서 이전 대화로 가서 새롭게 시작 가능.
- /compact: 이전 작업 내용을 축약해서 Claude가 다음 대화에 활용할 수 있게.
- /clear: 새로운 일을 할 때.
### Custom commands
- 동영상에는 .claude 디렉토리가 이미 있는데 나는 없었다. 하지만 일부러 만들어서 테스트해보니 되긴 된다.
  - .claude/commands/audit.md 작성.
  - "/"만 치면 방금 만든 audit가 목록에 뜬다.
  - 실행 정상 종료.
- 슬래시 명령어 만들 때 인자도 넘겨줄 수 있다.
  - write_tests.md 안에 $ARGUMENTS를 추가.
  - "/write_test use-auth.ts file in the hooks dir" 실행하면 그 파일에 대해서 테스트 실행.
### MCP Servers with Claude Code
- Playwright를 설치하고 "navigate to localhost:3000" 실행하니 진짜로 알아서 브라우저 띄움.
  - mcp 설치할 때 그냥 config 파일에 다음 줄을 추가하기만 해도 된다. 그런데 어떤 파일? -> .mcp.json
```plain
  "mcpServers": {
	      "playwright": {
      		"type": "stdio",
      		"command": "npx",
      		"args": [
      			"@playwright/mcp@latest"
      		],
      		"env": {}
  		}
	},
```
- settings.local.json이 .claude 디렉토리에 저절로 만들어졌다. 여기에 mcp playwright가 그냥 실행하도록 permissions 수정. 
```plain text
{
  "permissions": {
    "allow": [
      "Bash(npm audit:*)",
      "Bash(npm test:*)",
      "mcp__playwright"
    ],
    "deny": []
  }
}
```
- 이걸 이용하는 방법이 playwright github에 안 나와있는데...그냥 browser와 navigate라는 단어만 있으면 되나?
	- daum.net으로 해봤는데 "browser www.daum.net"으로만 해도 된다. 다만, 첫화면에 너무 많은 정보와 그림들이 있다 보니 playwright가 받을 수 있는 제한 용량을 넘는 모양.
- "claude mcp list"를 하면 설치한 mcp가 나오는데 playwright는 uigen 디렉토리에만 나타나네.
### Github integration
- 슬래시 명령어 중 "/install-github-app" 실행하면 github CLI 설치하라고 나옴.
  - 인증에서 에러가 나서 일단 gh(Github CLI) 설치. -> 결국 gh가 설치되어야 전 과정이 제대로 된다.
  - github.com/apps에 여러 도구가 있고 그 중 github.com/apps/claude도 설치
  - api-key 등록: claude code workspace에서 새 API 키 생성이 되지 않지만 default에서 생성한 키로 진행함.
  - 이후 첫 github pull request가 만들어짐.
  - github에서 create pull request, merge 다 진행하면 main 브랜치에 claude action이 추가됨. 이후 새 커밋이나 pull request가 있을 때마다 자동으로 code review가 진행됨.
- git 변경사항을 내 PC로 받음.
  - ![[100. media/image/ApwlGE5LIO.png]]
- yml 파일 수정해서 workflow 바꾼 후, commit
- github 웹에서 issue 등록하면 잠시 후, github의 claude app이 자동으로 issue 테스트하고 결과 보고를 만들어낸다. 우와....
  - 그런데 이슈를 테스트하는 과정에서 내 PC에서 playwright mcp를 실행하려는데...개발 서버가 따로 있을 경우 거기서 테스트할 수 있도록 바꿔야겠네...
- 결론: github action과 claude app를 통합하면, 이슈 디버깅, 문제 해결도 자동으로 처리할 수 있구나...물론 pull request 시, code review로 문제점을 미리 파악할 수 있다.
### 09:51 Hooks and SDK
- Introducing hooks
- Defining hooks
  - 새 프로젝트 query를 받아서 git에 올림.
  - npm run setup 실행.
- Implementing hooks
  - 민감한 정보가 있는 .env만 읽지 못하게 read_hook.js를 수정.
- Gotchas around hooks
  - settings.local.json에 $PWD 사용.
- Useful hooks
  - typescript에서 어떤 함수의 원형을 바꾸면 그 함수를 호출하는 다른 소스도 수정해야 할 때, post-tool-use hook이 typescript compiler를 실행하도록 한다.
  - db query가 이미 있는데도 claude새로 sql을 만들지 않도록 pre-too-use hook에서 query가 있는 디렉토리를 먼저 검색하도록 한다.
- Another useful hooks
  - PreToolUse, PostToolUse 외 다른 것
    - Notification
    - Stop
    - SubagentStop
    - PreCompact
  - Hook에 입력되는 stdin을 보고 싶으면 jq 명령어로 남기는 로그를 보면 된다.
### 11:23 Claude code SDK -> 굳이 프로그래밍하면서 구현할 것이 무엇일지 잘 모르겠다.
- Claude code를 프로그래밍할 수 있다. 
- sdk.ts를 실행하려면 typescript comiler도. "npx ts sdk.ts" -> claude code와 LLM이 주고 받는 내용을 볼 수 있다. 
## [Super claude](https://github.com/SuperClaude-Org/SuperClaude_Framework) 설치해서 Claude code 기능 확장
claude code를 위한 프레임웍
그냥 설치하려고 uv를 쓰면 에러 발생. uv는 pyproject.toml을 검색한다. 즉, 파이썬 프로젝트 환경에서만 uv가 통한다.
### 설치 과정

실패 과정:

- pip3 install SuperClaude -> 이건 윈도우에서만 되는 듯.
- uvx pip3 install SuperClaude -> ubuntu 시스템에 pip만 있어서?
- python3 -m SuperClaude install

성공과정:

- uvx pip install SuperClaude
- uv tool install SuperClaude <- claude 제안
- SuperClaude install

```shell

❯ pip3 install SuperClaude
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.
    
    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.
    
    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
 sudo apt install python3-SuperClaude
[sudo] password for genext: 
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
E: Unable to locate package python3-SuperClaude
❯ uvx pip3 install SuperClaude
  × No solution found when resolving tool dependencies:
  ╰─▶ Because pip3 was not found in the package registry and you require pip3,
      we can conclude that your requirements are unsatisfiable.
❯ uvx pip install SuperClaude
Installed 1 package in 12ms
Collecting SuperClaude
  Downloading superclaude-3.0.0.2-py3-none-any.whl.metadata (13 kB)
Collecting setuptools>=45.0.0 (from SuperClaude)
  Using cached setuptools-80.9.0-py3-none-any.whl.metadata (6.6 kB)
Downloading superclaude-3.0.0.2-py3-none-any.whl (142 kB)
Using cached setuptools-80.9.0-py3-none-any.whl (1.2 MB)
Installing collected packages: setuptools, SuperClaude
Successfully installed SuperClaude-3.0.0.2 setuptools-80.9.0
❯ python3 -m SuperClaude install
/usr/bin/python3: No module named SuperClaude
❯ python3 -m SuperClaude install
/usr/bin/python3: No module named SuperClaude
❯ which SuperClaude
SuperClaude not found
❯ uv tool install SuperClaude
Resolved 2 packages in 58ms
Prepared 2 packages in 144ms
Installed 2 packages in 6ms
 + setuptools==80.9.0
 + superclaude==3.0.0.2
Installed 2 executables: SuperClaude, superclaude
> SuperClaude install
```
### 활용

자동 동작:

```plain text
# 시스템 설계 관련 작업 → architect 자동 활성화
/sc:design --plan

# UI 작업 → frontend 자동 활성화  
/sc:implement --react --component

# 데이터베이스 작업 → backend 자동 활성화
/sc:build --database --api

# 보안 검토 → security 자동 활성화
/sc:analyze --security --vulnerability
```

수동 동작:

```plain text
# 특별히 다른 관점이 필요할 때만
/sc:design --plan --persona-frontend  # 프론트엔드 관점에서 설계
/sc:analyze --api --persona-security  # 보안 관점에서 API 분석
```
## 기타 활용 방법
프롬프트가 길거나 또는 잘 생각할 필요가 있을 때는 파일에 적고 "@"를 이용해서 그 파일을 읽도로 하면  된다.