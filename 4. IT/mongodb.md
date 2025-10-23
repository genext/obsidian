---
title: "mongodb"
created: 2023-11-30 08:27:52
updated: 2024-02-29 16:29:13
---
  * 에러 및 처리 방법
    * 원인 코드
      * ```javascript
export default async function handler(req, res) {
  try {
    await connectToDatabase();
    const { method, query, body } = req;
    let promptModule = null;

    switch (method) {
      case 'GET':
        if (query.id) {
          // 특정 프롬프트 모듈 하나만 조회할 때(수정 화면용)
          const data = await PromptModule.findById(query.id)
            .populate('promptType')
            .populate('gptModelType')
            .populate('gptModelVersion')
            .populate('reportType')
            .populate('slideType')
            .populate('slideLayout');
          const formattedData = {
            ...data.toObject(),
            createdAt: formatMongoDate(data.createdAt),
            updatedAt: formatMongoDate(data.updatedAt),
          };
          res.status(200).json(formattedData);
        } else {
          console.log('query: ', query);
          const buildQueryCondition = (body, field) => {
            const excludeFields = ['action', 'page', 'limit'];

            if (!excludeFields.includes(field)) {
              if (Array.isArray(body[field]) && body[field].length > 0) {
                return { [field]: { $in: body[field] } };
              } else if (body[field]) {
                return { [field]: body[field] };
              }
            }
            return null;
          };
          let promptModules = null;
          let queryConditions = [];
          const fields = [
            'promptType',
            'reportType',
            'slideType',
            'slideLayout',
            'gptModelType',
            'gptModelVersion',
            'code',
            'name',
            'modifier',
          ];

          /*
          fields.forEach((field) => {
            const condition = buildQueryCondition(query, field);
            if (condition) queryConditions.push(condition);
          });
          */
          Object.keys(query).forEach((field) => {
            const condition = buildQueryCondition(query, field);
            if (condition) queryConditions.push(condition);
          });

          // You must use $and to combine multiple conditions because queryConditions is just an array not an object that MongoDB expects.
          const matchConditions = queryConditions.length > 0 ? { $and: queryConditions } : {};
          console.log('queryConditions: ', queryConditions);
          const querySelect =
            '_id code name promptType gptModelType gptModelVersion prompt applied_count description creator createAt modifier updatedAt';
          if (query.action === 'popup') {
            console.log('popup!!!!');
            // 메가 프롬프트 등록 화면 중 프롬프트 모듈 추가 버튼 누르면 보여줘야 하는 프롬프트 모듈 코드 팝업용
            promptModules = await PromptModule.find(queryConditions)      --------------> 여기서 queryConditions가 한 오브젝트가 아님. 에러 메시지 참고.
              .populate('promptType')
              .populate('gptModelType')
              .populate('gptModelVersion')
              .sort({ code: 1 })
              .select(querySelect);
            const formattedData = promptModules.map((module) => ({
              ...module.toObject(),
              createdAt: formatMongoDate(module.createdAt),
              updatedAt: formatMongoDate(module.updatedAt),
            }));
            res.json(formattedData);
          } else {
            const projectFields = querySelect.split(' ').reduce((acc, field) => {
              acc[field] = 1; // Set each field to 1 to include it in the output
              return acc;
            }, {});
            // 목록 조회 화면용
            const page = query.page ? Number(query.page) : 1;
            const pageSize = query.limit ? Number(query.limit) : 10;

            const aggregationPipeline = [
              { $match: matchConditions },
              {
                $lookup: {
                  from: 'prompttypes',
                  localField: 'promptType',
                  foreignField: '_id',
                  as: 'promptType',
                },
              },
              {
                $lookup: {
                  from: 'gptmodeltypes',
                  localField: 'gptModelType',
                  foreignField: '_id',
                  as: 'gptModelType',
                },
              },
              {
                $lookup: {
                  from: 'gptmodelversions',
                  localField: 'gptModelVersion',
                  foreignField: '_id',
                  as: 'gptModelVersion',
                },
              },
              {
                $facet: {
                  totalData: [{ $count: 'totalCount' }],
                  promptModules: [
                    { $sort: { updatedAt: -1 } },
                    { $skip: (page - 1) * pageSize },
                    { $limit: pageSize },
                    {
                      $project: {
                        ...projectFields,
                        createdAt: {
                          $dateToString: { format: '%Y.%m.%d %H:%M:%S', date: '$createdAt' },
                        },
                        updatedAt: {
                          $dateToString: { format: '%Y.%m.%d %H:%M:%S', date: '$updatedAt' },
                        },
                      },
                    },
                  ],
                },
              },
            ];
            const result = await PromptModule.aggregate(aggregationPipeline);
            // console.log('result: ', result[0].promptModules);
            const totalRecords = result[0].totalData[0]?.totalCount || 0;
            const promptModules = result[0].promptModules;
            res.json({ promptModules, totalRecords });
          }
        }
        break;
   ```
    * 에러
      * ```plain text
Parameter "filter" to find() must be an object, got "[object Object],[object Object],[object Object],[object Object],[object Object]" (type object)
ObjectParameterError: Parameter "filter" to find() must be an object, got "[object Object],[object Object],[object Object],[object Object],[object Object]" (type object)
    at Query.find (C:\genai\tokaireport\node_modules\mongoose\lib\query.js:2329:16)
    at Function.find (C:\genai\tokaireport\node_modules\mongoose\lib\model.js:2079:13)
    at handler (webpack-internal:///(api)/./pages/api/v1/report/prompt-management/prompt-module/index.js:343:127)
    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)```
    * 원인: You must use $and to combine multiple conditions because queryConditions is just an array not an object that MongoDB expects.
    * 수정 코드
      * ```javascript
// find 인자로 오브젝트 배열이 아닌 오브젝트 자체를 넘겨준다.
promptModules = await PromptModule.find(queryConditions)   ----->     promptModules = await PromptModule.find(matchConditions)```
  * 복잡한 조회조건을 만드는 소스
    * ```python
import { connectToDatabase } from '@/lib/db';
import PromptModule from '@/models/prompt-management/prompt-module';
import PromptType from '@/models/prompt-management/prompt-type';
import GPTModelType from '@/models/prompt-management/gpt-model-type';
import GPTModelVersion from '@/models/prompt-management/gpt-model-version';
import ReportType from '@/models/prompt-management/report-type';
import SlideType from '@/models/prompt-management/slide-type';
import SlideLayout from '@/models/prompt-management/slide-layout';
import logger from '@/lib/winston';
import { formatMongoDate } from '@/app/_util/common-util';
import { ObjectId } from 'mongodb';

/**
 * @swagger
 * /api/v1/report/prompt-module:
 *   get:
 *     tags:
 *       - 프롬프트 모듈 관리
 *     summary: 프롬프트 모듈 조회
 *     description: |
 *       여러 시나리오에 따라 프롬프트 모듈을 조회합니다.
 *       - 시나리오 1: 특정 프롬프트 모듈 하나만 조회 (Query Parameter: id)
 *       - 시나리오 2: 메가 프롬프트 등록 화면 중 프롬프트 모듈 추가할 때 프롬프트 모듈 코드 팝업용 (RequestBody: action = 'popup')
 *       - 시나리오 3: 일반 목록 조회, 필터링 및 페이지네이션 적용 (Query Parameters: page, limit; RequestBody for filtering)
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: false
 *         description: 조회할 프롬프트 모듈의 MongoDB ObjectId (시나리오 1용)
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *         required: false
 *         description: 페이지 번호 (시나리오 3용)
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *         required: false
 *         description: 페이지 당 항목 수 (시나리오 3용)
 *     requestBody:
 *       required: false
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               action:
 *                 type: string
 *                 example: "popup"
 *               promptType:
 *                 type: string
 *                 example: "prompt-type의 objectId"
 *               gptModelType:
 *                 type: string
 *                 example: gpt-model-type의 objectId
 *               gptModelVersion:
 *                 type: string
 *                 example: gpt-model-version의 objectId
 *               reportType:
 *                 type: string
 *                 example: report-type의 objectId
 *               slideType:
 *                 type: string
 *                 example: slide-type의 objectId
 *               slideLayout:
 *                 type: string
 *                 example: slide-layout의 objectId
 *               code:
 *                 type: string
 *                 example: 모듈 코드
 *               name:
 *                 type: string
 *                 example: 모듈명
 *               modifier:
 *                 type: string
 *                 example: 수정자
 *     responses:
 *       200:
 *         description: A successful response with one or more prompt modules
 *         example:
 *           {
 *             "promptModules": [
 *                {
 *                  "_id": "655d3e69985442c8040d37ed",
 *                  "code": "prompt_code_2",
 *                  "name": "Sample Prompt Module",
 *                  "prompt": "Write a short story based on given keywords.",
 *                  "applied_count": 0,
 *                  "description": "This module generates creative writing prompts.",
 *                  "creator": "jkoh",
 *                  "updatedAt": "2023-11-21T23:34:01.458Z",
 *                  "promptType": [],
 *                  "gptModelType": [],
 *                  "gptModelVersion": [
 *                    {
 *                       "_id": "655d42bdb1769baefdfa0eb8",
 *                       "type": "4.0",
 *                       "description": "4.0 버전",
 *                       "__v": 0
 *                    }
 *                  ]
 *                }
 *             ],
 *             "totalRecords": 2
 *           }
 *       404:
 *         description: Prompt module not found
 *
 *   post:
 *     tags:
 *       - 프롬프트 모듈 관리
 *     summary: Create a Prompt Module
 *     description: Create a new prompt module.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/PromptModule'
 *           example:
 *             code: "PM-001"
 *             name: "Analysis Module"
 *             promptType: "Data Analysis"
 *             gptModelType: "GPT-4"
 *             gptModelVersion: "4.0"
 *             prompt: "Analyze the given dataset and provide insights"
 *             applied_count: 0
 *             description: "This module provides deep analysis for data sets"
 *             creator: "User123"
 *             modifier: "User456"
 *             reportType: "report-type의 objectId"
 *             slideType: "slide-type의 objectId"
 *             slideLayout: "slide-layout의 objectId"
 *     responses:
 *       201:
 *         description: The newly created prompt module
 *
 *   put:
 *     tags:
 *       - 프롬프트 모듈 관리
 *     summary: Update a Prompt Module
 *     description: Update an existing prompt module.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/PromptModule'
 *           example:
 *             code: "PM-001"
 *             name: "Analysis Module"
 *             promptType: "Data Analysis"
 *             gptModelType: "GPT-4"
 *             gptModelVersion: "4.0"
 *             prompt: "Analyze the given dataset and provide insights"
 *             applied_count: 2
 *             description: "This module provides deep analysis for data sets"
 *             creator: "User123"
 *             modifier: "User456"
 *             reportType: "report-type의 objectId"
 *             slideType: "slide-type의 objectId"
 *             slideLayout: "slide-layout의 objectId"
 *     responses:
 *       200:
 *         description: The updated prompt module
 *       404:
 *         description: Prompt module not found
 *
 *   delete:
 *     tags:
 *       - 프롬프트 모듈 관리
 *     summary: Delete Prompt Modules
 *     description: Delete one or more prompt modules.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               delete_targets:
 *                 type: array
 *                 items:
 *                   type: string
 *                 description: 삭제할 프롬프트 모듈의 MongoDB ObjectId 배열
 *           example:
 *             delete_targets:
 *               - "62c5ed1f3537f3ee89e33780"
 *               - "62c5ed1f3537f3ee89e33781"
 *     responses:
 *       200:
 *         description: Prompt module(s) successfully deleted
 *       400:
 *         description: Invalid request or prompt module is in use
 *       404:
 *         description: Prompt module not found
 *
 * components:
 *   schemas:
 *     PromptModule:
 *       type: object
 *       properties:
 *         code:
 *           type: string
 *           required: true
 *           unique: true
 *         name:
 *           type: string
 *           required: true
 *         promptType:
 *           type: string
 *           format: uuid
 *           required: true
 *           description: Reference to a prompt type
 *         gptModelType:
 *           type: string
 *           format: uuid
 *           required: true
 *           description: Reference to a gpt model type
 *         gptModelVersion:
 *           type: string
 *           format: uuid
 *           required: true
 *           description: Reference to a gpt model version
 *         prompt:
 *           type: string
 *           required: true
 *         applied_count:
 *           type: integer
 *           required: true
 *         description:
 *           type: string
 *         creator:
 *           type: string
 *         createdAt:
 *           type: string
 *           format: date-time
 *         modifier:
 *           type: string
 *         updatedAt:
 *           type: string
 *           format: date-time
 *         reportType:
 *           type: string
 *           format: uuid
 *           description: Reference to a report document
 *         slideType:
 *           type: string
 *           format: uuid
 *           description: Reference to a slide type document
 *         slideLayout:
 *           type: string
 *           format: uuid
 *           description: Reference to a slide layout document
 *           required: false
 */
export default async function handler(req, res) {
  try {
    await connectToDatabase();
    const { method, query, body } = req;
    let promptModule = null;

    switch (method) {
      case 'GET':
        if (query.id) {
          // 특정 프롬프트 모듈 하나만 조회할 때(수정 화면용)
          const data = await PromptModule.findById(query.id)
            .populate('promptType')
            .populate('gptModelType')
            .populate('gptModelVersion')
            .populate('reportType')
            .populate('slideType')
            .populate('slideLayout');
          const formattedData = {
            ...data.toObject(),
            createdAt: formatMongoDate(data.createdAt),
            updatedAt: formatMongoDate(data.updatedAt),
          };
          res.status(200).json(formattedData);
        } else {
          console.log('query: ', query);
          const buildQueryCondition = (field) => {
            console.log('field in buildQueryCondition: ', field);
            const excludeFields = ['action', 'page', 'limit'];
            const objectIdFields = [
              'promptType',
              'reportType',
              'slideType',
              'slideLayout',
              'gptModelType',
              'gptModelVersion',
            ];

            let actualField = field;
            if (query.hasOwnProperty(`${field}[]`)) {
              actualField = `${field}[]`;
            }
            if (!excludeFields.includes(field)) {
              if (objectIdFields.includes(field)) {
                if (Array.isArray(query[actualField]) && query[actualField].length > 0) {
                  return { [field]: { $in: query[actualField].map((id) => new ObjectId(id)) } };
                } else if (query[actualField]) {
                  return { [field]: new ObjectId(query[actualField]) };
                }
              } else {
                console.log('no objectId', query[actualField]);
                return query[actualField] ? { [field]: { $regex: new RegExp(query[actualField], 'i') } } : null;
              }
            }
            return null;
          };
          let promptModules = null;
          let queryConditions = [];
          const fields = [
            'promptType',
            'reportType',
            'slideType',
            'slideLayout',
            'gptModelType',
            'gptModelVersion',
            'code',
            'name',
            'modifier',
          ];

          fields.forEach((field) => {
            const condition = buildQueryCondition(field);
            if (condition) queryConditions.push(condition);
          });

          console.log('queryConditions: ', queryConditions);
          // You must use $and to combine multiple conditions because queryConditions is just an array not an object that MongoDB expects.
          const matchConditions = queryConditions.length > 0 ? { $and: queryConditions } : {};
          const querySelect =
            '_id code name promptType reportType slideType slideLayout gptModelType gptModelVersion prompt applied_count description creator createAt modifier updatedAt';
          if (query.action === 'popup') {
            // 메가 프롬프트 등록 화면 중 프롬프트 모듈 추가 버튼 누르면 보여줘야 하는 프롬프트 모듈 코드 팝업용
            promptModules = await PromptModule.find(matchConditions)
              .populate('promptType')
              .populate('gptModelType')
              .populate('gptModelVersion')
              .sort({ code: 1 })
              .select(querySelect);
            const formattedData = promptModules.map((module) => ({
              ...module.toObject(),
              createdAt: formatMongoDate(module.createdAt),
              updatedAt: formatMongoDate(module.updatedAt),
            }));
            res.json(formattedData);
          } else {
            const projectFields = querySelect.split(' ').reduce((acc, field) => {
              acc[field] = 1; // Set each field to 1 to include it in the output
              return acc;
            }, {});
            // 목록 조회 화면용
            const page = query.page ? Number(query.page) : 1;
            const pageSize = query.limit ? Number(query.limit) : 10;

            const aggregationPipeline = [
              { $match: matchConditions },
              {
                $lookup: {
                  from: 'prompttypes',
                  localField: 'promptType',
                  foreignField: '_id',
                  as: 'promptType',
                },
              },
              {
                $lookup: {
                  from: 'gptmodeltypes',
                  localField: 'gptModelType',
                  foreignField: '_id',
                  as: 'gptModelType',
                },
              },
              {
                $lookup: {
                  from: 'gptmodelversions',
                  localField: 'gptModelVersion',
                  foreignField: '_id',
                  as: 'gptModelVersion',
                },
              },
              {
                $facet: {
                  totalData: [{ $count: 'totalCount' }],
                  promptModules: [
                    { $sort: { updatedAt: -1 } },
                    { $skip: (page - 1) * pageSize },
                    { $limit: pageSize },
                    {
                      $project: {
                        ...projectFields,
                        createdAt: {
                          $dateToString: { format: '%Y.%m.%d %H:%M:%S', date: '$createdAt' },
                        },
                        updatedAt: {
                          $dateToString: { format: '%Y.%m.%d %H:%M:%S', date: '$updatedAt' },
                        },
                      },
                    },
                  ],
                },
              },
            ];
            const result = await PromptModule.aggregate(aggregationPipeline);
            // console.log('result: ', result[0].promptModules);
            const totalRecords = result[0].totalData[0]?.totalCount || 0;
            const promptModules = result[0].promptModules;
            res.json({ promptModules, totalRecords });
          }
        }
        break;
      case 'POST':
        console.log('--------------------------------------');
        console.log('body: ', body);
        promptModule = await PromptModule.create(body);
        res.status(201).json(promptModule);
        break;
      case 'PUT':
        const { action, update_targets } = body;
        if (action === 'addCount' && Array.isArray(update_targets)) {
          for (const target of update_targets) {
            const { _id, count } = target;
            await PromptModule.findByIdAndUpdate(
              _id,
              { $inc: { applied_count: count } },
              { new: true, runValidators: true }
            );
          }
        } else {
          promptModule = await PromptModule.findByIdAndUpdate(body._id, body, {
            new: true,
            runValidators: true,
          });
          if (!promptModule) {
            return res.status(404).json({ success: false });
          }
          res.status(200).json(promptModule);
        }
        break;
      case 'DELETE':
        console.log('delete request: ', query);
        // 하나만 삭제 요청해도 삭제 대상 오브젝트 ID는 항상 배열에 담아서 요청.
        if (Array.isArray(query.delete_targets)) {
          const objectIds = query.delete_targets.map((id) => new ObjectId(id));
          try {
            const result = await PromptModule.deleteMany({ _id: { $in: objectIds } });
            if (result.deletedCount === 0)
              return res.status(200).json({ success: false, message: 'No documents found with the provided IDs.' });
            return res.status(200).json({ success: true, deletedCount: result.deletedCount });
          } catch (error) {
            console.error('Error in deleteMany operation:', error);
            return res.status(500).json({ error: 'Internal Server Error' });
          }
        } else {
          console.log('delete only one');
          const objectId = new ObjectId(query.delete_targets);
          try {
            const result = await PromptModule.deleteOne({ _id: objectId });
            if (result.deletedCount === 0)
              return res.status(200).json({ success: false, message: 'No documents found with the provided IDs.' });
            return res.status(200).json({ success: true, deletedCount: result.deletedCount });
          } catch (error) {
            console.error('Error in deleteOne operation:', error);
            return res.status(500).json({ error: 'Internal Server Error' });
          }
        }
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.error(error);
    logger.error('An error occurred:', error);
    return res.status(500).json({ error: `An error occurred: ${error}` });
  }
}

```