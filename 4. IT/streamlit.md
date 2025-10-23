---
title: "streamlit"
created: 2024-03-21 12:15:27
updated: 2024-03-21 15:16:46
---
  * hello world
    * home.py
      * ```python
import streamlit as st

st.title("Hello World")```
    * streamlit 서버 실행
      * ```shell
streamlit run home.py```
      * 실행 결과 화면
        * ![[100. media/image/5lUicyyQDu.png]]
  * st.write()
    * 웬만한 데이터(문자열, dictionary, 라이브러리의 클래스 등)는 웹 화면에 출력할 수 있음.
    * 내 pc에 streamlit을 실행하고서 클래스나 기타 문서를 텍스트가 아닌 웹에서 볼 수 있다.
    * magic
      * 하지만 그냥 데이터만 적어도 화면에 st.write()를 쓴 것처럼 그대로 표시되지만 소스가 알아보기 힘들게 되는 단점이 있어서 st.write()로 명확하게 표시하는 것이 나을 수도 있다. 
  * data flow
    * 소스 속 데이터가 변경되면 streamlit은 react와 달리 해당 소스를 처음부터 렌더링한다. 따라서 if-else 구문에 넣은 위젯들은 조건에 따라 나타나게 또는 나타나지 않게 할 수 있다.
  * sidebar and multi page
    * sidebar 생성
      * ```python
import streamlit as st

st.title("Hello World")

st.sidebar.title("sidebar")

st.sidebar.text_input("xxx")
st.sidebar.text_input("yyy")```
      * with를 쓰면 매번 sidebar를 칠 필요 없음.
        * ```python
import streamlit as st

st.title("Hello World")

with st.sidebar:
    st.title("sidebar")
    st.text_input("xxx")
    st.text_input("yyy")```
    * pages
      * pages 디렉토리 생성하고 그 안에 파이썬 스크립트 생성
        * ```python
import streamlit as st

st.title("DocumentGPT")```
        * ![[100. media/image/481549qnkK.png]]
      * 왼쪽 sidebar에 나타나는 페이지 순서를 정하고 싶으면 각 스크립트명에 "01_", "02_" 추가
  * tab
    * ```python
import streamlit as st


with st.sidebar:
    st.title("sidebar")
    st.text_input("xxx")

tab_a, tab_b, tab_c = st.tabs(["A", "B", "C"])

with tab_a:
    st.title("tab A")
with tab_b:
    st.title("tab B")
with tab_c:
    st.title("tab C")```
    * output
      * ![[100. media/image/kQioaD1VWY.png]]
  * page title and icon
    * ```python
import streamlit as st

st.set_page_config(
    page_title="test",
    page_icon=":shark:"
)

st.title("Look at the browser tab and check the page_title and the icon")```
    * ![[100. media/image/qpDm3f1d14.png]]
  * 이후는 [[Roam/genext-2025-10-05-02-18-30/Langchain#^gNC9v0q68|chatGPT with streamlit]]에...