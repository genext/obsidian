---
title: "javascript"
created: 2023-09-24 09:21:33
updated: 2025-03-23 15:54:09
---
## Form tag
    *  default behavior when when you have a <form> tag and you submit it using a button or by pressing Enter in an input field, the default behavior is for the browser to send a request to the server and reload the page with the response.
    * <form> tag's default behavior with
    * onSubmit 이벤트 처리할 때 event.preventDefault()를 기본적으로 한다.
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Form Submission</title>
</head>
<body>

<form id="myForm">
  <input type="text" name="username" placeholder="Username">
  <button type="submit">Submit</button>
</form>

<script>
document.getElementById("myForm").addEventListener("submit", function(event) {
  // Prevent the default form submission behavior
  event.preventDefault();
  
  // Perform your custom logic here, such as validation or sending data via AJAX
  
  // For demonstration, let's just log the form data to the console
  const formData = new FormData(this);
  for (const entry of formData.entries()) {
    console.log(entry[0], entry[1]);
  }
});
</script>

</body>
</html>
```
## fetch
    * url을 받아서 데이터를 가져오기
      * 주의!! url 넘길 때 `` 쓴다.
    * Basics
```javascript
fetch(`https://api.coinpaprika.com/v1/tikcers`)
  .then(response => response.json())
  .then(json => consolog.log(json));
```
    * async
```javascript
const getMovies = async() => {
  const response = await fetch(`https://api.coinpaprika.com/v1/tikcers`);
  const json = await response.json()
}

// or
const getMovies = async() => {
  const json = await(
                  await fetch(`https://api.coinpaprika.com/v1/tikcers`)
                ).json;
}
```
## setTimeout
    * 아래 코드 중 첫 번째는 setTimeout을 사용. 
    * ```javascript
useEffect(() => {
  setTimeout(() => {
    getApps();
  }, 0);
}, []);
```
      * useEffect 훅을 여러 개 쓴다면, setTimeout은 getApps를 event loop의 맨 마지막에 놓아서 비동기적으로 실행하게 하는 효과가 있다.
      * 따라서 getApps가 시간이 걸리는 함수일 때 비동기적으로 나머지 코드를 실행할 수 있다.
      * 더구나 getApps 내부에는 API를 호출하는 부분이 있는데, API 호출할 때 반드시 인증 토큰을 함께 보내야 한다. 
      * requestHandler가 이 역할을 하는데 이것도 useEffect에 등록되었다. component tree에서 requestHandler가 등록된 컴포넌트는 getApps가 등록된 컴포넌트보다 나중에 선언되었을 가능성이 있거나 useSelect가 인증 토큰을 바로 읽지 못할 가능성도 있다.
      * setTimeout 효과 덕분에 API 요청할 때 HTTP header의 Authorization에 인증 토큰을 저장하는 requestHandler가 getApps보도 먼저 실행될 수 있게 된다.
    * ```javascript
useEffect(() => {
  getApps();
}, []);
```
      * 이 코드는 간단하지만 위와 달리 getApps가 동기적으로 실행된다.
      * useEffect를 여러 개 쓰면 useEffect 선언 순서에 따라 getApps가 실행된다. 따라서 getApps전에 실행되어야 하는 함수가 useEffect 선언 순서가 getApps보다 뒤에 있다면 에러가 발생한다.
    * getApps 내부에서 사용하는 axiosUtil
```javascript
'use client';

import { useState, useEffect } from 'react';
import { useSelector } from 'react-[[Redux]]';
import { useRouter, usePathname } from 'next/navigation';

import axios from 'axios';
import qs from 'qs';
const axiosObj = axios.create({
  baseURL: '',
  timeout: 210000,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: (params) => {
    return qs.stringify(params, { arrayFormat: 'brackets' });
  },
});

const AxiosInterceptor = ({ children }) => {
  let { accessToken, userInfo } = useSelector((state) => state.auth);
  const [isSet, setIsSet] = useState(false);
  const router = useRouter();
  const currentPath = usePathname();

  useEffect(() => {
    setIsSet(true);

    const requestHandler = (config) => {

      if (currentPath === '/login') {
      } else {
        if (userInfo === null || accessToken === null) {
          router.push('/login');
          return;
        }

        // header에 userid, accessToken 추가
        config.headers.Userid = userInfo?.userid;
        config.headers.accessToken = accessToken;
        config.headers.Authorization = accessToken;
      }

      return config;
    };

    const responseHandler = (response) => {
      if (process.env.NODE_ENV !== 'production') {
        const config = response.config;
        const { url, method } = config;
        const resultResponse = response.data;
        const data = config.params || config.data;

        console.groupCollapsed('API request >> ', url);
        console.log('request', {
          method,
          url,
          data,
        });
        console.log('response', resultResponse);
        console.groupEnd();
      }

      return Promise.resolve(response);
    };

    const errorHandler = (error) => {
      return Promise.reject(error);
    };

    const requsetInterceptor = axiosObj.interceptors.request.use(requestHandler, errorHandler);
    const responseInterceptor = axiosObj.interceptors.response.use(responseHandler, errorHandler);

    return () => {
      axiosObj.interceptors.request.eject(requsetInterceptor);
      axiosObj.interceptors.response.eject(responseInterceptor);
    };
  }, [accessToken, currentPath, router, userInfo]);

  return isSet && children;
};

const common = (config, successHandling, errorHandling) => {
  const resultPromise = axiosObj(config);

  if (successHandling) {
    return resultPromise
      .then((response) => {
        successHandling(response);
      })
      .catch((error) => {
        if (errorHandling) {
          errorHandling(error);
        } else {
          console.error(error);
        }
      });
  } else {
    return resultPromise;
  }
};

const axiosUtil = {
  get: (url, data, successHandling, errorHandling) =>
    common(
      {
        method: 'get',
        url,
        data,
        params: data?.params,
      },
      successHandling,
      errorHandling
    ),
  post: (url, data, successHandling, errorHandling) => {
    let options = {};

    if (data instanceof FormData) {
      options.headers = { 'Content-Type': 'multipart/form-data;' };
      options.maxContentLength = Infinity;
      options.maxBodyLength = Infinity;
    }

    return common(
      {
        method: 'post',
        url,
        data,
        ...options,
      },
      successHandling,
      errorHandling
    );
  },
  put: (url, data, successHandling, errorHandling) =>
    common(
      {
        method: 'put',
        url,
        data,
      },
      successHandling,
      errorHandling
    ),
  delete: (url, data, successHandling, errorHandling) =>
    common(
      {
        method: 'delete',
        url,
        data,
      },
      successHandling,
      errorHandling
    ),
  patch: (url, data, successHandling, errorHandling) =>
    common(
      {
        method: 'patch',
        url,
        data,
      },
      successHandling,
      errorHandling
    ),
  options: (url, data, successHandling, errorHandling) =>
    common(
      {
        method: 'options',
        url,
        data,
      },
      successHandling,
      errorHandling
    ),
  request: (config) => axios(config),
};

export default axiosUtil;
export { AxiosInterceptor };
```
## destructuring assignment: unpacking in python
```javascript
// Array Destructuring
const numbers = [1, 2, 3];
const [a, b, c] = numbers;

console.log(a); // Output: 1
console.log(b); // Output: 2
console.log(c); // Output: 3

// Object Destructuring
const person = {
  name: 'John Doe',
  age: 30,
  profession: 'Developer'
};

const { name, age, profession } = person;

console.log(name);       // Output: John Doe
console.log(age);        // Output: 30
console.log(profession); // Output: Developer
```
## spread operator(또는 rest parameter): 배열과 함수 인자 조작을 간편하게
    * 위 destructuing assignment와 비슷한 기능
    * 배열 내 요소를 분할 또는 객체 속성 각 요소를 할당
```javascript
// 배열 복사
const originalArray = [1, 2, 3];
const copiedArray = [...originalArray];

console.log(copiedArray); // Output: [1, 2, 3]
```
```javascript
// 배열 병합
const array1 = [1, 2, 3];
const array2 = [4, 5, 6];
const mergedArray = [...array1, ...array2];

console.log(mergedArray); // Output: [1, 2, 3, 4, 5, 6]
```
    * 또는 오브젝트 각 요소를 키-값 쌍으로 분할.
    * 함수 인자를 배열로 표시
```javascript
function sum(...numbers) {
  return numbers.reduce((acc, curr) => acc + curr, 0);
}

console.log(sum(1, 2, 3));      // Output: 6
console.log(sum(4, 5, 6, 7));   // Output: 22
console.log(sum(10, 20, 30));   // Output: 60
```
    * Object.assign()과 차이
      * The spread operator (...) and Object.assign() can sometimes be used interchangeably, but they have some subtle differences that may make one more suitable than the other depending on the situation.
        * Inheritance: **Object.assign()** copies both enumerable **own properties** and **inherited properties** from the source objects to the target. The spread operator, however, only includes an object's own enumerable properties, ignoring inherited properties.
        * Property Order: The spread operator has a more predictable property enumeration order that aligns with ES6 property enumeration rules (integer keys first, in ascending order, followed by string keys in insertion order, etc.), while Object.assign() does not guarantee any specific order.
        * Setters: Object.assign() triggers setters whereas the spread operator doesn't. If the object has setter methods, using Object.assign() would invoke those methods, but the spread operator would just get the values.
        * Syntax: Spread syntax can be shorter and sometimes more readable than Object.assign(), especially when merging multiple objects. It also allows for more flexible code arrangements. However, the spread operator creates a new object, while Object.assign() modifies the target object in place.
        * Browser Support: Object.assign() is generally better supported in older browsers compared to the spread operator, although this may not be an issue depending on your target environment.
      * In your specific code snippet:
```javascript
if (additionalFields) Object.assign(rawSlide, additionalFields);
```
        * Here, Object.assign() modifies rawSlide in-place, which could be desirable depending on the context. If the original object (rawSlide) is to be used later in the code, then using Object.assign() would be the right choice. With the spread operator, you would need to create a new object to hold the combined properties.
      * If you were to use the spread operator, the code would look something like:
```javascript
const rawSlides = report.slides.map((slide) => {
  const { title, layoutType, additionalFields } = slide;

  return {
    ...{
      title,
      layoutType,
    },
    ...additionalFields,
  };
});
```
        * Both approaches have their pros and cons, and the choice between them depends on the specific requirements of the task at hand.
## Object.assign()
    * The Object.assign() method is used to copy all enumerable own properties from one or more source objects to a target object. It returns the target object, which is modified as a result of the method call. The syntax is:
```javascript
Object.assign(target, ...sources)
```
      * target: The target object you want to modify.
      * ...sources: The source object(s) from which properties will be copied onto the target.
      * In your provided code snippet, Object.assign(rawSlide, additionalFields); is used to copy all enumerable own properties from the additionalFields object to the rawSlide object.
    * sample code
```javascript
const target = { a: 1, b: 2 };
const source = { b: 4, c: 5 };

Object.assign(target, source);

console.log(target);  // Output: { a: 1, b: 4, c: 5 }
```
      * In this example, the target object originally has properties a and b. The source object has properties b and c. After Object.assign(target, source) is called, the target object is modified to include all properties from source, and its existing b property is updated with the new value from source.
      * Similarly, in your code snippet, Object.assign(rawSlide, additionalFields); would add or update properties from additionalFields to rawSlide.
## reduce
    * 배열 각 요소에 대해 reducer 함수 실행하고 결과값을 하나만 반환.
    * the difference between reduce and map
      * map
        * Applies a given function to each item of an array, in order, and returns a new array from the results.
      * reduce
        *  Applies a function against an accumulator and each element in the array (from left to right) to reduce it to a single value.
      * example
        * ```javascript
// Sample array
const numbers = [1, 2, 3, 4, 5];

// Map operation: Double each number
const doubled = numbers.map(number => number * 2);

// Reduce operation: Sum all numbers
const sum = doubled.reduce((accumulator, current) => accumulator + current, 0);

console.log(sum); // Output will be the sum of all doubled numbers```
## [[mongodb]]에서 데이터 읽은 다음, 다른 형태로 전환하고자 하면 조회결과를 먼저 일반 오브젝트로 바꿔야 한다. **toObject()** 메소드 사용.
    * ```plain text
MongoDB often returns document objects as instances of a Document class provided by Mongoose or another ODM (Object Document Mapper). These objects behave almost like regular JavaScript objects, but they have additional methods and properties and are not extensible in the same way. In your specific case, it looks like directly modifying the slides array is not affecting the original report object as expected.
Try converting the Mongoose document to a plain JavaScript object before modifying it. This can be done using the .toObject() method.```
    * ```javascript
const reportDoc = await Report.findById(query.id);
          if (!reportDoc) {
            return res.status(404).json({ error: 'Report not found' });
          }

          // To change the data, you must objectify the data from mongoDB.
          const report = reportDoc.toObject();```
## 테스트 데이터를 엑셀에 저장하고 해당 파일을 읽어서 mongoDB에 저장
    * 엑셀파일
      * ![[100. media/documents/astfq14Mwy.xlsx]]
    * save_test-data.js
```javascript
import mongoose from 'mongoose';
import XLSX from 'xlsx';
import PromptModule from './models/prompt-management/prompt-module.js';
import PromptType from './models/prompt-management/prompt-type.js';
import GPTModelType from './models/prompt-management/gpt-model-type.js';
import GPTModelVersion from './models/prompt-management/gpt-model-version.js';
import ReportType from './models/prompt-management/report-type.js';
import SlideType from './models/prompt-management/slide-type.js';
import SlideLayout from './models/prompt-management/slide-layout.js';
import crypto from 'crypto';

const encryptionKey = Buffer.from('f5fdf4ad6ee79159b4c41762e72521e19e55478f3caf8b2807129bca1d3ecb3b', 'hex');
const iv = Buffer.from('e56cc137af91b4b4a589f66225efc073', 'hex');

function encrypt(text) {
  const cipher = crypto.createCipheriv('aes-256-cbc', encryptionKey, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

function decrypt(text) {
  const decipher = crypto.createDecipheriv('aes-256-cbc', encryptionKey, iv);
  let decrypted = decipher.update(text, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}
const readExcelAndSaveToDB = async (filePath) => {
  mongoose
    .connect('mongodb+srv://gai:gai1234@zoona.zcdwncl.mongodb.net/test', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    })
    .then()
    .catch((err) => {
      logger.error(`DB Connection Error: ${err.message}`);
    });
  const workbook = XLSX.readFile(filePath);
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];
  const data = XLSX.utils.sheet_to_json(sheet);

  // Pre-fetch ObjectIds
  const promptTypes = await PromptType.find().lean();
  console.log('promptTypes: ', promptTypes);
  const gptModelTypes = await GPTModelType.find().lean();
  console.log('gptModelTypes: ', gptModelTypes);
  const gptModelVersions = await GPTModelVersion.find().lean();
  console.log('gptModelVersions: ', gptModelVersions);
  const reportTypes = await ReportType.find().lean();
  console.log('reportTypes: ', reportTypes);
  const slideTypes = await SlideType.find().lean();
  console.log('slideTypes: ', slideTypes);
  const slideLayouts = await SlideLayout.find().lean();
  console.log('slideLayouts: ', slideLayouts);

  for (const row of data) {
    console.log('row: ', row);
    const promptTypeId = promptTypes.find((type) => type.type === row.promptType)?._id;
    const gptModelTypeId = gptModelTypes.find((type) => type.type === row.gptModelType)?._id;
    const gptModelVersionId = gptModelVersions.find((type) => type.type === row.gptModelVersion.toString())?._id;
    const reportTypeId = reportTypes.find((type) => type.type === row.reportType)?._id;
    const slideTypeId = slideTypes.find((type) => type.type === row.slideType)?._id;
    const slideLayoutId = slideLayouts.find((type) => type.type === row.slideLayout)?._id;

    const promptModule = new PromptModule({
      code: row.code,
      name: row.code, // Adjust as necessary
      promptType: promptTypeId,
      gptModelType: gptModelTypeId,
      gptModelVersion: gptModelVersionId,
      prompt: encrypt(row.prompt),
      applied_count: 0, // Default value if not provided in Excel
      description: row.prompt, // Adjust as necessary
      creator: row.creator,
      modifier: row.modifier,
      reportType: reportTypeId,
      slideType: slideTypeId,
      slideLayout: slideLayoutId,
    });

    await promptModule.save();
  }
};

readExcelAndSaveToDB('./prompt_module_data2.xlsx')
  .then(() => {
    console.log('Data imported successfully');
    mongoose.disconnect();
  })
  .catch((err) => {
    console.error('Error importing data:', err);
    mongoose.disconnect();
  });

```
## 암호화
  Node의 cipher 클래스 이용
```javascript
import { scrypt, randomFill, createCipheriv } from 'node:crypto';

function encryptData() {
  const algorithm = 'aes-256-cbc';
  const password = 'Password used to generate key';

  scrypt(password, 'salt', 32, (err, key) => {
    if (err) throw err;

    randomFill(new Uint8Array(16), (err, iv) => {
      console.log('password: ', password);
      if (err) throw err;

      const cipher = createCipheriv(algorithm, key, iv);

      let encrypted = cipher.update('some clear text data', 'utf8', 'hex');
      encrypted += cipher.final('hex');
      console.log(`Encrypted: ${encrypted}`);
      console.log(`Key (hex): ${key.toString('hex')}`);
      console.log(`IV (hex): ${Buffer.from(iv).toString('hex')}`);
    });
  });
}

// Call the function to perform encryption
encryptData();

```
## [[Typescript]]
## Promise --> javascript에서  async 처리를 위한 것으로 java의 future와 비슷.
## 읽을 책: https://eloquentjavascript.net/