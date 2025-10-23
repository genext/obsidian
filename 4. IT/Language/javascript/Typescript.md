---
title: "Typescript"
created: 2024-03-10 17:40:04
updated: 2025-06-13 09:47:00
---
  * MS가 개발
  * typescript로 작성하면 컴파일러(npm run build)가 javascript로 변환해줌.
  * typescript type safety
    * explicit type 지정(python과 동일)
      * variables
        * ```typescript
let a : boolean = false
let b : number[] = [1,2,3]```
      * functions
        * ```typescript
function fname(name: string) : Player {
  ...
}
// or => expression
fname = (name: string) : Player => {
  ...
}```
    * type alias
      * define new type
        * ```typescript
type Player = {
  name: string,
  age?: number
}

let a : Player = {
  name: "jkoh",
}

// or you can use built-in type to define a type
type Name = string

// or you can define a type with specific values
type Team = "red" | "blue", "yellow"
type Health = 1|2|3|4|5```
      * define readonly to provide immutability
        * ```typescript
type Player = {
  readonly name: string,
  age?: number
}```
    * Optional 지정
      * ```typescript
const player : {
  name: string,
  age?: number
} = {
  name: "jkoh"
}```
    * tuple
      * only in typescript
        * ```typescript
const player: [string, number, boolean] = ["jay", 12, true]```
    * any
      * typescript의 타입 보호장치로부터 벗어나고 싶을 때 사용.
      * ```typescript
let a: any = [1,2,3]
let b: any = true
a + b  --> javascript처럼 그냥 실행.```
    * unknown
      * ```typescript
let a: unknown;

if (typeof a === number) {
  let b = a + 1;
}```
    * never
      * shows a function never return but can throw Errors
        * ```typescript
function hello(): never {
  throw new Error("xxx")
}```
      * or a function might return two types(?)
        * ```typescript
function hello(name:string|number) {
  if (typeof name === "string") {...}
  else if (typeof name === number) {...}
  else {name} // --> never execute this block
}```
  * function
    * call signature
      * 일단 signature의 타입만 정의하고 구현 내용은 나중에
      * function overloading을 type으로 정의
      * 함수 정의 시 구현 내용 정리
    * call signature + Generic
      * ```typescript
// 1+2. call signature + function overloading
type SuperPrint = {
  <T>(arr: T[]): T
}

// 3 구현 정의
// const superPrint: SuperPrint = (arr) => {
//     arr.forEach(i => console.log(i))
//   }

const superPrint: SuperPrint = (arr) => arr[0]
// or
function superPrint<T>(arr: T[]) {
  return arr[0]
}

let a = superPrint([1,2,3,4])
let b = superPrint([true, false, true])
let c = superPrint(["a", "b", "c"])
let d = superPrint([1,2, true, false])```
    * Gereric -> 다른 언어처럼 collection의 바탕이 됨.
  * [[OOP]] 방법(class and interface)
    * abstract class
      * ```typescript
abstract class User {
  constructor(
    private firstName: string,
    private lastName: string,
    public nickname
  ) {}
}

class Player extends User {
  
}```
      * abstract method 가능
    * 클래스를 타입으로 정의해서 메소드의 파라미터로 전달 가능. javascript의 오브젝트를 확장. 즉 key에 해당하는 것까지도 이름을 정하지 않고 타입만 정의 가능.
      * ```typescript
type Word = {
  [key: string]: string
}```
    * Interface
      * abstract class 대신 interface로 클래스 타입을 정해서 상속 가능.
      * typescript에는 오브젝트 모양을 정해주는 방법이 두 개 있다?
        * type은 팔방미인
          * ```typescript
type Player = {
  name: string,
  team: Team,
  health: Health
}```
        * interface는 오로지 오브젝트 모양을 정할 때 또는 객체지향방법론에서 일컫는 interface 정의할 때 사용.
          * 오브젝트로서 상속 가능
            * ```typescript
// type으로 정의할 때와 달리 '='가 없음.
interface User {
  name: string,
  age: number
}

interface Player extends User {
  sports: string
}```
          * interface 정의
            * 복수 interface 상속 가능.
            * interface를 데이터 타입처럼 사용해서 함수 파라미터로 사용 가능.
            * ```typescript
interface User {
  firstName: string
  lastName: string
  sayHi(name: string): string
  fullName(): string
}

class Player implements User {
  constructor(
    public firstName: string
    public lastName: string
  ) {}

  fullName() {
    return `this.${firstName} this.${lastName}`
  }
  sayHi(name: string) {
    return `Hello ${name}. My name is ${this.fullName()}`
  }
}

function makeUser(user: User) {
  ...
}```
  * typescript 프로젝트 설정
    * 프로젝트 디렉토리 생성
    * terminal에서 다음 명령어 치면 package.json 생성됨.
      * ```shell
npm init -y```
    * package.json에서 
      * "main": "index.js" 삭제
      * scripts에서 test 삭제하고 공란으로 남김
        * package.json
          * ```json
"scripts": {
  
}```
    * typescript 설치 --> package.json에 devDependencies항목 추가 및 package-lock.json 생성
      * ```shell
npm install -D typescript```
    * src 디렉토리 생성하고 그 안에 index.ts 생성 및 코딩
      * index.ts
        * ```typescript
const hello = () => "hi";```
    * typescript 컴파일 -> javascript 생성
      * root 디렉토리에 tsconfig.json 생성 -> vscode는 이로부터 typescript 프로젝트라는 것을 알게됨.
        * tsconfig.json
          * ```json
{
    "include": [ "src" ],
    "compilerOptions": {"outDir": "build"}
}```
      * package.json의 script에 build 추가
        * package.json
          * ```json
"scripts": {
  "build": "tsc"
}```
      * 컴파일 --> build 디렉토리 생성 --> old version javascript로 index.js 생성
        * ```shell
npm run build```
        * index.js
          * ```javascript
var hello = function () { return "hi"; };```
      * javascript와 lib 버전 설정
        * tsconfig.json에서 target, lib 설정
          * ```json
{
    "include": [ "src" ],
    "compilerOptions": {
        "outDir": "build",
        "target": "ES6",
        "lib": ["ES6", "DOM"],
        "strict": true
    }
}```
          * browser에서도 실행하려면 "DOM" 추가하지만, node.js용으로만, 즉 서버용으로만 할 때는 ES6만 추가.
  * typescript가 모듈에 있는 함수 등의 타입을 알아낼 수 있는 것은 "moduleName.d.ts"라는 declaration file 덕분. 
    * node_module내 lib
      * node_modules/...lib/.../sampleModule.js
        * ```typescript
export function init(config) {
    return true;
}

export function exit(code) {
    return code + 1;
}```
      * node_modules/.../lib/sampleModule.d.ts
        * ```typescript
interface Config {
   url: string; 
}

declare module "myPackage" {
    function init(config: Config): boolean;
    function exit(code: number): number;
}```
      * index.ts
        * ```typescript
import { init, exit } from "sampleModule";

init({url: "true"});

exit(1);```
  * javascript 프로젝트를 typescript 프로젝트로 바꾸거나 javascript와 typescript가 섞여 있을 때
    * 일반 javascript
      * myPackage.js
        * ```javascript
export function init(config) {
    return true;
}

export function exit(code) {
    return code + 1;
}```
    * index.ts
      * ```typescript
import { init } from "./myPackage" --> 같은 디렉토리에 myPackage.js가 있어도 빨간색 밑줄을 표시하며 myPackage를 찾을 수 없다고 나옴. 

init({url: "true"});
```
    * tsconfig.json를 아래와 같이 수정하면 index.ts의 에러 사라짐.
      * ```json
{
    "include": [ "src" ],
    "compilerOptions": {
        "outDir": "build",
        "target": "ES6",
        "lib": ["ES6", "dom"],
        "strict": true,
        "allowJs": true
    }
}```
    * javascript도 typescript의 보호를 받도록 설정.
      * 설정 방법
        * ```javascript
// @ts-check

/**    --> 여기까지 치고 엔터 치면 자동으로 JSDoc 형식 보여줌.
 * 
 * @param {*} config 
 * @returns 
 */```
      * 설정 후 myPackage.js 모습
        * ```javascript
/**
 * Initialize the project
 * @param {object} config 
 * @param {boolean} config.debug
 * @param {string} config.url
 * @returns boolean
 */
export function init(config) {
    return true;
}

/**
 * 
 * @param {number} code 
 * @returns number
 */
export function exit(code) {
    return code + 1;
}```
      * 이후 typescript는 위에서 설정한 comment로 기존 javascript 소스에 타입 안정성을 제공.
  * 개발 환경에서 typescript 빨리 실행하기
    * ts-node
      * 컴파일 없이 바로 실행?
      * ts-node install
        * ```shell
npm -i -D ts-node```
      * package.json 수정
        * dev 추가
        * ```json
"scripts": {
    "build": "tsc",
    "dev": "ts-node src/index",
    "start": "node build/index.js"
  },```
    * nodemon
      * 소스 수정하면 서버를 재시작할 필요 없이 바로 실행.
      * nodemon install
        * ```shell
npm i nodemon```
      * package.json 수정
        * ```json
"scripts": {
    "build": "tsc",
    "dev": "nodemon --exec ts-node src/index.ts",
    "start": "node build/index.js"
  },```
  * typescript ((qGaMODV2-)) project
  * 날짜값을 배열로 받았을 때 오류 회피: [[Roam/genext-2025-10-05-02-18-30/October 18th, 2024#^hThMM6XGD|13:36 서버에서 시간을 보내줄 때 완전하게 보내지 않는 경우가 있다. ]]