---
title: "September 8th, 2023"
created: 2023-09-08 07:15:19
updated: 2024-08-07 17:18:08
---
  * 07:15 Roam research 시작.
  * 09:47 김호준 매니저와 merge 작업 같이 살펴봄.
    * remote로 push하기 전에 꼼꼼하게 확인하고 로그 메시지도 정확하게.
    * gitLens가 괜찮아 보이는데...
    * [[git commit 취소]]
    * 김호준 매니저는 일이 잘 안 되어갈 때도 평정을 유지하는 것 같다.
      * 나는 젊었을 때는 일이 잘 안 되어 가면 마음이 조급해지고 평정을 쉽게 잃었는데...
      * 일이 생각한 대로, 계획한 대로 잘 안 되는 것은 항상 있는 일이니 그걸 기본이라고 생각하고 일을 하는 것이 마음 편하다.
  * [x] dev에서 새 브랜치 따서 retirieval streaming 적용. [[September 11th, 2023]]
    * sk c&c 디렉토리에 retrieval streaming을 테스트하기 위해서 작업한 코드를 담은 page, llm 파일이 있음.
  * [x] 기업 분석 내용 생성시 docQuery등 값이 없을 때 공백 처리. [[September 11th, 2023]]
  * 12:52 98-lnb-db 앱 목록 db 조회
    * [[Redux]] 사용해서 처음 로그인할 때 DB에서 앱 목록 조회. ^sTP_YzVBs
      * 디렉토리 구조
        * ```plain text
next.js-project-root/
└── [[Redux]]/
    ├── reducers/
    │   ├── appinfos.js
    │   └── auth.js
    ├── local-storage.js
    ├── providers.js
    └── store.js```
      * [[Redux]]에 로그인 정보 저장(auth.js)
        * ```javascript
'use client';
import { createSlice } from '@[[Redux]]js/toolkit';
import LocalStorage from '../local-storage';

const accessToken = LocalStorage.get('accessToken');
const userInfo = JSON.parse(LocalStorage.get('userInfo'));

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    accessToken: accessToken !== null ? accessToken : null,
    userInfo: userInfo !== null ? userInfo : null,
  },
  reducers: {
    setAccessToken: (state, action) => {
      state.accessToken = action.payload;
      localStorage.setItem('accessToken', action.payload);
    },
    setUserInfo: (state, action) => {
      state.userInfo = {
        userid: action.payload.userid,
        type: action.payload.type,
        email: action.payload.email,
        username: action.payload.username,
        department: action.payload.department,
        currentCredit: action.payload.currentCredit,
        totalCredit: action.payload.totalCredit,
      };

      localStorage.setItem('userInfo', JSON.stringify(state.userInfo));
    },
    unsetAccessToken: (state) => {
      state.accessToken = null;
      localStorage.removeItem('accessToken');
    },
    unsetUserInfo: (state) => {
      state.userInfo = null;
      localStorage.removeItem('userInfo');
    },
  },
});

export default authSlice.reducer;
export const { setAccessToken, setUserInfo, unsetAccessToken, unsetUserInfo } = authSlice.actions;```
      * [[Redux]]에 앱 목록 저장(appinfos.js)
        * ```javascript
'use client'
import { createSlice } from '@[[Redux]]js/toolkit';
import LocalStorage from '../local-storage';

const storedAppInfos = LocalStorage.get('appInfos');
const appInfos = storedAppInfos ? JSON.parse(storedAppInfos) : [];

const appInfoSlice = createSlice({
  name: 'AppInfos',
  initialState: {
    appInfos,
  },
  reducers: {
    setAppInfos: (state, action) => {                       // reducers 내에서 함수 정의할 때 state가 항상 첫 번째 파라미터?
      // Using spread syntax to add all new elements
      state.appInfos = [...state.appInfos, ...action.payload];
      LocalStorage.set('appInfos', JSON.stringify(state.appInfos));
    },
    unsetAppInfos: (state) => {
      state.appInfos = [];
      LocalStorage.remove('appInfos');
    },
  },
});

export default appInfoSlice.reducer;
export const { setAppInfos, unsetAppInfos } = appInfoSlice.actions;
```
        * 로그인 후 landing page에서 앱 목록 조회 api 호출해서 [[Redux]]에 저장
          * ```javascript

import { useDispatch, useSelector } from 'react-[[Redux]]';
import { setAppInfos, unsetAppInfos } from '@/[[Redux]]/reducers/appinfos';

export default function LobbyLeft({ onShowToast }) {
  const dispatch = useDispatch();

  const [cateLists, setCateLists] = useState([]);
  // 앱 목록을 common backend의 DB에서 읽어온다.
  useEffect(() => {
    setTimeout(() => {                // 여기서 setTimeout을 사용해서 getApps를 호출한 이유는 getApps가 제일 나중에 실행하도록?
      getApps();
    }, 0);
  }, []);

  const getApps = () => {
    axiosUtil
      .get(COMMON_APPS)
      .then((res) => {
        console.log('getApps res: ', res);
        const appInfosFromAPI = res.data;
        dispatch(unsetAppInfos());
        // [[Redux]] Tookit은 appInfosFromAPI를 {type: 'AppInfos/setAppInfos', payload: appInfosFromAPI}로 변환해서 setAppInfos의 action 인자에 넣어준다.
        dispatch(setAppInfos(appInfosFromAPI));
        // 다른 컴포넌트에서 사용할 수 있도록 [[Redux]] 변수에 앱 목록을 저장한 후, 현 컴포넌트의 앱 정보 저장 데이터(cateLists)에 저장. 
        setCateLists(appInfosFromAPI);
      })
      .catch(handleAxiosError);
  };
}```
          * 앱 목록 조회 결과
            * ![[100. media/image/q5lok5OdYS.png]]
          * [x] 테스트를 해도 localstorage에 저장되지 않아서 원인을 추적하니 configure 문제였다!! [[Roam/genext-2025-10-05-02-18-30/Redux#^rkwaSSECK|store]]와 [[Roam/genext-2025-10-05-02-18-30/Redux#^kbYhHYiOj|provider]]를 확인할 것.
        * 이후 useState로 cateLists에 저장
    * [[Redux]] State를 브라우저 메모리에 저장, 삭제하는 프로그램
      * ```javascript
export default class LocalStorage {
  static set(key, value) {
    if (typeof window !== 'undefined') localStorage.setItem(key, value);       // Node.js(서버 환경)가 아닌 브라우저 환경에서 실행하는지 확인. 
  }

  static get(key) {
    if (typeof window !== 'undefined') return localStorage.getItem(key);
    return null;
  }

  static remove(key) {
    if (typeof window !== 'undefined') localStorage.removeItem(key);
  }

  static clear() {
    if (typeof window !== 'undefined') localStorage.clear();
  }
}```
      * 위 코드에서 window는 DOM 객체를 품은 전역 객체로 브라우저 환경이 제공하며 localStorage는 window에 속하는 속성이다. 하지만 window.localStorage라고 쓰지 않아도 됨.
    * [[Redux]] store
      * ```javascript
import { combineReducers, configureStore } from '@[[Redux]]js/toolkit';
import promptReducer from './reducers/prompt';
import authReducer from './reducers/auth';
import reportReducer from './reducers/report';
import appInfosReducer from './reducers/appinfos';
import gptModelReducer from './reducers/gptModel';

const rootReducer = combineReducers({
  prompt: promptReducer,
  auth: authReducer,
  report: reportReducer,
  appinfos: appInfosReducer,
  gptModel: gptModelReducer,
});

export const store = configureStore({
  reducer: rootReducer,
});```
    * [[Redux]] provider
      * ```javascript
"use client";

import { store } from "./store";
import { Provider } from "react-[[Redux]]";

export default function Providers({ children }) {
  return <Provider store={store}>{children}</Provider>;
}

```
  * 18:37 LNB 관련 백엔드와 프론트엔드 api 송수신 개발 완료.