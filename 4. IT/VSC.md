---
title: "VSC"
created: 2023-09-30 18:10:30
updated: 2025-09-21 10:06:29
---
  * # NeoVim 설정
    * ## Toggle
      * Ctrl + Shift + X -> Enable/Disable
    * Copy(ctrl+c): 주의 vsc 버전이 올라감에 따라 아래 내용 중 일부가 조금 바뀐다.
      * old version(?)
        * Go to File" > "Preferences" > "Keyboard Shortcuts"
        * Click "keybindings.json" link located at the top-right corner of the Keyboard
        * In the keyboard shortcut editor, search for 'Copy in the search bar.
        * Look for "Editor: Copy'
        * Press ctrl+c
        * Search for "Copy With Syntax Highlighting" in the search bar.
        * Click on the pencil icon (Edit keybinding) next to "Editor: Copy With Syntax Highlighting."
        * Press ctrl+c
      * new 2024.12.13
        * ctrl + shift + x 눌러서 설치 확장판 창 띄우기
        * neo vim 선택
        * 설정 아이콘 클릭 -> keyboard shortcuts 선택
        * 검색창에 editor: copy 입력
        * Search for "Copy With Syntax Highlighting" in the search bar.
        * keybinding 클릭해서 ctr + c 입력
    * multitab switch
      * Press Ctrl + w, release, and then press w(next tab) or  press Shift + w(previous tab).
    * copy all contents
      * Open command palette(ctrl+shift+p)
      * type "Open Keyboard Shortcuts(JSON)"
      * Add this configuration
        * ```plain text
{
    "key": "ctrl+a",
    "command": "editor.action.selectAll",
    "when": "editorTextFocus && neovim.mode != 'insert'"
}```
  * 단축키
    * ctrl+p: 파일명으로 검색.
  * extension
    * Rest Client by Huachao Mao
      * project 폴더에 http 확장자 가진 파일을 만들어서 rest api url 등록하면 자동으로 "Send Request" 버튼이 생기고 이걸 누르면 rest api 호출 테스트 실행.
      * GET
        * ```plain text
http://localhost:4000/```
      * POST
        * ```plain text
POST http://localhost:5000/transactions

{
    "to":"lynn",
    "amount":10
}```