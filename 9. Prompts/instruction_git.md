그동안 "roam research"를 썼다. 이제 obsidian으로 옮기려고 한다. 일단 "roam research"의 export 기능을 사용해서 obsidian으로 import했다. 하지만 깔끔하게 import 되지 않았다. 

그래서 markdown으로 된 예전 roam research 기록을 obsidian 형식에 맞게 변경하려고 한다.

1. 원천과 목적지
원천: "/home/genext/Documents/Obsidian Vault/Roam/genext-2025-10-05-02-18-30/git.md"
목적지:  "/home/genext/Documents/Obsidian Vault/3. IT/git"

2. 옮길 내용
알다시피 "roam research"는 블록이 기본 단위이다. 그래서 가장 상위에 있는 "*"까지 폴더로 잡는다. 예를 들어, 위 원천에 있는 git.md를 보면 title이 "git"이고 바로 최상위 "*"는 Basics와 [[git commit 취소]], [[Rebase]]가 있는데 Basics만  폴더가 된다. [[git commit 취소]], [[Rebase]]은 링크를 넣는 대신 아예 해당 페이지를 Basics 폴더 안에 note로 따로 만든다.
위 최상위 "*"외 나머지 indented "*"은 obsidian의 note로 잡아야 하고 거기에 속하는 것은 해당 note에 들어간다. 

3. media 파일 처리
만약 그림 파일이나, 음성 파일이 있다면 아마도 해당 파일을 가리키는 link가 있을 것이다. 그 위치에 있는 media 파일을 "/home/genext/Documents/Obsidian Vault/100. media"에 있는 audio, image에 파일 형식에 따라 적절한 위치에 저장하고 링크도 거기에 맞게 수정한다.