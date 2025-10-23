---
title: "Redux"
created: 2023-09-12 21:01:04
updated: 2024-08-07 17:18:08
---
  * [[Redux]] is a predictable state container designed to help you write JavaScript apps that behave consistently across different environments and are easy to test. It's a standalone library that can be used with any UI layer or framework, including [[React]], Angular, Vue, and even vanilla JavaScript.
  * [[Redux]] centralizes the application's state, making it easy to manage. As the application grows, managing state can become complicated, and [[Redux]] helps alleviate that complexity. It enforces a unidirectional data flow and follows a strict structure which allows for more predictable code.
  * In a [[Redux]] application, the state of your whole application is stored in an object tree inside a single store.
  * To change something in the state, you need to dispatch an action. An action is a plain JavaScript object describing the change. They are the only way to get data into the store.
  * Reducers are pure functions that take the current state and an action and return a new state, they are the only way to change state. It's important to keep reducers pure as they are not meant to perform side effects like API calls and routing transitions.
  * It's also important to note that [[Redux]] requires you to keep your state immutable and to never modify state directly. Instead, state is updated by returning a new copy of the state with the changes.
    * ```javascript
import { createStore } from '[[Redux]]'

// The reducer
function counter(state = 0, action) {
  switch (action.type) {
    case 'INCREMENT':
      return state + 1
    case 'DECREMENT':
      return state - 1
    default:
      return state
  }
}

// Create a [[Redux]] store holding the state of your app.
let store = createStore(counter)

// You can use subscribe() to update the UI in response to state changes.
store.subscribe(() => console.log(store.getState()))

// The only way to mutate the internal state is to dispatch an action.
store.dispatch({ type: 'INCREMENT' })
store.dispatch({ type: 'DECREMENT' })```
      * In this example, we've created a very simple [[Redux]] store that manages a counter. It has two actions: INCREMENT and DECREMENT, which increase and decrease the counter respectively.
  * 활용 예제: [[September 8th, 2023#^sTP_YzVBs|Redux 사용해서 처음 로그인할 때 DB에서 앱 목록 조회.]]
  * store ^rkwaSSECK
    * 앱의 전체 상태 트리가 있는 저장소
  * provider ^kbYhHYiOj
    * 앱이 [[Redux]] store에 접근할 수 있도록 함.
    * a Provider is a type of React component provided by the react-[[Redux]] library which makes the [[Redux]] store available to any nested components that have been wrapped in the connect() function.
    * The Provider component is used to wrap the top level component in your React application.
    * The [[Redux]] store that you create is passed as a prop to the Provider.
    * Any component that is a child of this Provider can access the [[Redux]] store.
    * This pattern is used to implicitly pass down the [[Redux]] store to components without having to manually pass the store as a prop to every component.
    * Here is a simple example of how it might be used:
    * ```javascript
import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-[[Redux]]';
import { createStore } from '[[Redux]]';
import rootReducer from './reducers';
import App from './components/App';

const store = createStore(rootReducer);

render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('root')
);```
      * In this example, the Provider is wrapping the App component and the [[Redux]] store is being passed as a prop to the Provider. This makes the [[Redux]] store available to all components within App.

### Recoil도 비슷한 종류.