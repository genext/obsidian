---
title: "React"
created: 2023-09-17 15:59:36
updated: 2025-09-08 15:00:15
---
## nomad coder 강의 정리
    * old version(2017)
      * why react?
        * basics
          * element dynamic creation in javascript
            * basics.html
              * ```html
<!DOCTYPE html>
<html>
    <body></body>
    <script>
        // Create a new div element
        var divElement = document.createElement('div');

        // Set some attributes (optional)
        divElement.id = 'myDiv';
        divElement.className = 'myClassName';

        // Append the div element to the body
        document.body.appendChild(divElement);

    </script>
</html>```
        * html in vanilla javascript
          * html tag first -> javascript control
          * vanilla.html
            * ```html
<!DOCTYPE html>
<html>
    <body>
        <span>Total Click: 0</span>
        <button id="btn">Click me</button>
        <script>
            let counter = 0;
            const button = document.getElementById("btn");
            const span = document.querySelector("span");
            function handleClick() {
                counter += 1
                span.innerText = `Total Click: ${counter}`;
            }
            button.addEventListener("click", handleClick)
        </script>
    </body>
</html>```
        * html with React
          * javascript control -> react render -> html tag.
          * react 원리 파악용
            * tag 하나만 생성
              * ```html
<!DOCTYPE html>
<html>
    <body>
        <div id="root"></div>
    </body>
    <script src="https://unpkg.com/react@17.0.2/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.production.min.js"></script>
    <script>
        const root = document.getElementById("root");
        const span = React.createElement("span", 
                                        {id: "span-test", 
                                         style:{color:"red"}},
                                         "Hello, I'm a span");
        ReactDOM.render(span, root);
    </script>
</html>```
            * tag 두 개 이상 생성 + even listener 등록
              * react_inner.html
                * ```html
<!DOCTYPE html>
<html>
    <body>
        <div id="root"></div>
    </body>
    <script src="https://unpkg.com/react@17.0.2/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.production.min.js"></script>
    <script>
        let counter = 0;
        const root = document.getElementById("root");
        const h3 = React.createElement("h3", {id: "title",
                                            // 아래 event listener에 대소문자 주의! 
                                            // 대문자 제대로 안 들어가면 이벤트 처리 안 함.
                                            // onMouseenter, onmouseEnter 둘 다 제대로 안 됨.
                                            onMouseEnter: () => console.log("mouse enter")}, "Hello, I'm a span");
        const btn = React.createElement("button", {onClick: () => {
            counter += 1;
            console.log("counter: ", counter);
        }}, "Click me");
        const container = React.createElement("div", null, [h3, btn]);
        ReactDOM.render(container, root);
    </script>
</html>```
          * jsx
            * Babel
              * jsx를 브라우저가 이해할 수 있는 코드로 변환
            * jsx.html
              * ```html
<!DOCTYPE html>
<html>
    <body>
        <div id="root"></div>
    </body>
    <script src="https://unpkg.com/react@17.0.2/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel">
        let counter = 0;
        const root = document.getElementById("root");
        function Title() {
            return (
            <h3 id="title"
                onMouseEnter={() => console.log("mouse enter")}>
               Hello, I'm a span
            </h3>);
        }

        // 내가 생성하는 custom tag는 반드시 대문자로. 그래야 react가 <button>과 혼동하지 않음.
        const Button = () => (
            <button onClick={() => {
                    counter += 1;
                    console.log("counter: ", counter);
                }}> Click me
            </button>);

        const Container = () => (
            <div>
                <Title />
                <Button />
            </div>
        );
        ReactDOM.render(<Container />, root);
    </script>
</html>```
          * manual rendering
            * ```html
<!DOCTYPE html>
<html>
    <body>
        <div id="root"></div>
    </body>
    <script src="https://unpkg.com/react@17.0.2/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel">
        let counter = 0;
        const root = document.getElementById("root");

        const counterUp = () => {
            counter += 1;
            render();
        }

        const render = () => ReactDOM.render(<Container />, root);

        const Container = () => (
            <div>
            <h3> Total Clicks: {counter} </h3>
            <button onClick={counterUp}> Click me </button>
            </div>
        );
        render();
        
    </script>
</html>```
          * 개발자 도구의 Elements 탭, react 최소 rendering.
          * automatic rendering ^YOEhRZ4Nb
            * auto_rendering.html
              * ```html
<!DOCTYPE html>
<html>
    <body>
        <div id="root"></div>
    </body>
    <script src="https://unpkg.com/react@17.0.2/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel">
        const root = document.getElementById("root");

        function App() {
            const [counter, setCounter] = React.useState(0);
            const onClick = () => {
                setCounter(current => current + 1)
            }

            return (
                <div>
                <h3> Total Clicks: {counter} </h3>
                <button onClick={onClick}> Click me </button>
                </div>
            );
        }
        ReactDOM.render(<App />, root);
        
    </script>
</html>```
        * State
          * react compenent안에서 데이터 변경하면 자동으로 re-render
          * useState
            * arguments
              * 1st argument: initial value
            * return
              * [data, modifier]
                * data
                  * initialized data from 1st argument
                * modifier
                  * update and data and re-render
                  * **set**Data()
            * [[Roam/genext-2025-10-05-02-18-30/React#^YOEhRZ4Nb|automatic rendering]]
            * Flip
              * unit_converter.html
                * ```javascript
<!DOCTYPE html>
<html>
    <body>
        <div id="root"></div>
    </body>
    <script src="https://unpkg.com/react@17.0.2/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel">
        const root = document.getElementById("root");

        function MinutesToHours() {
            const [amount, setAmount] = React.useState(0);
            const [flipped, setFlipped] = React.useState(false);
            const onChange = (event) => {
                setAmount(event.target.value);
            }

            const reset = () => setAmount(0);
            const flip = () => {
                reset();
                setFlipped(current => !current);
            }
            return (
                <div>
                    <div>
                        <label htmlFor="minutes">Minutes</label>
                        <input value={flipped ? amount * 60 : amount} 
                            id="minutes" 
                            placeholder="Minutes" 
                            type="number" 
                            onChange={onChange}
                            disabled={flipped}/>
                    </div>
                    <div>
                        <label htmlFor="hours">Hours</label>
                        <input value={flipped ? amount : Math.round(amount / 60)} 
                            id="hours" 
                            placeholder="Hours" 
                            type="number" 
                            onChange={onChange}
                            disabled={!flipped} />
                    </div>
                    <button onClick={reset}> Reset </button>
                    <button onClick={flip}> Flip </button>
                </div>
            );
        }
        
        function KmToMiles() {
            return (
                <div> Not implemented yet! </div>
            )
        }

        const App = () => {
            const [index, setIndex] = React.useState("xx");
            
            const onSelect = (event) => {
                setIndex(event.target.value);
            }

            return (
                <div>
                    <h1> Super Converter </h1>
                    <select value={index} onChange={onSelect}>
                        <option value="xx"> Select your units </option>
                        <option value="0"> Minutes to Hours </option>
                        <option value="1"> Km to Miles </option>
                    </select>
                    <hr />
                    {index === "0" ? <MinutesToHours /> : null }
                    {index === "1" ? <KmToMiles /> : null }
                </div>
            )

        }
        ReactDOM.render(<App />, root);
        
    </script>
</html>```
        * function처럼 작성한 component를 만들어서 분할 코딩, 재활용 가능.
      * Props
        * 부모 컴포넌트가 자식 컴포넌트에게 전달하는 오브젝트
        * 실제 앱 만들 때는 아래 예제와 달리 import해서 사용.
          * ```javascript
npm install prop-types 실행 후,
import PropTypes from "prop-types";```
        * memo
          * parent component의 state가 변하면 그에 속하는 모든 child component도 re-render!!!
            * child의 props가 변하지 않으면 re-render X
          * props_without_memo.html
            * ```html
<!DOCTYPE html>
<html>
    <body>
        <div id="root"></div>
    </body>
    <script src="https://unpkg.com/react@17.0.2/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel">
        const root = document.getElementById("root");

        function Btn({text, changeValue}) {
            return (
                <button 
                    onClick = {changeValue}
                    style={{
                        backgroundColor: "tomato",
                        color: "white",
                        padding: "10px 20px",
                        border: 0,
                        borderRadius: 10,
                    }}
                >
                {text}
                </button>
            )
        }
        const App = () => {
            const [value, SetValue] = React.useState("Save Changes")

            const changeValue = () => {
                SetValue("Revert Changes");
            }

            return (
                <div>
                    <Btn text={value} changeValue={changeValue}/>
                    <Btn text="Continue" />
                </div>
            )

        }
        ReactDOM.render(<App />, root);
        
    </script>
</html>```
          * props_with_memo.html
            * ```html
<!DOCTYPE html>
<html>
    <body>
        <div id="root"></div>
    </body>
    <script src="https://unpkg.com/react@17.0.2/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel">
        const root = document.getElementById("root");

        function Btn({text, changeValue}) {
            console.log(text, "was rendered");
            return (
                <button 
                    onClick = {changeValue}
                    style={{
                        backgroundColor: "tomato",
                        color: "white",
                        padding: "10px 20px",
                        border: 0,
                        borderRadius: 10,
                    }}
                >
                {text}
                </button>
            )
        }
        
        const MemorizedBtn = React.memo(Btn);

        const App = () => {
            const [value, SetValue] = React.useState("Save Changes")

            const changeValue = () => {
                SetValue("Revert Changes");
            }

            return (
                <div>
                    <MemorizedBtn text={value} changeValue={changeValue}/>
                    <MemorizedBtn text="Continue" />
                </div>
            )

        }
        ReactDOM.render(<App />, root);
        
    </script>
</html>```
        * propTypes
          * propTypes.html
            * ```html
<!DOCTYPE html>
<html>
    <body>
        <div id="root"></div>
    </body>
    <script src="https://unpkg.com/react@17.0.2/umd/react.development.js"></script>
    <!-- <script src="https://unpkg.com/react@17.0.2/umd/react.production.min.js"></script> -->
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/prop-types@15.7.2/prop-types.js"></script>
    <script type="text/babel">

        function Btn({text, fontSize = 16}) {
            console.log(text, "was rendered");
            return (
                <button 
                    style={{
                        backgroundColor: "tomato",
                        color: "white",
                        padding: "10px 20px",
                        border: 0,
                        borderRadius: 10,
                        fontSize: fontSize,
                    }}
                >
                {text}
                </button>
            )
        }
        
        Btn.propTypes = {
            text: PropTypes.string.isRequired,
            fontSize: PropTypes.number,
        }
        const App = () => {
            return (
                <div>
                    <Btn text="Save Changes" fontSize={18}/>
                    <Btn text={"Continue"} />
                </div>
            )

        }

        const root = document.getElementById("root");
        ReactDOM.render(<App />, root);
        
    </script>
</html>```
      * create react app
        * css module
          * Button.js
            * ```javascript
import PropTypes from "prop-types"
import styles from "./Button.module.css"

function Button({text}) {
    return (
        <button className={styles.btn}>{text}</button>
    );
}

Button.propTypes = {
    text: PropTypes.string.isRequired
}
export default Button;```
          * Button.module.css
            * Button.css로 하면 안 된다...왜 안 되지...
            * ```javascript
.btn {
    color: white;
    background-color: tomato;
}```
      * useEffect
        * 어떤 함수를 특정 state가 변하거나 아니면 딱 한 번만 실행하도록 하고 싶을 때
          * 한 번만 실행. API 호출 등.
            * useEffect(함수명, []);
            * ```javascript
import { useState, useEffect } from "react";

function App() {
  const [value, setValue] = useState(0);
  
  const onClick = () => setValue(current => current + 1);
  console.log("rendered");
  //const iRunOnlyOnce = () => console.log("I run only once.")
  useEffect(() => console.log("I run only once."), [])

  return (
    <div>
      <h1>{value}</h1>
      <button onClick={onClick}>Click me</button>
    </div>
  );
}

export default App;
```
        * cleanup function
          * component가 종료할 때 실행될 함수
          * useEffect 첫 번째 인자로 넘겨주는 함수가 종료 시 실행할 함수를 return.
          * ```javascript
//import Button from "./Button"
import { useState, useEffect } from "react";

function Hello() {
  useEffect(() => {
    console.log("created :)");
    return () => console.log("bye :(");
  }, []);

  return (
    <div>
      Hello
    </div>
  );
}

function App() {
  const [showing, setShowing] = useState(false);
  
  const onClick = () => setShowing(current => !current);

  return (
    <div>
      {showing ? <Hello /> : null}
      <button onClick={onClick}>{showing ? "Hide" : "Show"}</button>
    </div>
  );
}

export default App;
```
      * react router
        * page간 이동 처리
          * import Link from "react-router-dom"
          * <Link to="/movie" >{title}</Link>
        * 설치
          * ```shell
npm install react-router-dom```
        * 환경 설정
          * src/routes 생성
            * Home.js
            * Detail.js
          * 각 페이지를 담을 디렉토리 따로 생성(components)
          * App.js는 router를 render하는 역할로.
        * useParams
          * url(/movie/:id)에 있는 변수 id값을 얻기
      * movie app
        * source는 github에 있지만 현재 에러 발생. 나중에 고칠 것.
      * Publishing
        * github pages
          * web page 자동 생성 무료 서비스
        * npm run build 실행하여 product code 생성함.
    * new version(2019)
      * requirement
        * node.js(npm included)
          * ```shell
node -v
npm -v```
        * npx
          * install
            * ```shell
npm install npx -g```
        * create-react-app install
          * 2019 이후 react app을 쉽게 만들 수 있음. 아래 명령어 실행하면 기본적인 환경 구성 완료.
          * ```shell
npx create-react-app movie_app_2019```
      * 웹서버 시작
        * 이미 웹서버 환경까지 자동으로 만들어졌기 때문에 npm start만 치면 웹페이지(localhost:3000) 뜸.
        * React가 src에 있는 내용을 index.html에 알아서 삽입해줌.
          * index.js
            * ```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);```
      * 필요없는 파일들 삭제 -> blank page
        * src에 App.js, index.js만 남기고 삭제한 파일을 참조하는 줄도 삭제.
      * component
        * A function that returns html code.
        * <ComponentName />. First letter is always a capital.
## React에서 login, logout 처리 방법 예시
    * 소스 코드 구성
      * /app/page.js
        * ```python
import Home from "@/app/home/page";
export default function Main() {
  return (
      <Home />
  )
}```
      * /app/layout.js
        * ```python
import './globals.scss';
import Providers from '/[[Redux]]]]/providers';
import Header from '@/app/components/header';
import { AxiosInterceptor } from '@/app/util/axios-util';
import LoginUtil from '@/app/util/login-util';

export const metadata = {
  title: 'Ai',
  description: 'AI 앱 플랫폼',
};

export default function RootLayout({ children, showHeader = true }) {
  return (
    <html lang="en">
      <head>
        <title>G.AI Report Generator - prototype</title>
      </head>
      <body>
        <Providers>
          <AxiosInterceptor>
            <div className="main">
              {/* <div className="Layout w-screen h-screen px-8 pt-8 flex-col justify-start items-start gap-[10px] inline-flex"> */}
              {/* <Header /> */}
              {showHeader && <Header />}
              {children}
              {/* <Footer /> */}
            </div>
            <LoginUtil />
          </AxiosInterceptor>
        </Providers>
      </body>
    </html>
  );
}```
      * /app/util/login-util.js
```javascript
'use client';
import { useRouter, usePathname, useSearchParams, redirect } from 'next/navigation';
import { useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-[[Redux]]]]';
import { unsetAccessToken, unsetUserInfo } from '@/[[Redux]]]]/reducers/auth';
import { unsetAll } from '@/[[Redux]]]]/reducers/prompt';

export default function LoginUtil() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { accessToken, userInfo } = useSelector((state) => state.auth);
  const dispatch = useDispatch();

  // 로그인이 필요하지 않은 페이지
  const noLoginPage = useMemo(() => ['/login', '/signup', '/reset'], []);

  useEffect(() => {
    // 로그아웃 처리
    if (searchParams.get('logout')) {
      dispatch(unsetUserInfo());
      dispatch(unsetAccessToken());
      dispatch(unsetAll());
      redirect('/login');

      // 로그인 필요 페이지 진입시
    } else if (!noLoginPage.includes(pathname) && (!accessToken || !userInfo)) {
      redirect(`/login?nextPage=${pathname}`);

      // 로그인 상태
    } else if (accessToken && userInfo) {
      const nextPage = searchParams.get('nextPage');
      if (nextPage) {
        redirect(nextPage);
      } else if (pathname === '/' || pathname === '/login') {
        redirect('/lobby');
      }
    }
  }, [router, noLoginPage, pathname, searchParams, accessToken, userInfo, dispatch]);
}
```
      * logout 처리
        * 어느 곳에서든 router.push('?logout=true');를 삽입하면 된다.
## Hooks
    * useEffect
      *  Execution timing
        * a built-in hook that allows you to run side effects (such as fetching data from an API, updating the DOM, or subscribing to events) in response to changes in your component's props or state.
      * Cleanup
        * `useEffect` provides a way to perform cleanup actions when the component unmounts or when the dependencies change.
      *  Dependency array
        * The second argument to `useEffect` is an array of dependencies that determines when the effect should run. If the dependency array is empty, the effect runs only once after the initial render.
      * Parallelism
        * Unlike class components' `componentDidUpdate`, `useEffect` runs in parallel and not serially, meaning that multiple effects can run at the same time without blocking each other. This can improve performance and reduce jankiness.
        * 병렬 실행 시 실행 순서가 중요할 때 [[Roam/genext-2025-10-05-02-18-30/javascript#^c3vrowcaq|setTimeout]]
    * javascript로 간단하게 표현한 useState, useEffect 내부. 
      * ```javascript
let hooks = [];
let currentHook = 0; // index to keep track of current hook

function useState(initialValue) {
  const hookIndex = currentHook; // capture current hook index

  // Initialize state value
  if (hooks.length <= hookIndex) {
    hooks.push(initialValue);
  }

  const setState = (newValue) => {
    hooks[hookIndex] = newValue;
  };

  // Move to the next hook for the next call
  currentHook++;

  return [hooks[hookIndex], setState];
}

function useEffect(callback, depsArray) {
  const hookIndex = currentHook; // capture current hook index

  const prevDeps = hooks[hookIndex]; // get previous dependencies
  let hasChanged = true; // flag to check if dependencies have changed

  if (prevDeps) {
    hasChanged = !depsArray.every((dep, i) => dep === prevDeps[i]);
  }

  if (hasChanged) {
    callback();
  }

  hooks[hookIndex] = depsArray; // update the hook with the new dependencies

  // Move to the next hook for the next call
  currentHook++;
}

// Example component using these hooks
function App() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState("hello");

  useEffect(() => {
    console.log("Count changed:", count);
  }, [count]);

  useEffect(() => {
    console.log("Text changed:", text);
  }, [text]);

  setCount(count + 1);
  setText(text + " world");
}

// Simulate React's render process
App(); // initial render
currentHook = 0; // reset hook index
App(); // re-render
currentHook = 0; // reset hook index
App(); // re-render
```
    * Custom Hooks
      * 보통 'use'로 시작
    * memoization techniques
      * useCallback
        * is used for memoizing a funciton.
        * 성능 향상에 좋고 특히, callback을 하위 컴포넌트에 props로 전달할 때 유용.
          * 해당 하위 컴포넌트가 re-render할 때마다 함수를 생성하지 않고 dependency 배열에 등록된 요소가 바뀌지 않으면 memoized된 함수를 전달한다.
          * ```javascript
const requsetPrompt = useCallback(
    async (slidePrompt, onProcess = requsetPromptCallback, onDone = () => {}) => {
      // your code logic
    },
    [fileSeqArray, requsetPromptCallback]
  );
  ```
          * 위 코드에서 onProcess와 onDone은 기본값이 있는데 fileSeqArray나 requestPromptCallback이 변할 때에만 requestPrompt 함수가 다시 만들어진다.
      * useMemo
        * dependencies가 변하지 않으면 이전에 저장한 rendering한 결과를 바로 돌려줌. 
        * 함수형 컴포넌트 성능 개선
          * 특히, 해당 컴포넌트 re-render가 자원을 많이 소모하거나 복잡할 때
```javascript
const memoizedValue = useMemo(() => {
  // computation that returns the value you want to memoize
}, [dependency1, dependency2, ...]);
```
        * profile performance first!!! 과용은 금물. 
    * useQuery
      * https://tigerabrodi.blog/become-expert-in-react-query

## 설계
    * [Single Responsibility Principle in React: The Art of Component Focus](https://cekrem.github.io/posts/single-responsibility-principle-in-react/)
## Popup component 예
    * SK C&C 방식
      * 컴포넌트
        * ```javascript
export const POPUP_TYPE = {
  CONFIRM: 'confirm',
  ALERT: 'alert',
};

export const initState = {
  type: POPUP_TYPE.CONFIRM,
  message: '',
  errorcode: '',
  onCancel: () => {},
  onConfirm: () => {},
  confirmBtnText: '확인',
  cancelBtnText: '취소',
};

export const setPopupProps = ({
  type,
  message,
  errorCode,
  onCancel,
  onConfirm,
  confirmBtnText = '확인',
  cancelBtnText = '취소',
}) => ({
  ...initState,
  type,
  message,
  errorCode,
  onCancel,
  onConfirm,
  confirmBtnText,
  cancelBtnText,
});

export default function PopupConfirmAlert({
  type,
  message,
  errorcode,
  onCancel,
  onConfirm,
  confirmBtnText = '확인',
  cancelBtnText = '취소',
}) {
  return (
    <aside className="popup center">
      <div className="dimmed"></div>
      <div className="pop-content small">
        <div className="wrap-message">
          {message}
          {errorcode && <p className="wrap-error">{errorcode}</p>}
        </div>
        {type === POPUP_TYPE.CONFIRM && (
          <div className="wrap-btn">
            <button onClick={onCancel}>{cancelBtnText}</button>
            <button onClick={onConfirm}>{confirmBtnText}</button>
          </div>
        )}
        {type === POPUP_TYPE.ALERT && (
          <div className="wrap-btn">
            <button onClick={onConfirm}>{confirmBtnText}</button>
          </div>
        )}
      </div>
    </aside>
  );
}```
      * 호출
        * ```javascript
export default function AAA() {
  ...
  return (
    <div className="container">
    ...
     {openErrorPopup && (
        <PopupConfirmAlert
          type={'alert'}
          message={
            <>
              저장에 실패하였습니다.
              <br /> 다시 시도하시거나, 관리자에게 문의해 주세요.
            </>
          }
          errorcode={'에러코드'}
          onConfirm={onCloseErrorPopup}
        />
      )}
      {openDeletePopup && (
        <PopupConfirmAlert
          type={'confirm'}
          message={
            <>
              삭제하시겠습니까?
              <br /> 삭제한 항목은 복원할 수 없습니다.
            </>
          }
          onCancel={onCloseDeletePopup}
          onConfirm={onConfirmDelete}
        />
      )}
      {showPopupModule && (
        <PopupModule
          onHidePopupModule={onHidePopupModule}
          promptContent={promptContent}
          searchParams={searchParams}
          errorHandler={handleAxiosError}
        />
      )}
      {openSuccessToast && <PopupToast toastMessage={toastMessage} onHideToast={onCloseSuccessToast} />}
      {confirmPopup && (
        <PopupConfirmAlert
          type={'alert'}
          message={popupMessage}
          onConfirm={() => {
            setConfirmPopup(false);
            if (shouldNavigate) {
              setShouldNavigate(false);
              router.push('/admin/mega');
            }
          }}
        />
      )}
      {inputMissedPopup && (
        <PopupConfirmAlert
          type={'alert'}
          message={popupMessage}
          onConfirm={() => {
            setConfirmPopup(false);
          }}
        />
      )}
    </div>
  );
}
```
    * 디지털 바우처 금결원 방식
      * 타입 정의 /src/port/toast.port.ts
        * ```javascript
export type ToastMessageService = {
  toastLoadingMessage: ({
    title,
    description,
  }: {
    title: string;
    description?: string;
  }) => void;
  toastSuccessMessage: ({
    title,
    description,
  }: {
    title: string;
    description?: string;
  }) => void;
  toastErrorMessage: ({
    title,
    description,
  }: {
    title: string;
    description?: string;
  }) => void;
  toastInfoMessage: ({
    title,
    description,
  }: {
    title: string;
    description?: string;
  }) => void;

  toastWarningMessage: ({
    title,
    description,
  }: {
    title: string;
    description?: string;
  }) => void;
};
```
      * 컴포넌트
        * ```javascript
import { ToastMessageService } from "@/port/toast.port";
import { useRef } from "react";
import { toast } from "sonner";

export const useToastMessage = (): ToastMessageService => {
  const toastIdRef = useRef<null | string | number>(null);

  const toastLoadingMessage = ({
    title,
    description = "",
  }: {
    title: string;
    description?: string;
  }) => {
    if (toastIdRef.current === null) {
      const id = toast.loading(title, {
        description,
        duration: 5000,
      });

      toastIdRef.current = id;
    } else {
      const id = toast.loading(title, {
        id: toastIdRef.current,
        description,
        duration: 5000,
      });
    }
  };

  const toastErrorMessage = ({
    title,
    description = "",
  }: {
    title: string;
    description?: string;
  }) => {
    if (toastIdRef.current === null) {
      const id = toast.error(title, {
        description,
        duration: 5000,
      });

      toastIdRef.current = id;
    } else {
      const id = toast.error(title, {
        id: toastIdRef.current,
        description,
        duration: 5000,
      });
    }
  };

  const toastSuccessMessage = ({
    title,
    description = "",
  }: {
    title: string;
    description?: string;
  }) => {
    if (toastIdRef.current === null) {
      const id = toast.success(title, {
        description,
        duration: 5000,
      });

      toastIdRef.current = id;
    } else {
      const id = toast.success(title, {
        id: toastIdRef.current,
        description,
        duration: 5000,
      });
    }
  };

  const toastInfoMessage = ({
    title,
    description = "",
  }: {
    title: string;
    description?: string;
  }) => {
    if (toastIdRef.current === null) {
      const id = toast.info(title, {
        description,
        duration: 5000,
      });

      toastIdRef.current = id;
    } else {
      const id = toast.info(title, {
        id: toastIdRef.current,
        description,
        duration: 5000,
      });
    }
  };

  const toastWarningMessage = ({
    title,
    description = "",
  }: {
    title: string;
    description?: string;
  }) => {
    if (toastIdRef.current === null) {
      const id = toast.warning(title, {
        description,
        duration: 5000,
      });

      toastIdRef.current = id;
    } else {
      const id = toast.warning(title, {
        id: toastIdRef.current,
        description,
        duration: 5000,
      });
    }
  };

  //   useEffect(() => {
  //     return () => {
  //       if (toastIdRef.current !== null) {
  //         toast.dismiss(toastIdRef.current);
  //       }
  //     };
  //   }, []);

  return {
    toastLoadingMessage,
    toastErrorMessage,
    toastSuccessMessage,
    toastInfoMessage,
    toastWarningMessage,
  };
};
```
      * 호출
        * ```javascript
imuport { useToastMessage } from "@/adaptor/toast/useToastMessage";

export default function VoucherIssuePage() {

  const { toastSuccessMessage, toastErrorMessage, toastWarningMessage } =
    useToastMessage();


  const handleSubmit = async () => {
    if (templateId === "") {
      toastWarningMessage({
        title: "알림",
        description: "템플릿을 선택해주세요.",
      });
      return;
    }
    ...

  const requestData = {
        templateId,
        voucherName,
        voucherRequestedAgency,
        status: VoucherStatus.APPLIED,
        initializer,
      };

      const response = await SystemService.POST(
        VOUCHER_INSERT_DEPLOY_REQUEST,
        requestData,
      );

      if (response?.success) {
        toastSuccessMessage({
          title: "성공",
          description: "바우처 배포 승인 요청이 처리되었습니다.",
        });
        setIsDeployed(true);
        router.push("/participants/voucher/dashboard");
      } else {
        toastErrorMessage({
          title: "실패",
          description: `바우처 배포 승인 요청 실패: ${response.message}`,
        });
      }
      // TODO 승인 버튼 비활성화
    } catch (error) {
      handleAxiosError(
        error,
        "바우처 배포 승인 요청이 실패했습니다",
        toastErrorMessage,
      );
    }
  };
}
  ```
## 프로젝트 개발
    * [[SK C&C AI기반 보고서 자동 생성]]
    * [[디지털 바우처 프로젝트]]
## Websockets with React
    * WebSockets and React
      * WebSockets have a [Web API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) accessible in all major web browsers, and since React is “just JavaScript” you can access it without any additional modules or React-specific code:
        * ```javascript
const socket = new WebSocket("ws://localhost:8080")

// Connection opened
socket.addEventListener("open", event => {
  socket.send("Connection established")
});

// Listen for messages
socket.addEventListener("message", event => {
  console.log("Message from server ", event.data)
});```
      * Instead of reinventing the wheel, it’s usually more productive to use a general **WebSocket library** that provides the features listed above out of the box - this allows you to focus on building features unique to your application instead of generic realtime messaging code.
    * Best React WebSocket libraries
      * React useWebSocket
        * A thin layer on top of the WebSocket API that features automatic reconnection and a fallback to [Server-Sent Events](https://ably.com/blog/websockets-vs-sse) (as long as you’ve coded support on your server). This library is specifically **made for React**, so it’s very natural to utilise the useWebSocket hook and all its options. The downside is that useWebSocket might not have all the features and reliability guarantees you need in production. [Learn more](https://ably.com/blog/websockets-react-tutorial?utm_source=Nomad+Academy&utm_campaign=46bb3efc2b-EMAIL_CAMPAIGN_2023_11_03&utm_medium=email&utm_term=0_4313d957c9-46bb3efc2b-355886828&mc_cid=46bb3efc2b&mc_eid=6de7159142#how-to-use-web-sockets-with-react-and-node).
      * Socket.IO
        * A JavaScript realtime messaging library based on WebSockets with an optional fallback to HTTP long polling in case the [WebSocket connection can’t be established](https://ably.com/blog/websockets-vs-http-streaming-vs-sse#challenges-with-web-sockets). Socket.IO has more features than useWebSocket, but it’s **not specific to React**, and there’s still work to do to ensure good performance and reliability in production. [Learn more](https://ably.com/topic/socketio).
      * React useWebSocket with Socket.IO
        * useWebSocket actually works with Socket.IO, meaning you might be able to use them together in your React project. I haven’t tested this extensively, but it looks promising!
      * Ably
        * **A realtime infrastructure platform** featuring [first-class React client support](https://ably.com/blog/react-hooks-javascript-sdk). With useWebSocket or Socket.IO, you need to host your own WebSocket server. That sounds simple enough, but it’s actually a big burden to [manage your own WebSocket backend](https://ably.com/topic/the-challenge-of-scaling-websockets). With Ably, you create an account, and all the messages route through the Ably global infrastructure with the lowest possible latency. Instead of worrying about uptime or if your messages will be delivered exactly-once and in the correct order, you can just plug into the React hook and focus on building the features that actually matter to your users. [Learn more](https://ably.com/).
    * [x] SSE(Server Sent Event)와 비교 - [SSE](https://ably.com/topic/server-sent-events)
    * source: https://ably.com/blog/websockets-react-tutorial?utm_source=Nomad+Academy&utm_campaign=46bb3efc2b-EMAIL_CAMPAIGN_2023_11_03&utm_medium=email&utm_term=0_4313d957c9-46bb3efc2b-355886828&mc_cid=46bb3efc2b&mc_eid=6de7159142
      *  [youtube 강의](https://www.youtube.com/watch?v=RATHiI8iNuk)

## Refactoring
- [Common sense of refactoring of a messy react component](https://alexkondov.com/refactoring-a-messy-react-component/?utm_source=Nomad+Academy&utm_campaign=e793e779d6-EMAIL_CAMPAIGN_2024_08_16&utm_medium=email&utm_term=0_4313d957c9-e793e779d6-355886828&mc_cid=e793e779d6&mc_eid=6de7159142)
	- messy code that seemed to be maintained by several developers.
```javascript
function Form() {
  const [formLink, setFormLink] = useState('')
  const [userPersona, setUserPersona] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [numberOfVisits, setNumberOfVisits] = useState('')
  const [companyNumber, setCompanyNumber] = useState('')
  const [numberIncorrect, setNumberIncorrect] = useState(0)
  const [isFormValid, setIsFormValid] = useState(false)
  const [buttonText, setButtonText] = useState('Next')
  const [isProcessing, setIsProcessing] = useState(false)
  const [estimatedTime, setEstimatedTime] = useState('Enter number')
  const [recentActions, setRecentActions] = useState([])
  const [abortController, setAbortController] = useState(null)

  useEffect(() => {
    fetchPreviousActions()
  }, [])

  const fetchPreviousActions = async () => {
    try {
      const response = await fetch('https://api.com/actions', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      data.sort(
        (a, b) => new Date(b.actiond_date) - new Date(a.actiond_date)
      )
      setRecentActions(data)
    } catch (error) {
      console.error('Failed to fetch recent actions', error)
    }
  }

  const [showOverlay, setShowOverlay] = useState(false)

  const renderLayout = () => (
    <div>
      <div>
        <div>Analyzing...</div>
        <button onClick={handleCancelaction}>Cancel</button>
      </div>
    </div>
  )

  const formatDate = (dateStr) => {
    return dateStr.replace(/-/g, '')
  }

  const callBackendAPI = async (formData) => {
    const controller = new AbortController()
    setAbortController(controller)
    formData.startDate = formatDate(formData.startDate)
    formData.endDate = formatDate(formData.endDate)

    try {
      const response = await fetch('https://api.com/action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setShowOverlay(false)
      window.open(
        'https://app.com/action/' + data.id,
        '_blank',
        'noopener,noreferrer'
      )
      window.location.reload()
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Scraping halted')
      } else {
        console.error('Failed to call the API', error)
      }
    } finally {
      setShowOverlay(false)
      setIsProcessing(false)
    }
  }

  const handleCancelaction = () => {
    if (abortController) {
      abortController.abort() // Abort the fetch request
    }
    setShowOverlay(false)
    setIsProcessing(false)
  }

  useEffect(() => {
    if (!recentActions) {
      fetchPreviousActions()
    }

    setIsFormValid(startDate && endDate && endDate > startDate)
  }, [numberOfVisits, startDate, endDate])

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!isFormValid) return

    setShowOverlay(true)
    setIsProcessing(true)

    // Construct the form data object
    const formData = {
      userPersona,
      startDate,
      endDate,
      numberOfVisits: parseInt(numberOfVisits, 10),
    }
    // Calling the API with the form data
    await callBackendAPI(formData)
    setIsProcessing(false)
  }

  const handleSubmitCompanyNumber = (number) => {
    // this is unneeded, we've already set the value in state
    setCompanyNumber(number)
    if (number.length < 9) setNumberIncorrect(1)
    else setNumberIncorrect(0)
  }

  return !numberIncorrect ? (
    <div>
      <div>
        <img src={require('../imgs/LogoWhite.png')} alt="Logo" />
      </div>
      <div>
        <div>Tool</div>
        <form onSubmit={handleSubmit}>
          <label htmlFor="company_number">
            Enter your credentials
          </label>
          <input
            type="text"
            name="company_number"
            id="company_number"
            placeholder="Company Number"
            value={companyNumber}
            onChange={(e) => setCompanyNumber(e.target.value)}
          />
          <button
            type="submit"
            onClick={(e) => handleSubmitCompanyNumber(companyNumber)}
          >
            <span>Login</span>
            <span>&gt;</span>
          </button>
          {numberIncorrect > 0 ? (
            <span>The number you entered is incorrect</span>
          ) : (
            ''
          )}
        </form>
      </div>
    </div>
  ) : (
    <div>
      <div>
        <img
          src={require('../imgs/LogoWhite.png')}
          style={{ width: '200px', marginTop: '50px' }}
          alt="Logo"
        />
      </div>
      <div>
        <div>
          <div>New action</div>
          <form style={{ marginTop: '3vh' }} onSubmit={handleSubmit}>
            <div>
              <label>
                Visits
                <span
                  style={{
                    color: 'gray',
                    fontWeight: 'lighter',
                  }}
                >
                  (optional)
                </span>
              </label>
              <input
                type="number"
                value={numberOfVisits}
                onChange={(e) => setNumberOfVisits(e.target.value)}
              />
              <label className="form-label">
                Define a user persona{' '}
                <span
                  style={{
                    color: 'gray',
                    fontWeight: 'lighter',
                  }}
                >
                  (optional)
                </span>
              </label>
              <input
                type="text"
                id="posts-input"
                value={userPersona}
                onChange={(e) => setUserPersona(e.target.value)}
              />
            </div>
            <label
              className="form-label"
              style={{ textAlign: 'left' }}
            >
              Time period{' '}
              <span
                style={{
                  color: 'gray',
                  fontWeight: 'lighter',
                }}
              >
                (available for dates before June 2023)
              </span>
            </label>

            <div id="time-input">
              <input
                type="date"
                style={{ marginRight: '20px' }}
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
              <span style={{ fontSize: '15px' }}>to</span>
              <input
                type="date"
                style={{ marginLeft: '20px' }}
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <button
              type="submit"
              className={`next-button ${isFormValid ? 'active' : ''}`}
              disabled={!isFormValid || isProcessing}
            >
              <span>Begin</span>
              <span>→</span>
            </button>
          </form>
        </div>
        <div id="divider"></div>

        <div>
          <div>Recents</div>
          <div>
            <div>
              {recentActions.map((action, index) => (
                <div key={index}>
                  <a href={action.link} target="_blank">
                    <span>r/{action.obfuscated}</span>{' '}
                    <span>{action.actiond_date} (UTC)</span>
                  </a>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      {showOverlay ? renderLayout() : null}
    </div>
  )
}
```
      * Start with a test
        * We need to focus only on tests that test the component as a black box and validate the result.
      * Add a Lint rule
      * Remove dead code
        * ```javascript
const [userPersona, setUserPersona] = useState('')
const [startDate, setStartDate] = useState('')
const [endDate, setEndDate] = useState('')
const [numberOfVisits, setNumberOfVisits] = useState('')
const [companyNumber, setCompanyNumber] = useState('')
const [numberIncorrect, setNumberIncorrect] = useState(0)
const [isFormValid, setIsFormValid] = useState(false)
const [isProcessing, setIsProcessing] = useState(false)
const [recentActions, setRecentActions] = useState([])
const [abortController, setAbortController] = useState(null)```
      * Bloated state is a code smell but it doesn’t directly show us where the “seams” between the potential components are. To do this we need to explore the JSX.
      * Large conditionals
        * ```javascript
return !numberIncorrect ? (
    // A lot of JSX...
) : (
    // Even more JSX...
)```
        * We could use the existing Form component to only make the decision what to render then leave the rest to the child components.
        * refactored code
          * ```javascript
function Form() {
  const [companyNumber, setCompanyNumber] = useState(undefined)

  return (
    <div>
      <div>
        <img
          src={require('../imgs/LogoWhite.png')}
          style={{ width: '200px', marginTop: '50px' }}
          alt="Logo"
        />
      </div>
      {!companyNumber ? (
        <CompanyNumberForm onSubmit={setCompanyNumber} />
      ) : (
        <ActionForm companyNumber={companyNumber} />
      )}
    </div>
  )
}```
        * When we move the JSX away to a child component, the IDE will immediately highlight all the functions and values that are missing, making it easier for us to split up the state.
      * Component responsibility

### 이름 없는 html 태그
* <>\</> Fragment
	* [[React]] 사용할 때 컴포넌트마다 return으로 페이지 생성한다.
    * return 문 안에는 한 태그, 즉 한 덩어리만 들어간다.
    * 따라서 \<div className="...">으로 시작하고 그 안에 중첩되어서 다른 태그들이 들어가게 된다.
	- 팝업처럼 div의 class에 상관없이 독립적으로 쓰고 싶은 것은 \<div> 밖에 두면 syntax error발생
	```python
return (
	<div className="page">
		{/* 페이지 내용 */}
	</div>
	<Popup /> // ❌ Syntax Error - 형제 요소는 불가능
)
	```
- 대신 아래처럼 return안에 <>\</>으로 시작해서 기존 \<div>...\</div>을 넣고 popup component를 별도로 div 태그 밖에 둘 수 있다.
```python
return (
	<>
		<div className="page">
		 {/* 페이지 내용 */}
		</div>
		<Popup /> // ✅ 가능 - Fragment 안에서 여러 요소 허용
	</>
)
```