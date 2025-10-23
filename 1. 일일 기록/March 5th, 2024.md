---
title: "March 5th, 2024"
created: 2024-03-05 08:43:23
updated: 2024-03-15 20:29:09
---
  * 08:43: 어제 잠도 안 오고 그냥 공부나 더 하다가 늦게 잠자리에 들어서 오늘 늦게 일어남. 점점 불안해진다. 3월에 프로젝트 구해야 하는데 못 구할 가능성이 클 지도 모르겠다.
  * 오늘 할 일
    * javascript review
      * interview questions
  * 15:07 javascript 공부하다가 [[ollama]]를 텍스트 환경에서 사용하는 것이 불편해서 web ui를 찾아서 설치할 예정. 
    * [[docker]] 설치
  * 19:18 내 큰 노트북에 [[docker]] for windows 및 WSL 설치
    * wsl2는 windows 10 이상에 기본으로 설치됨. 아래 명령 바로 실행 가능.
    * wsl로 ubuntu 설치
      * ```shell
wsl --list --online

다음은 설치할 수 있는 유효한 배포 목록입니다.
'wsl --install -d <배포>'를 사용하여 설치하세요.

NAME                                   FRIENDLY NAME
Ubuntu                                 Ubuntu
Debian                                 Debian GNU/Linux
kali-linux                             Kali Linux Rolling
Ubuntu-18.04                           Ubuntu 18.04 LTS
Ubuntu-20.04                           Ubuntu 20.04 LTS
Ubuntu-22.04                           Ubuntu 22.04 LTS
OracleLinux_7_9                        Oracle Linux 7.9
OracleLinux_8_7                        Oracle Linux 8.7
OracleLinux_9_1                        Oracle Linux 9.1
openSUSE-Leap-15.5                     openSUSE Leap 15.5
SUSE-Linux-Enterprise-Server-15-SP4    SUSE Linux Enterprise Server 15 SP4
SUSE-Linux-Enterprise-15-SP5           SUSE Linux Enterprise 15 SP5
openSUSE-Tumbleweed                    openSUSE Tumbleweed

wsl --install -d Ubuntu-22.04
```
    * wsl로 Ubuntu 설치
      * user:  내 우분투와 동일하게 genext 생성 및 비밀번호 설정 후
      * wsl.exe --update 실행
    * ubuntu-22.04 LTS가 윈도우즈 시작 메뉴에 나타나면 설치 완료
    * [[ollama]]-webui 이미지를 도커에서 실행 완료 http://localhost:3000