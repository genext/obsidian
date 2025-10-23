---
title: "November 23rd, 2023"
created: 2023-11-23 08:20:51
updated: 2023-11-23 15:46:22
---
  * 09:17 [ ] useCallback, handleAxiosError, useEffect 비교 및 다시 공부
    * 특히 이번에 추가한 promptTypeData 처리 부분과 비교해서 어떤 방식이 가장 좋은지 비교 분석.
    * custome hook을 만들었더니 re-render가 반복되었다. 이를 useCallback으로 해결.
      * 잘못된 버전
        * custom hook
          * ```javascript
import { useState, useEffect } from 'react';
import axiosUtil from '@/app/util/axios-util';

const useFetchAndTransform = (url, transformFunction, errorHandler) => {
  if (!url || !transformFunction || !errorHandler) {
    console.error('Missing required parameters.');
    return [];
  }
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axiosUtil.get(url);
        const transformedData = response.data.map(transformFunction);
        setData(transformedData);
      } catch (error) {
        console.error('Error fetching data: ', error);
        errorHandler(error);
      }
    };
    fetchData();
  }, [url, transformFunction, errorHandler]);
  return data;
};

export default useFetchAndTransform;

```
        * custom hook을 호출하는 컴포넌트
          * ```javascript
'use client';

import Link from 'next/link';
// import Image from "next/image"
import { useState, useRef, useEffect } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import AdminLeft from '@/app/admin/components/admin-left';
import PopupPromptEdit from '../popup-prompt-edit';
import PopupPromptDelete from '../popup-prompt-delete';
import PopupConfirmAlert from '@/app/components/popup-confirm-alert';
import PopupToast from '@/app/components/popup-toast';
import { promptData } from '@/app/admin/components/temp-data';
import axiosUtil from '@/app/util/axios-util';
import {
  PROMPT_TYPE,
  REPORT_TYPE,
  SLIDE_TYPE,
  SLIDE_LAYOUT,
  GPT_MODEL_TYPE,
  GPT_MODEL_VERSION,
} from '@/config/apiPaths';
import usePopupAndLogout from '@/app/util/error-popup-logout';
import useFetchAndTransform from '@/app/util/fetch-transform';

export default function AdminPromptDetail() {
  const { confirmPopup, setConfirmPopup, popupMessage, handlePopupMessage, handleAxiosError } = usePopupAndLogout();
  const pathname = usePathname();
  const pathId = pathname.substring(pathname.lastIndexOf('/') + 1);
  const router = useRouter();

  // 적용프롬프트 팝업
  const [showPopupPromptEdit, setShowPopupPromptEdit] = useState(false);
  const [showPopupPromptDelete, setShowPopupPromptDelete] = useState(false);
  const [selectedModule, setSelectedModule] = useState(null);
  const onPromptPopupEdit = (module) => {
    setSelectedModule(module);
    setShowPopupPromptEdit(true);
  };
  const onPromptPopupDelete = (module) => {
    setSelectedModule(module);
    setShowPopupPromptDelete(true);
  };
  function onHidePopupPrompt() {
    setShowPopupPromptEdit(false);
    setShowPopupPromptDelete(false);
  }

  // 저장
  const onSave = () => {
    if (bodyValue === '성공') {
      //임시
      onPromptPopupEdit(mnameValue);
      // onOpenSuccessToast();
      // router.push('/admin/prompt');
    } else {
      onOpenErrorPopup();
    }
  };
  // 삭제
  const [openDeletePopup, setOpenDeletePopup] = useState(false);
  const onDelete = () => {
    setOpenDeletePopup(true);
  };
  const onConfirmDelete = () => {
    // 삭제시키기
    onPromptPopupDelete(mnameValue);
    setOpenDeletePopup(false);
  };
  const onCloseDeletePopup = () => {
    setOpenDeletePopup(false);
  };
  useEffect(() => {
    if (openDeletePopup) {
      document.body.classList.add('on-pop');
    } else {
      document.body.classList.remove('on-pop');
    }
  }, [openDeletePopup]);

  // ErrorPopup
  const [openErrorPopup, setOpenErrorPopup] = useState(false);
  function onOpenErrorPopup() {
    setOpenErrorPopup(true);
  }
  function onCloseErrorPopup() {
    setOpenErrorPopup(false);
  }

  // SuccessToast
  const [openSuccessToast, setOpenSuccessToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  function onOpenSuccessToast() {
    if (pathId === 'regist') {
      setToastMessage('저장되었습니다.');
    } else {
      setToastMessage('정보가 수정되었습니다.');
    }
    setOpenSuccessToast(true);
  }
  function onCloseSuccessToast() {
    setOpenSuccessToast(false);
  }

  const [activeLnav, setactiveLnav] = useState(21);

  const [mcodeValue, setMcodeValue] = useState('');
  const [mnameValue, setMnameValue] = useState('');
  const [mtypeValue, setMtypeValue] = useState('모듈유형 선택');
  const [templateValue, setTemplateValue] = useState('보고서 템플릿 선택');
  const [btypeValue, setBtypeValue] = useState('유형 선택');
  const [layoutValue, setLayoutValue] = useState('보고서 레이아웃 선택');
  const [applyValue, setApplyValue] = useState('');
  const [modelValue, setModelValue] = useState('');
  const [versionValue, setVersionValue] = useState('');
  const [bodyValue, setBodyValue] = useState('');
  const [noteValue, setNoteValue] = useState('');
  const [registrantValue, setRegistrantValue] = useState('');
  const [emailRegistrantValue, setEmailRegistrantValue] = useState('');
  const [dateRegistValue, setDateRegistValue] = useState('');
  const [modifierValue, setModifierValue] = useState('');
  const [emailModifierValue, setEmailModifierValue] = useState('');
  const [dateModifyValue, setDateModifyValue] = useState('');

  useEffect(() => {
    const foundItem = promptData.find((item) => String(item.id) === pathId);
    if (foundItem) {
      setMcodeValue(foundItem.mcode);
      setMnameValue(foundItem.mname);
      setMtypeValue(foundItem.mtype);
      setTemplateValue(foundItem.template);
      setBtypeValue(foundItem.btype);
      setLayoutValue(foundItem.layout);
      setApplyValue(foundItem.apply);
      setModelValue(foundItem.model);
      setVersionValue(foundItem.version);
      setBodyValue(foundItem.body);
      setNoteValue(foundItem.note);
      setRegistrantValue(foundItem.registrant);
      setEmailRegistrantValue(foundItem.email_registrant);
      setDateRegistValue(foundItem.date_regist);
      setModifierValue(foundItem.modifier);
      setEmailModifierValue(foundItem.email_modifier);
      setDateModifyValue(foundItem.date_modify);
    }
  }, [pathId]);

  // 저장 disabled
  const requiredItems = [
    mcodeValue,
    mnameValue,
    mtypeValue,
    templateValue,
    btypeValue,
    modelValue,
    versionValue,
    bodyValue,
  ];
  const isAllRequiredItems = requiredItems.every(Boolean);

  // prompt type, report type, slide type, slide layout을 mongoDB에서 읽기
  const [slideTypeData, setSlideTypeData] = useState([]);
  const [slideLayoutData, setSlideLayoutData] = useState([]);

  const transformPromptType = (item) => ({
    id: item._id,
    label: item.type,
    isChecked: false,
  });

  const transformReportType = (item) => ({
    id: item._id,
    label: item.type,
  });

  const fetchedPromptTypeData = useFetchAndTransform(PROMPT_TYPE, transformPromptType, handleAxiosError);
  const fetchedReportTypeData = useFetchAndTransform(REPORT_TYPE, transformReportType, handleAxiosError);

  // gpt model type을 mongoDB에서 읽기
  const [gptModelTypeData, setGPTModelTypeData] = useState([]);
  const [selectedGPTModel, setSelectedGPTModel] = useState('');
  useEffect(() => {
    const fetchGPTModelTypeData = async () => {
      try {
        const response = await axiosUtil.get(GPT_MODEL_TYPE);
        const transformedData = response.data.map(({ _id, type }) => ({
          _id,
          type,
        }));
        setGPTModelTypeData(transformedData);
        if (transformedData.length > 0) {
          setSelectedGPTModel(transformedData[0]._id);
        }
      } catch (err) {
        console.error('Error fetching GPT model type data:', err);
        handleAxiosError(err);
      }
    };
    fetchGPTModelTypeData();
  }, []);

  const handleModelChange = (id) => {
    setSelectedGPTModel(id);
  };
  return (
    <div className="container">
      <AdminLeft activeLnav={activeLnav} setactiveLnav={setactiveLnav} />
      <main className="main">
        <div className="contents-admin">
          <div className="area-admin">
            {pathId === 'regist' ? <h2>프롬프트 모듈 등록</h2> : <h2>프롬프트 모듈 상세/수정</h2>}
            <div className="contents-admin-wide h800">
              <div className="contents-admin-left">
                <section className="box-t1">
                  <ul className="list-form">
                    <li>
                      <h3 className="required">모듈 코드</h3>
                      <div className="wrap-input">
                        <input
                          type="text"
                          placeholder="모듈 코드를 입력해주세요."
                          autoComplete="off"
                          defaultValue={mcodeValue}
                          onChange={(e) => setMcodeValue(e.target.value)}
                        ></input>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">모듈 이름</h3>
                      <div className="wrap-input">
                        <input
                          type="text"
                          placeholder="모듈 이름를 입력해주세요."
                          autoComplete="off"
                          defaultValue={mnameValue}
                          onChange={(e) => setMnameValue(e.target.value)}
                        ></input>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">모듈 유형</h3>
                      <div className="wrap-select">
                        <select value={mtypeValue} onChange={(e) => setMtypeValue(e.target.value)}>
                          <option value="">{mtypeValue}</option>
                          {fetchedPromptTypeData.map((option) => (
                            <option key={option.id} value={option.id}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">보고서 템플릿 선택</h3>
                      <div className="wrap-select">
                        <select value={templateValue} onChange={(e) => setTemplateValue(e.target.value)}>
                          <option value="">{templateValue}</option>
                          {fetchedReportTypeData.map((option) => (
                            <option key={option.id} value={option.id}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">유형 선택</h3>
                      <div className="wrap-select">
                        <select value={btypeValue} onChange={(e) => setBtypeValue(e.target.value)}>
                          <option value="">{btypeValue}</option>
                          {slideTypeData.map((option) => (
                            <option key={option.id} value={option.id}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">보고서 레이아웃 선택</h3>
                      <div className="wrap-select">
                        <select
                          value={layoutValue}
                          onChange={(e) => setLayoutValue(e.target.value)}
                          disabled={mtypeValue === '1' ? true : false}
                        >
                          <option value="">{layoutValue}</option>
                          {slideLayoutData.map((option) => (
                            <option key={option.id} value={option.id}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </li>
                  </ul>
                </section>
              </div>
              <div className="contents-admin-right">
                <section className="box-t1">
                  <ul className="list-form">
                    <li>
                      <h3 className="required">GPT 모델 유형</h3>
                      <div className="wrap-range gap30">
                        {gptModelTypeData.map(({ _id, type }) => (
                          <label key={_id} className="wrap-radio">
                            <input
                              type="radio"
                              name="s1"
                              value={type}
                              checked={selectedGPTModel === _id}
                              onChange={() => handleModelChange(_id)}
                            />
                            <span>{type}</span>
                          </label>
                        ))}
                      </div>
                    </li>
                    <li>
                      <h3 className="required">GPT 모델 버전</h3>
                      <div className="wrap-range gap30">
                        <label className="wrap-radio">
                          <input
                            type="radio"
                            name="s2"
                            value="3.5"
                            checked={versionValue === '3.5'}
                            onChange={(e) => setVersionValue(e.target.value)}
                          />
                          <span>3.5</span>
                        </label>
                        <label className="wrap-radio">
                          <input
                            type="radio"
                            name="s2"
                            value="4.0"
                            checked={versionValue === '4.0'}
                            onChange={(e) => setVersionValue(e.target.value)}
                          />
                          <span>4.0</span>
                        </label>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">프롬프트 내용</h3>
                      <div className="wrap-textarea">
                        <textarea
                          rows="7"
                          placeholder="본문 내용을 입력해 주세요."
                          defaultValue={bodyValue}
                          onChange={(e) => setBodyValue(e.target.value)}
                        ></textarea>
                      </div>
                    </li>
                    <li>
                      <h3>비고</h3>
                      <div className="wrap-textarea">
                        <textarea
                          rows="3"
                          placeholder="비고 내용을 입력해 주세요."
                          defaultValue={noteValue}
                          onChange={(e) => setNoteValue(e.target.value)}
                        ></textarea>
                      </div>
                    </li>
                    <li>
                      <h3>최초 등록자 / 일시</h3>
                      <div className="wrap-input">
                        <input
                          type="text"
                          value={`${registrantValue}(${emailRegistrantValue}) / ${dateRegistValue}`}
                          readOnly
                          className="readonly2"
                        />
                      </div>
                    </li>
                    <li>
                      <h3>마지막 수정자 / 일시</h3>
                      <div className="wrap-input">
                        <input
                          type="text"
                          value={`${modifierValue}(${emailModifierValue}) / ${dateModifyValue}`}
                          readOnly
                          className="readonly2"
                        />
                      </div>
                    </li>
                  </ul>
                </section>
              </div>
            </div>
            <div className="wrap-btn bc">
              <button className="btn-mid secondary" onClick={onDelete}>
                삭제
              </button>
              <div className="flex-bc gap10">
                <Link href="/admin/prompt" className="btn-mid secondary">
                  취소
                </Link>
                <button className="btn-mid primary" disabled={!isAllRequiredItems} onClick={onSave}>
                  저장
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
      {openErrorPopup && (
        <PopupConfirmAlert
          type={alert}
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
          type={confirm}
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
      {showPopupPromptEdit && <PopupPromptEdit onHidePopupPrompt={onHidePopupPrompt} module={selectedModule} />}
      {showPopupPromptDelete && <PopupPromptDelete onHidePopupPrompt={onHidePopupPrompt} module={selectedModule} />}
      {openSuccessToast && <PopupToast toastMessage={toastMessage} onHideToast={onCloseSuccessToast} />}
      {confirmPopup && (
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
      * 수정 버전
        * Wrap transformFunction and errorHandler with useCallback:
          * Ensure URLs are Constants: If PROMPT_TYPE and REPORT_TYPE are constants and not changing between renders, they won’t cause re-renders. Ensure they are defined outside of the component or in a way that keeps them stable.
          * Review Custom Hook: Review your useFetchAndTransform hook to ensure it's handling dependencies correctly. The useEffect inside should not be causing re-renders unless its dependencies (url, transformFunction, errorHandler) change.
          * By **memoizing** transformPromptType, transformReportType, and handleAxiosError with useCallback, you prevent these functions from being recreated on each render, thereby stabilizing the dependencies of your custom hook's useEffect. This should address the issue of repeated re-renders.
        * custom hook을 호출하는 컴포넌트
          * ```javascript
// prompt type, report type, slide type, slide layout을 mongoDB에서 읽기
  const transformWithDefault = useCallback(
    (item) => ({
      id: item._id,
      label: item.type,
      isChecked: false,
    }),
    []
  );

  const simpleTransform = useCallback(
    (item) => ({
      id: item._id,
      label: item.type,
    }),
    []
  );

  const fetchedPromptTypeData = useFetchAndTransform(PROMPT_TYPE, transformWithDefault, handleAxiosError);
  const fetchedReportTypeData = useFetchAndTransform(REPORT_TYPE, transformWithDefault, handleAxiosError);
  const fetchedSlideTypeData = useFetchAndTransform(SLIDE_TYPE, transformWithDefault, handleAxiosError);
  const fetchedSlideLayoutData = useFetchAndTransform(SLIDE_LAYOUT, transformWithDefault, handleAxiosError);
  const fetchedModelTypeData = useFetchAndTransform(GPT_MODEL_TYPE, simpleTransform, handleAxiosError);
  const fetchedModelVersionData = useFetchAndTransform(GPT_MODEL_VERSION, simpleTransform, handleAxiosError);```