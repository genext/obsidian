---
title: "SK C&C AI기반 보고서 자동 생성"
created: 2023-12-18 16:31:31
updated: 2025-09-08 14:54:07
---
### chatBot
#### streaming 처리
##### app/lobby
###### page.js
* ```javascript
'use client';

import Link from 'next/link';
import Image from 'next/image';
import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useRouter } from 'next/navigation';
import moment from 'moment'

import PopHistory from './pop-history';
import LobbyLeft from './lobby-left';
// import LobbyRight from './lobby-right';
import ChatIntro from './chat-intro';
import ChatResult from './chat-result';
import PopupReferences from '@/app/_components/popup-references';
import PopupConfirmAlert from '@/app/_components/popup-confirm-alert';
import PopupToast from '@/app/_components/popup-toast';
import usePopupAndLogout from '@/app/_util/error-popup-logout';
import { setFiles } from '@/redux/reducers/report';
import { createChatHistoryApi, getChatHistoryListApi, getChatHistoryApi, updateChatHistoryApi } from '../api/historyLocal'
import { chatApi, documentsChatApi } from '../api/chat';

const TABS = {
  GPT: 0,
  NAVER: 1,
  ADOT: 2,
  BARD: 3,
};

export default function Lobby() {

  const { accessToken, userInfo } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const router = useRouter();

  const [activeBTab, setActiveBTab] = useState(TABS.GPT);
  const [PopupHistoryOpen, setPopupHistoryOpen] = useState(false);
  const [isResultVisible, setIsResultVisible] = useState(false);
  const [chat, setChat] = useState('');
  const [error, setError] = useState(null);
  const [chatLog, setChatLog] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [newChat, setNewChat] = useState(true);
  // const [historyId, setHistoryId] = useState(0);
  const [referenceFiles, setReferenceFiles] = useState([]);

  const [type, setType] = useState('init')
  const [curHistoryId, setCurHistoryId] = useState(-1)
  const [messageHistory, setMessageHistory] = useState([])
  const messages = useRef([])
  const reloadedTimestamp = useRef("");

  const chatRef = useRef(null);

  const openPopupHistory = () => {
    setPopupHistoryOpen(true);
  };

  const closePopupHistory = () => {
    setPopupHistoryOpen(false);
  };

  const { setPopupMessage } = usePopupAndLogout();
  const { confirmPopup, setConfirmPopup, popupMessage, handleFetchError } = usePopupAndLogout();

  // 페이지 처음 열 때
  useEffect(() => {
    if (accessToken === null || userInfo === null) {
      router.push('/login');
    }
    const textarea = chatRef.current;
    const adjustHeight = () => {
      if (textarea.value.slice(-1) !== '\n') {
        textarea.style.height = 'auto';
        textarea.style.height = `${textarea.scrollHeight + 2}px`;
      }
    };
    textarea.addEventListener('input', adjustHeight);
    return () => {
      textarea.removeEventListener('input', adjustHeight);
    };
  }, []);

  const getHistoryList = () => {
    const res = getChatHistoryListApi("all")
    setChatHistory(res)
  }

  const createChatHistory = (msg) => {
    let apiChatType = 'simple'
    if (referenceFiles.length > 0) {
        apiChatType = 'doc'
    }
    const model = localStorage.getItem('modelVersion') === '3.5' ? 'gpt-3.5-turbo' : 'gpt-4'
    const h = createChatHistoryApi(apiChatType, model, msg)
    setCurHistoryId(h.seq)
    return h.seq
  }

  const getChatHistory = (historyId) => {
      const res = getChatHistoryApi(historyId);

      messages.current = res.reduce((acc, cur) => {
        if (cur.type === "ask") {
            acc.push({ type: "ask", userName: userInfo.username, message: cur.message, timestamp: moment(cur.create_dt).format("YYYY-MM-DD HH:mm:ss") })
        } else if (cur.type === "answer") {
            acc.push({ type: "answer", message: cur.message, thoughts: null, data_points: [], timestamp: moment(cur.create_dt).format("YYYY-MM-DD HH:mm:ss") })
        }
        return acc;
      }, [])

      setMessageHistory(messages.current);
  }

  // 이전 대화 보기 창 열었을 때 실행
  useEffect(() => {
    PopupHistoryOpen && getHistoryList()
  }, [PopupHistoryOpen]);

  useEffect(() => {
    setReferenceFiles(referenceFiles);
    dispatch(setFiles(referenceFiles));
  }, [dispatch, referenceFiles]);

  const isStreaming = useRef(false);
  const streamingShouldStop = useRef(false);
  const [stopping, setStopping] = useState(false)

  const handleStopChat = async () => {
    if (isStreaming.current === true) streamingShouldStop.current = true;
    await sleep(500)
    setStopping(true)
  }

  function handleOnKeyUpToSend(event) {
    if (event.key === 'Enter' && !event.shiftKey && chat && !processing) {
      event.preventDefault();
      handleOnClickSend();
    }
  }

  const handleOnKeyDown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
      }
  };

  const handleOnClickSend = () => {
    if (!newChat && type !== 'init' && curHistoryId !== -1) {
      processStream('gen')
      return
    }
    if (referenceFiles.length === 0) {
      setType("simple")
    } else {
      setType("doc_search")
    }
    processStream('gen');
  };

  const sleep = (t) => {
    return new Promise(resolve => setTimeout(resolve, t));
  }

  async function processStream(type) {
    const modelVersion = localStorage.getItem('modelVersion');
    setError(null);

    let timestamp = moment().utc().toISOString();
    // const basedFileName = (baseDoc === 'all') ? 'all' : baseDoc?.filename;
    const basedFileName = "all"
    messages.current = [
        ...messages.current
        , { type: "ask", userName: userInfo.username, message: chat, timestamp }
        , { type: "loading", timestamp, basedFileName }
    ];
    const loadingIdx = messages.current.length - 1;
    setMessageHistory([...messages.current]);

    let historyId = -1
    if (curHistoryId === -1) {
      historyId = createChatHistory(chat)
    } else {
      historyId = curHistoryId
      updateChatHistoryApi(historyId, "ask", chat)
    }

    setChat('');
    isStreaming.current = true;
    setProcessing(true);

    try {
      const history = messages.current.reduce((acc, cur, idx) => {
        if (cur.type === "ask") {
            acc.push({ user: cur.message, bot: undefined });
        } else if ((cur.type === "answer" || cur.type === "summary") && idx) {
            acc[acc.length - 1].bot = cur.message;
        } else if (!["ask", "answer", "summary", "loading"].includes(cur.type) && idx && !acc[acc.length - 1].bot) {
            acc.splice(-1);
        }
        return acc;
      }, []);

      let response = null;
      const referenceIds = referenceFiles.map((file) => file.seq);
      if (referenceIds.length === 0) {
        response = await chatApi({
          historyId,
          history,
          approach: "gpt3",
          model: modelVersion === '3.5' ? 'gpt-3.5-turbo' : 'gpt-4',
          overrides: {
              promptTemplate: "",
              excludeCategory: "",
              top: "3",
              semanticRanker: true,
              semanticCaptions: false,
              suggestFollowupQuestions: false,
              temperature: 0.0,
              maxTokens: 0,
          },
        })
      } else {
        response = await documentsChatApi({
          historyId,
          history,
          approach: "rrr",
          model: modelVersion === '3.5' ? 'gpt-3.5-turbo' : 'gpt-4',
          overrides: {
              promptTemplate: "",
              excludeCategory: "",
              top: "3",
              semanticRanker: true,
              semanticCaptions: false,
              suggestFollowupQuestions: false,
              temperature: 0.0,
              maxTokens: 0,
              docIds: referenceIds,
          },
        })
      }

      if (!response || !response.ok) {
        handleFetchError(response);
      }
      
      const reader = response.body?.pipeThrough(new TextDecoderStream()).getReader()
      let answer = ""
      while (true) {
        if (streamingShouldStop.current) {
          await reader.cancel()
          break
        }

        const res = await reader?.read()
        if (res == undefined) continue
        if (res?.done) break

        for (let i = 0; i < res.value.length; i++) {
          answer = answer + res.value.charAt(i)
          const a = { message: answer, data_points: [], thoughts: null }

          if (!reloadedTimestamp.current || moment(timestamp).isAfter(reloadedTimestamp.current)) {
              timestamp = moment().utc().toISOString();
              messages.current[loadingIdx] = { ...a, type: "answer", timestamp, basedFileName };
          }
          setMessageHistory([...messages.current]);
          await sleep(20)
        }
      }
      
      if (streamingShouldStop.current || answer === "") {
        // process streaming canceled
        messages.current.pop(loadingIdx)
        setMessageHistory([...messages.current])
      } else {
        updateChatHistoryApi(historyId, "answer", answer)
      }

      isStreaming.current = false
      streamingShouldStop.current = false
      setStopping(false);
      setProcessing(false);
      setNewChat(false); 
    
    } catch (error) {
      console.error('error:', error);
      if (!reloadedTimestamp.current || moment(timestamp).isAfter(reloadedTimestamp.current)) {
        const timestamp = moment().utc().toISOString();
        const errorMsg = error.message || error || "알 수 없는 오류가 발생했습니다.";
        messages.current[loadingIdx] = { type: "error", timestamp, error: errorMsg, ask: chat };
        setMessageHistory([...messages.current]);
        setProcessing(false);
        isStreaming.current = false
        streamingShouldStop.current = false
      }
      handleFetchError(error)
    }
  }

  const handleChatHistoryDelete = (deletedChat) => {
    if (deletedChat.seq === curHistoryId) {
      handleNewChat()
    }
    setChatHistory((prevChatHistory) => prevChatHistory.filter((chat) => chat.historyId !== deletedChat.seq));
  };

  const handleShowOldChat = (oldChat) => {
    setType(oldChat.chat_type)
    setNewChat(false);
    setCurHistoryId(oldChat.seq);
    getChatHistory(oldChat.seq)
    closePopupHistory()
  };

  const handleNewChat = () => {
    setType('init')
    setNewChat(true);
    setPopupHistoryOpen(false);
    setChat('');
    setMessageHistory([])
    setCurHistoryId(-1)
    messages.current = []
    setReferenceFiles([])
  };

  const [PopupRefOpen, setPopupRefOpen] = useState(false);
  
  const openPopupRef = () => {
    setPopupRefOpen(true);
  };
  const closePopupRef = () => {
    setPopupRefOpen(false);
  };

  useEffect(() => {
    if (PopupRefOpen) {
      document.body.classList.add('on-pop');
    } else {
      document.body.classList.remove('on-pop');
    }
  }, [PopupRefOpen]);

  function addFilesFromMyFiles(filesToAdd) {
    setReferenceFiles([...filesToAdd]);
    closePopupRef();
  }

  // toast popup
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const onShowToast = (message) => {
    setToastMessage(message);
    setShowToast(true);
  };
  const onHideToast = () => {
    setShowToast(false);
  };

  // 채팅 맨 아래로 이동
  const onGoChatBtm = () => {
    const element = document.querySelector('.chat-list > li:last-of-type');
    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
      });
    }
  };

  const deleteReferenceFile = (file) => {
    setReferenceFiles(referenceFiles.filter(referenceFile => referenceFile.seq !== file.seq))
  }

  return (
    <>
      <div className="container">
        <LobbyLeft onShowToast={onShowToast} />

        <main className="main">
          <div className="contents-center no-right">
            <section className="area-chat-output">
              {type === 'init' ? <ChatIntro /> : <ChatResult chatLog={messageHistory} />}
            </section>
            <section className="area-chat-input">
              <div className="wrap-textarea chat">
                <textarea
                  ref={chatRef}
                  rows="1"
                  placeholder="메시지를 입력해 채팅을 시작하세요."
                  value={chat}
                  onChange={(e) => setChat(e.target.value)}
                  onKeyUp={handleOnKeyUpToSend}
                  onKeyDown={handleOnKeyDown}
                ></textarea>
                <button className="btn-icon plus" onClick={openPopupRef} title="자료 추가" disabled={processing} ></button>
                {referenceFiles.length > 0 && (
                  <div className="attach">
                    <ul className="list-attach">
                      {referenceFiles.map((item, _id) => (
                        <li key={_id}>
                          <span>
                            {item.filename.length > 18
                              ? `${item.filename.substring(0, 18)}...${item.filename.substring(
                                  item.filename.lastIndexOf('.')
                                )}`
                              : item.filename}
                          </span>
                          <button className="btn-icon delete" title="삭제" onClick={() => deleteReferenceFile(item)}></button>
                        </li>
                      ))}
                    </ul>
                    <button className="btn-txt" onClick={openPopupRef}>
                      총 {referenceFiles.length}건
                    </button>
                  </div>
                )}
                <button
                  className="btn-send"
                  disabled={!chat || processing}
                  onClick={handleOnClickSend}
                ></button>
                {processing && (
                  <div className="wrap-btn">
                    {/* <button className="btn-rechat">다시 생성</button> */}
                    {/* <button className="btn-newchat">새로운 대화 시작하기</button> */}
                    <button className="btn-stop" onClick={() => handleStopChat()}>
                      <span>{stopping ? "답변 중지 중" : "답변 중지"}</span>
                    </button>
                  </div>
                )}
                {type !== 'init' && (
                  <button className="btn-btm" onClick={onGoChatBtm} title="채팅 맨 아래로 이동"></button>
                )}
              </div>
              <div className="area-chat-btm">
                <div className="wrap-tab-chat" style={{visibility: "hidden"}}>
                  <ul className="tab">
                    <li>
                      <button className={activeBTab === TABS.GPT ? 'on' : ''} onClick={() => onBTabClick(TABS.GPT)}>
                        GPT
                      </button>
                    </li>
                    <li>
                      <button
                        className={activeBTab === TABS.NAVER ? 'on' : ''}
                        onClick={() => onShowToast('준비중입니다.')}
                      >
                        네이버 하이퍼클로바X
                      </button>
                    </li>
                    <li>
                      <button
                        className={activeBTab === TABS.ADOT ? 'on' : ''}
                        onClick={() => onShowToast('준비중입니다.')}
                      >
                        에이닷
                      </button>
                    </li>
                    <li>
                      <button
                        className={activeBTab === TABS.BARD ? 'on' : ''}
                        onClick={() => onShowToast('준비중입니다.')}
                      >
                        BARD
                      </button>
                    </li>
                  </ul>
                </div>
                <div className="pos-r">
                  <button className="btn-small history" onClick={openPopupHistory}>
                    이전 대화 보기
                  </button>
                </div>
              </div>
            </section>
          </div>
        </main>
        {/* <LobbyRight onShowToast={onShowToast} /> */}

        {PopupHistoryOpen && (
          <PopHistory
            onClose={closePopupHistory}
            onDeleteOneChat={handleChatHistoryDelete}
            onShowOldChat={handleShowOldChat}
            onNewChat={handleNewChat}
          />
        )}
        {PopupRefOpen && <PopupReferences onClose={closePopupRef} addFiles={addFilesFromMyFiles} />}
        {showToast && <PopupToast toastMessage={toastMessage} onHideToast={onHideToast} />}
      </div>
      {confirmPopup && (
        <PopupConfirmAlert
          type={'alert'}
          message={popupMessage}
          onConfirm={() => {
            setConfirmPopup(false);
          }}
        />
      )}
    </>
  );
}

```
##### app/report/editor.js
* ```javascript
'use client';

import Link from 'next/link';
import Image from 'next/image';
import React, { useState, useRef, useEffect } from 'react';
import { useSelector } from 'react-redux';
import ChatResult from './chat/chat-result';
import { AI_CHAT_CHAIN } from '@/config/apiPaths';
import PopupConfirmAlert from '@/app/_components/popup-confirm-alert';
import usePopupAndLogout from '@/app/_util/error-popup-logout';

export default function EditorChat({ onPrompt, onShowToast }) {
  const [username, setUsername] = useState('사용자');
  const [chatResult, setChatResult] = useState(false);
  const [chatFocus, setChatFocus] = useState(false);

  // chat-input
  const [chatValue, setchatValue] = useState('');
  const chatRef = useRef(null);

  const { modelType, modelVersion } = useSelector((state) => state.gptModel);
  const [error, setError] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [newChat, setNewChat] = useState(true);
  const [chatLog, setChatLog] = useState([]);
  const streamingShouldStop = useRef(false);
  const isStreaming = useRef(false);
  const { accessToken, userInfo } = useSelector((state) => state.auth);
  const { confirmPopup, setConfirmPopup, popupMessage, handleFetchError } = usePopupAndLogout();

  let debounceTimer;

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (chatFocus && !e.target.closest('.focus')) {
        setChatFocus(false);
      }
    };

    document.addEventListener('click', handleClickOutside);

    return () => document.removeEventListener('click', handleClickOutside);
  }, [chatFocus]);

  const onChatSend = () => {
    setChatResult(true);
  };
  const onChatChange = (e) => {
    setchatValue(e.target.value);
  };

  const onChatKeyDown = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      clearTimeout(debounceTimer);

      debounceTimer = setTimeout(() => {
        onPrompt(chatValue, []);
        e.preventDefault();
        setChatLog((prevChatLog) => {
          return [...prevChatLog, { role: 'user', content: chatValue }];
        });

        onChatSend();
        setchatValue('');
      }, 500);
    }
    // if (e.keyCode === 13 && !e.shiftKey) {
    else if (e.key === 'Enter' && chatValue && !processing) {
      // Enter key (not shift)
      e.preventDefault();
      if (chatValue.trim() !== '') {
        processStream('gen');
        onChatSend();
      }
    }
  };

  const onChatFocusin = () => {
    setChatFocus(true);
  };

  useEffect(() => {
    setUsername(userInfo.username);

    const textarea = chatRef.current;
    const adjustHeight = () => {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight + 2}px`;
    };
    textarea.addEventListener('input', adjustHeight);
    return () => {
      textarea.removeEventListener('input', adjustHeight);
    };
  }, []);

  //////////////////////////////////////////////////////////////////////////////

  function handleStopChat() {
    if (isStreaming.current === true) streamingShouldStop.current = true;
  }

  async function processStream(type) {
    setProcessing(true);
    setError(null);

    try {
      let history = [];

      // GPT에게 질의할 때 같이 보낼 history를 만들기 위해 화면 표시용 chatLog를 변환
      for (let i = 0; i < chatLog.length; i += 2) {
        let pair = {};
        pair[chatLog[i].role] = chatLog[i].content;
        pair[chatLog[i + 1].role] = chatLog[i + 1].content[0];
        history.push(pair);
      }

      if (type === 're-gen') {
        history[history.length - 1] = { user: history[history.length - 1].user };
      } else {
        if (Object.keys(history).length === 0) {
          history = [{ user: chatValue }];
        } else {
          history = [...history, { user: chatValue }];
        }
      }

      const response = await fetch(AI_CHAT_CHAIN, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: accessToken,
        },
        body: JSON.stringify({
          prompt: type === 're-gen' ? history[history.length - 1].user : chatValue,
          model: modelVersion === '3.5' ? 'gpt-3.5-turbo' : 'gpt-4-0613',
          init: newChat ? 1 : 0,
          service_type: 0,
          regen: type === 're-gen' ? 1 : 0,
          // TODO Add OverrideOptions?
        }),
      });

      if (!response.ok) {
        handleFetchError(response);
      }
      // Existing code to handle text/html and text/event-stream content-type
      const reader = response.body.getReader();
      setchatValue('');
      let buffer = '';
      isStreaming.current = true;
      setNewChat(false);
      let newUserContent = { role: 'user', content: history[history.length - 1].user };
      let newBotContent = { role: 'bot', content: '' };

      // Update the state with the new entries
      if (type === 're-gen') {
        console.log('------------------------ re-gen');
        setChatLog((prevChatLog) => {
          let newChatLog = [...prevChatLog];
          console.log('re-gen newChatLog: ', newChatLog);
          console.log('re-gen newChatLog.content: ', newChatLog[newChatLog.length - 1].content);
          newChatLog[newChatLog.length - 1].content.push(newBotContent.content);
          return newChatLog;
        });
      } else {
        setChatLog((prevChatLog) => {
          console.log('gen pervChat: ', prevChatLog);
          console.log('gen pervChat length: ', prevChatLog.length);
          if (prevChatLog.length > 0) {
            console.log('prevChatLog[prevChatLog.length - 1].role: ', prevChatLog[prevChatLog.length - 1].role);
            console.log('prevChatLog[prevChatLog.length - 1].content: ', prevChatLog[prevChatLog.length - 1].content);
          }
          return [...prevChatLog, newUserContent, newBotContent];
        });
      }

      const handleData = async ({ done, value }) => {
        // setIsResultVisible(true);

        if (done) {
          isStreaming.current = false;
          setChatLog((prevChatLog) => {
            const updatedTraceChatLog = [...prevChatLog];
            updatedTraceChatLog[updatedTraceChatLog.length - 1].content = buffer;
            console.log('updatedTraceChatLog: ', updatedTraceChatLog);
            return updatedTraceChatLog;
          });

          setProcessing(false);
          // saveChatHistory(userInfo.userid, activeBTab, savedHistoryId, [newUserContent, newBotContent]);
          return;
        }

        if (streamingShouldStop.current) {
          reader
            .cancel()
            .then(() => {
              streamingShouldStop.current = false;
            })
            .catch((error) => {
              console.error('streaming cancel error: ', error);
            });
        }
        const chunk = new TextDecoder().decode(value);
        buffer += chunk;
        setChatLog((prevChatLog) => {
          const updatedTraceChatLog = [...prevChatLog];
          updatedTraceChatLog[updatedTraceChatLog.length - 1].content = buffer;
          return updatedTraceChatLog;
        });
        reader
          .read()
          .then(handleData)
          .catch((res) => {
            handleFetchError(res);
          });
      };

      reader.read().then(handleData);
    } catch (error) {
      console.error('error:', error);
      setError(`Fetch failed: ${error.message}`);
      setProcessing(false);
      return `stream processing error: ${error}`;
    }
  }

  ///////////////////////////////////////////////
  return (
    <>
      <aside className={chatFocus ? 'side editor-bottom focus' : 'side editor-bottom'}>
        {chatFocus && (
          <div className="manager-top">
            <div className="inner">
              <div className="manager-message">
                <i className="badge">tok</i>
                <p>
                  반가워요 {username}님.
                  <br />
                  tok.AI 매니저는 슬라이드 만드는걸 도와드릴 수 있어요. 슬라이드에 어떤 내용을 넣으면 좋을지, 어떤
                  디자인으로 변경할지 알려주세요!
                </p>
              </div>
              <div className="manager-btns">
                <ul>
                  <li>
                    <button onClick={() => onShowToast('준비중입니다.')}>사례 추가</button>
                  </li>
                  <li>
                    <button onClick={() => onShowToast('준비중입니다.')}>내용 바꾸기</button>
                  </li>
                  <li>
                    <button onClick={() => onShowToast('준비중입니다.')}>슬라이드 레이아웃 변경</button>
                  </li>
                  <li>
                    <button onClick={() => onShowToast('준비중입니다.')}>자료 변경</button>
                  </li>
                  <li>
                    <button onClick={() => onShowToast('준비중입니다.')}>이미지 추가</button>
                  </li>
                </ul>
              </div>
              <section className="area-chat-output">
                <div className="area-chat-result">
                  <ul className="chat-list">
                    <li>
                      <dl>
                        <dt className="chat-q">
                          <i className="badge"></i>
                          <div className="contents">
                            <p>tok.AI는 무슨 일을 할 수 있어?</p>
                          </div>
                        </dt>
                      </dl>
                    </li>
                    <li>
                      <dl>
                        <dt className="chat-a">
                          <i className="badge"> tok</i>
                          <div className="contents">
                            <p>
                              tok.AI는 다양한 대화형 인공지능 모델을 활용합니다. 사용자가 입력한 대규모 텍스트 데이터를
                              학습하며 상호 작용하여 요청한 정보를 처리하기 위해 최선을 다합니다. tok.AI는 다양한 주제와
                              문맥에서 대화를 지속하고 유창한 답변과 유의미한 결과를 생성하기 위해 꾸준히 노력하고
                              있습니다.
                            </p>
                          </div>
                        </dt>
                      </dl>
                    </li>
                    {chatResult && (
                      <ChatResult
                        chatLog={chatLog}
                        isStreaming={isStreaming}
                        streamingShouldStop={streamingShouldStop}
                      />
                    )}
                  </ul>
                  <div className="chat-btn">
                    {/* <button className="btn-rechat">되돌리기</button> */}
                    <button className="btn-stop" onClick={handleStopChat}>
                      중단하기
                    </button>
                  </div>
                </div>
              </section>
            </div>
          </div>
        )}
        <div className="wrap-textarea chat">
          <textarea
            ref={chatRef}
            rows="1"
            placeholder="tok.AI에게 무엇이든 물어보세요."
            value={chatValue}
            onChange={onChatChange}
            onKeyDown={onChatKeyDown}
            onFocus={onChatFocusin}
          ></textarea>
          <button className="btn-send" disabled={chatValue ? false : true} onClick={onChatSend}></button>
        </div>
      </aside>
      {confirmPopup && (
        <PopupConfirmAlert
          type={'alert'}
          message={popupMessage}
          onConfirm={() => {
            setConfirmPopup(false);
          }}
        />
      )}
    </>
  );
}

```
##### lib
###### llm.js
* ```javascript
import { getEncoding } from 'js-tiktoken';
import { AI_COMPLETION } from '@/config/apiPaths';

export function getTokenLength(text) {
  return getEncoding('cl100k_base').encode(text).length;
}

export async function processStream(prompt, isStreaming, shouldStop, onProcess, onDone, accessToken) {
  return fetch(`${process.env.COMMON_BACKEND_URL}/api/chat_simple`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `${accessToken}`,
    },
    body: JSON.stringify({
      approach: 'gpt4',
      history: [
        {
          user: prompt,
        },
      ],
      history_id: 9,
      model: 'gpt-4',
    }),
  })
    .then((response) => {
      const reader = response.body.getReader();
      let buffer = '';
      isStreaming.current = true;
      const handleData = async ({ done, value }) => {
        if (done) {
          isStreaming.current = false;
          console.log('streaming done');
          onDone();
          return;
        }

        const chunk = new TextDecoder().decode(value);
        buffer += chunk;
        onProcess(buffer);
        console.log(buffer);

        reader.read().then(handleData);

        if (shouldStop.current === true) {
          reader
            .cancel()
            .then(() => {
              console.log('streaming canceled');
              shouldStop.current = false;
            })
            .catch((e) => {
              console.log('streaming cancel error: ', e);
            });
        }
      };

      reader.read().then(handleData);
    })
    .catch((e) => {
      console.log('error: ', e);
      return `stream processing error: ${e}`;
    });
}

let abortController = null;
let processStreamPublicReader = null;
export async function processStreamPublic(
  prompt,
  isStreaming,
  shouldStop,
  onProcess,
  onDone,
  onError,
  { references, query }
) {
  const modelType = localStorage.getItem('modelType');
  const modelVersion = localStorage.getItem('modelVersion');
  const accessToken = localStorage.getItem('accessToken');

  try {
    function finish() {
      isStreaming.current = false;
      processStreamPublicReader = null;
      shouldStop.current = false;
    }

    function init() {
      if (abortController && (isStreaming.current || shouldStop.current)) {
        abortController.abort();
      }
      abortController = new AbortController();
      isStreaming.current = true;
    }

    init();

    return await fetch(AI_COMPLETION, {
      method: 'POST',
      signal: abortController.signal,
      headers: {
        'Content-Type': 'application/json',
        Authorization: accessToken,
      },
      body: JSON.stringify({
        prompt: prompt,
        llm: {
          modelType: modelType,
          modelVersion: modelVersion,
        },
        query,
        references,
        options: {
          top: process.env.COMPLETION_TOP_K,
          searchType: 'similarity',
          temperature: process.env.COMPLETION_TEMPERATURE,
        },
      }),
    }).then(async (response) => {
      // Before we call getReader, we must check the result first.
      // if we call getReader first, we can't get the error message Server sent.
      if (!response.ok) {
        try {
          const responseBody = await response.text();
          const parsedBody = JSON.parse(responseBody);
          const result = { status: response.status, statusText: parsedBody.detail };
          onError && onError(result);
        } catch (e) {
          console.log('error response parsing error: ', e);
          const result = { status: 0, statusText: e.name + ': ' + e.message };
          onError && onError(result);
        }
        finish();
        return;
      }

      processStreamPublicReader = response.body.getReader();
      let buffer = '';

      const handleData = async ({ done, value }) => {
        if (abortController && shouldStop.current === true) {
          processStreamPublicReader?.cancel();
          isStreaming.current = false;
          shouldStop.current = false;
        }

        const chunk = new TextDecoder().decode(value);
        buffer += chunk;

        if (done) {
          finish();
          console.log('streaming done', done);
          onDone(buffer);
          return;
        } else if (buffer.includes('!!ERROR!!')) {
          const message = '토큰 허용량을 초과하였습니다.';
          const status = 500;

          onError && onError({ statusText: message });
          finish && finish();
          throw { status, message };
        } else {
          onProcess(buffer);
        }
        processStreamPublicReader.read().then(handleData);
      };

      processStreamPublicReader.read().then(handleData);

      abortController?.signal?.addEventListener('abort', () => {
        processStreamPublicReader?.cancel();
        finish && finish();
      });
    });
  } catch (e) {
    finish && finish();
    const { name, status, message } = e;
    if (name === 'AbortError') {
      console.log('Abort Controller의 취소');
      return false;
    }

    console.log('error: ', e);
    onError && onError(e);
    throw { status, message };
  }
}

```
### 프롬프트 관리 - 내가 처음으로 full stack engineer로서 개발한 것.
#### 환경
##### .env
* ```javascript
PINECONE_ENVIRONMENT=asia-southeast1-gcp-free
PINECONE_API_KEY=...
PINECONE_INDEX=prototype
MONGODB_URI=mongodb+srv://gai:gai1234@zoona.zcdwncl.mongodb.net/test
# COMMON_BACKEND_URL=http://127.0.0.1:8000
COMMON_BACKEND_URL=http://20.127.36.48:8001
# COMMON_BACKEND_URL=http://10.250.124.188:8000
LLM_BACKEND_URL=http://20.127.36.48:8002
COMPLETION_TEMPERATURE=0.2
COMPLETION_TOP_K=5
ENCRYPTION_KEY=f5fdf4ad6ee79159b4c41762e72521e19e55478f3caf8b2807129bca1d3ecb3b
IV=e56cc137af91b4b4a589f66225efc073
```
##### package.json
* ```javascript
{
  "name": "tok.ai",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "swagger": "node swaggerServer.js",
    "dev:all": "concurrently \"npm run dev\" \"npm run swagger\""
  },
  "dependencies": {
    "@heroicons/react": "^2.0.18",
    "@jsdevtools/rehype-toc": "^3.0.2",
    "@pinecone-database/pinecone": "^0.1.6",
    "@reduxjs/toolkit": "^1.9.5",
    "axios": "^1.4.0",
    "chart.js": "^4.3.3",
    "child_process": "^1.0.2",
    "classnames": "^2.3.2",
    "dotenv": "^16.3.1",
    "dropzone": "^6.0.0-beta.2",
    "eslint": "^8.42.0",
    "eslint-config-next": "13.4.6",
    "eslint-config-prettier": "^8.8.0",
    "flowbite": "^1.6.6",
    "flowbite-react": "^0.4.9",
    "form-data": "^4.0.0",
    "formidable": "^3.4.0",
    "js-tiktoken": "^1.0.7",
    "konva": "^9.2.0",
    "langchain": "^0.0.98",
    "lottie-react": "^2.4.0",
    "mdast-util-toc": "^7.0.0",
    "mongoose": "^7.3.1",
    "morgan": "^1.10.0",
    "multer": "1.4.4",
    "next": "13.4.6",
    "next-connect": "^1.0.0",
    "openai": "^3.3.0",
    "pdf-parse": "^1.1.1",
    "pixi.js": "^7.2.4",
    "pptxgenjs": "^3.12.0",
    "react": "18.2.0",
    "react-chartjs-2": "^5.2.0",
    "react-date-range": "^1.4.0",
    "react-dom": "18.2.0",
    "react-dropzone": "^14.2.3",
    "react-konva": "^18.2.10",
    "react-markdown": "^9.0.0",
    "react-modal": "^3.16.1",
    "react-quill": "^2.0.0",
    "react-slick": "^0.29.0",
    "react-syntax-highlighter": "^15.5.0",
    "recharts": "^2.7.3",
    "rehype-autolink-headings": "^7.0.0",
    "rehype-parse": "^9.0.0",
    "rehype-react": "^8.0.0",
    "rehype-slug": "^6.0.0",
    "rehype-stringify": "^10.0.0",
    "remark-gfm": "^4.0.0",
    "remark-rehype": "^11.0.0",
    "remark-toc": "^9.0.0",
    "sass": "^1.65.1",
    "slick-carousel": "^1.8.1",
    "swagger-jsdoc": "^6.2.8",
    "swagger-ui-express": "^5.0.0",
    "tiktoken": "^1.0.10",
    "turndown": "^7.1.2",
    "typechat": "^0.0.10",
    "unified": "^11.0.3",
    "utf8-encoding": "^0.1.2",
    "winston": "^3.10.0",
    "winston-daily-rotate-file": "^4.7.1"
  },
  "devDependencies": {
    "@types/node": "^20.4.5",
    "@types/react": "^18.2.17",
    "autoprefixer": "^10.4.14",
    "concurrently": "^8.2.2",
    "mongodb": "^5.6.0",
    "postcss": "^8.4.24",
    "prettier": "2.8.8",
    "react-redux": "^8.1.1",
    "tailwindcss": "^3.3.2",
    "typescript": "^5.1.6"
  }
}

```
##### next.config.js
* ```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        // matching all API routes
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' }, // replace this your actual origin
          { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT' },
          {
            key: 'Access-Control-Allow-Headers',
            value:
              'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version',
          },
        ],
      },
    ];
  },
  reactStrictMode: false,
  env: {
    COMMON_BACKEND_URL: process.env.COMMON_BACKEND_URL,
    COMPLETION_TOP_K: process.env.COMPLETION_TOP_K,
    COMPLETION_TEMPERATURE: process.env.COMPLETION_TEMPERATURE,
  },
  sassOptions: {
    includePaths: [require('path').join(__dirname, 'styles')],
    // prependData: `@import "@/app/styles/variables"; @import "@/app/styles/mixins";`,
  },
  images: {
    // @TODO: MD 이미지 테스트용 임시 설정, 삭제 예정
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.pexels.com',
        port: '',
        pathname: '/photos/**',
      },
    ],
  },
};

console.log('env:' + process.env.NODE_ENV);
if (process.env.NODE_ENV === 'production') {
  nextConfig.compiler = {
    removeConsole: {
      exclude: ['error', 'warn'],
    },
  };
}

module.exports = nextConfig;

```
##### jsonconfig.json
* ```javascript
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}

```
##### docker
###### dockerfile-dev
* ```plain text
FROM node:alpine as builder

WORKDIR /app

COPY package*.json /app
RUN npm install

COPY .next /app/.next
COPY node_modules /app/node_modules
COPY public /app/public
COPY scripts /app/scripts
COPY ecosystem.config.js /app
COPY .env /app

FROM node:alpine

LABEL authors="tok.AI"

WORKDIR /app

COPY --from=builder /app/.next /app/.next
COPY --from=builder /app/node_modules /app/node_modules
COPY --from=builder /app/public /app/public
COPY --from=builder /app/scripts /app/scripts
COPY --from=builder /app/ecosystem.config.js /app/ecosystem.config.js
COPY --from=builder /app/.env /app/.env
COPY --from=builder /app/package*.json /app/
RUN mkdir -p /app/exported-report
RUN apk add --update python3 py3-pip && rm -rf /var/cache/apk/*vate
RUN pip install -r /app/scripts/python/requirements.txt --break-system-packages
RUN npm install -g pm2

EXPOSE 3000

CMD ["pm2-runtime", "start", "ecosystem.config.js"]

```
###### docker-compose-dev.yml
* ```javascript
services:
  tokai-report-dev:
    image: $DEPLOY_IMAGE
    volumes:
      - /aireportdisk/tokai/$CI_COMMIT_REF_NAME/tokai-report-generator/logs:/logs
    ports:
      - "3001:3000"
```
##### config file(/config)
###### apiPaths.js
* ```javascript
import { BASE_URL, API_V1 } from './constants';

// common(python) backend
export const COMMON_APPS = `${BASE_URL}${API_V1}/common/apps`;
export const COMMON_FAVORITES = `${BASE_URL}${API_V1}/common/favorite`;
export const AI_DOCS = `${BASE_URL}${API_V1}/ai/docs`;
export const AI_DOC = `${BASE_URL}${API_V1}/ai/doc`;
export const AI_CHAT_HISTORY = `${BASE_URL}${API_V1}/ai/chat_history`;
export const AI_CHAT_CHAIN = `${BASE_URL}${API_V1}/ai/chat_chain`;

export const AI_CHAT_STREAMING_QA = `${BASE_URL}${API_V1}/ai/chat/streaming-qa`;
export const AI_COMPLETION = `${BASE_URL}${API_V1}/ai/completion`;
export const AUTH_LOGIN = `${BASE_URL}${API_V1}/auth/login`;
export const AUTH_VALIDATION = `${BASE_URL}${API_V1}/auth/validation`;
export const DOC_DART_COMPANIES = `${BASE_URL}${API_V1}/document/dart/companies`;
export const USER_EMAIL_DUP = `${BASE_URL}${API_V1}/user/email-duplication`;
export const USER_REGISTRATION = `${BASE_URL}${API_V1}/user/registration`;
export const COMPANY_LOGO_IMG = `${BASE_URL}${API_V1}/common/logo-img-url`;
export const PASSWORD_INIT = `${BASE_URL}${API_V1}/user/send_temp_password`;
export const CHANGE_TEMP_PASSWORD = `${BASE_URL}${API_V1}/user/temp-password-change`;

// service(node.js) backend
export const PROMPT_TEMPLATE = `${API_V1}/report/prompt-template`;
export const DART_API = `${API_V1}/report/dart`;
export const CORP_API = `${API_V1}/report/corp-analysis`;
export const NOTICE_RECENT = `${API_V1}/report/announcement/latest`;
export const NOTICE_LIST = `${API_V1}/report/announcement`;
export const REPORT = `${API_V1}/report/report`;
export const PROMPT_TYPE = `${API_V1}/report/prompt-management/prompt-type`;
export const MEGA_TYPE = `${API_V1}/report/prompt-management/mega-type`;
export const REPORT_TYPE = `${API_V1}/report/prompt-management/report-type`;
export const SLIDE_TYPE = `${API_V1}/report/prompt-management/slide-type`;
export const SLIDE_LAYOUT = `${API_V1}/report/prompt-management/slide-layout`;
export const GPT_MODEL_TYPE = `${API_V1}/report/prompt-management/gpt-model-type`;
export const GPT_MODEL_VERSION = `${API_V1}/report/prompt-management/gpt-model-version`;
export const PROMPT_MODULE = `${API_V1}/report/prompt-management/prompt-module`;
export const MEGA_PROMPT_MODULE = `${API_V1}/report/prompt-management/mega-prompt`;

```
###### constants.js
* ```javascript
export const BASE_URL = process.env.COMMON_BACKEND_URL;
export const API_V1 = '/api/v1';
// 영어 대소문자, 숫자, 특수문자 허용
export const allowedCharsRegex = /^[A-Za-z0-9!\"#$%&'()*+,\-./:;<=>?@\[₩\]^_`{|}~]+$/;
// 한글, 영어 대소문자, 숫자, 특수문자 허용
export const allowed2BytesCharsRegex = /^[A-Za-z0-9!\"#$%&'()*+,\-./:;<=>?@\[₩\]^_`{|}~\uAC00-\uD7AF ]+$/;

```
#### 라이브러리
##### mongoDB
###### db.js
* ```javascript
import mongoose from 'mongoose';
import * as logger from 'winston';

const uri = process.env.MONGODB_URI;

export async function connectToDatabase() {
  if (mongoose.connection.readyState !== 1) {
    try {
      await mongoose.connect(uri, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
      });
      logger.info('Successfully connected to the Mongo database.');
    } catch (error) {
      logger.error(`DB Connection Error: ${err.message}`);
      throw err;
    }
  }
}

```
#### DB model
##### 독립적인 모델들
###### mega-type.js
* ```javascript
import mongoose from 'mongoose';
const { Schema } = mongoose;

// GPT 모델 유형
const megaTypeSchema = new Schema({
  type: { type: String, required: true, unique: true },
  description: { type: String, required: true },
});

const MegaType = mongoose.models.MegaType || mongoose.model('MegaType', megaTypeSchema);
export default MegaType;

```
###### prompt-type.js
* ```javascript
import mongoose from 'mongoose';
const { Schema } = mongoose;

// 프롬프트 유형
const promptTypeSchema = new Schema({
  type: { type: String, required: true, unique: true },
  description: { type: String, required: true },
});

const PromptType = mongoose.models.PromptType || mongoose.model('PromptType', promptTypeSchema);
export default PromptType;

```
###### gpt-model-type.js
* ```javascript
import mongoose from 'mongoose';
const { Schema } = mongoose;

// GPT 모델 유형
const gptModelTypeSchema = new Schema({
  type: { type: String, required: true, unique: true },
  description: { type: String, required: true },
});

const GPTModelType = mongoose.models.GPTModelType || mongoose.model('GPTModelType', gptModelTypeSchema);
export default GPTModelType;

```
##### 연결된 모델들
###### 기본 구성 요소 모델
###### report-type.js
* ```javascript
import mongoose from 'mongoose';
const { Schema } = mongoose;

// 보고서 유형
const reportTypeSchema = new Schema({
  type: { type: String, required: true, unique: true },
  description: { type: String, required: true },
  slideTypes: [
    {
      type: Schema.Types.ObjectId,
      ref: 'SlideType',
    },
  ],
});

const ReportType = mongoose.models.ReportType || mongoose.model('ReportType', reportTypeSchema);
export default ReportType;

```
###### slide-type.js
* ```javascript
import mongoose from 'mongoose';
const { Schema } = mongoose;

// 컨텐츠 유형
const slideTypeSchema = new Schema({
  type: { type: String, required: true },
  description: { type: String, required: true },
  reportTypes: [
    {
      type: Schema.Types.ObjectId,
      ref: 'ReportType',
      required: true,
    },
  ],
  slideLayouts: [
    {
      type: Schema.Types.ObjectId,
      ref: 'SlideLayout',
    },
  ],
});

const SlideType = mongoose.models.SlideType || mongoose.model('SlideType', slideTypeSchema);
export default SlideType;

```
###### slide-layout.js
* ```javascript
import mongoose from 'mongoose';
const { Schema } = mongoose;

// 컨텐츠 형태
const slideLayoutSchema = new Schema({
  type: { type: String, required: true },
  description: { type: String, required: true },
  slideType: {
    type: Schema.Types.ObjectId,
    ref: 'SlideType',
    required: true,
  },
});

const SlideLayout = mongoose.models.SlideLayout || mongoose.model('SlideLayout', slideLayoutSchema);
export default SlideLayout;

```
###### 상위 모델
###### mega-prompt.js
* ```javascript
import mongoose from 'mongoose';
const { Schema } = mongoose;
import PromptModule from './prompt-module';
import MegaType from '@/models/prompt-management/mega-type';
import reportType from '@/models/prompt-management/report-type';
import slideType from '@/models/prompt-management/slide-type';

const megaPromptSchema = new Schema(
  {
    code: { type: String, required: true, unique: true },
    name: { type: String, required: true },
    megaType: { type: Schema.Types.ObjectId, ref: 'MegaType', required: true },
    gptModelType: { type: Schema.Types.ObjectId, ref: 'GPTModelType', required: true },
    gptModelVersion: { type: Schema.Types.ObjectId, ref: 'GPTModelVersion', required: true },
    promptContent: {
      type: [
        {
          _id: { type: Schema.Types.ObjectId, ref: 'PromptModule', required: true },
          code: { type: String, required: true },
        },
      ],
      /*
    validate: {
      validator: async function (modules) {
        for (let module of modules) {
          const item = await PromptModule.findById(module._id);
          console.log('-------------------------------------');
          console.log('item', item);
          console.log('this', this);
          if (
            !item ||
            item.gptModelType !== this.gptModelType ||
            item.gptModelVersion !== this.gptModelVersion
          ) {
            console.log('item.gptModelType: ', item.gptModelType);
            console.log('item.gptModelVersion: ', item.gptModelVersion);
            console.log('this.gptModelType: ', this.gptModelType);
            console.log('this.gptModelVersion: ', this.gptModelVersion);
            return false;
          }
        }
        return true;
      },
      message: "Modules in promptContent must match MegaPrompt's gptModelType and gptModelVersion",
    },
    */
    },
    description: String,
    reportType: {
      type: Schema.Types.ObjectId,
      ref: 'ReportType',
      /*
      required: async function () {
        try {
          if (!this.populated('megaType')) await this.populate('megaType');
          if (this.megaType.type === '보고서') {
            console.log('repoprt type result: ', this.megaType.type === '보고서');
            return true;
          } else {
            console.log('repoprt type result: ', this.megaType.type === '보고서');
            return false;
          }
        } catch (error) {
          console.error('Error in populating megaType:', error);
          return false;
        }
      },
      required: function () {
        if (this.megaType) {
          console.log('mega type in reportType: ', this.megaType.type);
          if (this.megaType.type === '보고서') {
            console.log('report type result: ', this.megaType.type === '보고서');
            return true;
          } else {
            console.log('repoprt type result: ', this.megaType.type === '보고서');
            return false;
          }
        } else {
          console.log('no mega type in reportType');
        }
      },
      */
    },
    slideType: {
      type: Schema.Types.ObjectId,
      ref: 'SlideType',
      /*
      required: async function () {
        try {
          if (!this.populated('megaType')) await this.populate('megaType');
          if (this.megaType.type === '보고서') {
            console.log('slide type result: ', this.megaType.type === '보고서');
            return true;
          } else {
            console.log('repoprt type result: ', this.megaType.type === '보고서');
            return false;
          }
        } catch (error) {
          console.error('Error in populating megaType:', error);
          return false;
        }
      },
      required: function () {
        if (this.megaType) {
          console.log('mega type in slideType: ', this.megaType.type);
          if (this.megaType.type === '보고서') {
            console.log('slide type result: ', this.megaType.type === '보고서');
            return true;
          } else {
            console.log('slide type result: ', this.megaType.type === '보고서');
            return false;
          }
        } else {
          console.log('no mega type in slideType');
        }
      },
      */
    },
    slideLayout: {
      type: Schema.Types.ObjectId,
      ref: 'SlideLayout',
      required: false,
    },
    creator: String,
    modifier: String,
  },
  { timestamps: true }
);

const MegaPrompt = mongoose.models.MegaPrompt || mongoose.model('MegaPrompt', megaPromptSchema);
export default MegaPrompt;

```
###### prompt-module.js
* ```javascript
import { Int32 } from 'mongodb';
import mongoose from 'mongoose';
const { Schema } = mongoose;

const promptModulechema = new Schema(
  {
    code: { type: String, required: true, unique: true },
    name: { type: String, required: true },
    promptType: { type: Schema.Types.ObjectId, ref: 'PromptType', required: true },
    gptModelType: { type: Schema.Types.ObjectId, ref: 'GPTModelType', required: true },
    gptModelVersion: { type: Schema.Types.ObjectId, ref: 'GPTModelVersion', required: true },
    prompt: { type: String, required: true },
    applied_count: { type: Number, required: true },
    description: String,
    creator: String,
    modifier: String,
    // Reference to a report document
    reportType: { type: Schema.Types.ObjectId, ref: 'ReportType' },
    slideType: { type: Schema.Types.ObjectId, ref: 'SlideType' },
    slideLayout: { type: Schema.Types.ObjectId, ref: 'SlideLayout' },
  },
  { timestamps: true }
);

const PromptModule = mongoose.models.PromptModule || mongoose.model('PromptModule', promptModulechema);
export default PromptModule;

```
#### server-side(/pages/api/vi/report/prompt-management)
##### 기본 구성요소 CRUD API(index.js)
###### gpt-model-type
* ```javascript
import { connectToDatabase } from '@/lib/db';
import GPTModelType from '@/models/prompt-management/gpt-model-type';
import logger from '@/lib/winston';

/**
 * @swagger
 * /api/v1/report/gpt-model-type:
 *   get:
 *     tags:
 *       - GPT 모델 유형
 *     summary: GPT 모델 유형 조회
 *     description: GPT 모델 유형 정보를 조회합니다. 특정 ID로 조회 가능.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: false
 *         description: GPT 모델 유형의 MongoDB ObjectId
 *     responses:
 *       200:
 *         description: A successful response with one or more GPT model types
 *       404:
 *         description: GPTModelType not found
 *
 *   post:
 *     tags:
 *       - GPT 모델 유형
 *     summary: 새 GPT 모델 유형 추가
 *     description: 새 GPT 모델 유형을 추가합니다.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/GPTModelType'
 *     responses:
 *       201:
 *         description: The newly created GPT model type
 *
 *   put:
 *     tags:
 *       - GPT 모델 유형
 *     summary: GPT 모델 유형 데이터 수정
 *     description: 기존 GPT 모델 유형 데이터를 수정합니다.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/GPTModelType'
 *     responses:
 *       200:
 *         description: The updated GPT model type
 *       404:
 *         description: GPTModelType not found
 *
 *   delete:
 *     tags:
 *       - GPT 모델 유형
 *     summary: GPT 모델 유형 삭제
 *     description: 특정 GPT 모델 유형을 삭제합니다.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: GPT 모델 유형의 MongoDB ObjectId
 *     responses:
 *       204:
 *         description: GPT Model Type deleted
 *       400:
 *         description: ID is required
 *       404:
 *         description: GPTModelType not found
 *
 * components:
 *   schemas:
 *     GPTModelType:
 *       type: object
 *       properties:
 *         type:
 *           type: string
 *           required: true
 *           description: "GPT 모델 유형의 이름"
 *         description:
 *           type: string
 *           required: true
 *           description: "GPT 모델 유형에 대한 설명"
 */

export default async function handler(req, res) {
  try {
    await connectToDatabase();
    const { method, query, body } = req;

    switch (method) {
      case 'GET':
        if (query.id) {
          const gptModelType = await GPTModelType.findById(query.id);
          if (!gptModelType) {
            return res.status(404).json({ message: 'GPTModelType not found' });
          }
          res.status(200).json(gptModelType);
        } else {
          const gptModelTypes = await GPTModelType.find({});
          if (!gptModelTypes) return res.status(404).send('GPTModel Type not found');
          res.status(200).json(gptModelTypes);
        }
        break;
      case 'POST':
        console.log('body: ', body);
        const newGPTModelType = new GPTModelType(body);
        await newGPTModelType.save();
        res.status(201).json(newGPTModelType);
        break;
      case 'PUT':
        const updatedGPTModelType = await GPTModelType.findByIdAndUpdate(body._id, body, { new: true });
        if (!updatedGPTModelType) {
          return res.status(404).json({ message: 'GPTModelType not found' });
        }
        res.status(200).json(updatedGPTModelType);
        break;
      case 'DELETE':
        if (!query.id) {
          return res.status(400).json({ message: 'ID must be provided' });
        }
        const deletedGPTModelType = await GPTModelType.findByIdAndDelete(query.id);
        if (!deletedGPTModelType) {
          return res.status(404).json({ message: 'GPTModelType not found' });
        }
        res.status(204).send();
        break;
      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.log(error);
    logger.error(`An error occurred: ${error}`);
    return res.status(500).json({ error: `An error occurred: ${error}` });
  }
}

```
###### mega-type
* ```javascript
import { connectToDatabase } from '@/lib/db';
import MegaType from '@/models/prompt-management/mega-type';
import logger from '@/lib/winston';

/**
 * @swagger
 * /api/v1/report/mega-type:
 *   get:
 *     tags:
 *       - GPT 모델 유형
 *     summary: GPT 모델 유형 조회
 *     description: GPT 모델 유형 정보를 조회합니다. 특정 ID로 조회 가능.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: false
 *         description: GPT 모델 유형의 MongoDB ObjectId
 *     responses:
 *       200:
 *         description: A successful response with one or more GPT model types
 *       404:
 *         description: MegaType not found
 *
 *   post:
 *     tags:
 *       - GPT 모델 유형
 *     summary: 새 GPT 모델 유형 추가
 *     description: 새 GPT 모델 유형을 추가합니다.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/MegaType'
 *     responses:
 *       201:
 *         description: The newly created GPT model type
 *
 *   put:
 *     tags:
 *       - GPT 모델 유형
 *     summary: GPT 모델 유형 데이터 수정
 *     description: 기존 GPT 모델 유형 데이터를 수정합니다.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/MegaType'
 *     responses:
 *       200:
 *         description: The updated GPT model type
 *       404:
 *         description: MegaType not found
 *
 *   delete:
 *     tags:
 *       - GPT 모델 유형
 *     summary: GPT 모델 유형 삭제
 *     description: 특정 GPT 모델 유형을 삭제합니다.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: GPT 모델 유형의 MongoDB ObjectId
 *     responses:
 *       204:
 *         description: GPT Model Type deleted
 *       400:
 *         description: ID is required
 *       404:
 *         description: MegaType not found
 *
 * components:
 *   schemas:
 *     MegaType:
 *       type: object
 *       properties:
 *         type:
 *           type: string
 *           required: true
 *           description: "GPT 모델 유형의 이름"
 *         description:
 *           type: string
 *           required: true
 *           description: "GPT 모델 유형에 대한 설명"
 */

export default async function handler(req, res) {
  try {
    await connectToDatabase();
    const { method, query, body } = req;

    switch (method) {
      case 'GET':
        if (query.id) {
          const megaType = await MegaType.findById(query.id);
          if (!megaType) {
            return res.status(404).json({ message: 'MegaType not found' });
          }
          res.status(200).json(megaType);
        } else {
          const megaTypes = await MegaType.find({});
          if (!megaTypes) return res.status(404).send('Mege Type not found');
          res.status(200).json(megaTypes);
        }
        break;
      case 'POST':
        console.log('body: ', body);
        const newMegaType = new MegaType(body);
        await newMegaType.save();
        res.status(201).json(newMegaType);
        break;
      case 'PUT':
        const updatedMegaType = await MegaType.findByIdAndUpdate(body._id, body, { new: true });
        if (!updatedMegaType) {
          return res.status(404).json({ message: 'MegaType not found' });
        }
        res.status(200).json(updatedMegaType);
        break;
      case 'DELETE':
        if (!query.id) {
          return res.status(400).json({ message: 'ID must be provided' });
        }
        const deletedMegaType = await MegaType.findByIdAndDelete(query.id);
        if (!deletedMegaType) {
          return res.status(404).json({ message: 'MegaType not found' });
        }
        res.status(204).send();
        break;
      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.log(error);
    logger.error(`An error occurred: ${error}`);
    return res.status(500).json({ error: `An error occurred: ${error}` });
  }
}

```
###### prompt-type
* ```javascript
import { connectToDatabase } from '@/lib/db';
import PromptType from '@/models/prompt-management/prompt-type';
import logger from '@/lib/winston';

/**
 * @swagger
 * /api/v1/report/prompt-type:
 *   get:
 *     tags:
 *       - 프롬프트 유형
 *     summary: 프롬프트 유형 조회
 *     description: 프롬프트 유형 정보를 조회합니다. 특정 ID로 조회 가능.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: false
 *         description: 프롬프트 유형의 MongoDB ObjectId
 *     responses:
 *       200:
 *         description: A successful response with one or more prompt types
 *       404:
 *         description: Prompt Type not found
 *
 *   post:
 *     tags:
 *       - 프롬프트 유형
 *     summary: 새 프롬프트 유형 추가
 *     description: 새 프롬프트 유형을 추가합니다.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/PromptType'
 *     responses:
 *       201:
 *         description: The newly created prompt type
 *
 *   put:
 *     tags:
 *       - 프롬프트 유형
 *     summary: 프롬프트 유형 데이터 수정
 *     description: 기존 프롬프트 유형 데이터를 수정합니다.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/PromptType'
 *     responses:
 *       200:
 *         description: The updated prompt type
 *       404:
 *         description: Prompt Type not found
 *
 *   delete:
 *     tags:
 *       - 프롬프트 유형
 *     summary: 프롬프트 유형 삭제
 *     description: 특정 프롬프트 유형을 삭제합니다.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 프롬프트 유형의 MongoDB ObjectId
 *     responses:
 *       204:
 *         description: Prompt Type deleted
 *       400:
 *         description: ID is required
 *       404:
 *         description: Prompt Type not found
 *
 * components:
 *   schemas:
 *     PromptType:
 *       type: object
 *       properties:
 *         type:
 *           type: string
 *           required: true
 *           description: "프롬프트 유형의 이름"
 *         description:
 *           type: string
 *           required: true
 *           description: "프롬프트 유형에 대한 설명"
 */

export default async function handler(req, res) {
  try {
    await connectToDatabase();
    const { method, query, body } = req;

    switch (method) {
      case 'GET':
        if (query.id) {
          const promptType = await PromptType.findById(query.id);
          if (!promptType) {
            return res.status(404).json({ message: 'PromptType not found' });
          }
          res.status(200).json(promptType);
        } else {
          const promptTypes = await PromptType.find({});
          if (!promptTypes) return res.status(404).send('Prompt Type not found');
          res.status(200).json(promptTypes);
        }
        break;
      case 'POST':
        console.log('body: ', body);
        const newPromptType = new PromptType(body);
        await newPromptType.save();
        res.status(201).json(newPromptType);
        break;
      case 'PUT':
        const updatedPromptType = await PromptType.findByIdAndUpdate(body._id, body, { new: true });
        if (!updatedPromptType) {
          return res.status(404).json({ message: 'PromptType not found' });
        }
        res.status(200).json(updatedPromptType);
        break;
      case 'DELETE':
        if (!query.id) {
          return res.status(400).json({ message: 'ID must be provided' });
        }
        const deletedPromptType = await PromptType.findByIdAndDelete(query.id);
        if (!deletedPromptType) {
          return res.status(404).json({ message: 'PromptType not found' });
        }
        res.status(204).send();
        break;
      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.log(error);
    logger.error(`An error occurred: ${error}`);
    return res.status(500).json({ error: `An error occurred: ${error}` });
  }
}

```
###### report-type
* ```javascript
import { connectToDatabase } from '@/lib/db';
import PromptModule from '@/models/prompt-management/prompt-module';
import ReportType from '@/models/prompt-management/report-type';
import SlideType from '@/models/prompt-management/slide-type';
import logger from '@/lib/winston';

/**
 * @swagger
 * /api/v1/report/report-type:
 *   get:
 *     tags:
 *       - 보고서 유형
 *     summary: 보고서 유형(interactive, 간단 보고서 등) 조회
 *     description: 프롬포트 모듈, 메가 프롬프트 등록 화면 시작 시 호출.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: false
 *         description: 보고서 유형별 mongoDB objectId
 *     responses:
 *       200:
 *         description: A successful response with one or more report types
 *       404:
 *         description: Report Type not found
 *
 *   post:
 *     tags:
 *       - 보고서 유형
 *     summary: 새 보고서 유형 추가
 *     description: 새 보고서 유형 추가
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/ReportType'
 *     responses:
 *       201:
 *         description: The newly created report type
 *
 *   put:
 *     tags:
 *       - 보고서 유형
 *     summary: 보고서 유형 데이터 수정
 *     description: 보고서 유형 데이터 수정
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/ReportType'
 *     responses:
 *       200:
 *         description: The updated report type
 *       404:
 *         description: Report Type not found
 *
 *   delete:
 *     tags:
 *       - 보고서 유형
 *     summary: 보고서 유형 삭제
 *     description: 보고서 유형 삭제
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 보고서 유형별 mongoDB objectId
 *     responses:
 *       200:
 *         description: Report Type deleted
 *       400:
 *         description: Report Type ID is required or Report Type is used in Prompt Module/SlideType
 *       404:
 *         description: Report Type not found
 *
 * components:
 *   schemas:
 *     ReportType:
 *       type: object
 *       properties:
 *         type:
 *           type: string
 *           required: true
 *           description: "보고서 유형 데이터의 mongoDB objectId."
 *         description:
 *           type: string
 *           required: true
 *           description: "보고서 유형 설명. 예: interactive"
 *         slideTypes:
 *           description: "이 보고서 유형이 가질 수 있는 슬라이드 유형 데이터의 objectId 배열."
 *           type: array
 *           items:
 *             type: string
 *             format: uuid
 */
export default async function handler(req, res) {
  try {
    await connectToDatabase();
    const { method, query, body } = req;
    let reportType = null;

    switch (method) {
      case 'GET':
        if (query.id) {
          reportType = await ReportType.findById(query.id);
          if (!reportType) return res.status(404).send('Report Type not found');
          res.status(200).json(reportType);
        } else {
          reportType = await ReportType.find({});
          if (!reportType) return res.status(404).send('Report Type not found');
          res.status(200).json(reportType);
        }
        break;
      case 'POST':
        reportType = new ReportType(body);
        await reportType.save();
        res.status(201).json(reportType);
        break;
      case 'PUT':
        reportType = await ReportType.findByIdAndUpdate(body._id, body, { new: true, runValidators: true });
        if (!reportType) return res.status(404).send('Report Type not found');
        res.status(200).json(reportType);
        break;
      case 'DELETE':
        if (query.id) {
          const mongoose = require('mongoose');
          console.log(`query_id: ${query.id}, type: ${typeof query.id}`);
          const objectId = new mongoose.Types.ObjectId(query.id);
          // console.log(`objectId: ${objectId}, type: ${typeof objectId}`);

          // promptModule에서 사용하지 않아야 삭제 가능.
          // const usedInPromptModule = await PromptModule.findOne({ reportType: query.id });
          const usedInPromptModule = await PromptModule.findOne({ reportType: objectId });
          if (usedInPromptModule) return res.status(400).send('Report Type is used in Prompt Module');

          // slideType에서 참조하지 않아야 삭제 가능.
          const slideTypes = await SlideType.find({});
          let isUsedInSlideType = false;

          for (let slideType of slideTypes) {
            if (slideType.reportTypes.includes(objectId)) {
              isUsedInSlideType = true;
              break;
            }
          }

          if (isUsedInSlideType) {
            return res.status(400).send('ReportType is used in SlideType');
          }

          reportType = await ReportType.findByIdAndDelete(query.id);
          if (!reportType) return res.status(404).send('Report Type not found');
          res.status(200).json({ message: 'Report Type deleted' });
        } else {
          res.status(400).send('Report Type ID is required');
        }
        break;
      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.log(error);
    logger.error(`An error occurred: ${error}`);
    return res.status(500).json({ error: `An error occurred: ${error}` });
  }
}

```
###### slide-type
* ```javascript
import { connectToDatabase } from '@/lib/db';
import SlideType from '@/models/prompt-management/slide-type';
import ReportType from '@/models/prompt-management/report-type';
import SlideLayout from '@/models/prompt-management/slide-layout';
import logger from '@/lib/winston';
import mongoose from 'mongoose';

/**
 * @swagger
 * /api/v1/report/slide-type:
 *   get:
 *     tags:
 *       - 슬라이드 유형
 *     summary: Get Slide Types
 *     description: Retrieve a list of slide types or a specific slide type by ID.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: false
 *         description: The ID of the slide type to retrieve.
 *     responses:
 *       200:
 *         description: A successful response with one or more slide types.
 *       404:
 *         description: Slide Type not found.
 *
 *   post:
 *     tags:
 *       - 슬라이드 유형
 *     summary: Create a Slide Type
 *     description: Create a new slide type.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/SlideType'
 *     responses:
 *       201:
 *         description: The newly created slide type.
 *
 *   put:
 *     tags:
 *       - 슬라이드 유형
 *     summary: Update a Slide Type
 *     description: Update an existing slide type.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/SlideType'
 *     responses:
 *       200:
 *         description: The updated slide type.
 *       404:
 *         description: Slide Type not found.
 *
 *   delete:
 *     tags:
 *       - 슬라이드 유형
 *     summary: Delete a Slide Type
 *     description: Delete a slide type by ID.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: The ID of the slide type to delete.
 *     responses:
 *       200:
 *         description: Slide Type successfully deleted.
 *       400:
 *         description: Slide Type is used in ReportType or SlideLayout.
 *       404:
 *         description: Slide Type not found.
 * components:
 *   schemas:
 *     SlideType:
 *       type: object
 *       required:
 *         - type
 *         - description
 *         - reportTypes
 *       properties:
 *         type:
 *           type: string
 *           description: "슬라이드 유형 데이터의 mongoDB objectId."
 *         description:
 *           type: string
 *           description: "슬라이드 유형 설명. 예: content"
 *         reportTypes:
 *           type: array
 *           items:
 *             type: string
 *             description: "이 슬라이드 유형이 속한 보고서 유형 데이터의 objectId 배열."
 *         slideLayouts:
 *           type: array
 *           items:
 *             type: string
 *             description: "이 슬라이드 유형이 가질 수 있는 슬라이드 지면배치 데이터의 objectId 배열."
 */
export default async function handler(req, res) {
  try {
    await connectToDatabase();
    const { method, query, body } = req;
    let slideType = null;

    switch (method) {
      case 'GET':
        if (query.id) {
          slideType = await SlideType.findById(query.id);
          if (!slideType) return res.status(404).send('Slide Type not found');
          res.status(200).json(slideType);
        } else if (query.parent_id) {
          const parentId = new mongoose.Types.ObjectId(query.parent_id);
          slideType = await SlideType.find({ reportTypes: parentId });
          if (!slideType || slideType.length === 0) return res.status(404).send('Slide Type not found');
          res.status(200).json(slideType);
        } else {
          slideType = await SlideType.find({});
          if (!slideType) return res.status(404).send('Slide Type not found');
          res.status(200).json(slideType);
        }
        break;
      case 'POST':
        slideType = new SlideType(body);
        await slideType.save();
        res.status(201).json(slideType);
        break;
      case 'PUT':
        slideType = await SlideType.findByIdAndUpdate(body._id, body, { new: true, runValidators: true });
        if (!slideType) return res.status(404).send('Slide Type not found');
        res.status(200).json(slideType);
        break;
      case 'DELETE':
        if (query.id) {
          console.log(`query_id: ${query.id}, type: ${typeof query.id}`);
          const mongoose = require('mongoose');
          const objectId = new mongoose.Types.ObjectId(query.id);

          // reportType에서 사용하지 않아야 삭제 가능.
          const reportTypes = await ReportType.find({});
          let isUsedInReportType = false;

          for (let reportType of reportTypes) {
            if (reportType.slideTypes.includes(objectId)) {
              isUsedInReportType = true;
              break;
            }
          }

          if (isUsedInReportType) return res.status(400).send('SlideType is used in ReportType');

          // slideLayout에서 참조하지 않아야 삭제 가능.
          const usedInSlideLayout = await SlideLayout.findOne({ slideType: objectId });
          if (usedInSlideLayout) return res.status(400).send('SlideType is used in SlideLayout');

          slideType = await SlideType.findByIdAndDelete(query.id);
          if (!slideType) return res.status(404).send('SlideType not found');
          res.status(200).json({ message: 'SlideType deleted' });
        } else {
          res.status(400).send('SlideType ID is required');
        }
        break;
      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.log(error);
    logger.error(`An error occurred: ${error}`);
    return res.status(500).json({ error: `An error occurred: ${error}` });
  }
}

```
###### slide-layout
* ```javascript
import { connectToDatabase } from '@/lib/db';
import SlideLayout from '@/models/prompt-management/slide-layout';
import SlideType from '@/models/prompt-management/slide-type';
import logger from '@/lib/winston';
import mongoose from 'mongoose';

/**
 * @swagger
 * /api/v1/report/slide-layout:
 *   get:
 *     tags:
 *       - 슬라이드 지면배치
 *     summary: Get Slide Layouts
 *     description: Retrieve a list of slide layouts or a specific slide layout by ID.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: false
 *         description: The ID of the slide layout to retrieve.
 *     responses:
 *       200:
 *         description: A successful response with one or more slide layouts.
 *       404:
 *         description: Slide Layout not found.
 *
 *   post:
 *     tags:
 *       - 슬라이드 지면배치
 *     summary: Create a Slide Layout
 *     description: Create a new slide layout.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/SlideLayout'
 *     responses:
 *       201:
 *         description: The newly created slide layout.
 *
 *   put:
 *     tags:
 *       - 슬라이드 지면배치
 *     summary: Update a Slide Layout
 *     description: Update an existing slide layout.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/SlideLayout'
 *     responses:
 *       200:
 *         description: The updated slide layout.
 *       404:
 *         description: Slide Layout not found.
 *
 *   delete:
 *     tags:
 *       - 슬라이드 지면배치
 *     summary: Delete a Slide Layout
 *     description: Delete a slide layout by ID.
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: The ID of the slide layout to delete.
 *     responses:
 *        200:
 *          description: Slide Layout successfully deleted.
 *        400:
 *          description: Slide Layout is used in SlideType.
 *        404:
 *          description: Slide Layout not found.
 * components:
 *   schemas:
 *     SlideLayout:
 *       type: object
 *       required:
 *         - type
 *         - description
 *         - slideType
 *       properties:
 *         type:
 *           type: string
 *           required: true
 *           description: "슬라이드 지면배치 데이터의 mongoDB objectId."
 *         description:
 *           type: string
 *           description: "슬라이드 지면배치 설명. 예: contents_1x3_message."
 *         slideType:
 *           type: string
 *           description: "이 슬라이드 지면배치가 속한 슬라이드 유형의 mongoDB objectId."
 */
export default async function handler(req, res) {
  try {
    await connectToDatabase();
    const { method, query, body } = req;
    let slideLayout = null;

    switch (method) {
      case 'GET':
        if (query.id) {
          slideLayout = await SlideLayout.findById(query.id);
          if (!slideLayout) return res.status(404).send('SlideLayout not found');
          res.status(200).json(slideLayout);
        } else if (query.parent_id) {
          const parentId = new mongoose.Types.ObjectId(query.parent_id);
          slideLayout = await SlideLayout.find({ slideType: parentId });
          if (!slideLayout || slideLayout.length === 0) return res.status(404).send('Slide Layout not found');
          res.status(200).json(slideLayout);
        } else {
          slideLayout = await SlideLayout.find({});
          if (!slideLayout) return res.status(404).send('SlideLayout not found');
          res.status(200).json(slideLayout);
        }
        break;
      case 'POST':
        slideLayout = new SlideLayout(body);
        await slideLayout.save();
        res.status(201).json(slideLayout);
        break;
      case 'PUT':
        slideLayout = await SlideLayout.findByIdAndUpdate(body._id, body, { new: true, runValidators: true });
        if (!slideLayout) return res.status(404).send('SlideLayout not found');
        res.status(200).json(slideLayout);
        break;
      case 'DELETE':
        if (query.id) {
          const mongoose = require('mongoose');
          const objectId = new mongoose.Types.ObjectId(query.id);
          console.log(`query_id: ${query.id}, type: ${typeof query.id}`);

          // slideType에서 참조하지 않아야 삭제 가능.
          const slideTypes = await SlideType.find({});
          let isUsedInSlideType = false;

          for (let slideType of slideTypes) {
            if (slideType.slideLayouts.includes(objectId)) {
              isUsedInSlideType = true;
              break;
            }
          }
          if (isUsedInSlideType) return res.status(400).send('SlideLayout is used in SlideType');

          const slideLayout = await SlideLayout.findByIdAndDelete(objectId);
          if (!slideLayout) return res.status(404).send('SlideLayout not found');
          res.status(200).json({ message: 'SlideLayout deleted' });
        } else {
          res.status(400).send('SlideLayout ID is required');
        }
        break;
      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.log(error);
    logger.error(`An error occurred: ${error}`);
    return res.status(500).json({ error: `An error occurred: ${error}` });
  }
}

```
##### 프롬프트 모듈
###### 프롬프트 기본 단위
* ```javascript
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
import crypto from 'crypto';

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
const encryptionKey = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
const iv = Buffer.from(process.env.ENCRYPTION_IV, 'hex');

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
          data.prompt = decrypt(data.prompt);

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
              // 'slideLayout',
              'gptModelType',
              'gptModelVersion',
            ];

            let actualField = field;
            if (query.hasOwnProperty(`${field}[]`)) {
              actualField = `${field}[]`;
            }
            if (!excludeFields.includes(field)) {
              if (field === 'slideLayout') {
                console.log('slideLayout here');
                // Handle slideLayout specifically
                return query[actualField]
                  ? {
                      $or: [{ [field]: new ObjectId(query[actualField]) }, { [field]: { $exists: false } }],
                    }
                  : { $or: [{ [field]: { $exists: true } }, { [field]: { $exists: false } }] };
              } else if (objectIdFields.includes(field)) {
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
        try {
          body.prompt = encrypt(body.prompt);
          const insert = { ...body };
          if (body.promptTypeValue === 'system') {
            insert.$unset = {
              slideLayout: '',
            };
          }
          promptModule = await PromptModule.create({ ...insert, promptTypeValue: undefined });
          res.status(201).json(promptModule);
        } catch (error) {
          console.log('error: ', error);
          const duplicateKeyError = /E11000 duplicate key error.*code: "(.*?)"/.exec(error);
          if (duplicateKeyError) {
            console.error('Duplicate key error:', duplicateKeyError[1]);
            return res.status(409).json({ detail: '이미 사용 중인 모듈 코드입니다. 확인 후 다시 입력해 주세요.' });
          }
          return res.status(500).json({
            detail: `저장에 실패하였습니다. 다시 시도해주시거나, 관리자에게 문의해주세요. 에러 내용: ${error}`,
          });
        }
        break;
      case 'PUT':
        const { action, update_targets } = body;
        console.log('body in PUT: ', body);
        try {
          body.prompt = encrypt(body.prompt);
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
            const update = { ...body };
            if (body.promptTypeValue === 'system') {
              update.$unset = {
                slideLayout: '',
              };
            }
            promptModule = await PromptModule.findByIdAndUpdate(body._id, update, {
              new: true,
              runValidators: true,
            });
            if (!promptModule) {
              return res.status(404).json({ detail: '수정하고자 하는 프롬프트 모듈이 DB에 없습니다.' });
            }
            res.status(200).json(promptModule);
          }
        } catch (error) {
          return res.status(500).json({
            detail: `저장에 실패하였습니다. 다시 시도해주시거나, 관리자에게 문의해주세요. 에러 내용: ${error}`,
          });
        }
        break;
      case 'DELETE':
        console.log('delete request: ', query);
        // 하나만 삭제 요청해도 삭제 대상 오브젝트 ID는 항상 배열에 담아서 요청.
        try {
          if (Array.isArray(query.delete_targets)) {
            const objectIds = query.delete_targets.map((id) => new ObjectId(id));
            const result = await PromptModule.deleteMany({ _id: { $in: objectIds } });
            if (result.deletedCount === 0)
              return res.status(404).json({ detail: '삭제 대상 프롬프트 모듈이 DB에 없습니다.' });
            return res.status(200).json({ success: true, deletedCount: result.deletedCount });
          } else {
            const objectId = new ObjectId(query.delete_targets);
            const result = await PromptModule.deleteOne({ _id: objectId });
            if (result.deletedCount === 0)
              return res.status(404).json({ detail: '삭제 대상 프롬프트 모듈이 DB에 없습니다.' });
            return res.status(200).json({ success: true, deletedCount: result.deletedCount });
          }
        } catch (error) {
          return res.status(500).json({
            detail: `삭제에 실패하였습니다. 다시 시도해주시거나, 관리자에게 문의해주세요. 에러 내용: ${error}`,
          });
        }
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.error(error);
    logger.error('An error occurred:', error);
    return res.status(500).json({ detail: `서버에서 에러가 발생했습니다. 프롬프트 모듈 관련 에러 내용: ${error}` });
  }
}```
##### 메가 프롬프트
###### 프롬프트 모듈을 포함하는 최상위 모듈
* ```javascript
import { connectToDatabase } from '@/lib/db';
import MegaPrompt from '@/models/prompt-management/mega-prompt';
import mongoose from 'mongoose';
import MegaType from '@/models/prompt-management/mega-type';
import ReportType from '@/models/prompt-management/report-type';
import SlideType from '@/models/prompt-management/slide-type';
import SlideLayout from '@/models/prompt-management/slide-layout';
import GPTModelType from '@/models/prompt-management/gpt-model-type';
import GPTModelVersion from '@/models/prompt-management/gpt-model-version';
import logger from '@/lib/winston';
import { ObjectId } from 'mongodb';
import PromptModule from '@/models/prompt-management/prompt-module';

/**
 * @swagger
 * /api/v1/report/mega-prompt:
 *   get:
 *     tags:
 *       - 메가 프롬프트 관리
 *     summary: 메가 프롬프트 조회
 *     description: |
 *       여러 시나리오에 따라 메가 프롬프트를 조회합니다.
 *       - 시나리오 1: 특정 메가 프롬프트 하나만 조회 (Query Parameter: id)
 *       - 시나리오 2: 프롬프트 모듈 관리 화면 중 "적용 프롬프트" 항목 내 숫자를 선택한 경우 (Query Parameter: id, action = "promptModule_applied")
 *       - 시나리오 3: 일반 목록 조회, 필터링 및 페이지네이션 적용 (Query Parameter: page, limit, RequestBody for filtering)
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: false
 *         description: 조회할 메가 프롬프트의 objectId (시나리오 1용) 또는 프롬프트 모듈의 objectId(시나리오 2용)
 *       - in: query
 *         name: page
 *         schema:
 *           type: number
 *         required: false
 *         description:  페이지 번호 (시나리오 3용)
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
 *                 example: "promptModule_applied"
 *               megeType:
 *                 type: string
 *                 example: "mege-type의 objectId"
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
 *                 example: 메가 프롬프트 코드
 *               name:
 *                 type: string
 *                 example: 메가 프롬프트명
 *               modifier:
 *                 type: string
 *                 example: 수정자
 *     responses:
 *       200:
 *         description: A successful response with one or more mega prompts.
 *       404:
 *         description: Mega prompt not found.
 *
 *   post:
 *     tags:
 *       - 메가 프롬프트 관리
 *     summary: Create a Mega Prompt
 *     description: Create a new mega prompt.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/MegaPrompt'
 *           example:
 *             code: "MP-001"
 *             name: "Comprehensive Analysis Module"
 *             type: "Data Analysis"
 *             gptModelType: "GPT-4"
 *             gptModelVersion: "4.0"
 *             promptContent: [
 *               {
 *                 "_id": "62c5ed1f3537f3ee89e33783",
 *                 "code": "PM-001"
 *               },
 *               {
 *                 "_id": "62c5ed1f3537f3ee89e33784",
 *                 "code": "PM-002"
 *               }
 *             ]
 *             description: "This MegaPrompt combines multiple modules for in-depth data analysis"
 *             reportType: "62c5ed1f3537f3ee89e33785"
 *             slideType: "62c5ed1f3537f3ee89e33786"
 *             slideLayout: "62c5ed1f3537f3ee89e33787"
 *             creator: "AdminUser"
 *             modifier: "AdminUser"
 *     responses:
 *       201:
 *         description: The newly created mega prompt.
 *
 *   put:
 *     tags:
 *       - 메가 프롬프트 관리
 *     summary: Update a Mega Prompt
 *     description: Update an existing mega prompt.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/MegaPrompt'
 *     responses:
 *       200:
 *         description: The updated mega prompt.
 *       404:
 *         description: Mega prompt not found.
 *
 *   delete:
 *     tags:
 *       - 메가 프롬프트 관리
 *     summary: Delete Mega Prompts
 *     description: Delete one or more mega prompts.
 *     parameters:
 *       - in: query
 *         name: delete_targets
 *         schema:
 *           type: array
 *           items:
 *             type: string
 *         required: true
 *         description: Array of mega prompt IDs to delete.
 *     responses:
 *       204:
 *         description: Mega prompt(s) successfully deleted.
 *       404:
 *         description: Mega prompt not found.
 *
 * components:
 *   schemas:
 *     MegaPrompt:
 *       type: object
 *       required:
 *         - code
 *         - name
 *         - megaType
 *         - gptModelType
 *         - gptModelVersion
 *         - promptContent
 *       properties:
 *         code:
 *           type: string
 *         name:
 *           type: string
 *         megaType:
 *           type: string
 *           format: uuid
 *           description: Reference to a mega prompt type document
 *         gptModelType:
 *           type: string
 *           format: uuid
 *           description: Reference to a gpt model type document
 *         gptModelVersion:
 *           type: string
 *           format: uuid
 *           description: Reference to a gpt model version document
 *         promptContent:
 *           type: array
 *           items:
 *             type: object
 *             properties:
 *               _id:
 *                 type: string
 *                 format: uuid
 *               code:
 *                 type: string
 *         description:
 *           type: string
 *         reportType:
 *           type: string
 *           format: uuid
 *           description: Reference to a report type document
 *         slideType:
 *           type: string
 *           format: uuid
 *           description: Reference to a slide type document
 *         slideLayout:
 *           type: string
 *           format: uuid
 *           description: Reference to a slide layout document
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
 */
export default async function handler(req, res) {
  try {
    await connectToDatabase();
    const { method, query, body } = req;
    let megaPrompt = null;

    switch (method) {
      case 'GET':
        let megaPrompts = null;

        if (query.action === 'report') {
          let queryConditions = [];
          const convertToObjectId = async (field, model) => {
            console.log(`query[${field}]: ${query[field]}`);
            if (query[field]) {
              const doc = await model.findOne({ type: query[field] }).lean();
              console.log('result of elementary id for ', field, ': ', doc);

              return doc ? { [field]: doc._id } : null;
            }
            return null;
          };

          const fieldsMapping = {
            reportType: ReportType,
            slideType: SlideType,
            slideLayout: SlideLayout,
            gptModelType: GPTModelType,
            gptModelVersion: GPTModelVersion,
          };

          for (let [field, model] of Object.entries(fieldsMapping)) {
            const condition = await convertToObjectId(field, model);
            if (condition) queryConditions.push(condition);
          }
          console.log('queryConditions: ', queryConditions);

          const matchConditions = queryConditions.length > 0 ? { $and: queryConditions } : {};

          // Fetch megaPrompts
          let megaPrompts = await MegaPrompt.find(matchConditions).lean();

          for (let megaPrompt of megaPrompts) {
            console.log('megaPrompt: ', megaPrompt);
            const promptContentIds = megaPrompt.promptContent.map((prompt) => prompt._id);
            const promptModules = await PromptModule.find({ _id: { $in: promptContentIds } });
            console.log('promptModules: ', promptModules);

            megaPrompt.promptContent = promptModules.map((prompt) => prompt.prompt);
          }

          const response = megaPrompts.reduce((acc, megaPrompt, index) => {
            acc[`prompt${index + 1}`] = megaPrompt.promptContent;
            return acc;
          }, {});

          return res.status(200).json(response);
        } else if (query.action === 'promptModule_applied' && query.id) {
          // 1. 프롬프트 모듈 관리 화면 중 "적용 프롬프트" 항목 내 숫자를 선택한 경우
          // 2. 프롬프트 모듈 삭제 도중 적용된 메가 프롬프트 조회하는 경우
          megaPrompts = MegaPrompt.find({
            promptContent: { $elemMatch: { _id: new ObjectId(query.id) } },
          })
            .sort({ code: 1 })
            .select('_id code')
            .then((megaPrompts) => {
              console.log('megaPrompts: ', megaPrompts);
              res.status(200).json(megaPrompts);
            })
            .catch((err) => {
              console.error('An error occurred: ', err);
              res.status(500).json({ error: 'Internal Server Error' });
            });
          // If aboe code block doesn't work, try this code.
          // const megaPrompts = await MegaPrompt.find({});
          // let megaPromptCodes = [];

          // for (let megaPrompt of megaPrompts) {
          // if (megaPrompt.promptContent.some(module => module._id.toString() === query.promptModuleId)) {
          // megaPromptCodes.push(megaPrompt.code);
          // }
          // }

          // if (megaPromptCodes.length > 0) {
          // return res.status(200).json({ success: true, codes: megaPromptCodes });
          // } else {
          // return res.status(404).json({ success: false, message: "No MegaPrompt uses the specified PromptModule." });
          // }
        } else if (query.id) {
          console.log('query.id', query.id);
          // 특정 메가 프롬프트 하나만 조회할 때(수정 화면용)
          megaPrompt = await MegaPrompt.findById(query.id)
            .populate('megaType')
            .populate('gptModelType')
            .populate('gptModelVersion')
            .populate('reportType')
            .populate('slideType')
            .populate('slideLayout');
          console.log('megaPrompt', megaPrompt);
          res.status(200).json(megaPrompt);
        } else {
          // 조회 조건에 맞는 메가 프롬프트 복수 조회
          const buildQueryCondition = (field) => {
            const excludeFields = ['action', 'page', 'limit'];
            const objectIdFields = ['megaType', 'gptModelType', 'gptModelVersion'];

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
          let megaPrompt = null;
          let queryConditions = [];
          const fields = ['code', 'name', 'megaType', 'gptModelType', 'gptModelVersion', 'modifier'];

          fields.forEach((field) => {
            const condition = buildQueryCondition(field);
            if (condition) queryConditions.push(condition);
          });

          console.log('queryConditions: ', queryConditions);
          // You must use $and to combine multiple conditions because queryConditions is just an array not an object that MongoDB expects.
          const matchConditions = queryConditions.length > 0 ? { $and: queryConditions } : {};
          const querySelect =
            '_id code name megaType gptModelType gptModelVersion reportType slideType slideLayout promptContent description creator createAt modifier updatedAt';
          const projectFields = querySelect.split(' ').reduce((acc, field) => {
            acc[field] = 1;
            return acc;
          }, {});
          // 목록 조회 화면용
          const page = query.page ? Number(query.page) : 1;
          const pageSize = query.limit ? Number(query.limit) : 10;

          const aggregationPipeline = [
            { $match: matchConditions },
            {
              $lookup: {
                from: 'megatypes',
                localField: 'megaType',
                foreignField: '_id',
                as: 'megaType',
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
              $lookup: {
                from: 'reporttypes',
                localField: 'reportType',
                foreignField: '_id',
                as: 'reportType',
              },
            },
            {
              $lookup: {
                from: 'slidetypes',
                localField: 'slideType',
                foreignField: '_id',
                as: 'slideType',
              },
            },
            {
              $lookup: {
                from: 'slidelayouts',
                localField: 'slideLayout',
                foreignField: '_id',
                as: 'slideLayout',
              },
            },
            {
              $facet: {
                totalData: [{ $count: 'totalCount' }],
                megaPrompts: [
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

          const result = await MegaPrompt.aggregate(aggregationPipeline);
          const totalRecords = result.length > 0 && result[0].totalData[0] ? result[0].totalData[0]?.totalCount : 0;
          const megaPrompts = result.length > 0 ? result[0].megaPrompts : [];
          return res.status(200).json({ megaPrompts, totalRecords });

          /* mongoDB 관련 validation 에러로 제대로 실행되지 않음.
          const aggregationPipeline = [
            { $match: queryConditions },
            // Replace the populate methods with $lookup stages
            { $lookup: { from: 'reportTypes', localField: 'reportType', foreignField: '_id', as: 'reportType' } },
            { $lookup: { from: 'slideTypes', localField: 'slideType', foreignField: '_id', as: 'slideType' } },
            { $lookup: { from: 'slideLayouts', localField: 'slideLayout', foreignField: '_id', as: 'slideLayout' } },
            {
              $facet: {
                totalData: [{ $count: 'totalCount' }],
                megaPrompts: [
                  { $sort: { updatedAt: -1 } },
                  { $skip: (page - 1) * pageSize },
                  { $limit: pageSize },
                  {
                    $project: {
                      _id: 1,
                      code: 1,
                      name: 1,
                      type: 1,
                      gptModelType: 1,
                      gptModelVersion: 1,
                      promptContent: 1,
                      description: 1,
                      creator: 1,
                      createAt: 1,
                      modifier: 1,
                      updatedAt: 1,
                      reportType: 1,
                      slideType: 1,
                      slideLayout: 1,
                    },
                  },
                ],
              },
            },
          ];

          const result = await MegaPrompt.aggregate(aggregationPipeline);
          console.log(`result of aggregation: ${result}`);
          const totalRecords = result[0].totalData[0]?.totalCount || 0;
          megaPrompts = result[0].megaPrompts;

          res.status(200).json({ megaPrompts, totalRecords });
          */
        }
        break;
      case 'POST':
        const createSession = await mongoose.startSession();
        createSession.startTransaction();
        try {
          const insert = { ...body };
          if (body.megaTypeValue !== '보고서') {
            insert.$unset = {
              reportType: '',
              slideType: '',
              slideLayout: '',
            };
          }
          megaPrompt = await MegaPrompt.create({ ...insert, changedPromptContent: undefined });
          if (!megaPrompt) {
            throw new Error('MegaPrompt insert failed');
          }

          //update promptModule's applied_count
          if (body.changedPromptContent && Array.isArray(body.changedPromptContent)) {
            for (const change of body.changedPromptContent) {
              await PromptModule.findByIdAndUpdate(
                change._id,
                { $inc: { applied_count: change.change } },
                { createSession }
              );
            }
          }
          await createSession.commitTransaction();

          res.status(201).json(megaPrompt);
        } catch (error) {
          await createSession.abortTransaction();
          console.error('Error in  insert new megaPrompt:', error);
          const duplicateKeyError = /E11000 duplicate key error.*code: "(.*?)"/.exec(error);
          if (duplicateKeyError) {
            console.error('Duplicate key error:', duplicateKeyError[1]);
            return res
              .status(409)
              .json({ detail: '이미 사용 중인 메가 프롬프트 코드입니다. 확인 후 다시 입력해 주세요.' });
          }
          return res.status(500).json({
            detail: `저장에 실패하였습니다. 다시 시도해주시거나, 관리자에게 문의해주세요. 에러 내용: ${error}`,
          });
        } finally {
          createSession.endSession();
        }
        break;
      case 'PUT':
        console.log('body in PUT: ', body);
        const updateSession = await mongoose.startSession();
        updateSession.startTransaction();
        try {
          console.log();
          const update = { $set: { ...body, changedPromptContent: undefined } };
          if (body.megaTypeValue !== '보고서') {
            console.log('해당없음 update start!!"');
            update.$unset = {
              reportType: '',
              slideType: '',
              slideLayout: '',
            };
          }
          console.log('update: ', update);
          megaPrompt = await MegaPrompt.findByIdAndUpdate(body._id, update, {
            new: true,
            runValidators: true,
            session: updateSession,
          });
          if (!megaPrompt) {
            throw new Error('MegaPrompt not found');
          }
          // Update promptModule's applied_count
          if (body.changedPromptContent && Array.isArray(body.changedPromptContent)) {
            for (const change of body.changedPromptContent) {
              await PromptModule.findByIdAndUpdate(
                change._id,
                { $inc: { applied_count: change.change } },
                { updateSession }
              );
            }
          }
          await updateSession.commitTransaction();
          res.status(200).json(megaPrompt);
        } catch (error) {
          await updateSession.abortTransaction();
          console.error('Error in update operation:', error);
          return res.status(500).json({
            detail: `저장에 실패하였습니다. 다시 시도해주시거나, 관리자에게 문의해주세요. 에러 내용: ${error}`,
          });
        } finally {
          updateSession.endSession();
        }
        break;
      case 'DELETE':
        console.log('delete request: ', query);
        const deleteSession = await mongoose.startSession();
        deleteSession.startTransaction();
        try {
          const objectIds = Array.isArray(query.delete_targets)
            ? query.delete_targets.map((id) => new ObjectId(id))
            : [new ObjectId(query.delete_targets)];

          const megaPrompts = await MegaPrompt.find({ _id: { $in: objectIds } }).session(deleteSession);

          for (const megaPrompt of megaPrompts) {
            for (const promptModule of megaPrompt.promptContent) {
              await PromptModule.updateOne({ _id: promptModule._id }, { $inc: { applied_count: -1 } }).session(
                deleteSession
              );
            }
          }

          const deleteResult = Array.isArray(query.delete_targets)
            ? await MegaPrompt.deleteMany({ _id: { $in: objectIds } }).session(deleteSession)
            : await MegaPrompt.deleteOne({ _id: objectIds }).session(deleteSession);

          if (deleteResult.deletedCount === 0) {
            throw new Error('No documents found with the provided IDs.');
          }
          await deleteSession.commitTransaction();
          res.status(200).json({ success: true, deletedCount: deleteResult.deletedCount });
        } catch (error) {
          console.error('Error in transaction:', error);
          await deleteSession.abortTransaction();
          return res.status(500).json({
            detail: `삭제에 실패하였습니다. 다시 시도해주시거나, 관리자에게 문의해주세요. 에러 내용: ${error}`,
          });
        } finally {
          deleteSession.endSession();
        }
        break;

      default:
        res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
        res.status(405).end(`Method ${method} Not Allowed`);
    }
  } catch (error) {
    console.error(error);
    logger.error('An error occurred:', error);
    return res.status(500).json({ detail: `서버에서 에러가 발생했습니다. 메가 프롬프트 관련 에러 내용: ${error}` });
  }
}

```
#### client-side 
##### _component
###### admin-left.js
* ```javascript
'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState, useRef, useEffect } from 'react';

export default function AdminLeft({ activeLnav, setactiveLnav }) {
  const onLnav = (index) => {
    setactiveLnav(index);
  };
  const onLcate = (e) => {
    const li = e.target.parentNode;
    li.classList.toggle('open');
  };

  return (
    <aside className="side admin-left">
      <div className="inner">
        <ul className="admin-cate">
          <li className={activeLnav > 10 && activeLnav < 20 ? 'on' : ''}>
            <button className="user" onClick={onLcate}>
              사용자 관리
            </button>
            <ul className="d2">
              <li className={activeLnav === 11 ? 'on' : ''}>
                <Link href="/admin/user" onClick={() => onLnav(11)}>
                  사용자 목록
                </Link>
              </li>
              <li className={activeLnav === 12 ? 'on' : ''}>
                <Link href="/admin/organ" onClick={() => onLnav(12)}>
                  조직관리
                </Link>
              </li>
            </ul>
          </li>
          <li className={activeLnav > 20 && activeLnav < 30 ? 'on' : ''}>
            <button className="prompt" onClick={onLcate}>
              프롬프트 설정
            </button>
            <ul className="d2">
              <li className={activeLnav === 21 ? 'on' : ''}>
                <Link href="/admin/prompt/module" onClick={() => onLnav(21)}>
                  프롬프트 모듈 관리
                </Link>
              </li>
              <li className={activeLnav === 22 ? 'on' : ''}>
                <Link href="/admin/prompt/mega" onClick={() => onLnav(22)}>
                  메가 프롬프트 관리
                </Link>
              </li>
            </ul>
          </li>
          <li className={activeLnav > 30 && activeLnav < 40 ? 'on' : ''}>
            <button className="credit" onClick={onLcate}>
              크레딧 관리
            </button>
          </li>
          <li className={activeLnav > 40 && activeLnav < 50 ? 'on' : ''}>
            <button className="community" onClick={onLcate}>
              커뮤니티 관리
            </button>
            <ul className="d2">
              <li className={activeLnav === 41 ? 'on' : ''}>
                <Link href="/admin/notice" onClick={() => onLnav(41)}>
                  공지사항
                </Link>
              </li>
              <li className={activeLnav === 42 ? 'on' : ''}>
                <Link href="/admin/faq" onClick={() => onLnav(42)}>
                  FAQ
                </Link>
              </li>
              <li className={activeLnav === 43 ? 'on' : ''}>
                <Link href="/admin/manual" onClick={() => onLnav(43)}>
                  이용가이드 관리
                </Link>
              </li>
              <li className={activeLnav === 44 ? 'on' : ''}>
                <Link href="/admin/inquiry" onClick={() => onLnav(44)}>
                  1:1문의 관리
                </Link>
              </li>
            </ul>
          </li>
          <li className={activeLnav > 50 && activeLnav < 60 ? 'on' : ''}>
            <button className="system" onClick={onLcate}>
              시스템 관리
            </button>
          </li>
          <li>
            <button className="log" onClick={onLcate}>
              로그 조회
            </button>
          </li>
        </ul>
        <footer className="footer">
          <p className="copy">
            COPYRIGHT (C) BY SK INC.
            <br />
            ALL RIGHT RESERVED.
          </p>
        </footer>
      </div>
    </aside>
  );
}

```
###### popup-confirm-alert.js
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
}

```
###### popup-toast.js
* ```javascript
import { useEffect, useState } from 'react';

const onTimer = (timer) => {
  return timer && setTimeout(timer, 2500);
};

export const showToastMessage = ({ setState, message }) => {
  setState(message);
  onTimer(() => setState(''));
};

export default function PopupToast({ onHideToast, toastMessage }) {
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    const timer = onTimer(onHideToast);
    return () => clearTimeout(timer);
  }, [onHideToast]);

  useEffect(() => {
    if (toastMessage) {
      setShowToast(true);
    } else {
      setShowToast(false);
    }
  }, [toastMessage]);

  return (
    showToast && (
      <aside className="popup center">
        <div className="pop-content toast">
          <div className="wrap-message">{toastMessage}</div>
          {/* <div className="wrap-btn">
            <button onClick={onHideToast}>취소</button>
          </div> */}
        </div>
      </aside>
    )
  );
}

```
###### multi-select.js
* ```javascript
import { useState, useEffect } from 'react';

export default function MultiSelect({
  multiSelectData,
  placeholder,
  multiSelectValue,
  setMultiSelectValue,
  resetAll,
  resetFlag,
}) {
  const [multiSelectCheckAll, setMultiSelectCheckAll] = useState(false);
  const [multiSelectCheckbox, setMultiSelectCheckbox] = useState(multiSelectData);
  useEffect(() => {
    const checkedLabels = multiSelectCheckbox.filter((item) => item.isChecked).map((item) => item.label);
    if (checkedLabels.length === multiSelectCheckbox.length) {
      setMultiSelectValue('전체');
    } else {
      setMultiSelectValue(checkedLabels.join(', '));
    }
  }, [multiSelectCheckbox]);

  useEffect(() => {
    const isAllChecked = multiSelectCheckbox.every((item) => item.isChecked);
    setMultiSelectCheckAll(isAllChecked);
  }, [multiSelectCheckbox]);

  const onMultiSelectCheckAll = () => {
    const updateMultiSelectCheckbox = multiSelectCheckbox.map((item) => ({
      ...item,
      isChecked: !multiSelectCheckAll,
    }));
    setMultiSelectCheckbox(updateMultiSelectCheckbox);
    setMultiSelectCheckAll(!multiSelectCheckAll);

    if (multiSelectCheckbox.some((item) => item.isChecked)) {
      setMultiSelectCheckAll(true);
      const updateMultiSelectCheckbox = multiSelectCheckbox.map((item) => ({
        ...item,
        isChecked: false,
      }));
      setMultiSelectCheckbox(updateMultiSelectCheckbox);
    }
  };

  const onMultiSelectCheck = (id) => {
    const updateMultiSelectCheckbox = multiSelectCheckbox.map((item) => {
      if (item.id === id) {
        return {
          ...item,
          isChecked: !item.isChecked,
        };
      }
      return item;
    });
    setMultiSelectCheckbox(updateMultiSelectCheckbox);
  };

  const [toggleMultiSelect, setToggleMultiSelect] = useState(false);
  const onToggleMultiSelect = () => {
    setToggleMultiSelect(!toggleMultiSelect);
  };
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (toggleMultiSelect && !e.target.closest('.popup-select')) {
        setToggleMultiSelect(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [toggleMultiSelect]);

  return (
    <div className="wrap-select">
      <div className="wrap-input">
        <input type="text" placeholder={placeholder} value={multiSelectValue} onClick={onToggleMultiSelect} readOnly />
      </div>
      <div className={toggleMultiSelect ? 'popup-select on' : 'popup-select'}>
        <div className="inner">
          <div className="wrap-checkbox-list">
            <ul>
              {multiSelectCheckbox.map((item) => (
                <li key={item.id}>
                  <span className="wrap-checkbox">
                    <input
                      type="checkbox"
                      name="type"
                      id={item.id}
                      checked={item.isChecked || false}
                      onChange={() => onMultiSelectCheck(item.id)}
                    />
                    <span>{item.label}</span>
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="wrap-checkbox-btm">
            <label className="wrap-checkbox">
              <input type="checkbox" checked={multiSelectCheckAll} onChange={onMultiSelectCheckAll} />
              <span className={multiSelectCheckbox.some((item) => item.isChecked) ? 'some' : ''}>
                {multiSelectCheckbox.some((item) => item.isChecked) ? '선택 해제' : '전체 선택'}
              </span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}

```
##### /app/admin/_component
###### admin-left.js
* ```javascript
'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState, useRef, useEffect } from 'react';

export default function AdminLeft({ activeLnav, setactiveLnav }) {
  const onLnav = (index) => {
    setactiveLnav(index);
  };
  const onLcate = (e) => {
    const li = e.target.parentNode;
    li.classList.toggle('open');
  };

  return (
    <aside className="side admin-left">
      <div className="inner">
        <ul className="admin-cate">
          <li className={activeLnav > 10 && activeLnav < 20 ? 'on' : ''}>
            <button className="user" onClick={onLcate}>
              사용자 관리
            </button>
            <ul className="d2">
              <li className={activeLnav === 11 ? 'on' : ''}>
                <Link href="/admin/user" onClick={() => onLnav(11)}>
                  사용자 목록
                </Link>
              </li>
              <li className={activeLnav === 12 ? 'on' : ''}>
                <Link href="/admin/organ" onClick={() => onLnav(12)}>
                  조직관리
                </Link>
              </li>
            </ul>
          </li>
          <li className={activeLnav > 20 && activeLnav < 30 ? 'on' : ''}>
            <button className="prompt" onClick={onLcate}>
              프롬프트 설정
            </button>
            <ul className="d2">
              <li className={activeLnav === 21 ? 'on' : ''}>
                <Link href="/admin/prompt/module" onClick={() => onLnav(21)}>
                  프롬프트 모듈 관리
                </Link>
              </li>
              <li className={activeLnav === 22 ? 'on' : ''}>
                <Link href="/admin/prompt/mega" onClick={() => onLnav(22)}>
                  메가 프롬프트 관리
                </Link>
              </li>
            </ul>
          </li>
          <li className={activeLnav > 30 && activeLnav < 40 ? 'on' : ''}>
            <button className="credit" onClick={onLcate}>
              크레딧 관리
            </button>
          </li>
          <li className={activeLnav > 40 && activeLnav < 50 ? 'on' : ''}>
            <button className="community" onClick={onLcate}>
              커뮤니티 관리
            </button>
            <ul className="d2">
              <li className={activeLnav === 41 ? 'on' : ''}>
                <Link href="/admin/notice" onClick={() => onLnav(41)}>
                  공지사항
                </Link>
              </li>
              <li className={activeLnav === 42 ? 'on' : ''}>
                <Link href="/admin/faq" onClick={() => onLnav(42)}>
                  FAQ
                </Link>
              </li>
              <li className={activeLnav === 43 ? 'on' : ''}>
                <Link href="/admin/manual" onClick={() => onLnav(43)}>
                  이용가이드 관리
                </Link>
              </li>
              <li className={activeLnav === 44 ? 'on' : ''}>
                <Link href="/admin/inquiry" onClick={() => onLnav(44)}>
                  1:1문의 관리
                </Link>
              </li>
            </ul>
          </li>
          <li className={activeLnav > 50 && activeLnav < 60 ? 'on' : ''}>
            <button className="system" onClick={onLcate}>
              시스템 관리
            </button>
          </li>
          <li>
            <button className="log" onClick={onLcate}>
              로그 조회
            </button>
          </li>
        </ul>
        <footer className="footer">
          <p className="copy">
            COPYRIGHT (C) BY SK INC.
            <br />
            ALL RIGHT RESERVED.
          </p>
        </footer>
      </div>
    </aside>
  );
}

```
##### _util
###### axios-util.js
* ```javascript
'use client';

import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useRouter, usePathname } from 'next/navigation';

import axios from 'axios';
import qs from 'qs';
/*
    axios 인스턴스를 생성합니다.
    생성할때 사용하는 옵션들 (baseURL, timeout, headers 등)은 다음 URL에서 확인할 수 있습니다.
    https://github.com/axios/axios 의 Request Config 챕터 확인
*/
const axiosObj = axios.create({
  baseURL: '',
  timeout: 900000,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: (params) => {
    return qs.stringify(params, { arrayFormat: 'brackets' });
  },
});

const AxiosInterceptor = ({ children }) => {
  // 사용자 토큰 제어
  let { accessToken, userInfo } = useSelector((state) => state.auth);
  const [isSet, setIsSet] = useState(false);
  const router = useRouter();
  const currentPath = usePathname();

  useEffect(() => {
    setIsSet(true);

    //요청 핸들러
    const requestHandler = (config) => {
      // axios 설정값에 대해 작성합니다.

      if (currentPath === '/login' || currentPath === '/signup' || currentPath === '/reset') {
        // 로그인 페이지는 별도 동작을 하지 않는다.
        // + 회원 가입 페이지에도 별도 동작을 하지 않는다.
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

    // 응답 처리
    const responseHandler = (response) => {
      // 개발환경에서 로그 출력
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
      // 요청 에러 처리를 작성합니다.
      return Promise.reject(error);
    };

    const requestInterceptor = axiosObj.interceptors.request.use(requestHandler, errorHandler);
    const responseInterceptor = axiosObj.interceptors.response.use(responseHandler, errorHandler);

    return () => {
      axiosObj.interceptors.request.eject(requestInterceptor);
      axiosObj.interceptors.response.eject(responseInterceptor);
    };
  }, [accessToken, currentPath, router, userInfo]);

  return isSet && children;
};

/**
 * Request method 공통 처리
 * @param {RequestConfig} config
 * @param {function} [successHandling] 성공 callback
 * @param {function} [errorHandling] 실패 callback
 * @returns {Promise}
 */
const common = (config, successHandling, errorHandling) => {
  // axios 호출
  const resultPromise = axiosObj(config);

  // response 핸들링을 직접 처리하는 경우
  if (successHandling) {
    return resultPromise
      .then((response) => {
        successHandling(response);
      })
      .catch((error) => {
        if (errorHandling) {
          errorHandling(error);
        } else {
          console.log('axios-util-error');
          console.error(error);
        }
      });
    // response 핸들링을 다음 프로세스에게 위임하는 경우
  } else {
    return resultPromise;
  }
};

const axiosUtil = {
  /**
   * GET HTTP 요청
   * @param {string} url 요청 URL
   * @param {object} data 요청 파라미터
   * @param {function} [successHandling] 성공 callback
   * @param {function} [errorHandling] 실패 callback
   * @returns {Promise} promise
   */
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
  /**
   * POST HTTP 요청
   * @param {string} url 요청 URL
   * @param {object} data 요청 파라미터
   * @param {function} [successHandling] 성공 callback
   * @param {function} [errorHandling] 실패 callback
   * @returns {Promise} promise
   */
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
  /**
   * PUT HTTP 요청
   * @param {string} url 요청 URL
   * @param {object} data 요청 파라미터
   * @param {function} [successHandling] 성공 callback
   * @param {function} [errorHandling] 실패 callback
   * @returns {Promise} promise
   */
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
  /**
   * DELETE HTTP 요청
   * @param {string} url 요청 URL
   * @param {object} data 요청 파라미터
   * @param {function} [successHandling] 성공 callback
   * @param {function} [errorHandling] 실패 callback
   * @returns {Promise} promise
   */
  delete: (url, data, successHandling, errorHandling) =>
    common(
      {
        method: 'delete',
        url,
        data,
        params: data?.params,
      },
      successHandling,
      errorHandling
    ),
  /**
   * PATCH HTTP 요청
   * @param {string} url 요청 URL
   * @param {object} data 요청 파라미터
   * @param {function} [successHandling] 성공 callback
   * @param {function} [errorHandling] 실패 callback
   * @returns {Promise} promise
   */
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
  /**
   * OPTION HTTP 요청
   * @param {string} url 요청 URL
   * @param {object} data 요청 파라미터
   * @param {function} [successHandling] 성공 callback
   * @param {function} [errorHandling] 실패 callback
   * @returns {Promise} promise
   */
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
  /**
   * axios(config)
   * @param {RequestConfig} config
   */
  request: (config) => axios(config),
};

// 생성한 인스턴스를 익스포트 합니다.
export default axiosUtil;
export { AxiosInterceptor };

```
###### error-popup-logout.js
* ```javascript
import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';

const usePopupAndLogout = () => {
  const [confirmPopup, setConfirmPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');
  const router = useRouter();

  const handlePopupMessage = (message, status = 0) => {
    if (status === 0) {
      setPopupMessage(`${message}`);
    } else {
      setPopupMessage(`${message} (code: ${status})`);
    }
    setConfirmPopup(true);
  };

  const handleLogout = useCallback(
    (message) => {
      console.log('handleLogout message: ', message);
      router.push('?logout=true');
    },
    [router]
  );

  const handleAxiosError = useCallback(
    (err) => {
      if (err?.request?.response) {
        const { status, data } = err?.response;
        switch (status) {
          case 401:
            handlePopupMessage('사용자 정보가 유효하지 않아 로그인페이지로 이동 합니다.');
            setTimeout(() => {
              handleLogout('token expired');
            }, 2000);
            break;
          case 403:
            handlePopupMessage('사용자 정보가 유효하지 않아 로그인페이지로 이동 합니다.');
            setTimeout(() => {
              handleLogout('server refused to process this token');
            }, 2000);

            break;
          default:
            handlePopupMessage(data.detail, status);
            break;
        }
      } else if (err?.request) {
        handlePopupMessage(err.message, err.code);
      } else {
        handlePopupMessage(err.message, err.code);
      }
    },
    [handleLogout]
  );

  function handleFetchError(err) {
    if (err.status === 401) {
      handlePopupMessage('사용자 정보가 유효하지 않아 로그인페이지로 이동 합니다.');
      setTimeout(() => {
        handleLogout('token expired');
      }, 2000);
    } else if (err.status === 403) {
      handlePopupMessage('사용자 정보가 유효하지 않아 로그인페이지로 이동 합니다.');
      setTimeout(() => {
        handleLogout('server refused to process this token');
      }, 2000);
    } else {
      handlePopupMessage(err.statusText, err.status);
    }
  }

  return {
    confirmPopup,
    setConfirmPopup,
    popupMessage,
    setPopupMessage,
    handlePopupMessage,
    handleLogout,
    handleAxiosError,
    handleFetchError,
  };
};

export default usePopupAndLogout;

```
###### prompt-management.js
* ```javascript
import { useState, useEffect } from 'react';
import axiosUtil from '@/app/_util/axios-util';
import { allowedCharsRegex, allowed2BytesCharsRegex } from '@/config/constants';

export async function fetchAndTransform(url, parentId = null) {
  if (!url) {
    console.error('Missing required parameters.');
    return [];
  }

  try {
    let queryParams;
    if (parentId != null) {
      console.log('parentId: ', parentId);
      queryParams = { parent_id: parentId };
    }
    const response = await axiosUtil.get(url, { params: queryParams });
    return response.data.map((item) => ({
      id: item._id,
      label: item.type,
      isChecked: false, // ischecked는 React MultiSelect에서 쓰기 위한 것. 다른 곳에서 쓰이지 않음.
    }));
  } catch (error) {
    console.error('Error fetching data: ', error);
    handleAxiosError(error);
    return []; // Return an empty array in case of an error
  }
}

export function validateCode(code, title, setPopupMessage, setConfirmPopup) {
  if (code.length < 2 || code.length > 50 || code.includes(' ') || !allowedCharsRegex.test(code)) {
    setPopupMessage(
      title +
        ' 코드는 공백없이 최소 2자, 최대 50자로 한정되며 영어 대소문자, 숫자, 일부 특수문자! " # $ % & \' ( ) * + , - . / : ; < = > ? @ [ ₩ ] ^ _ ` { | } ~만 입력할 수 있습니다.'
    );
    setConfirmPopup(true);
    return false;
  }
  return true;
}

export function validateName(name, title, setPopupMessage, setConfirmPopup) {
  if (name.length < 2 || name.length > 50 || !allowed2BytesCharsRegex.test(name)) {
    setPopupMessage(
      title +
        ' 이름은 공백을 포함하여 최소 2자, 최대 50자로 한정되며 한글, 영어 대소문자, 숫자, 일부 특수문자! " # $ % & \' ( ) * + , - . / : ; < = > ? @ [ ₩ ] ^ _ ` { | } ~만 입력할 수 있습니다.'
    );
    setConfirmPopup(true);
    return false;
  }
  return true;
}

export function validatePromptDetail(promptDetail, setPopupMessage, setConfirmPopup) {
  if (promptDetail.length < 2 || promptDetail.length > 50000 || !allowed2BytesCharsRegex.test(promptDetail)) {
    setPopupMessage(
      '프롬프트 내용은 공백을 포함하여 최소 2자, 최대 50,000자로 한정되며 한글 ,영어 대소문자, 숫자, 일부 특수문자! " # $ % & \' ( ) * + , - . / : ; < = > ? @ [ ₩ ] ^ _ ` { | } ~만 입력할 수 있습니다.'
    );
    setConfirmPopup(true);
    return false;
  }
  return true;
}

export function validateDescription(description, setPopupMessage, setConfirmPopup) {
  if (description.length > 5000) {
    setPopupMessage('비고는 공백을 포함하여 최대 5,000자까지 입력할 수 있습니다.');
    setConfirmPopup(true);
    return false;
  }
  return true;
}

```
##### /app/admin/prompt
###### module (프롬프트 모듈 관리 화면)
###### [id]
###### page.js
* ```javascript
'use client';

import Link from 'next/link';
// import Image from "next/image"
import { useState, useRef, useEffect, useCallback } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import AdminLeft from '@/app/admin/_components/admin-left';
import PopupPromptEdit from '../popup-prompt-edit';
import PopupPromptDelete from '../popup-prompt-delete';
import PopupConfirmAlert from '@/app/_components/popup-confirm-alert';
import PopupToast from '@/app/_components/popup-toast';
import {
  PROMPT_TYPE,
  REPORT_TYPE,
  SLIDE_TYPE,
  SLIDE_LAYOUT,
  GPT_MODEL_TYPE,
  GPT_MODEL_VERSION,
  PROMPT_MODULE,
} from '@/config/apiPaths';
import usePopupAndLogout from '@/app/_util/error-popup-logout';
import { useContext } from 'react';
// import { PromptModuleContext } from '@/app/admin/prompt/prompt-module-context';
// import withPromptModuleContext from '@/app/admin/prompt/prompt-module-hoc';
import axiosUtil from '@/app/_util/axios-util';
import { useSelector } from 'react-redux';
import {
  fetchAndTransform,
  validateCode,
  validateName,
  validatePromptDetail,
  validateDescription,
} from '@/app/_util/prompt-management';

// const AdminPromptDetail = () => {
export default function AdminPromptDetail() {
  const { confirmPopup, setConfirmPopup, popupMessage, setPopupMessage, handlePopupMessage, handleAxiosError } =
    usePopupAndLogout();
  const { userInfo } = useSelector((state) => state.auth);
  // const { promptModuleData } = useContext(PromptModuleContext);

  const pathname = usePathname();
  const promptModuleId = pathname.substring(pathname.lastIndexOf('/') + 1);
  const router = useRouter();
  const isFirstRunSlideType = useRef(true);
  const isFirstRunSlideLayout = useRef(true);
  const [shouldNavigate, setShouldNavigate] = useState(false);
  const [proceed, setProceed] = useState(false);

  // 적용프롬프트 팝업
  const [showPopupPromptEdit, setShowPopupPromptEdit] = useState(false);
  const [showPopupPromptDelete, setShowPopupPromptDelete] = useState(false);
  const [selectedModule, setSelectedModule] = useState(null);
  const onPromptPopupEdit = (module) => {
    setSelectedModule(module);
    setShowPopupPromptEdit(true);
  };
  const onPromptPopupDelete = (id) => {
    setSelectedModule(id);
    setShowPopupPromptDelete(true);
  };
  function onHidePopupPrompt(proceed = false) {
    console.log('proceed in onHidePopupPrompt: ', proceed);
    setProceed(proceed);
    setShowPopupPromptEdit(false);
    onPopupPromptEditComplete();
  }

  function onHidePopupDelete() {
    setShowPopupPromptDelete(false);
  }

  const [selectedPromptTypeId, setSelectedPromptTypeId] = useState(null);
  const [selectedReportTypeId, setSelectedReportTypeId] = useState(null);
  const [selectedSlideTypeId, setSelectedSlideTypeId] = useState(null);
  const [selectedSlideLayoutId, setSelectedSlideLayoutId] = useState(null);
  const [selectedModelTypeId, setSelectedModelTypeId] = useState(null);
  const [selectedModelVertionId, setSelectedModelVersionId] = useState(null);
  const [isPopupPromptEditComplete, setIsPopupPromptEditComplete] = useState(false);
  const [activeLnav, setactiveLnav] = useState(21);
  const [mcodeValue, setMcodeValue] = useState('');
  const [mnameValue, setMnameValue] = useState('');
  const [promptTypeValue, setPromptTypeValue] = useState('');
  const [reportTypeValue, setReportTypeValue] = useState('');
  const [slideTypeValue, setSlideTypeValue] = useState('');
  const [slideLayoutValue, setSlideLayoutValue] = useState('');
  const [appliedCount, setAppliedCount] = useState(0);
  const [modelValue, setModelValue] = useState('');
  const [versionValue, setVersionValue] = useState('');
  const [promptDetail, setPromptDetail] = useState('');
  const [description, setDescription] = useState('');
  const [registrantValue, setRegistrantValue] = useState('');
  const [emailRegistrantValue, setEmailRegistrantValue] = useState('');
  const [dateRegistValue, setDateRegistValue] = useState('');
  const [modifierValue, setModifierValue] = useState('');
  const [emailModifierValue, setEmailModifierValue] = useState('');
  const [dateModifyValue, setDateModifyValue] = useState('');
  const [fetchedPromptTypeData, setFetchedPromptTypeData] = useState([]);
  const [fetchedReportTypeData, setFetchedReportTypeData] = useState([]);
  const [fetchedSlideTypeData, setFetchedSlideTypeData] = useState([]);
  const [fetchedSlideLayoutData, setFetchedSlideLayoutData] = useState([]);
  const [fetchedModelTypeData, setFetchedModelTypeData] = useState([]);
  const [fetchedModelVersionData, setFetchedModelVersionData] = useState([]);
  const [requiredItems, setRequiredItems] = useState([]);
  const [triggerFetchSlideType, setTriggerFetchSlideType] = useState(false);
  const [triggerFetchSlideLayout, setTriggerFetchSlideLayout] = useState(false);
  const [isModified, setIsModified] = useState(false);

  const onPopupPromptEditComplete = () => {
    setIsPopupPromptEditComplete(true);
  };

  const savePromptModule = () => {
    console.log('userInfo: ', userInfo);
    const updateData = {
      ...(promptModuleId !== 'regist' ? { _id: promptModuleId } : {}),
      code: mcodeValue,
      name: mnameValue,
      promptType: selectedPromptTypeId,
      ...(selectedReportTypeId ? { reportType: selectedReportTypeId } : {}),
      ...(selectedSlideTypeId ? { slideType: selectedSlideTypeId } : {}),
      ...(selectedSlideLayoutId ? { slideLayout: selectedSlideLayoutId } : {}),
      gptModelType: selectedModelTypeId,
      gptModelVersion: selectedModelVertionId,
      prompt: promptDetail,
      description: description,
      ...(promptModuleId === 'regist' ? { creator: userInfo.username } : {}),
      modifier: userInfo.username,
      ...(promptModuleId === 'regist' ? { applied_count: 0 } : {}),
      promptTypeValue: promptTypeValue,
    };

    const putData = async () => {
      try {
        if (promptModuleId === 'regist') {
          const response = await axiosUtil.post(PROMPT_MODULE, updateData);
          setToastMessage('저장되었습니다.');
        } else {
          const response = await axiosUtil.put(PROMPT_MODULE, updateData);
          setToastMessage('정보가 수정되었습니다.');
        }
        console.log('post is done. go to /admin/prompt. show the box here');
        onOpenSuccessToast();
        const timer = setTimeout(() => {
          router.push('/admin/prompt/module');
        }, 500);
      } catch (error) {
        console.error('Error occured in updating ', error);
        handleAxiosError(error);
        // setShouldNavigate(true);
      }
    };
    putData();
  };

  useEffect(() => {
    if (isPopupPromptEditComplete) {
      if (proceed) savePromptModule();
      setIsPopupPromptEditComplete(false);
      router.push('/admin/prompt/module');
    }
  }, [isPopupPromptEditComplete]);

  const validateValues = () => {
    if (
      validateCode(mcodeValue, '모듈', setPopupMessage, setConfirmPopup) &&
      validateName(mnameValue, '모듈', setPopupMessage, setConfirmPopup) &&
      validatePromptDetail(promptDetail, setPopupMessage, setConfirmPopup) &&
      validateDescription(description, setPopupMessage, setConfirmPopup)
    )
      return true;
  };
  // 저장
  const onSave = () => {
    console.log(`appliedCount in onSave: ', ${appliedCount}`);
    if (promptModuleId === 'regist' || appliedCount === 0) {
      if (validateValues()) {
        savePromptModule();
      }
    } else {
      onPromptPopupEdit(mnameValue);
    }
  };

  const onCancelPopup = () => {
    if (isModified) onOpenCancelPopup();
    else router.push('/admin/prompt/module');
  };

  // 삭제
  const [openDeletePopup, setOpenDeletePopup] = useState(false);
  const [openCancelPopup, setOpenCancelPopup] = useState(false);

  const onDelete = async () => {
    try {
      const queryString = `delete_targets=${promptModuleId}`;
      const url = `${PROMPT_MODULE}?${queryString}`;
      const response = await axiosUtil.delete(url);
      if (response.data.deletedCount) {
        setToastMessage('삭제되었습니다.');
        onOpenSuccessToast();
        const timer = setTimeout(() => {
          setShouldNavigate(false);
          router.push('/admin/prompt/module');
        }, 500);
      }
    } catch (error) {
      console.error('Error occurred in deleting promptModules');
      handleAxiosError(error);
    }
    setOpenDeletePopup(false);
  };

  useEffect(() => {
    if (openDeletePopup) {
      console.log('add on-pop');
      document.body.classList.add('on-pop');
    } else {
      console.log('remove on-pop');
      document.body.classList.remove('on-pop');
    }
  }, [openDeletePopup]);

  // DeletePopup
  function handleDeleteClick() {
    if (appliedCount !== 0) {
      onPromptPopupDelete(promptModuleId);
    } else {
      setOpenDeletePopup(true);
    }
  }

  function onCloseDeletePopup() {
    setOpenDeletePopup(false);
  }
  function onConfirmDelete() {
    onDelete();
    setOpenDeletePopup(false);
  }

  const onOpenCancelPopup = () => {
    setOpenCancelPopup(true);
  };

  const onCloseCancelPopup = () => {
    setOpenCancelPopup(false);
  };

  // SuccessToast
  const [openSuccessToast, setOpenSuccessToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  function onOpenSuccessToast() {
    setOpenSuccessToast(true);
  }

  function onCloseSuccessToast() {
    setOpenSuccessToast(false);
  }

  useEffect(() => {
    if (promptModuleId !== 'regist') {
      // fetch data from API
      const queryParams = {
        id: promptModuleId,
      };
      const fetchAndSetData = async () => {
        try {
          const response = await axiosUtil.get(PROMPT_MODULE, { params: queryParams });
          if (response.data) {
            const transformedData = {
              ...response.data,
              id: response.data._id,
            };
            console.log('transformed data: ', transformedData);

            setSelectedPromptTypeId(transformedData.promptType?._id ?? '');

            // promptType이 'system'이면 reportType, slideType, slideLayout이 존재하지 않는다.
            setSelectedReportTypeId(transformedData.reportType?._id ?? '');
            setReportTypeValue(transformedData.reportType?.type ?? '');
            setSelectedSlideTypeId(transformedData.slideType?._id ?? '');
            setSlideTypeValue(transformedData.slideType?.type ?? '');
            setSelectedSlideLayoutId(transformedData.slideLayout?._id ?? '');
            setSlideLayoutValue(transformedData.slideLayout?.type ?? '');
            setSelectedModelTypeId(transformedData.gptModelType?._id ?? '');
            setSelectedModelVersionId(transformedData.gptModelVersion?._id ?? '');

            setMcodeValue(transformedData.code ?? '');
            setMnameValue(transformedData.name ?? '');
            setPromptTypeValue(transformedData.promptType?.type ?? '');
            setAppliedCount(transformedData.applied_count ?? '');
            setModelValue(transformedData.gptModelType?.type ?? '');
            setVersionValue(transformedData.gptModelVersion?.type ?? '');
            setPromptDetail(transformedData.prompt ?? '');
            setDescription(transformedData.description ?? '');
            setRegistrantValue(transformedData.creator ?? '');
            // setEmailRegistrantValue(transformedData.email_registrant);
            setDateRegistValue(transformedData.createdAt ?? '');
            setModifierValue(transformedData.modifier ?? '');
            // setEmailModifierValue(transformedData.email_modifier);
            setDateModifyValue(transformedData.updatedAt ?? '');
          } else {
            // TODO show error message
            console.error('Fetch is 200 OK but response.data is empty');
          }
        } catch (error) {
          console.error('Error occurred in fetching ', error);
          handleAxiosError(error);
        }
      };
      fetchAndSetData();
    }
    fetchAndTransform(PROMPT_TYPE, handleAxiosError)
      .then((data) => {
        console.log('data: ', data);
        setFetchedPromptTypeData(data);
      })
      .catch((error) => console.error('Failed to fetch prompt type data:', error));

    fetchAndTransform(REPORT_TYPE, handleAxiosError)
      .then((data) => setFetchedReportTypeData(data))
      .catch((error) => console.error('Failed to fetch report type data:', error));

    fetchAndTransform(GPT_MODEL_TYPE, handleAxiosError)
      .then((data) => setFetchedModelTypeData(data))
      .catch((error) => console.error('Failed to fetch prompt type data:', error));

    fetchAndTransform(GPT_MODEL_VERSION, handleAxiosError)
      .then((data) => setFetchedModelVersionData(data))
      .catch((error) => console.error('Failed to fetch prompt type data:', error));
  }, [promptModuleId]);

  useEffect(() => {
    let newRequiredItems = [
      mcodeValue,
      mnameValue,
      promptTypeValue,
      modelValue,
      versionValue,
      promptDetail,
      reportTypeValue,
      slideTypeValue,
    ];

    if (promptTypeValue === 'system') {
      setFetchedSlideLayoutData([]);
      setSelectedSlideLayoutId(null);
    }
    setRequiredItems(newRequiredItems);
  }, [
    promptTypeValue,
    mcodeValue,
    mnameValue,
    modelValue,
    versionValue,
    promptDetail,
    reportTypeValue,
    slideTypeValue,
  ]);
  const isAllRequiredItems = requiredItems.every(Boolean);

  // Publishing 완료 후 코딩 시작
  // prompt type, report type, slide type, slide layout을 mongoDB에서 읽기
  useEffect(() => {
    if (isFirstRunSlideType.current) {
      isFirstRunSlideType.current = false;
      return;
    }
    fetchAndTransform(SLIDE_TYPE, handleAxiosError, selectedReportTypeId)
      .then((data) => setFetchedSlideTypeData(data))
      .catch((error) => console.error(error));
  }, [selectedReportTypeId]);
  // }, [selectedReportTypeId, triggerFetchSlideType]);

  useEffect(() => {
    if (isFirstRunSlideLayout.current) {
      isFirstRunSlideLayout.current = false;
      return;
    }
    fetchAndTransform(SLIDE_LAYOUT, handleAxiosError, selectedSlideTypeId)
      .then((data) => setFetchedSlideLayoutData(data))
      .catch((error) => console.error(error));
  }, [selectedSlideTypeId]);
  // }, [selectedSlideTypeId, triggerFetchSlideLayout]);

  const handleModelChange = (id, label) => {
    setSelectedModelTypeId(id);
    setModelValue(label);
  };

  const handleVersionChange = (id, label) => {
    setSelectedModelVersionId(id);
    setVersionValue(label);
  };

  return (
    <div className="container">
      <AdminLeft activeLnav={activeLnav} setactiveLnav={setactiveLnav} />
      <main className="main">
        <div className="contents-admin">
          <div className="area-admin">
            {promptModuleId === 'regist' ? <h2>프롬프트 모듈 등록</h2> : <h2>프롬프트 모듈 상세/수정</h2>}
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
                          value={mcodeValue}
                          onChange={(e) => setMcodeValue(e.target.value)}
                          readOnly={promptModuleId !== 'regist'}
                          className="readonly2"
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
                          value={mnameValue}
                          onChange={(e) => {
                            if (promptModuleId !== 'regist') setIsModified(true);
                            setMnameValue(e.target.value);
                          }}
                        ></input>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">모듈 유형</h3>
                      <div className="wrap-select">
                        <select
                          value={promptTypeValue}
                          disabled={appliedCount !== 0}
                          onChange={(e) => {
                            if (promptModuleId !== 'regist') setIsModified(true);
                            const selectedOption = fetchedPromptTypeData.find(
                              (option) => option.label === e.target.value
                            );
                            setSelectedPromptTypeId(selectedOption.id);
                            setPromptTypeValue(selectedOption.label);
                          }}
                        >
                          <option value="" disabled>
                            모듈 유형 선택
                          </option>
                          {Array.isArray(fetchedPromptTypeData) &&
                            fetchedPromptTypeData.map((option) => (
                              <option key={option.id} value={option.label}>
                                {option.label}
                              </option>
                            ))}
                        </select>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">보고서 템플릿 선택</h3>
                      <div className="wrap-select">
                        <select
                          value={reportTypeValue}
                          disabled={appliedCount !== 0}
                          onChange={(e) => {
                            console.log('fetchedReport: ', fetchedReportTypeData);
                            if (promptModuleId !== 'regist') setIsModified(true);
                            const selectedOption = fetchedReportTypeData.find(
                              (option) => option.label === e.target.value
                            );
                            setSelectedReportTypeId(selectedOption.id);
                            setReportTypeValue(selectedOption.label);
                            setSlideTypeValue('');
                            setSlideLayoutValue('');
                          }}
                        >
                          <option value="" disabled>
                            보고서 템플릿 선택
                          </option>
                          {fetchedReportTypeData.map((option) => (
                            <option key={option.id} value={option.label}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">유형 선택</h3>
                      <div className="wrap-select">
                        <select
                          value={slideTypeValue}
                          disabled={appliedCount !== 0 || fetchedSlideTypeData.length === 0}
                          onChange={(e) => {
                            if (promptModuleId !== 'regist') setIsModified(true);
                            const selectedOption = fetchedSlideTypeData.find(
                              (option) => option.label === e.target.value
                            );
                            setSelectedSlideTypeId(selectedOption.id);
                            setSlideTypeValue(selectedOption.label);
                            setSlideLayoutValue('');
                          }}
                        >
                          <option value="" disabled>
                            유형 선택
                          </option>
                          {fetchedSlideTypeData.map((option) => (
                            <option key={option.id} value={option.label}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </li>
                    {promptTypeValue !== '' && promptTypeValue !== 'system' && (
                      <>
                        <li>
                          <h3 className="required">보고서 레이아웃 선택</h3>
                          <div className="wrap-select">
                            <select
                              value={slideLayoutValue}
                              onChange={(e) => {
                                if (promptModuleId !== 'regist') setIsModified(true);
                                const selectedOption = fetchedSlideLayoutData.find(
                                  (option) => option.label === e.target.value
                                );
                                setSelectedSlideLayoutId(selectedOption.id);
                                setSlideLayoutValue(selectedOption.label);
                              }}
                              disabled={appliedCount !== 0 || fetchedSlideLayoutData.length === 0}
                            >
                              <option value="" disabled>
                                보고서 레이아웃 선택
                              </option>
                              {fetchedSlideLayoutData.map((option) => (
                                <option key={option.id} value={option.label}>
                                  {option.label}
                                </option>
                              ))}
                            </select>
                          </div>
                        </li>
                      </>
                    )}
                  </ul>
                </section>
              </div>
              <div className="contents-admin-right">
                <section className="box-t1">
                  <ul className="list-form">
                    <li>
                      <h3 className="required">GPT 모델 유형</h3>
                      <div className="wrap-range gap30">
                        {fetchedModelTypeData
                          .filter(({ id }) => appliedCount === 0 || id === selectedModelTypeId)
                          .map(({ id, label }) => (
                            <label key={id} className="wrap-radio">
                              <input
                                type="radio"
                                name="s1"
                                value={label}
                                checked={selectedModelTypeId === id}
                                onChange={() => {
                                  if (promptModuleId !== 'regist') setIsModified(true);
                                  appliedCount === 0 ? handleModelChange(id, label) : null;
                                }}
                              />
                              <span>{label}</span>
                            </label>
                          ))}
                      </div>
                    </li>
                    <li>
                      <h3 className="required">GPT 모델 버전</h3>
                      <div className="wrap-range gap30">
                        {fetchedModelVersionData
                          .filter(({ id }) => appliedCount === 0 || id === selectedModelVertionId)
                          .map(({ id, label }) => (
                            <label key={id} className="wrap-radio">
                              <input
                                type="radio"
                                name="s2"
                                value={label}
                                checked={selectedModelVertionId === id}
                                onChange={() => {
                                  if (promptModuleId !== 'regist') setIsModified(true);
                                  appliedCount === 0 ? handleVersionChange(id, label) : null;
                                }}
                              />
                              <span>{label}</span>
                            </label>
                          ))}
                      </div>
                    </li>
                    <li>
                      <h3 className="required">프롬프트 내용</h3>
                      <div className="wrap-textarea">
                        <textarea
                          maxLength="50000"
                          rows="7"
                          placeholder="본문 내용을 입력해 주세요."
                          value={promptDetail}
                          onChange={(e) => {
                            if (promptModuleId !== 'regist') setIsModified(true);
                            setPromptDetail(e.target.value);
                          }}
                        ></textarea>
                      </div>
                    </li>
                    <li>
                      <h3>비고</h3>
                      <div className="wrap-textarea">
                        <textarea
                          rows="3"
                          placeholder="비고 내용을 입력해 주세요."
                          defaultValue={description}
                          onChange={(e) => {
                            if (promptModuleId !== 'regist') setIsModified(true);
                            setDescription(e.target.value);
                          }}
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
              <button className="btn-mid secondary" onClick={handleDeleteClick}>
                삭제
              </button>
              <div className="flex-bc gap10">
                <button className="btn-mid primary" onClick={onCancelPopup}>
                  취소
                </button>
                <button className="btn-mid primary" disabled={!isAllRequiredItems} onClick={onSave}>
                  저장
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
      {openCancelPopup && (
        <PopupConfirmAlert
          type={'confirm'}
          message={<>변경사항을 저장하지 않고 이동하시겠습니까?</>}
          onCancel={onCloseCancelPopup}
          onConfirm={() => {
            router.push('/admin/prompt/module');
          }}
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
      {showPopupPromptEdit && (
        <PopupPromptEdit
          onHidePopupPrompt={onHidePopupPrompt}
          name={selectedModule}
          id={promptModuleId}
          errorHandler={handleAxiosError}
        />
      )}
      {showPopupPromptDelete && (
        <PopupPromptDelete
          onHidePopupDelete={onHidePopupDelete}
          module={selectedModule}
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
              router.push('/admin/prompt/module');
            }
          }}
        />
      )}
    </div>
  );
}

// export default withPromptModuleContext(AdminPromptDetail);

```
###### page.js
* ```javascript
'use client';

import Link from 'next/link';
import { useState, useRef, useEffect, useContext } from 'react';
import AdminLeft from '@/app/admin/_components/admin-left';
import PromptSearch from './prompt-search';
import PopupPrompt from './popup-prompt';
import PopupConfirmAlert from '@/app/_components/popup-confirm-alert';
import PopupToast from '@/app/_components/popup-toast';
import axiosUtil from '@/app/_util/axios-util';
import usePopupAndLogout from '@/app/_util/error-popup-logout';
import { PROMPT_MODULE } from '@/config/apiPaths';
// 아래 세 줄은 component 사이에서 데이터를 공유하기 위해 context API를 쓰려고 도입했지만 바로 되지 않아서 기능 구현 먼저 하고 나중에 refactoring할 때 재시도.
import withPromptModuleContext from './prompt-module-hoc';
import { PromptModuleContext } from './prompt-module-context';
import PopupPromptDelete from './popup-prompt-delete';

const AdminPrompt = () => {
  // context API
  // const { promptModuleData, setPromptModuleData } = useContext(PromptModuleContext);
  const [promptModuleData, setPromptModuleData] = useState([]);
  // board
  const [checkAll, setCheckAll] = useState(false);
  const [sortField, setSortField] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');

  useEffect(() => {
    const isAllChecked = promptModuleData.every((item) => item.isChecked);
    setCheckAll(isAllChecked);
  }, [promptModuleData]);

  // 전체 선택/해제 함수
  const onCheckAll = () => {
    const updatedCheckboxData = promptModuleData.map((item) => ({
      ...item,
      isChecked: !checkAll,
    }));
    setPromptModuleData(updatedCheckboxData);
    setCheckAll(!checkAll);

    // '전체 선택'에 'some' 클래스가 추가된 경우
    if (promptModuleData.some((item) => item.isChecked)) {
      setCheckAll(true);
      const updatedCheckboxData = promptModuleData.map((item) => ({
        ...item,
        isChecked: false,
      }));
      setPromptModuleData(updatedCheckboxData);
    }
  };

  // 개별 체크박스 변경 핸들러
  const onCheck = (id) => {
    const updatedCheckboxData = promptModuleData.map((item) => {
      if (item.id === id) {
        return {
          ...item,
          isChecked: !item.isChecked,
        };
      }
      return item;
    });
    setPromptModuleData(updatedCheckboxData);
  };

  // 정렬
  const onSort = (field) => {
    let direction = 'asc';
    if (sortField === field) {
      direction = sortDirection === 'asc' ? 'desc' : 'asc';
    }
    let updatedCheckboxData = [];
    updatedCheckboxData = [...promptModuleData].sort((a, b) => {
      let aValue, bValue;
      if (field === 'promptType' || field === 'gptModelType' || field === 'gptModelVersion') {
        aValue = (a[field][0] && a[field][0].type) || '';
        bValue = (b[field][0] && b[field][0].type) || '';
      } else {
        aValue = a[field];
        bValue = b[field];
      }

      if (aValue < bValue) return direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return direction === 'asc' ? 1 : -1;
      return 0;
    });

    setPromptModuleData(updatedCheckboxData);
    setSortField(field);
    setSortDirection(direction);
  };

  // 체크된 항목 유무 판단
  const isAnyChecked = promptModuleData.some((item) => item.isChecked);

  // 선택 삭제 함수
  const onDelete = async () => {
    const modulesToDelete = promptModuleData.filter((item) => item.isChecked).map((item) => item._id);

    if (modulesToDelete.length > 0) {
      try {
        const queryString = modulesToDelete.map((id) => `delete_targets=${id}`).join('&');
        const url = `${PROMPT_MODULE}?${queryString}`;
        const response = await axiosUtil.delete(url);
        if (response.data.deletedCount) {
          setToastMessage('삭제되었습니다.');
          onOpenSuccessToast();
        }
        const updatedCheckboxData = promptModuleData.filter((item) => !item.isChecked);
        setPromptModuleData(updatedCheckboxData);
      } catch (error) {
        console.error('Error occurred in deleting promptModules');
        handleAxiosError(error);
      }
    }
  };
  // 단일 삭제 함수
  const onDeleteSingle = (id) => {
    const updatedCheckboxData = promptModuleData.filter((item) => item.id !== id);
    console.log('single updatedCheckboxData: ', updatedCheckboxData);
    setPromptModuleData(updatedCheckboxData);
  };

  // 페이징 관련 상태
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecordCount, setTotalRecordCount] = useState(0);

  // 페이지 이동 함수
  const goToNextPage = () => {
    setCurrentPage(currentPage + 1);
  };
  const goToPreviousPage = () => {
    setCurrentPage(currentPage - 1);
  };
  const goToFirstPage = () => {
    setCurrentPage(1);
  };
  const goToLastPage = () => {
    const totalPages = Math.ceil(totalRecordCount / itemsPerPage);
    setCurrentPage(totalPages);
  };

  // 특정 페이지로 이동하는 함수
  const goToPage = (number) => {
    setCurrentPage(number);
  };

  // 한 페이지에 표시될 아이템 수 변경 함수
  const onPagingChange = (e) => {
    setItemsPerPage(parseInt(e.target.value));
  };

  // 적용프롬프트 팝업
  const [showPopupPrompt, setShowPopupPrompt] = useState(false);
  // const [showPopupPromptDelete, setShowPopupPromptDelete] = useState(false);
  const [selectedModule, setSelectedModule] = useState(null);
  const onPromptPopup = (item) => {
    setSelectedModule(item);
    setShowPopupPrompt(true);
  };
  function onHidePopupPrompt() {
    setShowPopupPrompt(false);
    // 여기 목록화면에서는 안 쓰는 것 같아서 일단 막음
    // setShowPopupPromptDelete(false);
  }

  // ErrorPopup
  const [openErrorPopup, setOpenErrorPopup] = useState(false);
  function onOpenErrorPopup() {
    setOpenErrorPopup(true);
  }
  function onCloseErrorPopup() {
    setOpenErrorPopup(false);
  }

  // DeletePopup
  function handleDeleteClick() {
    const mustNotDelete = promptModuleData.filter((item) => item.isChecked).some((item) => item.applied_count !== 0);
    if (mustNotDelete) {
      setPopupMessage(<>적용된 메가 프롬프트가 없는 모듈만 삭제할 수 있습니다.</>);
      setConfirmPopup(true);
    } else {
      setOpenDeletePopup(true);
    }
  }

  const [openDeletePopup, setOpenDeletePopup] = useState(false);
  function onCloseDeletePopup() {
    setOpenDeletePopup(false);
  }
  function onDeletePopup() {
    onDelete();
    setOpenDeletePopup(false);
  }

  // SuccessToast
  const [openSuccessToast, setOpenSuccessToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  function onOpenSuccessToast() {
    setOpenSuccessToast(true);
  }
  function onCloseSuccessToast() {
    setOpenSuccessToast(false);
  }

  const [activeLnav, setactiveLnav] = useState(21);

  // Publishing 작업 후 코딩 부분 시작
  const { confirmPopup, setConfirmPopup, popupMessage, setPopupMessage, handlePopupMessage, handleAxiosError } =
    usePopupAndLogout();
  const [searchParams, setSearchParams] = useState({});

  const handleSearch = (NewSearchParams) => {
    setSearchParams(NewSearchParams);
  };

  useEffect(() => {
    const queryParams = {
      ...searchParams,
      page: currentPage,
      limit: itemsPerPage,
    };

    // fetch data from API
    const fetchData = async () => {
      try {
        const response = await axiosUtil.get(PROMPT_MODULE, { params: queryParams });
        const transformedData = response.data.promptModules.map((module) => ({
          ...module,
          id: module._id,
          isChecked: false,
        }));
        setTotalRecordCount(response.data.totalRecords);
        setPromptModuleData(transformedData);
      } catch (error) {
        console.error('Error occurred in fetching ', error);
        handleAxiosError(error);
      }
    };
    fetchData();
  }, [currentPage, itemsPerPage, searchParams]);

  return (
    <div className="container">
      <AdminLeft activeLnav={activeLnav} setactiveLnav={setactiveLnav} />
      <main className="main">
        <div className="contents-admin">
          <div className="area-admin">
            <h2>프롬프트 모듈 관리</h2>
            <section className="box-t1">
              <PromptSearch onSearch={handleSearch} />
            </section>
            <section className="box-t1">
              <div className="flex-bc">
                <div className="wrap-btn al">
                  <span>선택된 항목을 : </span>
                  <button className={openDeletePopup ? 'btn-mid on' : 'btn-mid'} onClick={handleDeleteClick}>
                    삭제
                  </button>
                </div>
                <div className="wrap-btn">
                  <Link href="/admin/prompt/module/regist" className="btn-mid regist">
                    신규 등록
                  </Link>
                </div>
              </div>

              {!promptModuleData.length > 0 && (
                <div className="no-data">
                  <p>검색 결과가 없습니다.</p>
                </div>
              )}
              {promptModuleData.length > 0 && (
                <>
                  <table className="tbl-row hover">
                    <thead>
                      <tr>
                        <th>
                          <label className="wrap-checkbox">
                            <input type="checkbox" checked={checkAll} onChange={onCheckAll} />
                            <span className={promptModuleData.some((item) => item.isChecked) ? 'some' : ''}></span>
                          </label>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('code')}>
                            모듈 코드
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('name')}>
                            모듈 이름
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('promptType')}>
                            유형
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('applied_count')}>
                            적용 프롬프트
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('gptModelType')}>
                            GPT 모델
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('gptModelVersion')}>
                            GPT 버전
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('updatedAt')}>
                            마지막 수정일시
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('modifier')}>
                            마지막 수정자
                          </button>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {promptModuleData.map((item) => (
                        <tr key={item.id} className={item.isChecked ? 'on' : ''}>
                          <td>
                            <span className="wrap-checkbox">
                              <input
                                type="checkbox"
                                name="ref"
                                id={item.id}
                                checked={item.isChecked}
                                onChange={() => onCheck(item.id)}
                              />
                              <span></span>
                            </span>
                          </td>
                          <td className="w300">
                            <Link href={`/admin/prompt/module/${item.id}`} className="elipsis link" title={item.code}>
                              {item.code}
                            </Link>
                          </td>
                          <td className="w300">
                            <span title={item.name} className="elipsis">
                              {item.name}
                            </span>
                          </td>
                          <td>
                            <span>{item.promptType.length > 0 ? item.promptType[0].type : ''}</span>
                          </td>
                          <td>
                            <button onClick={() => onPromptPopup(item)} className="link">
                              {item.applied_count}
                            </button>
                          </td>
                          <td>
                            <span>{item.gptModelType.length > 0 ? item.gptModelType[0].type : ''}</span>
                          </td>
                          <td>
                            <span>{item.gptModelVersion.length > 0 ? item.gptModelVersion[0].type : ''}</span>
                          </td>
                          <td>
                            <span>{item.updatedAt}</span>
                          </td>
                          <td>
                            <span>{item.modifier ? item.modifier : item.creator}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              )}
              <div className="tbl-btm">
                <div className="exp">총 {totalRecordCount}개</div>
                <div className="list-paging">
                  <button
                    className="btn-first"
                    title="첫페이지로"
                    disabled={currentPage === 1}
                    onClick={goToFirstPage}
                  ></button>
                  <button
                    className="btn-prev"
                    title="이전"
                    disabled={currentPage === 1}
                    onClick={goToPreviousPage}
                  ></button>
                  <ul className="list-num">
                    {Array.from(
                      {
                        length: Math.min(10, Math.ceil(totalRecordCount / itemsPerPage)),
                      },
                      (_, index) => {
                        const pageIndex = Math.floor((currentPage - 1) / 10) * 10 + index + 1;
                        return (
                          <li key={index}>
                            <button
                              className={currentPage === pageIndex ? 'on' : ''}
                              onClick={() => goToPage(pageIndex)}
                            >
                              {pageIndex}
                            </button>
                          </li>
                        );
                      }
                    )}
                  </ul>
                  <button
                    className="btn-next"
                    title="다음"
                    disabled={currentPage === Math.ceil(totalRecordCount / itemsPerPage)}
                    onClick={goToNextPage}
                  ></button>
                  <button
                    className="btn-last"
                    title="마지막페이지로"
                    disabled={currentPage === Math.ceil(totalRecordCount / itemsPerPage)}
                    onClick={goToLastPage}
                  ></button>
                </div>
                <div>
                  <div className="wrap-select mw100">
                    <select onChange={onPagingChange}>
                      <option>5</option>
                      <option>10</option>
                      <option>20</option>
                      <option>100</option>
                    </select>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
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
          onConfirm={onDeletePopup}
        />
      )}
      {showPopupPrompt && (
        <PopupPrompt onHidePopupPrompt={onHidePopupPrompt} module={selectedModule} errorHandler={handleAxiosError} />
      )}
      {/* {showPopupPromptDelete && <PopupPromptDelete onHidePopupPrompt={onHidePopupDelete} module={selectedModule} />} */}
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
};

export default withPromptModuleContext(AdminPrompt);

```
###### popup-prompt-delete.js
* ```javascript
import axiosUtil from '@/app/_util/axios-util';
import { MEGA_PROMPT_MODULE } from '@/config/apiPaths';
import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function PopupPromptDelete({ onHidePopupDelete, module, errorHandler }) {
  const [megaPromptList, setMegaPromptList] = useState([]);

  useEffect(() => {
    const queryParams = {
      action: 'promptModule_applied',
      id: module,
    };
    const fetchAppliedMegaPrompt = async () => {
      try {
        const response = await axiosUtil.get(MEGA_PROMPT_MODULE, { params: queryParams });
        if (response.data && Array.isArray(response.data)) {
          const transformedData = response.data.map((item) => ({
            ...item,
            id: item._id,
          }));
          setMegaPromptList(transformedData);
        } else {
          // TODO show error message
          console.error('Fetch is 200 OK but response.data is empty');
        }
      } catch (error) {
        console.error('Error occurred in fetching ', error);
        errorHandler(error);
      }
    };
    fetchAppliedMegaPrompt();
  }, module);

  return (
    <aside className="popup center">
      <div className="dimmed"></div>
      <div className="pop-content admin">
        <div className="mb-10">
          <div className="tit">프롬프트 모듈 삭제</div>
          <div className="tit-exp">
            이 모듈은 다음 메가 프롬프트에서 사용하고 있습니다.
            <br />
            적용된 메가 프롬프트가 없는 모듈만 삭제할 수 있습니다.
          </div>
        </div>
        <div className="wrap-body">
          <div className="box-border h480">
            <ul className="list-dot li-mt12">
              {megaPromptList.map((item, index) => (
                <li key={index}>
                  <Link href={`/admin/prompt/mega/${item.id}`} target="_blank" className="link">
                    {item.code}
                  </Link>
                </li>
              ))}
              {/*               <li>
                <Link href="" target="_blank" className="link">
                  rep-int-cont-contents_1x2_message
                </Link>
              </li>
              <li>
                <Link href="" target="_blank" className="link">
                  rep-int-cont-progress_2x2_message
                </Link>
              </li>
  */}{' '}
            </ul>
          </div>
        </div>
        <div className="wrap-btn">
          <button onClick={onHidePopupDelete}>확인</button>
        </div>
      </div>
    </aside>
  );
}

```
###### popup-prompt-edit.js
* ```javascript
import axiosUtil from '@/app/_util/axios-util';
import { MEGA_PROMPT_MODULE } from '@/config/apiPaths';
import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function PopupPromptEdit({ onHidePopupPrompt, name, id, errorHandler }) {
  const [megaPromptList, setMegaPromptList] = useState([]);

  useEffect(() => {
    const queryParams = {
      action: 'promptModule_applied',
      id: id,
    };
    const fetchAppliedMegaPrompt = async () => {
      try {
        const response = await axiosUtil.get(MEGA_PROMPT_MODULE, { params: queryParams });
        if (response.data && Array.isArray(response.data)) {
          const transformedData = response.data.map((item) => ({
            ...item,
            id: item._id,
          }));
          setMegaPromptList(transformedData);
        } else {
          // TODO show error message
          console.error('Fetch is 200 OK but response.data is empty');
        }
      } catch (error) {
        console.error('Error occurred in fetching ', error);
        errorHandler(error);
      }
    };
    fetchAppliedMegaPrompt();
  }, name);

  return (
    <aside className="popup center">
      <div className="dimmed"></div>
      <div className="pop-content admin">
        <div className="mb-10">
          <div className="tit">프롬프트 모듈 수정</div>
          <div className="tit-exp">
            {name}을/를 수정하시겠습니까? 수정하는 경우, 다음 메가 프롬프트가 변경됩니다.
            <br />
            수정된 내용은 복원할 수 없습니다.
          </div>
        </div>
        <div className="wrap-body">
          <div className="box-border h480">
            <ul className="list-dot li-mt12">
              {megaPromptList.map((item, index) => (
                <li key={index}>
                  <Link href={`/admin/prompt/mega/${item.id}`} target="_blank" className="link">
                    {item.code}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="wrap-btn">
          <button onClick={() => onHidePopupPrompt(false)}>취소</button>
          <button onClick={() => onHidePopupPrompt(true)}>수정</button>
        </div>
      </div>
    </aside>
  );
}

```
###### popup-prompt.js
* ```javascript
import { MEGA_PROMPT_MODULE } from '@/config/apiPaths';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import axiosUtil from '@/app/_util/axios-util';

export default function PopupPrompt({ onHidePopupPrompt, module, errorHandler }) {
  const [megaPromptList, setMegaPromptList] = useState([]);

  useEffect(() => {
    const queryParams = {
      action: 'promptModule_applied',
      id: module.id,
    };

    const fetchAppliedMegaPrompt = async () => {
      try {
        const response = await axiosUtil.get(MEGA_PROMPT_MODULE, { params: queryParams });
        console.log('response: ', response);
        if (response.data && Array.isArray(response.data)) {
          const transformedData = response.data.map((item) => ({
            ...item,
            id: item._id,
          }));
          // const transformedMegaPromptCode = response.data.map((item) => item.code).join('\n');
          setMegaPromptList(transformedData);
        } else {
          // TODO show error message
          console.error('Fetch is 200k OK but response.data is empty');
        }
      } catch (error) {
        console.error('Error occurred in fetching ', error);
        errorHandler(error);
      }
    };
    fetchAppliedMegaPrompt();
  }, [module]);

  return (
    <aside className="popup center">
      <div className="dimmed"></div>
      <div className="pop-content admin">
        <div className="mb-10">
          <div className="tit">
            <span className="elipsis-8" title={module.name}>
              {module.name}
            </span>
            모듈이 적용된 메가 프롬프트
          </div>
          <div className="tit-exp">
            {module.name} 모듈이 적용된 메가 프롬프트에서 제외하기 위해서는 해당 메가 프롬프트의 수정 화면에서 모듈을
            제거해 주세요.
          </div>
        </div>
        <div className="wrap-body">
          <div className="box-border h480">
            <ul className="list-dot li-mt12">
              {megaPromptList.map((item, index) => (
                <li key={index}>
                  <Link href={`/admin/prompt/mega/${item.id}`} target="_blank" className="link">
                    {item.code}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="wrap-btn">
          <button onClick={onHidePopupPrompt}>취소</button>
          <button onClick={onHidePopupPrompt}>닫기</button>
        </div>
      </div>
    </aside>
  );
}

```
###### prompt-search.js
* ```javascript
import { useState, useEffect } from 'react';
import MultiSelect from '@/app/_components/multi-select';
import { fetchAndTransform } from '@/app/_util/prompt-management';
import { promptTypeData, gptTypeData, gptVersionData } from '@/app/admin/_components/temp-data';
import { PROMPT_TYPE, GPT_MODEL_TYPE, GPT_MODEL_VERSION } from '@/config/apiPaths';
import usePopupAndLogout from '@/app/_util/error-popup-logout';

export default function PromptSearch({ onSearch }) {
  // 검색
  const [searchCriteriaValue, setSearchCriteriaValue] = useState('');
  const [searchCriteriaName, setSearchCriteriaName] = useState('');
  const [searchValue, setSearchValue] = useState('');
  // MultiSelectSearch에 필요
  const [searchPromptTypeValue, setSearchPromptTypeValue] = useState([]);
  const [searchGptTypeValue, setSearchGptTypeValue] = useState([]);
  const [searchGptVersionValue, setSearchGptVersionValue] = useState([]);
  const [resetFlag, setResetFlag] = useState(false);
  const [fetchedPromptTypeData, setFetchedPromptTypeData] = useState([]);
  const [fetchedModelTypeData, setFetchedModelTypeData] = useState([]);
  const [fetchedModelVersionData, setFetchedModelVersionData] = useState([]);
  const { handleAxiosError } = usePopupAndLogout();

  const handleSearchCriteriaChange = (event) => {
    const selectedOption = event.target.value;
    setSearchCriteriaName(selectedOption);
    const mappedValue = criteriaValueMapping[selectedOption];
    console.log('mappedValue:', mappedValue);
    setSearchCriteriaValue(mappedValue);
  };

  useEffect(() => {
    fetchAndTransform(PROMPT_TYPE, handleAxiosError)
      .then((data) => {
        setFetchedPromptTypeData(data);
      })
      .catch((error) => console.error('Failed to fetch prompt type data:', error));

    fetchAndTransform(GPT_MODEL_TYPE, handleAxiosError)
      .then((data) => {
        setFetchedModelTypeData(data);
      })
      .catch((error) => console.error('Failed to fetch prompt type data:', error));

    fetchAndTransform(GPT_MODEL_VERSION, handleAxiosError)
      .then((data) => {
        setFetchedModelVersionData(data);
      })
      .catch((error) => console.error('Failed to fetch prompt type data:', error));
  }, []);

  // 초기화 함수
  const onReset = () => {
    setSearchCriteriaValue('');
    setSearchValue('');
    // MultiSelectSearch에 필요
    setSearchPromptTypeValue('');
    setSearchGptTypeValue('');
    setSearchGptVersionValue('');
    setResetFlag(true);
  };

  // Publishing 후 코딩 시작
  const criteriaValueMapping = {
    '모듈 코드': 'code',
    '모듈 이름': 'name',
    '마지막 수정자': 'modifier',
  };

  const handleSearchClick = () => {
    console.log('handleSearchClick start');
    const getSelectedIds = (selectedValues, fetchedData) => {
      console.log('selectedValue: ', selectedValues);
      console.log('fetchedData: ', fetchedData);
      return fetchedData
        .filter((item) => selectedValues.includes(item.label))
        .map((item) => {
          console.log('found item: ', item.id);
          return item.id;
        });
    };

    const searchParams = {
      ...(searchCriteriaValue ? { [searchCriteriaValue]: searchValue } : {}),
      ...(searchPromptTypeValue ? { promptType: getSelectedIds(searchPromptTypeValue, fetchedPromptTypeData) } : {}),
      ...(searchGptTypeValue ? { gptModelType: getSelectedIds(searchGptTypeValue, fetchedModelTypeData) } : {}),
      ...(searchGptVersionValue
        ? { gptModelVersion: getSelectedIds(searchGptVersionValue, fetchedModelVersionData) }
        : {}),
    };
    onSearch(searchParams);
    setResetFlag(false);
  };

  // 아래 MultiSelectData는 asynchronous state update 관련해서 데이터를 제대로 보여주지 못하는 문제가 있어서 key={data.length}를 꼭 넣어줘야 함.
  return (
    <div className="wrap-search">
      <div className="mw260">
        <MultiSelect
          key={fetchedPromptTypeData.length}
          multiSelectData={fetchedPromptTypeData}
          multiSelectValue={searchPromptTypeValue}
          setMultiSelectValue={setSearchPromptTypeValue}
          resetAll={onReset}
          resetFlag={resetFlag}
          placeholder="유형"
        />
      </div>
      <div className="mw260">
        <MultiSelect
          key={fetchedModelTypeData.length}
          multiSelectData={fetchedModelTypeData}
          multiSelectValue={searchGptTypeValue}
          setMultiSelectValue={setSearchGptTypeValue}
          resetAll={onReset}
          resetFlag={resetFlag}
          placeholder="GPT 모델 유형"
        />
      </div>
      <div className="mw260">
        <MultiSelect
          key={fetchedModelVersionData.length}
          multiSelectData={fetchedModelVersionData}
          multiSelectValue={searchGptVersionValue}
          setMultiSelectValue={setSearchGptVersionValue}
          resetAll={onReset}
          resetFlag={resetFlag}
          placeholder="GPT 모델 버전"
        />
      </div>
      <div className="wrap-select mw180">
        <select value={searchCriteriaName} onChange={handleSearchCriteriaChange}>
          <option>검색 조건 선택</option>
          <option>모듈 코드</option>
          <option>모듈 이름</option>
          <option>마지막 수정자</option>
        </select>
      </div>
      <div className="wrap-input flex-1">
        <input
          type="search"
          placeholder="검색어를 입력해 주세요."
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
        />
      </div>
      <button className="btn-mid" onClick={handleSearchClick}>
        조회
      </button>
      <button className="btn-small reset" onClick={onReset}>
        초기화
      </button>
    </div>
  );
}

```
###### mega (메가 프롬프트 관리 화면)
###### [id]
###### page.js
* ```javascript
'use client';

import Link from 'next/link';
// import Image from "next/image"
import { useState, useRef, useEffect } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import AdminLeft from '@/app/admin/_components/admin-left';
import PopupModule from '../popup-module';
import PopupConfirmAlert from '@/app/_components/popup-confirm-alert';
import PopupToast from '@/app/_components/popup-toast';
import {
  MEGA_TYPE,
  REPORT_TYPE,
  SLIDE_TYPE,
  SLIDE_LAYOUT,
  GPT_MODEL_TYPE,
  GPT_MODEL_VERSION,
  MEGA_PROMPT_MODULE,
} from '@/config/apiPaths';
import usePopupAndLogout from '@/app/_util/error-popup-logout';
import axiosUtil from '@/app/_util/axios-util';
import { useSelector } from 'react-redux';
import { fetchAndTransform, validateCode, validateName, validateDescription } from '@/app/_util/prompt-management';

export default function AdminMegaDetail() {
  const { confirmPopup, setConfirmPopup, popupMessage, setPopupMessage, handleAxiosError } = usePopupAndLogout();
  const { userInfo } = useSelector((state) => state.auth);

  const pathname = usePathname();
  const megaPromptId = pathname.substring(pathname.lastIndexOf('/') + 1);
  const router = useRouter();
  const isFirstRunSlideType = useRef(true);
  const isFirstRunSlideLayout = useRef(true);

  const [activeLnav, setactiveLnav] = useState(22);

  const [megaTypeValue, setMegaTypeValue] = useState('');
  const [divideValue, setDivideValue] = useState('');
  const [mcodeValue, setMcodeValue] = useState('');
  const [mnameValue, setMnameValue] = useState('');
  const [reportTypeValue, setReportTypeValue] = useState('');
  const [slideTypeValue, setSlideTypeValue] = useState('');
  const [slideLayoutValue, setSlideLayoutValue] = useState('');
  const [modelValue, setModelValue] = useState('');
  const [versionValue, setVersionValue] = useState('');
  const [promptContentScreen, setPromptContentScreen] = useState('');
  const [promptContentDB, setPromptContentDB] = useState([]);
  const [originalPromptContentDB, setrOriginalPromptContentDB] = useState([]);
  const [changedPromptContent, setPromptContentChanged] = useState([]);
  const [description, setDescription] = useState('');
  const [registrantValue, setRegistrantValue] = useState('');
  const [emailRegistrantValue, setEmailRegistrantValue] = useState('');
  const [dateRegistValue, setDateRegistValue] = useState('');
  const [modifierValue, setModifierValue] = useState('');
  const [emailModifierValue, setEmailModifierValue] = useState('');
  const [dateModifyValue, setDateModifyValue] = useState('');
  const [fetchedMegaTypeData, setFetchedMegaTypeData] = useState([]);
  const [fetchedReportTypeData, setFetchedReportTypeData] = useState([]);
  const [fetchedSlideTypeData, setFetchedSlideTypeData] = useState([]);
  const [fetchedSlideLayoutData, setFetchedSlideLayoutData] = useState([]);
  const [fetchedModelTypeData, setFetchedModelTypeData] = useState([]);
  const [fetchedModelVersionData, setFetchedModelVersionData] = useState([]);
  const [requiredItems, setRequiredItems] = useState([]);
  const [triggerFetchSlideType, setTriggerFetchSlideType] = useState(false);
  const [triggerFetchSlideLayout, setTriggerFetchSlideLayout] = useState(false);
  const [selectedMegaTypeId, setSelectedMegaTypeId] = useState(null);
  const [selectedReportTypeId, setSelectedReportTypeId] = useState(null);
  const [selectedSlideTypeId, setSelectedSlideTypeId] = useState(null);
  const [selectedSlideLayoutId, setSelectedSlideLayoutId] = useState(null);
  const [selectedModelTypeId, setSelectedModelTypeId] = useState(null);
  const [selectedModelVersionId, setSelectedModelVersionId] = useState(null);
  const [searchParams, setSearchParams] = useState({});
  const [shouldNavigate, setShouldNavigate] = useState(false);
  const [inputAlertPopup, setInputAlertPopup] = useState(false);
  const [openCancelPopup, setOpenCancelPopup] = useState(false);
  const [isModified, setIsModified] = useState(false);

  // 적용프롬프트 팝업
  const [showPopupModule, setShowPopupModule] = useState(false);
  const onShowPopupModule = () => {
    if (megaTypeValue === '보고서' && (reportTypeValue === '' || slideTypeValue === '')) {
      setPopupMessage('먼저 보고서 템플릿, 유형을 선태해 주세요.');
      setInputAlertPopup(true);
      return;
    }

    if (modelValue === '' || versionValue === '') {
      setPopupMessage('먼저 GPT 모델 유형과 버전을 선태해 주세요.');
      setInputAlertPopup(true);
      return;
    }

    let queryConditions = {};
    if (megaTypeValue === '보고서') {
      queryConditions = {
        action: 'popup',
        ...(selectedReportTypeId !== null && { reportType: selectedReportTypeId }),
        ...(selectedSlideTypeId !== null && { slideType: selectedSlideTypeId }),
        ...(selectedSlideLayoutId !== null && { slideLayout: selectedSlideLayoutId }),
        ...(selectedModelTypeId !== null && { gptModelType: selectedModelTypeId }),
        ...(selectedModelVersionId !== null && { gptModelVersion: selectedModelVersionId }),
      };
    } else {
      queryConditions = {
        action: 'popup',
        ...(selectedModelTypeId !== null && { gptModelType: selectedModelTypeId }),
        ...(selectedModelVersionId !== null && { gptModelVersion: selectedModelVersionId }),
      };
    }
    setSearchParams(queryConditions);
    setShowPopupModule(true);
  };

  const detectChanges = (original, changed) => {
    if (changed) {
      const changes = [];
      const originalIds = new Set(original.map((item) => item._id));
      const changedIds = new Set(changed.map((item) => item._id));

      // Detect deleted Items
      original.forEach((item) => {
        if (!changedIds.has(item._id)) changes.push({ change: -1, _id: item._id });
      });

      // Detect added Items
      changed.forEach((item) => {
        if (!originalIds.has(item._id)) changes.push({ change: 1, _id: item._id });
      });

      return changes;
    }
    return [];
  };

  function onHidePopupModule(promptContentScreen = '', finalPromptContentDB = '') {
    setPromptContentScreen(promptContentScreen);
    console.log('finalPromptContent onHidePopupModule: ', finalPromptContentDB);
    const result = detectChanges(originalPromptContentDB, finalPromptContentDB);
    console.log('result of detect: ', result);
    if (result.length > 0) {
      setPromptContentChanged(result);
      setPromptContentDB(finalPromptContentDB);
    }
    setShowPopupModule(false);
  }

  const validateValues = () => {
    if (
      validateCode(mcodeValue, '메가 프롬프트', setPopupMessage, setConfirmPopup) &&
      validateName(mnameValue, '메가 프롬프트', setPopupMessage, setConfirmPopup) &&
      validateDescription(description, setPopupMessage, setConfirmPopup)
    )
      return true;
  };
  // 저장
  const onSave = () => {
    if (validateValues()) {
      const updateMegaPromptData = {
        ...(megaPromptId !== 'regist' ? { _id: megaPromptId } : {}),
        code: mcodeValue,
        name: mnameValue,
        megaType: selectedMegaTypeId,
        ...(selectedReportTypeId ? { reportType: selectedReportTypeId } : {}),
        ...(selectedSlideTypeId ? { slideType: selectedSlideTypeId } : {}),
        ...(selectedSlideLayoutId ? { slideLayout: selectedSlideLayoutId } : {}),
        gptModelType: selectedModelTypeId,
        gptModelVersion: selectedModelVersionId,
        promptContent: promptContentDB,
        description: description,
        ...(megaPromptId === 'regist' ? { creator: userInfo.username } : {}),
        modifier: userInfo.username,
        changedPromptContent: changedPromptContent,
        megaTypeValue: megaTypeValue,
      };
      console.log('updateMegaPromptData:', updateMegaPromptData);

      const putData = async () => {
        try {
          if (megaPromptId === 'regist') {
            const response = await axiosUtil.post(MEGA_PROMPT_MODULE, updateMegaPromptData);
            setToastMessage('저장되었습니다.');
          } else {
            const response = await axiosUtil.put(MEGA_PROMPT_MODULE, updateMegaPromptData);
            setToastMessage('정보가 수정되었습니다.');
          }
          onOpenSuccessToast();
          const timer = setTimeout(() => {
            router.push('/admin/prompt/mega');
          }, 500);
        } catch (error) {
          console.error('Error occured in updating ', error);
          handleAxiosError(error);
        }
      };
      putData();
    }
  };

  const onCancelPopup = () => {
    if (mcodeValue !== '' || mnameValue !== '' || promptContentScreen !== '') {
      onOpenCancelPopup();
    }
  };

  // 삭제
  const [openDeletePopup, setOpenDeletePopup] = useState(false);

  // DeletePopup
  function onOpenDeletePopup() {
    setOpenDeletePopup(true);
  }
  function onCloseDeletePopup() {
    setOpenDeletePopup(false);
  }

  const onOpenCancelPopup = () => {
    setOpenCancelPopup(true);
  };

  const onCloseCancelPopup = () => {
    setOpenCancelPopup(false);
  };

  function onConfirmDelete() {
    onDelete();
    setOpenDeletePopup(false);
  }

  const onDelete = async () => {
    try {
      const queryString = `delete_targets=${megaPromptId}`;
      const url = `${MEGA_PROMPT_MODULE}?${queryString}`;
      const response = await axiosUtil.delete(url);
      console.log('response after delete: ', response);
      if (response.data.deletedCount) {
        console.log('load popup here');
        setToastMessage('삭제되었습니다.');
        onOpenSuccessToast();
        const timer = setTimeout(() => {
          setShouldNavigate(false);
          router.push('/admin/prompt/mega');
        }, 500);
      }
    } catch (error) {
      console.error('Error occurred in deleting megaPrompt');
      handleAxiosError(error);
    }
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
    setOpenSuccessToast(true);
  }
  function onCloseSuccessToast() {
    setOpenSuccessToast(false);
  }

  useEffect(() => {
    if (megaPromptId !== 'regist') {
      const queryParams = {
        id: megaPromptId,
      };
      const fetchAndSetData = async () => {
        try {
          const response = await axiosUtil.get(MEGA_PROMPT_MODULE, { params: queryParams });
          if (response.data) {
            const transformedData = {
              ...response.data,
              id: response.data._id,
            };
            console.log('transformed data: ', transformedData);
            setSelectedMegaTypeId(transformedData.megaType?._id);

            // promptType이 'system'이면 reportType, slideType, slideLayout이 존재하지 않는다.
            setSelectedReportTypeId(transformedData.reportType?._id ?? '');
            setReportTypeValue(transformedData.reportType?.type ?? '');
            setSelectedSlideTypeId(transformedData.slideType?._id ?? '');
            setSlideTypeValue(transformedData.slideType?.type ?? '');
            setSelectedSlideLayoutId(transformedData.slideLayout?._id ?? '');
            setSlideLayoutValue(transformedData.slideLayout?.type ?? '');
            setSelectedModelTypeId(transformedData.gptModelType?._id ?? '');
            setSelectedModelVersionId(transformedData.gptModelVersion?._id ?? '');

            setMcodeValue(transformedData.code ?? '');
            setMnameValue(transformedData.name ?? '');
            setMegaTypeValue(transformedData.megaType?.type ?? '');
            setModelValue(transformedData.gptModelType?.type ?? '');
            setVersionValue(transformedData.gptModelVersion?.type ?? '');

            const transformedPromptContent = transformedData.promptContent.map((item) => item.code).join('\n');
            console.log('transformedPromptContent: ', transformedPromptContent);
            console.log('PromptContentDBFormat: ', transformedData.promptContent);

            setPromptContentScreen(transformedPromptContent ?? []);
            setPromptContentDB(transformedData.promptContent ?? []);
            setrOriginalPromptContentDB(transformedData.promptContent ?? []);
            setDescription(transformedData.description ?? '');
            setRegistrantValue(transformedData.creator ?? '');
            // setEmailRegistrantValue(transformedData.email_registrant);
            setDateRegistValue(transformedData.createdAt ?? '');
            setModifierValue(transformedData.modifier ?? '');
            // setEmailModifierValue(transformedData.email_modifier);
            setDateModifyValue(transformedData.updatedAt ?? '');
          } else {
            // TODO show error message
            console.error('Fetch is 200 OK but response.data is empty');
          }
        } catch (error) {
          console.error('Error occurred in fetching ', error);
          handleAxiosError(error);
        }
      };
      fetchAndSetData();
    }
    fetchAndTransform(MEGA_TYPE, handleAxiosError)
      .then((data) => {
        console.log('data: ', data);
        setFetchedMegaTypeData(data);
      })
      .catch((error) => console.error('Failed to fetch mega type data:', error));

    fetchAndTransform(REPORT_TYPE, handleAxiosError)
      .then((data) => setFetchedReportTypeData(data))
      .catch((error) => console.error('Failed to fetch report type data:', error));

    fetchAndTransform(GPT_MODEL_TYPE, handleAxiosError)
      .then((data) => setFetchedModelTypeData(data))
      .catch((error) => console.error('Failed to fetch prompt type data:', error));

    fetchAndTransform(GPT_MODEL_VERSION, handleAxiosError)
      .then((data) => setFetchedModelVersionData(data))
      .catch((error) => console.error('Failed to fetch prompt type data:', error));
  }, [megaPromptId]);

  const [isAllRequiredItems, setIsAllRequiredItems] = useState(false);
  // 저장 disabled
  useEffect(() => {
    let newRequiredItems = [megaTypeValue, mcodeValue, mnameValue, modelValue, versionValue];

    if (megaTypeValue === '보고서') {
      newRequiredItems = newRequiredItems.concat([reportTypeValue, slideTypeValue]);
    } else {
      setFetchedSlideTypeData([]);
      setFetchedSlideLayoutData([]);
      setSelectedReportTypeId(null);
      setSelectedSlideTypeId(null);
      setSelectedSlideLayoutId(null);
      newRequiredItems = newRequiredItems.filter((item) => item !== reportTypeValue && item !== slideTypeValue);
    }
    console.log('requireditems: ', newRequiredItems);
    setRequiredItems(newRequiredItems);
  }, [
    megaTypeValue,
    mcodeValue,
    mnameValue,
    modelValue,
    versionValue,
    reportTypeValue,
    slideTypeValue,
    promptContentScreen,
  ]);

  // const isAllRequiredItems = requiredItems.every(Boolean);
  useEffect(() => {
    const allItemsFilled = requiredItems.length > 0 && requiredItems.every(Boolean);
    setIsAllRequiredItems(allItemsFilled);
  }, [requiredItems]);

  // prompt type, report type, slide type, slide layout을 mongoDB에서 읽기
  useEffect(() => {
    if (isFirstRunSlideType.current) {
      isFirstRunSlideType.current = false;
      return;
    }
    fetchAndTransform(SLIDE_TYPE, handleAxiosError, selectedReportTypeId)
      .then((data) => setFetchedSlideTypeData(data))
      .catch((error) => console.error(error));
  }, [selectedReportTypeId]);
  // }, [selectedReportTypeId, triggerFetchSlideType]);

  useEffect(() => {
    if (isFirstRunSlideLayout.current) {
      isFirstRunSlideLayout.current = false;
      return;
    }
    fetchAndTransform(SLIDE_LAYOUT, handleAxiosError, selectedSlideTypeId)
      .then((data) => setFetchedSlideLayoutData(data))
      .catch((error) => console.error(error));
  }, [selectedSlideTypeId]);
  // }, [selectedSlideTypeId, triggerFetchSlideLayout]);

  const handleMegaChange = (id, label) => {
    setSelectedMegaTypeId(id);
    setMegaTypeValue(label);
  };

  return (
    <div className="container">
      <AdminLeft activeLnav={activeLnav} setactiveLnav={setactiveLnav} />
      <main className="main">
        <div className="contents-admin">
          <div className="area-admin">
            {megaPromptId === 'regist' ? <h2>메가 프롬프트 등록</h2> : <h2>메가 프롬프트 상세/수정</h2>}
            <div className="contents-admin-wide h1200">
              <div className="contents-admin-left">
                <section className="box-t1">
                  <ul className="list-form">
                    <li>
                      <h3 className="required">app</h3>
                      <div className="wrap-range gap30">
                        {fetchedMegaTypeData
                          .filter(({ id }) => promptContentScreen.length === 0 || id === selectedMegaTypeId)
                          .map(({ id, label }) => (
                            <label key={id} className="wrap-radio">
                              <input
                                type="radio"
                                name="s3"
                                disabled={megaPromptId !== 'regist' && promptContentScreen.length > 0}
                                value={label}
                                checked={selectedMegaTypeId === id}
                                onChange={() => {
                                  if (megaPromptId !== 'regist') setIsModified(true);
                                  promptContentScreen.length === 0 ? handleMegaChange(id, label) : null;
                                }}
                              />
                              <span>{label}</span>
                            </label>
                          ))}
                      </div>
                    </li>
                    {megaTypeValue === '보고서' && (
                      <>
                        <li>
                          <h3 className="required">보고서 템플릿 선택</h3>
                          <div className="wrap-select">
                            <select
                              value={reportTypeValue}
                              disabled={promptContentScreen.length > 0}
                              onChange={(e) => {
                                if (megaPromptId !== 'regist') setIsModified(true);
                                const selectedOption = fetchedReportTypeData.find(
                                  (option) => option.label === e.target.value
                                );
                                setSelectedReportTypeId(selectedOption.id);
                                setReportTypeValue(selectedOption.label);
                                setSlideTypeValue('');
                                setSlideLayoutValue('');
                              }}
                              /*                               
                              보고서 템플릿이 1개인 경우가 없으므로 일단 막음.
                              onClick={() => {
                                if (fetchedReportTypeData.lengh === 1) {
                                  const selectedOption = fetchedReportTypeData[0];
                                  setSelectedReportTypeId(selectedOption.id);
                                  setReportTypeValue(selectedOption.label);
                                  setTriggerFetchSlideType((prev) => !prev);
                                }
                              }} */
                            >
                              <option value="" disabled>
                                보고서 템플릿 선택
                              </option>
                              {fetchedReportTypeData.map((option) => (
                                <option key={option.id} value={option.label}>
                                  {option.label}
                                </option>
                              ))}
                            </select>
                          </div>
                        </li>
                        <li>
                          <h3 className="required">유형 선택</h3>
                          <div className="wrap-select">
                            <select
                              value={slideTypeValue}
                              disabled={promptContentScreen.length > 0 || fetchedSlideTypeData.length === 0}
                              onChange={(e) => {
                                if (megaPromptId !== 'regist') setIsModified(true);
                                const selectedOption = fetchedSlideTypeData.find(
                                  (option) => option.label === e.target.value
                                );
                                setSelectedSlideTypeId(selectedOption.id);
                                setSlideTypeValue(selectedOption.label);
                                setSlideLayoutValue('');
                              }}
                            >
                              <option value="" disabled>
                                유형 선택
                              </option>
                              {fetchedSlideTypeData.map((option) => (
                                <option key={option.id} value={option.label}>
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
                              value={slideLayoutValue}
                              disabled={promptContentScreen.length > 0 || fetchedSlideLayoutData.length === 0}
                              onChange={(e) => {
                                if (megaPromptId !== 'regist') setIsModified(true);
                                const selectedOption = fetchedSlideLayoutData.find(
                                  (option) => option.label === e.target.value
                                );
                                setSelectedSlideLayoutId(selectedOption.id);
                                setSlideLayoutValue(selectedOption.label);
                              }}
                            >
                              <option value="" disabled>
                                보고서 레이아웃 선택
                              </option>
                              {fetchedSlideLayoutData.map((option) => (
                                <option key={option.id} value={option.label}>
                                  {option.label}
                                </option>
                              ))}
                            </select>
                          </div>
                        </li>
                      </>
                    )}
                    <li>
                      <h3 className="required">메가 프롬프트 코드</h3>
                      <div className="wrap-input">
                        <input
                          type="text"
                          placeholder="메가 프롬프트 코드를 입력해주세요."
                          autoComplete="off"
                          value={mcodeValue}
                          onChange={(e) => setMcodeValue(e.target.value)}
                          readOnly={megaPromptId !== 'regist'}
                        ></input>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">메가 프롬프트 이름</h3>
                      <div className="wrap-input">
                        <input
                          type="text"
                          placeholder="메가 프롬프트 이름를 입력해주세요."
                          autoComplete="off"
                          defaultValue={mnameValue}
                          onChange={(e) => {
                            if (megaPromptId !== 'regist') setIsModified(true);
                            setMnameValue(e.target.value);
                          }}
                        ></input>
                      </div>
                    </li>
                    <li>
                      <h3 className="required">GPT 모델 유형</h3>
                      <div className="wrap-range gap30">
                        {fetchedModelTypeData
                          .filter(({ id }) => promptContentScreen.length === 0 || id === selectedModelTypeId)
                          .map(({ id, label }) => (
                            <label key={id} className="wrap-radio">
                              <input
                                type="radio"
                                name="s1"
                                value={label}
                                checked={selectedModelTypeId === id}
                                onChange={() => {
                                  if (megaPromptId !== 'regist') setIsModified(true);
                                  setSelectedModelTypeId(id);
                                  setModelValue(label);
                                }}
                              />
                              <span>{label}</span>
                            </label>
                          ))}
                      </div>
                    </li>
                    <li>
                      <h3 className="required">GPT 모델 버전</h3>
                      <div className="wrap-range gap30">
                        {fetchedModelVersionData
                          .filter(({ id }) => promptContentScreen.length === 0 || id === selectedModelVersionId)
                          .map(({ id, label }) => (
                            <label key={id} className="wrap-radio">
                              <input
                                type="radio"
                                name="s2"
                                value={label}
                                checked={selectedModelVersionId === id}
                                onChange={() => {
                                  if (megaPromptId !== 'regist') setIsModified(true);
                                  setSelectedModelVersionId(id);
                                  setVersionValue(label);
                                }}
                              />
                              <span>{label}</span>
                            </label>
                          ))}
                      </div>
                    </li>
                    <li>
                      <div className="flex-bc">
                        <h3 className="required">프롬프트 모듈 코드</h3>
                        <button className="btn-small add" onClick={() => onShowPopupModule()}>
                          추가
                        </button>
                      </div>
                      <div className="wrap-textarea">
                        <textarea
                          rows="7"
                          placeholder="프롬프트 모듈 코드를 입력해 주세요."
                          value={promptContentScreen ? promptContentScreen : ''}
                          disabled
                          // onChange={(e) => setPromptContentScreen(e.target.value)}
                        ></textarea>
                      </div>
                    </li>
                    <li>
                      <h3>비고</h3>
                      <div className="wrap-textarea">
                        <textarea
                          rows="3"
                          placeholder="비고 내용을 입력해 주세요."
                          value={description}
                          onChange={(e) => {
                            if (megaPromptId !== 'regist') setIsModified(true);
                            setDescription(e.target.value);
                          }}
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
              <div className="contents-admin-right">
                <section className="box-t1">
                  <ul className="list-form">
                    <li>
                      <div className="flex-bc">
                        <h3 className="required">메가 프롬프트 미리보기</h3>
                        <button className="btn-small reset">새로고침</button>
                      </div>
                      <div className="wrap-textarea">
                        <textarea
                          rows="45"
                          placeholder=""
                          defaultValue={promptContentScreen}
                          readOnly
                          className="readonly2"
                        ></textarea>
                      </div>
                    </li>
                  </ul>
                </section>
              </div>
            </div>
            <div className="wrap-btn bc">
              <button className="btn-mid secondary" onClick={onOpenDeletePopup}>
                삭제
              </button>
              <div className="flex-bc gap10">
                <button className="btn-mid primary" onClick={onCancelPopup}>
                  취소
                </button>
                <button className="btn-mid primary" disabled={!isAllRequiredItems} onClick={onSave}>
                  저장
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
      {openCancelPopup && (
        <PopupConfirmAlert
          type={'confirm'}
          message={<>변경사항을 저장하지 않고 이동하시겠습니까?</>}
          onCancel={onCloseCancelPopup}
          onConfirm={() => {
            router.push('/admin/prompt/mega');
          }}
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
          promptContentScreen={promptContentScreen}
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
              router.push('/admin/prompt/mega');
            }
          }}
        />
      )}
      {inputAlertPopup && (
        <PopupConfirmAlert
          type={'alert'}
          message={popupMessage}
          onConfirm={() => {
            setInputAlertPopup(false);
          }}
        />
      )}
    </div>
  );
}```
###### page.js
* ```javascript
'use client';

import Link from 'next/link';
// import Image from "next/image"
import { useState, useEffect } from 'react';
import AdminLeft from '@/app/admin/_components/admin-left';
import MegaSearch from './mega-search';
import PopupConfirmAlert from '@/app/_components/popup-confirm-alert';
import PopupToast from '@/app/_components/popup-toast';
import axiosUtil from '@/app/_util/axios-util';
import usePopupAndLogout from '@/app/_util/error-popup-logout';
import { MEGA_PROMPT_MODULE } from '@/config/apiPaths';

export default function AdminMega() {
  // board
  const [checkAll, setCheckAll] = useState(false);
  const [megaPromptData, setMegaPromptData] = useState([]);
  const [sortField, setSortField] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');

  useEffect(() => {
    const isAllChecked = megaPromptData.every((item) => item.isChecked);
    setCheckAll(isAllChecked);
  }, [megaPromptData]);

  // 전체 선택/해제 함수
  const onCheckAll = () => {
    const updatedCheckboxData = megaPromptData.map((item) => ({
      ...item,
      isChecked: !checkAll,
    }));
    setMegaPromptData(updatedCheckboxData);
    setCheckAll(!checkAll);

    // '전체 선택'에 'some' 클래스가 추가된 경우
    if (megaPromptData.some((item) => item.isChecked)) {
      setCheckAll(true);
      const updatedCheckboxData = megaPromptData.map((item) => ({
        ...item,
        isChecked: false,
      }));
      setMegaPromptData(updatedCheckboxData);
    }
  };

  // 개별 체크박스 변경 핸들러
  const onCheck = (id) => {
    const updatedCheckboxData = megaPromptData.map((item) => {
      if (item.id === id) {
        return {
          ...item,
          isChecked: !item.isChecked,
        };
      }
      return item;
    });
    setMegaPromptData(updatedCheckboxData);
  };

  // 정렬
  const onSort = (field) => {
    console.log('field: ', field);
    let direction = 'asc';
    if (sortField === field) {
      direction = sortDirection === 'asc' ? 'desc' : 'asc';
    }
    const differentSort = ['megaType', 'reportType', 'gptModelType', 'gptModelVersion'];
    let updatedCheckboxData = [];
    updatedCheckboxData = [...megaPromptData].sort((a, b) => {
      let aValue, bValue;
      if (differentSort.includes(field)) {
        console.log('now different sort field: ', field);
        aValue = (a[field][0] && a[field][0].type) || '';
        bValue = (b[field][0] && b[field][0].type) || '';
      } else {
        aValue = a[field];
        bValue = b[field];
      }
      if (aValue < bValue) return direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return direction === 'asc' ? 1 : -1;
      return 0;
    });

    setMegaPromptData(updatedCheckboxData);
    setSortField(field);
    setSortDirection(direction);
  };

  // 체크된 항목 유무 판단
  const isAnyChecked = megaPromptData.some((item) => item.isChecked);

  // 선택 삭제 함수
  const onDelete = async () => {
    const megaPromptToDelete = megaPromptData.filter((item) => item.isChecked).map((item) => item._id);

    if (megaPromptToDelete.length > 0) {
      try {
        const queryString = megaPromptToDelete.map((id) => `delete_targets=${id}`).join('&');
        const url = `${MEGA_PROMPT_MODULE}?${queryString}`;
        const response = await axiosUtil.delete(url);
        if (response.data.deletedCount) {
          setToastMessage('삭제되었습니다.');
          onOpenSuccessToast();
        }
        const updatedCheckboxData = megaPromptData.filter((item) => !item.isChecked);
        setMegaPromptData(updatedCheckboxData);
      } catch (error) {
        console.error('Error occurred in deleting megaPrompt');
        handleAxiosError(error);
      }
    }
  };
  // 단일 삭제 함수
  const onDeleteSingle = (id) => {
    const updatedCheckboxData = megaPromptData.filter((item) => item.id !== id);
    setMegaPromptData(updatedCheckboxData);
  };

  // 페이징 관련 상태
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalRecordCount, setTotalRecordCount] = useState(0);

  // 페이지 이동 함수
  const goToNextPage = () => {
    setCurrentPage(currentPage + 1);
  };
  const goToPreviousPage = () => {
    setCurrentPage(currentPage - 1);
  };
  const goToFirstPage = () => {
    setCurrentPage(1);
  };
  const goToLastPage = () => {
    const totalPages = Math.ceil(totalRecordCount / itemsPerPage);
    setCurrentPage(totalPages);
  };

  // 특정 페이지로 이동하는 함수
  const goToPage = (number) => {
    setCurrentPage(number);
  };

  // 한 페이지에 표시될 아이템 수 변경 함수
  const onPagingChange = (e) => {
    setItemsPerPage(parseInt(e.target.value));
  };

  // ErrorPopup
  const [openErrorPopup, setOpenErrorPopup] = useState(false);
  function onOpenErrorPopup() {
    setOpenErrorPopup(true);
  }
  function onCloseErrorPopup() {
    setOpenErrorPopup(false);
  }

  // DeletePopup
  const [openDeletePopup, setOpenDeletePopup] = useState(false);
  function onOpenDeletePopup() {
    setOpenDeletePopup(true);
  }
  function onCloseDeletePopup() {
    setOpenDeletePopup(false);
  }
  function onDeletePopup() {
    onDelete();
    setOpenDeletePopup(false);
  }

  // SuccessToast
  const [openSuccessToast, setOpenSuccessToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  function onOpenSuccessToast() {
    setOpenSuccessToast(true);
  }
  function onCloseSuccessToast() {
    setOpenSuccessToast(false);
  }

  const [activeLnav, setactiveLnav] = useState(22);

  // Publishing 작업 후 코딩 부분 시작
  const { confirmPopup, setConfirmPopup, popupMessage, handlePopupMessage, handleAxiosError } = usePopupAndLogout();
  const [searchParams, setSearchParams] = useState({});

  const handleSearch = (NewSearchParams) => {
    setSearchParams(NewSearchParams);
  };

  useEffect(() => {
    const queryParams = {
      ...searchParams,
      page: currentPage,
      limit: itemsPerPage,
    };

    // fetch data from API
    const fetchData = async () => {
      try {
        const response = await axiosUtil.get(MEGA_PROMPT_MODULE, { params: queryParams });
        const transformedData = response.data.megaPrompts.map((module) => ({
          ...module,
          id: module._id,
          isChecked: false,
        }));
        setTotalRecordCount(response.data.totalRecords);
        setMegaPromptData(transformedData);
      } catch (error) {
        console.error('Error occurred in fetching ', error);
        handleAxiosError(error);
      }
    };
    fetchData();
  }, [currentPage, itemsPerPage, searchParams]);

  return (
    <div className="container">
      <AdminLeft activeLnav={activeLnav} setactiveLnav={setactiveLnav} />
      <main className="main">
        <div className="contents-admin">
          <div className="area-admin">
            <h2>메가 프롬프트 관리</h2>
            <section className="box-t1">
              <MegaSearch onSearch={handleSearch} />
            </section>
            <section className="box-t1">
              <div className="flex-bc">
                <div className="wrap-btn al">
                  <span>선택된 항목을 : </span>
                  <button className={openDeletePopup ? 'btn-mid on' : 'btn-mid'} onClick={onOpenDeletePopup}>
                    삭제
                  </button>
                </div>
                <div className="wrap-btn">
                  <Link href="/admin/prompt/mega/regist" className="btn-mid regist">
                    신규 등록
                  </Link>
                </div>
              </div>

              {!megaPromptData.length > 0 && (
                <div className="no-data">
                  <p>검색 결과가 없습니다.</p>
                </div>
              )}
              {megaPromptData.length > 0 && (
                <>
                  <table className="tbl-row hover">
                    <thead>
                      <tr>
                        <th>
                          <label className="wrap-checkbox">
                            <input type="checkbox" checked={checkAll} onChange={onCheckAll} />
                            <span className={megaPromptData.some((item) => item.isChecked) ? 'some' : ''}></span>
                          </label>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('megaType')}>
                            app
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('reportType')}>
                            구분
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('code')}>
                            메가 프롬프트 코드
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('name')}>
                            메가 프롬프트 이름
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('gptModelType')}>
                            GPT 모델
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('gptModelVersion')}>
                            GPT 버전
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('updatedAt')}>
                            마지막 수정일시
                          </button>
                        </th>
                        <th>
                          <button className="btn-sort" onClick={() => onSort('modifier')}>
                            마지막 수정자
                          </button>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {megaPromptData.map((item) => (
                        <tr key={item.id} className={item.isChecked ? 'on' : ''}>
                          <td>
                            <span className="wrap-checkbox">
                              <input
                                type="checkbox"
                                name="ref"
                                id={item.id}
                                checked={item.isChecked}
                                onChange={() => onCheck(item.id)}
                              />
                              <span></span>
                            </span>
                          </td>
                          <td>
                            <span>{item.megaType.length > 0 ? item.megaType[0].type : ''}</span>
                          </td>
                          <td>
                            <span>
                              {item.reportType.length > 0
                                ? item.reportType[0].type +
                                  '/' +
                                  item.slideType[0].type +
                                  '/' +
                                  (item.slideLayout ? item.slideLayout[0].type : '')
                                : ''}
                            </span>
                          </td>
                          <td className="w300">
                            <Link href={`/admin/prompt/mega/${item.id}`} className="elipsis link" title={item.code}>
                              {item.code}
                            </Link>
                          </td>
                          <td className="w300">
                            <span title={item.name} className="elipsis">
                              {item.name}
                            </span>
                          </td>
                          <td>
                            <span>{item.gptModelType.length > 0 ? item.gptModelType[0].type : ''}</span>
                          </td>
                          <td>
                            <span>{item.gptModelVersion.length > 0 ? item.gptModelVersion[0].type : ''}</span>
                          </td>
                          <td>
                            <span>{item.updatedAt}</span>
                          </td>
                          <td>
                            <span>{item.modifier ? item.modifier : item.creator}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              )}
              <div className="tbl-btm">
                <div className="exp">총 {totalRecordCount}개</div>
                <div className="list-paging">
                  <button
                    className="btn-first"
                    title="첫페이지로"
                    disabled={currentPage === 1}
                    onClick={goToFirstPage}
                  ></button>
                  <button
                    className="btn-prev"
                    title="이전"
                    disabled={currentPage === 1}
                    onClick={goToPreviousPage}
                  ></button>
                  <ul className="list-num">
                    {Array.from(
                      {
                        length: Math.min(10, Math.ceil(totalRecordCount / itemsPerPage)),
                      },
                      (_, index) => {
                        const pageIndex = Math.floor((currentPage - 1) / 10) * 10 + index + 1;
                        return (
                          <li key={index}>
                            <button
                              className={currentPage === pageIndex ? 'on' : ''}
                              onClick={() => goToPage(pageIndex)}
                            >
                              {pageIndex}
                            </button>
                          </li>
                        );
                      }
                    )}
                  </ul>
                  <button
                    className="btn-next"
                    title="다음"
                    disabled={currentPage === Math.ceil(totalRecordCount / itemsPerPage)}
                    onClick={goToNextPage}
                  ></button>
                  <button
                    className="btn-last"
                    title="마지막페이지로"
                    disabled={currentPage === Math.ceil(totalRecordCount / itemsPerPage)}
                    onClick={goToLastPage}
                  ></button>
                </div>
                <div>
                  <div className="wrap-select mw100">
                    <select onChange={onPagingChange}>
                      <option>5</option>
                      <option>10</option>
                      <option>20</option>
                      <option>100</option>
                    </select>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
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
          onConfirm={onDeletePopup}
        />
      )}
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
###### mega-search.js
* ```javascript
import { useState, useEffect } from 'react';
import MultiSelect from '@/app/_components/multi-select';
import { fetchAndTransform } from '@/app/_util/prompt-management';
import { MEGA_TYPE, GPT_MODEL_TYPE, GPT_MODEL_VERSION } from '@/config/apiPaths';

export default function MegaSearch({ onSearch }) {
  // 검색
  const [searchCriteriaValue, setSearchCriteriaValue] = useState('');
  const [searchValue, setSearchValue] = useState('');
  // MultiSelectSearch에 필요
  const [searchMegaTypeValue, setSearchAppValue] = useState('');
  const [searchGptTypeValue, setSearchGptTypeValue] = useState('');
  const [searchGptVersionValue, setSearchGptVersionValue] = useState('');
  const [resetFlag, setResetFlag] = useState(false);
  const [fetchedMegaTypeData, setFetchedMegaTypeData] = useState([]);
  const [fetchedModelTypeData, setFetchedModelTypeData] = useState([]);
  const [fetchedModelVersionData, setFetchedModelVersionData] = useState([]);

  const handleSearchCriteriaChange = (event) => {
    const selectedOption = event.target.value;
    const mappedValue = criteriaValueMapping[selectedOption];
    console.log('mappedValue: ', mappedValue);
    setSearchCriteriaValue(mappedValue);
  };

  useEffect(() => {
    fetchAndTransform(MEGA_TYPE)
      .then((data) => {
        setFetchedMegaTypeData(data);
      })
      .catch((error) => console.error('Failed to fetch mega type data:', error));

    fetchAndTransform(GPT_MODEL_TYPE)
      .then((data) => {
        setFetchedModelTypeData(data);
      })
      .catch((error) => console.error('Failed to fetch prompt type data:', error));

    fetchAndTransform(GPT_MODEL_VERSION)
      .then((data) => {
        setFetchedModelVersionData(data);
      })
      .catch((error) => console.error('Failed to fetch prompt type data:', error));
  }, []);

  // 초기화 함수
  const onReset = () => {
    setSearchCriteriaValue('');
    setSearchValue('');
    // MultiSelectSearch에 필요
    setSearchAppValue('');
    setSearchGptTypeValue('');
    setSearchGptVersionValue('');
    setResetFlag(true);
  };

  // Publishing 후 코딩 시작
  const criteriaValueMapping = {
    '모듈 코드': 'code',
    '모듈 이름': 'name',
    '마지막 수정자': 'modifier',
  };

  const handleSearchClick = () => {
    console.log('handleSearchClick start');
    const getSelectedIds = (selectedValues, fetchedData) => {
      console.log('selectedValue: ', selectedValues);
      console.log('fetchedData: ', fetchedData);
      return fetchedData
        .filter((item) => selectedValues.includes(item.label))
        .map((item) => {
          return item.id;
        });
    };
    const searchParams = {
      ...(searchCriteriaValue ? { [searchCriteriaValue]: searchValue } : {}),
      ...(searchMegaTypeValue ? { megaType: getSelectedIds(searchMegaTypeValue, fetchedMegaTypeData) } : {}),
      ...(searchGptTypeValue ? { gptModelType: getSelectedIds(searchGptTypeValue, fetchedModelTypeData) } : {}),
      ...(searchGptVersionValue
        ? { gptModelVersion: getSelectedIds(searchGptVersionValue, fetchedModelVersionData) }
        : {}),
    };
    onSearch(searchParams);
    setResetFlag(false);
  };

  return (
    <div className="wrap-search">
      <div className="mw260">
        <MultiSelect
          key={fetchedMegaTypeData.length}
          multiSelectData={fetchedMegaTypeData}
          multiSelectValue={searchMegaTypeValue}
          setMultiSelectValue={setSearchAppValue}
          resetAll={onReset}
          resetFlag={resetFlag}
          placeholder="app"
        />
      </div>
      <div className="mw260">
        <MultiSelect
          key={fetchedModelTypeData.length}
          multiSelectData={fetchedModelTypeData}
          multiSelectValue={searchGptTypeValue}
          setMultiSelectValue={setSearchGptTypeValue}
          resetAll={onReset}
          resetFlag={resetFlag}
          placeholder="GPT 모델 유형"
        />
      </div>
      <div className="mw260">
        <MultiSelect
          key={fetchedModelVersionData.length}
          multiSelectData={fetchedModelVersionData}
          multiSelectValue={searchGptVersionValue}
          setMultiSelectValue={setSearchGptVersionValue}
          resetAll={onReset}
          resetFlag={resetFlag}
          placeholder="GPT 모델 버전"
        />
      </div>
      <div className="wrap-select mw180">
        <select value={searchCriteriaValue} onChange={handleSearchCriteriaChange}>
          <option>검색 조건 선택</option>
          <option>모듈 코드</option>
          <option>모듈 이름</option>
          <option>마지막 수정자</option>
        </select>
      </div>
      <div className="wrap-input flex-1">
        <input
          type="search"
          placeholder="검색어를 입력해 주세요."
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
        />
      </div>
      <button className="btn-mid" onClick={handleSearchClick}>
        조회
      </button>
      <button className="btn-small reset" onClick={onReset}>
        초기화
      </button>
    </div>
  );
}

```
###### popup-module.js
* ```javascript
import Link from 'next/link';
import { useState, useEffect } from 'react';
import axiosUtil from '@/app/_util/axios-util';
import { PROMPT_MODULE } from '@/config/apiPaths';

export default function PopupModule({ onHidePopupModule, promptContentScreen, searchParams, errorHandler }) {
  const [moduleList, setModuleList] = useState([]);
  const [selectedModules, setSelectedModules] = useState([]);
  const [nextSelectionOrder, setNextSelectionOrder] = useState(1);

  useEffect(() => {
    console.log('popup start!');
    console.log('searchParams: ', searchParams);
    const fetchData = async () => {
      try {
        const response = await axiosUtil.get(PROMPT_MODULE, { params: searchParams });
        if (Array.isArray(response.data) && response.data.length > 0) {
          const promptCodes = promptContentScreen.split('\n');
          const transformedData = response.data.map((module) => {
            const isSelected = promptCodes.includes(module.code);
            return {
              ...module,
              id: module._id,
              isChecked: false,
              isSelected,
              selectionOrder: isSelected ? promptCodes.indexOf(module.code) : null,
            };
          });
          setModuleList(transformedData);
          const initialSelectedModules = transformedData
            .filter((module) => module.isSelected)
            .sort((a, b) => a.selectionOrder - b.selectionOrder);
          setSelectedModules(initialSelectedModules);
          setNextSelectionOrder(promptCodes.length);
        } else {
          // TODO show error
          console.error('Unexpected response structure or No data: ', response.data);
        }
      } catch (error) {
        console.error('Error occurred in fetching ', error);
        errorHandler(error);
      }
    };
    fetchData();
  }, [searchParams, promptContentScreen]);

  const onCheck = (id) => {
    setModuleList((prevModuleList) =>
      prevModuleList.map((module) => (module.id === id ? { ...module, isChecked: !module.isChecked } : module))
    );
  };

  const onSelectedCheck = (id) => {
    setSelectedModules((prevModuleList) =>
      prevModuleList.map((module) => (module.id === id ? { ...module, isChecked: !module.isChecked } : module))
    );
  };

  const isSelectable = moduleList.some((item) => !item.isSelected && item.isChecked);
  const onSelect = () => {
    const newlySelectedModules = moduleList.filter((item) => item.isChecked && !item.isSelected);
    // set selected module was moved to selectedModules
    const updatedModuleList = moduleList.map((item) => {
      if (item.isChecked && !item.isSelected) {
        return { ...item, isSelected: true };
      }
      return item;
    });
    setModuleList(updatedModuleList);

    // add the selected item to selectedModules. The new added item will be the last in the order.
    let currentOrder = nextSelectionOrder;
    const updatedSelectedModules = [
      ...selectedModules,
      ...newlySelectedModules.map((module) => ({ ...module, selectionOrder: currentOrder++ })),
    ].sort((a, b) => a.selectionOrder - b.selectionOrder);

    setSelectedModules(updatedSelectedModules);
    setNextSelectionOrder(currentOrder);
  };
  const isDeselectable = selectedModules.some((item) => item.isChecked);
  const onDeselect = () => {
    const deselectedModuleIds = selectedModules.filter((item) => item.isChecked).map((item) => item.id);
    const updatedModuleList = moduleList.map((item) =>
      deselectedModuleIds.includes(item.id) ? { ...item, isSelected: false } : item
    );
    setModuleList(updatedModuleList);

    // remove the selected module from selectedModules.
    const updatedSelectedModules = selectedModules
      .filter((item) => !item.isChecked)
      .sort((a, b) => a.selectionOrder - b.selectionOrder);

    setSelectedModules(updatedSelectedModules);
  };

  const updatePromptContentAndHide = () => {
    console.log('selectedModules: ', selectedModules);
    const selectedCodes = selectedModules.map((item) => item.code).join('\n');

    const finalPromptContentDB = selectedModules.map((item) => ({ _id: item._id, code: item.code }));

    onHidePopupModule(selectedCodes, finalPromptContentDB);
  };

  return (
    <aside className="popup center">
      <div className="dimmed"></div>
      <div className="pop-content large">
        <div className="mb-10">
          <div className="tit">모듈 선택</div>
        </div>
        <div className="wrap-body">
          <div className="wrap-moveselect">
            <article>
              <p className="subtit">모듈 목록</p>
              <div className="box-border">
                <ul>
                  {moduleList.length > 0 ? (
                    moduleList.map(
                      (item) =>
                        item.isSelected === false && (
                          <li key={item.id} id={item.id}>
                            <label className="item-selector">
                              <input
                                type="checkbox"
                                name="before"
                                id={item.id}
                                checked={item.isChecked}
                                onChange={() => onCheck(item.id)}
                              />
                              <span>{item.code}</span>
                            </label>
                          </li>
                        )
                    )
                  ) : (
                    <li>조건에 맞는 모듈이 없습니다.</li>
                  )}
                </ul>
              </div>
            </article>
            <div className="btns">
              <button className="btn-icon arr1" title="선택" disabled={!isSelectable} onClick={onSelect}></button>
              <button
                className="btn-icon arr2"
                title="선택취소"
                disabled={!isDeselectable}
                onClick={onDeselect}
              ></button>
            </div>
            <article>
              <p className="subtit">선택한 모듈 ({moduleList.filter((module) => module.isSelected).length}개)</p>
              <div className="box-border">
                <ul>
                  {selectedModules.map((item) => (
                    <li key={item.id} id={item.id}>
                      <label className="item-selector">
                        <input
                          type="checkbox"
                          name="before"
                          id={item.id}
                          checked={item.isChecked}
                          onChange={() => onSelectedCheck(item.id)}
                        />
                        <span>{item.code}</span>
                      </label>
                    </li>
                  ))}
                </ul>
              </div>
            </article>
          </div>
        </div>
        <div className="wrap-btn btm">
          <button onClick={() => onHidePopupModule()}>취소</button>
          <button onClick={updatePromptContentAndHide}>추가</button>
        </div>
      </div>
    </aside>
  );
}```
#### test data 생성(엑셀 -> mongoDB)
##### excel
###### ![[100. media/documents/YZbF4RN1FB.xlsx]]
###### ![[100. media/documents/DeYJ-JXtv1.xlsx]]
##### 실행방법 package.json을 수정해서 "type": "module"을 넣어야 함. commonJS, ES6 사용여부에 관련됨.
* ```javascript
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

readExcelAndSaveToDB('./prompt_module_data1.xlsx')
  .then(() => {
    console.log('Data imported successfully');
    mongoose.disconnect();
  })
  .catch((err) => {
    console.error('Error importing data:', err);
    mongoose.disconnect();
  });

```
### DART crawler
#### README
* ```plain text
DART API 호출 프로그램 실행 방법
도움말 보기: main.py -h

- 특정 타입 데이터가 필요한 경우 (예: 일시(YYYYMMDD), 회사 고유번호(코드값) 등), 다음 기호 `< >`를 추가함. 
- 여러 값 중 하나만 선택해야 할 경우, `|`으로 구분함.
- 입력파일은 회사고유번호(corp_code)가 들어있는 csv 파일.

1. 공시정보 중 1.공시검색 수집 시:
    - python main.py search_report [--corp_code <고유번호>] [--bgn_de <YYYYMMDD>] [--end_de <YYYYMMDD>] [--last_reprt_at Y|N] [--pblntf_ty [A-J]] [--pblntf_detail_ty [A001-J009]] [--corp_cls Y|K|N|E] [--sort date|crp|rpt] [--sort_mth asc|desc]

2. 공시정보 중 2.기업개황 수집하고 파일/DB 저장:
    - python main.py corp_info --input 입력파일 --output 출력파일 --output_type [csv|db]

3. 공시정보 중 3.공시서류원본파일 다운로드 시:
    - python main.py orig_document --rcept_no 접수번호

4. 공시정보 중 4.고유번호 수집 시:
    - python main.py corp_code --output 고유번호저장파일

5. 상장기업 재무정보 중 4.단일회사 전체 재무제표 수집 시:
    - python main.py finance_info --corp_code <회사고유번호> --bsns_year <사업년도> --reprt_code 11011|11012|11013|11014 --fs_div OFS|CFS

6. 정기보고서(pdf) 다운로드 시:
    - python main.py pdf_download --start <YYYYMMDD> --end <YYYYMMDD>

7. 전일 종가정보 수집 시:
    - python main.py stock_price --output 출력파일 --page_count 건수
    
8. 고유번호 수집한 것 중 기업 정보가 바뀐 것 추리기(기간 입력) - 실행 후 생성된 csv 파일을 corp_info의 input으로 준다.
    - python extract_modified_corp_code.py corp_code.csv YYYYMMDD YYYYMMDD
```
#### requirement.txt
* ```plain text
beautifulsoup4==4.12.2
certifi==2023.7.22
charset-normalizer==3.3.0
colorama==0.4.6
finance-datareader==0.9.50
greenlet==3.0.0
idna==3.4
lxml==4.9.3
numpy==1.26.0
OpenDartReader==0.2.3
pandas==2.1.1
psycopg2==2.9.9
python-dateutil==2.8.2
pytz==2023.3.post1
requests==2.31.0
requests-file==1.5.1
six==1.16.0
soupsieve==2.5
SQLAlchemy==2.0.21
tqdm==4.66.1
typing_extensions==4.8.0
tzdata==2023.3
urllib3==2.0.6
xmltodict==0.13.0

```
#### main.py
* ```python
import argparse
import logging
import pandas as pd
from DART.dart_api_call import (
    get_corp_code,
    get_corp_info,
    get_finance_info,
    get_orig_document,
    search_report,
)
from DART.DartPdfDownloader import DartPdfDownloader
from STOCK.stock_api_call import get_stock_price
import re
from config.constants import API_KEYS

# TODO env에서 읽기
db_info = "postgresql+psycopg2://skopenai:!skcc1234@infratf-db.postgres.database.azure.com:5432/chatbot?sslmode=allow"

log_file_path = "./tokaicrawler.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


def validate_date_format(date_str):
    pattern = r"\d{4}\d{2}\d{2}"  # YYYYMMDD
    return bool(re.fullmatch(pattern, date_str))


if *name* == "*main*":
    parser = argparse.ArgumentParser(description="Execute specific tasks.")
    parser.add_argument(
        "task",
        choices=[
            "corp_code",
            "corp_info",
            "finance_info",
            "orig_document",
            "pdf_download",
            "search_report",
            "stock_price",
        ],
        help="Specify the task to execute: corp_code, corp_info, or finance_info, orig_document, pdf_download",
    )
    parser.add_argument(
        "--input",
        type=str,
        default="corp_code.csv",
        help="Input CSV file for the corp_info task",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output CSV file for tasks that generate data",
    )
    parser.add_argument(
        "--corp_code",
        type=str,
        default=None,
        help="To get information for a specific corp_code",
    )
    parser.add_argument("--bsns_year", type=str, default=None, help="Business year")
    parser.add_argument(
        "--reprt_code",
        type=str,
        choices=["11011", "11012", "11013", "11014"],
        default=None,
        help="Report Code [11011-사업보고서, 11012-반기보고서, 11013-1분기보고서, 11014-3분기보고서]",
    )
    parser.add_argument(
        "--fs_div",
        type=str,
        choices=["OFS", "CFS"],
        default=None,
        help="Code for financial report [OFS:재무제표, CFS:연결재무제표]",
    )
    parser.add_argument(
        "--rcept_no",
        type=str,
        default=None,
        help="reception number",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help="Start date(YYYYMMDD)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="End date(YYYYMMDD)",
    )
    parser.add_argument(
        "--bgn_de",
        type=str,
        default=None,
        help="Start date(YYYYMMDD) default is end_de",
    )
    parser.add_argument(
        "--end_de",
        type=str,
        default=None,
        help="End date(YYYYMMDD), default is today",
    )
    parser.add_argument(
        "--last_reprt_at",
        type=str,
        choices=["Y", "N"],
        default=None,
        help="Y or N",
    )
    parser.add_argument(
        "--pblntf_ty",
        type=str,
        choices=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        default=None,
        help="A: 정기공시, B: 주요사항보고, C: 발행공시, D: 지분공시, E: 기타공시, F: 외부감사관련, G: 펀드공시, H: 자산유동화, I: 거래소공시, J: 공정위공시",
    )
    parser.add_argument(
        "--pblntf_detail_ty",
        type=str,
        default=None,
        help="https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001 상세유형 참고",
    )
    parser.add_argument(
        "--corp_cls",
        type=str,
        choices=["Y", "K", "N", "E"],
        default=None,
        help="법인구분 : Y(유가), K(코스닥), N(코넥스), E(기타) ※ 없으면 전체조회, 복수조건 불가",
    )
    parser.add_argument(
        "--sort",
        type=str,
        choices=["date", "crp", "rpt"],
        default=None,
        help="접수일자: date, 회사명: crp, 보고서명: rpt ※ 기본값: date",
    )
    parser.add_argument(
        "--sort_mth",
        type=str,
        choices=["asc", "desc"],
        default=None,
        help="오름차순(asc), 내림차순(desc) ※ 기본값 : desc",
    )
    parser.add_argument(
        "--page_no",
        type=str,
        default=None,
        help="페이지 번호(1~n) 기본값 : 1",
    )
    parser.add_argument(
        "--page_count",
        type=str,
        default=None,
        help="페이지당 건수(1~100) 기본값 : 10, 최대값 : 100",
    )
    parser.add_argument(
        "--output_type",
        type=str,
        choices=["csv", "db"],
        help="Output type: csv or db (mandatory for corp_info task)",
    )
    args = parser.parse_args()

    if args.task == "corp_code":
        # get all corp_code 고유번호
        output_file = args.output if args.output else "corp_code.csv"
        get_corp_code(output_file)
    elif args.task == "corp_info":
        if args.output_type is None:
            parser.error(
                "the --output_type argument is required for the 'corp_info' task"
            )
        else:
            # get corp information 기업개황
            output_file = args.output if args.output else "corp_info.csv"
            corp_code_df = pd.read_csv(args.input, dtype={"corp_code": str})
            get_corp_info(corp_code_df, output_file, args.output_type)
    elif args.task == "finance_info":
        # get finance info 단일회사 전체 재무제표
        if all([args.corp_code, args.bsns_year, args.reprt_code, args.fs_div]):
            output_file = (
                f"{args.corp_code}_{args.bsns_year}_{args.reprt_code}_{args.fs_div}"
            )
            params = [args.corp_code, args.bsns_year, args.reprt_code, args.fs_div]
            get_finance_info(params, output_file)
        else:
            print("Error: Missing required parameters for the 'finance_info' task.")
            print("You must provide corp_code, bsns_year, reprt_code, and fs_div.")
            exit(1)
    elif args.task == "orig_document":
        if args.rcept_no:
            get_orig_document(args.rcept_no)
        else:
            print("You must provide rcept_no to get original document.")
            exit(1)
    elif args.task == "pdf_download":
        if all([args.start, args.end]):
            if validate_date_format(args.start) and validate_date_format(args.end):
                downloader = DartPdfDownloader(API_KEYS)
                downloader.get_pdf_report(args.start, args.end)
            else:
                print("Error: Invalid date format. Please use YYYYMMDD.")
                exit(1)
        else:
            print("You must provide start date and end date to download pdf files.")
            exit(1)
    elif args.task == "search_report":
        output_file = args.output if args.output else "search_result.csv"
        optional_params = {}

        if args.corp_code:
            optional_params["corp_code"] = args.corp_code
        if args.bgn_de:
            optional_params["bgn_de"] = args.bgn_de
        if args.end_de:
            optional_params["end_de"] = args.end_de
        if args.last_reprt_at:
            optional_params["last_reprt_at"] = args.last_reprt_at
        if args.pblntf_ty:
            optional_params["pblntf_ty"] = args.pblntf_ty
        if args.pblntf_detail_ty:
            optional_params["pblntf_detail_ty"] = args.pblntf_detail_ty
        if args.corp_cls:
            optional_params["corp_cls"] = args.corp_cls
        if args.sort:
            optional_params["sort"] = args.sort
        if args.sort_mth:
            optional_params["sort_mth"] = args.sort_mth
        if args.page_no:
            optional_params["page_no"] = args.page_no
        if args.page_count:
            optional_params["page_count"] = args.page_count

        search_report(output_file, **optional_params)
    elif args.task == "stock_price":
        output_file = args.output if args.output else "stock_price.csv"
        page_count = args.page_count if args.page_count else 4000
        get_stock_price(output_file, page_count)

```
#### bulk_process
##### bulk_get_finance_info.py
* ```python
import argparse
import pandas as pd
import requests
import logging
import jsonon]]
import time
import os

# Replace these with your actual API details
from config.constants import DART_API_URL, API_KEY

log_file_path = "./tokaicrawler.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


def get_finance_info(corp_code, bsns_year, reprt_code, fs_div):
    max_retries = 3  # Number of retries
    retries = 0  # Current retry count
    print("----------------------------------------------------------------------")
    print(
        f"Processing corp_code: 고유번호: {corp_code} 사업년도: {bsns_year} 보고서 종류:{reprt_code} 재무제표: {fs_div}"
    )
    logging.info(
        f"Processing corp_code: 고유번호: {corp_code} 사업년도: {bsns_year} 보고서 종류:{reprt_code} 재무제표: {fs_div}"
    )
    while retries <= max_retries:
        dart_finance = f"""{DART_API_URL}/api/fnlttSinglAcntjsonjson?crtfc_key={API_KEY}&corp_code={corp_code}&bsns_year={bsns_year}&reprt_code={reprt_code}&fs_div={fs_div}"""
        try:
            response = requests.get(dart_finance, timeout=30, verify=False)
            response.raise_for_status()
            jsonnce_jsonjsonesponse.json()

            if "stajson in finance_jsonn]] and finance_json["status"] != "000":
                logging.error(
                    f"Error for corp_codjsonorp_code}: {finance_json.get('message', 'Unknown error')}"
                )
                print(
                    f"Error for corpjsone {corp_code}: {finance_json.get('message', 'Unknown error')}"
                )
              jsonturn

            # Process json and save to CSV (You can add your own logic here)
            output_dir = "./finance_download"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            output_file = os.path.join(
                output_dir, f"{corp_code}_{bsns_year}_{reprt_code}_{fs_div}.csv"
           json           pd.DataFrame(finance_json.get("list", [])).to_csv(output_file, index=False)
            logging.info(
                f"Data saved successfully for {corp_code} year:{bsns_year} report:{reprt_code} fs_div:{fs_div}."
            )
            break

        except (requests.Timeout, requests.ConnectionError) as retryable_err:
            retries += 1
            logging.warning(
                f"Retryable error for corp_code: {corp_code}, Attempt: {retries}/{max_retries} - {retryable_err}"
            )
            if retries <= max_retries:
                time.sleep(5)  # Sleep before retrying
            else:
                logging.error(
                    f"Max retries reached for corp_code: {corp_code} - {retryable_err}"
                )
        except requests.HTTPError as http_err:
            logging.error(f"HTTP Error for corp_code: {corp_code} {http_err}")
            break
        except requests.RequestException as e:
            logging.error(f"Network Error for corp_code {corp_code}:json"json          break
        except json.jsonDejsonError:
            logging.error(f"Decoding json Error for corp_code {corp_code}")
            break
        except Exception as e:
            logging.error(f"Unexpected Error for corp_code {corp_code}: {e}")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Fetch finance information based on an input file(stock_list)."
    )
    parser.add_argument("input_file", type=str, help="Path to the stock_list.csv.")

    args = parser.parse_args()
    input_file = args.input_file

    # Read the input_file
    df = pd.read_csv(input_file, dtype={"corp_code": str})

    # Fixed variables
    # bsns_years = ["2020", "2021", "2022", "2023"]
    # 10월 27일에 이미 기업개황 3천 건 넘게 읽었기 때문에 남은 API 호출 가능 건수가 6천 미만.
    # 2020년도 split_file_stock_list_1.csv(1,000건) 처리.
    # 김호준 메니저에게서 인증키를 하나 받아서
    # 10.28. 2020년도 split_file_stock_list2.csv 처리. 4천 건.
    # 10.28. 개발서버에서 2020년도 split_file_stock_list_3.csv 처리. 4천 건.
    # 10.29. 개발서버에서 2020년도 split_file_stock_list_4.csv 처리. 4천 건.
    # 10.30 개발서버에서 인증키 두 개로 2021 다 처리
    # 10.31 개발서버에서 2021 split_file_stock_list4.csv 처리.
    # 10.31 개발서버에서 2022 split 1,2,3 처리
    # 문기식 팀장님 api key를 받아서 2022 split 4까지 처리.
    # cron에 2023 split 1,2,3,4 처리하도록 설정.

    bsns_years = ["2020"]
    reprt_codes = ["11011", "11012", "11013", "11014"]
    fs_div = "OFS"

    # Nested loops
    for _, row in df.iterrows():
        corp_code = row["corp_code"]
        for bsns_year in bsns_years:
            for reprt_code in reprt_codes:
                get_finance_info(corp_code, bsns_year, reprt_code, fs_div)
                time.sleep(1)


if *name* == "*main*":
    main()

```
##### bulk_insert_corp_info.py
* ```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import argparse
from database.db_connection import get_session
from models.corporate import CorpInfo


def save_csv_to_db(input_csv):
    session = get_session()

    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv, dtype=str)
    df.where(pd.notna(df), None, inplace=True)

    bulk_data = []
    first_header = True
    for index, row in df.iterrows():
        if first_header:
            first_header = False
            continue
        elif row["corp_code"] == "corp_code":
            continue
        data = {
            "corp_code": row["corp_code"],
            "corp_name": row["corp_name"],
            "corp_name_eng": row["corp_name_eng"],
            "stock_name": row["stock_name"],
            "stock_code": row["stock_code"],
            "ceo_nm": row["ceo_nm"],
            "corp_cls": row["corp_cls"],
            "jurir_no": row["jurir_no"],
            "bizr_no": row["bizr_no"],
            "adres": row["adres"],
            "hm_url": row["hm_url"],
            "ir_url": row["ir_url"],
            "phn_no": row["phn_no"],
            "fax_no": row["fax_no"],
            "induty_code": row["induty_code"],
            "est_dt": row["est_dt"],
            "acc_mt": row["acc_mt"],
        }
        bulk_data.append(data)

    try:
        session.bulk_insert_mappings(CorpInfo, bulk_data)
        session.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
        session.rollback()
    finally:
        session.close()


parser = argparse.ArgumentParser(description="Bulk save corp_info.csv to Database.")
parser.add_argument("input_csv", help="Path to the input CSV file.")

if *name* == "*main*":
    args = parser.parse_args()
    save_csv_to_db(args.input_csv)

```
##### bulk_insert_finance_info_without_normalization.py
* ```python
import os, csv, glob
import pandas as pd
import numpy as np
import argparse
from sqlalchemy.exc import IntegrityError, StatementError, SQLAlchemyError
import logging
from database.db_connection import get_session

log_file_path = "./insert_finance.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


def preprocess_data(df):
    cols_to_convert = [
        "thstrm_amount",
        "frmtrm_amount",
        "frmtrm_q_amount",
        "frmtrm_add_amount",
        "bfefrmtrm_amount",
        "thstrm_add_amount",
    ]
    existing_cols = {col: "Int64" for col in cols_to_convert if col in df.columns}
    for col in existing_cols.keys():
        df[col] = df[col].fillna(0).astype(np.int64)

    df["rcept_no"] = df["rcept_no"].astype(str)
    df["reprt_code"] = df["reprt_code"].astype(str)
    df["bsns_year"] = df["bsns_year"].astype(str)
    df["corp_code"] = df["corp_code"].astype(str)
    df.replace({pd.NaT: None, pd.NA: None, np.nan: None}, inplace=True)

    return df


def insert_data(df, session, corp_code, year, filename):
    reprt_code = df["reprt_code"].iloc[0]
    financial_report_base_list = []
    for _, row in df.iterrows():
        financial_report_base_dict = {
            "rcept_no": row["rcept_no"],
            "reprt_code": row["reprt_code"],
            "bsns_year": row["bsns_year"],
            "corp_code": row["corp_code"],
            "report_type": "A" if reprt_code == "11011" else "Q",
            "fs_type": "OFS",
            "sj_div": row["sj_div"],
            "sj_nm": row["sj_nm"],
            "account_id": row["account_id"],
            "account_nm": row["account_nm"],
            "thstrm_nm": row["thstrm_nm"],
            "thstrm_amount": int(row["thstrm_amount"]),
            "frmtrm_nm": row.get("frmtrm_nm"),
            "frmtrm_amount": int(row.get("frmtrm_amount", 0)),
            "ord": row["ord"],
            "currency": row["currency"],
            "thstrm_add_amount": int(row["thstrm_add_amount"]),
            "frmtrm_q_nm": row.get("frmtrm_q_nm", None),
            "frmtrm_q_amount": int(row.get("frmtrm_q_amount", 0)),
            "frmtrm_add_amount": int(row.get("frmtrm_add_amount", 0)),
            "bfefrmtrm_nm": row.get("bfefrmtrm_nm", None),
            "bfefrmtrm_amount": int(row.get("bfefrmtrm_amount", 0)),
        }
        financial_report_base_list.append(financial_report_base_dict)
    try:
        session.bulk_insert_mappings(FinancialReportBase, financial_report_base_list)
        session.commit()
        logging.info(f"Saved data for corp_code: {corp_code}, year: {year}")
    except IntegrityError as ie:
        session.rollback()
        # Handle IntegrityError more robustly
        if "duplicate key" in str(ie.orig).lower():
            logging.warning(
                f"Duplicate entry for corp_code: {corp_code}, year: {year}, file: {filename}. Skipping..."
            )
        else:
            logging.error(
                f"IntegrityError for corp_code: {corp_code}, year: {year}, file: {filename}. Error: {str(ie)}"
            )
    except (StatementError, SQLAlchemyError, Exception) as e:
        session.rollback()
        error_type = type(e).*name*
        logging.error(
            f"{error_type} occurred for corp_code: {corp_code}, year: {year}, file: {filename}. Error: {str(e)}"
        )


def main():
    parser = argparse.ArgumentParser(description="Read CSV and save to DB")
    parser.add_argument(
        "--corp_list", required=True, help="Path to the corp_code list file"
    )
    args = parser.parse_args()

    session = get_session()

    # Read corp codes
    with open(args.corp_list, "r", newline="", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            corp_code = row["corp_code"]
            logging.info(
                "======================================================================="
            )
            logging.info("Start new company!!!")
            logging.info(f"corp_code: {corp_code}")

            for year in range(2020, 2024):
                logging.info(f"year: {year}")
                file_pattern = f"./finance_download/{corp_code}_{year}_*.csv"

                for filename in glob.glob(file_pattern):
                    logging.info(
                        "-----------------------------------------------------------------------"
                    )
                    logging.info(f"file to process: {filename}")
                    df = pd.read_csv(filename, dtype={"corp_code": str})
                    df = preprocess_data(df)
                    insert_data(df, session, corp_code, year, filename)

    session.close()


if *name* == "*main*":
    main()

```
##### bulk_insert_finance_info.py
* ```python
import os, csv, glob
import pandas as pd
import numpy as np
import argparse
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.exc import IntegrityError, StatementError, SQLAlchemyError
import logging
from database.db_connection import get_session

Base = sqlalchemy.orm.declarative_base()

log_file_path = "./insert_finance.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


class FinancialReportBase(Base):
    *tablename* = "financial_report_base"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rcept_no = Column(String(14))
    reprt_code = Column(String(5), nullable=False)
    bsns_year = Column(String(4), nullable=False)
    corp_code = Column(String(8), ForeignKey("corp_info.corp_code"), nullable=False)
    report_type = Column(String(1), nullable=False)
    fs_type = Column(String(3), nullable=False)


class FinancialStatement(Base):
    *tablename* = "financial_statement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("financial_report_base.id"))
    sj_div = Column(String(3), nullable=False)
    sj_nm = Column(String)
    account_id = Column(String(3), nullable=False)
    account_nm = Column(String)
    account_detail = Column(String)
    thstrm_nm = Column(String)
    thstrm_amount = Column(BigInteger)
    frmtrm_nm = Column(String(255))
    frmtrm_amount = Column(BigInteger)
    ord = Column(Integer)
    currency = Column(String(3))


class FinancialQuarterlyReport(Base):
    *tablename* = "financial_quarterly_report"
    id = Column(Integer, ForeignKey("financial_statement.id"), primary_key=True)
    frmtrm_q_nm = Column(String)
    frmtrm_q_amount = Column(BigInteger)
    frmtrm_add_amount = Column(BigInteger)
    thstrm_add_amount = Column(BigInteger)


class FinancialAnnualReport(Base):
    *tablename* = "financial_annual_report"
    id = Column(Integer, ForeignKey("financial_statement.id"), primary_key=True)
    bfefrmtrm_nm = Column(String)
    bfefrmtrm_amount = Column(BigInteger)


def main():
    parser = argparse.ArgumentParser(description="Read CSV and save to DB")
    parser.add_argument(
        "--corp_list", required=True, help="Path to the corp_code list file"
    )
    args = parser.parse_args()

    # DB setup
    session = get_session()

    # Read corp codes
    with open(args.corp_list, "r", newline="", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            corp_code = row["corp_code"]
            logging.info(
                "======================================================================="
            )
            logging.info("Start new company!!!")
            logging.info(f"corp_code: {corp_code}")

            for year in range(2020, 2024):
                logging.info(f"year: {year}")
                file_pattern = f"./finance_download/{corp_code}_{year}_*.csv"

                for filename in glob.glob(file_pattern):
                    logging.info(
                        "-----------------------------------------------------------------------"
                    )
                    logging.info(f"file to process: {filename}")
                    df = pd.read_csv(filename, dtype={"corp_code": str})

                    # preprocess data
                    # Your list of columns to convert
                    cols_to_convert = [
                        "thstrm_amount",
                        "frmtrm_amount",
                        "frmtrm_q_amount",
                        "frmtrm_add_amount",
                        "bfefrmtrm_amount",
                        "thstrm_add_amount",
                    ]

                    # Create a dictionary for columns that need to be converted to Int64
                    existing_cols = {
                        col: "Int64" for col in cols_to_convert if col in df.columns
                    }

                    # Fill NaN values and convert types in one go
                    for col in existing_cols.keys():
                        df[col] = df[col].fillna(0).astype(np.int64)

                    df["rcept_no"] = df["rcept_no"].astype(str)
                    df["reprt_code"] = df["reprt_code"].astype(str)
                    df["bsns_year"] = df["bsns_year"].astype(str)
                    df["corp_code"] = df["corp_code"].astype(str)

                    # Replace NaN with None
                    df.replace({pd.NaT: None, pd.NA: None, np.nan: None}, inplace=True)

                    # Prepare a list to hold the rows to be inserted in batch
                    financial_statement_list = []
                    financial_annual_report_list = []
                    financial_quarterly_report_list = []

                    reprt_code = df["reprt_code"].iloc[0]

                    try:
                        # Step 1: Save to financial_report_base
                        financial_report_base = FinancialReportBase(
                            rcept_no=df["rcept_no"].iloc[0],
                            reprt_code=reprt_code,
                            bsns_year=df["bsns_year"].iloc[0],
                            corp_code=df["corp_code"].iloc[0],
                            report_type="A" if reprt_code == "11011" else "Q",
                            fs_type="OFS",
                        )
                        session.add(financial_report_base)
                        session.commit()
                        logging.info("financial_report_base commit ok")

                        # Step 2: Save to financial_statement
                        for _, row in df.iterrows():
                            financial_statement_dict = {
                                "report_id": financial_report_base.id,
                                "sj_div": row["sj_div"],
                                "sj_nm": row["sj_nm"],
                                "account_id": row["account_id"],
                                "account_nm": row["account_nm"],
                                "thstrm_nm": row["thstrm_nm"],
                                "thstrm_amount": int(row["thstrm_amount"]),
                                "frmtrm_nm": row["frmtrm_nm"],
                                "frmtrm_amount": int(row["frmtrm_amount"]),
                                "ord": row["ord"],
                                "currency": row["currency"],
                            }
                            financial_statement_list.append(financial_statement_dict)

                        # Batch insert and commit for financial_statement
                        session.bulk_insert_mappings(
                            FinancialStatement, financial_statement_list
                        )
                        session.commit()
                        logging.info("financial_statement commit ok")

                        # Query last inserted set of IDs
                        last_ids = (
                            session.query(FinancialStatement.id)
                            .order_by(FinancialStatement.id.desc())
                            .limit(len(financial_statement_list))
                            .all()
                        )
                        last_ids = [i[0] for i in reversed(last_ids)]

                        # Step 3: Prepare data for financial_annual_report and financial_quarterly_report
                        financial_annual_report_list = []
                        financial_quarterly_report_list = []

                        for idx, (_, row) in enumerate(df.iterrows()):
                            id_reference = last_ids[idx]

                            if reprt_code == "11011":
                                financial_annual_report_dict = {
                                    "id": id_reference,
                                    "bfefrmtrm_nm": row["bfefrmtrm_nm"],
                                    "bfefrmtrm_amount": int(row["bfefrmtrm_amount"]),
                                }
                                financial_annual_report_list.append(
                                    financial_annual_report_dict
                                )
                            else:
                                financial_quarterly_report_dict = {
                                    "id": id_reference,
                                    "frmtrm_q_nm": row["frmtrm_q_nm"],
                                    "frmtrm_q_amount": int(row["frmtrm_q_amount"]),
                                    "frmtrm_add_amount": int(row["frmtrm_add_amount"]),
                                    "thstrm_add_amount": int(row["thstrm_add_amount"]),
                                }
                                financial_quarterly_report_list.append(
                                    financial_quarterly_report_dict
                                )

                        # Batch insert
                        session.bulk_insert_mappings(
                            FinancialAnnualReport, financial_annual_report_list
                        )
                        session.bulk_insert_mappings(
                            FinancialQuarterlyReport,
                            financial_quarterly_report_list,
                        )

                        # Commit transaction
                        session.commit()
                        logging.info(
                            f"Saved data for corp_code: {corp_code}, year: {year}"
                        )
                    except IntegrityError as e:
                        session.rollback()
                        logging.error(
                            f"IntegrityError: A unique constraint or foreign key constraint violation occurred for corp_code: {corp_code}, year: {year}: {str(e)}"
                        )
                    except StatementError as e:
                        session.rollback()
                        logging.error(
                            f"StatementError: Invalid SQL expression or a bad parameter for corp_code: {corp_code}, year: {year}: {str(e)}"
                        )
                    except SQLAlchemyError as e:
                        session.rollback()
                        logging.error(
                            f"SQLAlchemyError: An unknown SQLAlchemy error occurred for corp_code: {corp_code}, year: {year}: {str(e)}"
                        )
                    except Exception as e:
                        session.rollback()
                        logging.error(
                            f"An unknown error occurred for corp_code: {corp_code}, year: {year}: {str(e)}"
                        )
                    finally:
                        session.close()


if *name* == "*main*":
    main()

```
#### config
##### constants.py
* ```python
DART_URL = "https://dart.fss.or.kr"
DART_API_URL = "https://opendart.fss.or.kr"
API_KEYS = [
    "xxx",
    "xxx",
    "xxx",
]
API_KEY = "xxxxx"
MAX_RETRIES = 3
DB_URI = "postgresql+psycopg2://skopenai:!skcc1234@infratf-db.postgres.database.azure.com:5432/chatbot?sslmode=allow"

```
#### database
##### db_connection.py
* ```python
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.constants import DB_URI

_engine = None
Base = sqlalchemy.orm.declarative_base()


# Private function or variable for engine creation, not intended for external use
def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DB_URI)
    return _engine


# Public function to get session, this is what will be called by external modules
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

```
#### models
##### corporate.py
* ```python
from sqlalchemy import Column, String
from database.db_connection import Base


class CorpInfo(Base):
    *tablename* = "corp_info"
    corp_code = Column(String(8), primary_key=True)
    corp_name = Column(String)
    corp_name_eng = Column(String)
    stock_name = Column(String)
    stock_code = Column(String(6))
    ceo_nm = Column(String)
    corp_cls = Column(String(1))
    jurir_no = Column(String(13))
    bizr_no = Column(String)
    adres = Column(String)
    hm_url = Column(String)
    ir_url = Column(String)
    phn_no = Column(String)
    fax_no = Column(String)
    induty_code = Column(String(10))
    est_dt = Column(String(8))
    acc_mt = Column(String(2))
    logo_img_url = Column(String)

```
##### finance.py
* ```python
from sqlalchemy import Column, Integer, String, BigInteger
from database.db_connection import Base


class FinancialReportBase(Base):
    *tablename* = "financial_report_base"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rcept_no = Column(String(14))
    reprt_code = Column(String(5), nullable=False)
    bsns_year = Column(String(4), nullable=False)
    corp_code = Column(String(8), nullable=False)
    report_type = Column(String(1), nullable=False)
    fs_type = Column(String(3), nullable=False)
    sj_div = Column(String(3), nullable=False)
    sj_nm = Column(String)
    account_id = Column(String(3), nullable=False)
    account_nm = Column(String)
    account_detail = Column(String)
    thstrm_nm = Column(String)
    thstrm_amount = Column(BigInteger)
    frmtrm_nm = Column(String(255))
    frmtrm_amount = Column(BigInteger)
    ord = Column(Integer)
    currency = Column(String(3))
    thstrm_add_amount = Column(BigInteger)
    frmtrm_q_nm = Column(String)
    frmtrm_q_amount = Column(BigInteger)
    frmtrm_add_amount = Column(BigInteger)
    bfefrmtrm_nm = Column(String)
    bfefrmtrm_amount = Column(BigInteger)

```
#### openDataReader
##### dart_list.py
* ```python
# -*- coding:utf-8 -*-
# 2020-2023 FinanceData.KR http://financedata.kr fb.com/financedata

import requests
import zipfile
import io
import os
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import logging
import time


# 1. 공시정보 - 공시검색(목록)
def list(
    api_key, corp_code="", start=None, end=None, kind="", kind_detail="", final=False
):
    start = pd.to_datetime(start) if start else pd.to_datetime("1900-01-01")
    end = pd.to_datetime(end) if end else datetime.today()
    call_count = 0

    url = "https://opendart.fss.or.kr/api/list.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bgn_de": start.strftime("%Y%m%d"),
        "end_de": end.strftime("%Y%m%d"),
        "last_reprt_at": "Y" if final else "N",  # 최종보고서 여부
        "page_no": 1,
        "page_count": 100,
    }
    if kind:
        params["pblntf_ty"] = kind  # 공시유형: 기본값 'A'=정기공시
    if kind_detail:
        params["pblntf_detail_ty"] = kind_detail

    def make_request(url, params):
        nonlocal call_count
        retries = 2
        while retries >= 0:
            try:
                response = requests.get(url, params=params, timeout=30, verify=False)
                call_count += 1
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logging.error(f"request error: message {e}")
                if retries == 0:
                    raise e
                time.sleep(5)
                retries -= 1
                call_count += 1

    response = make_request(url, params)
    try:
        tree = ET.XML(response.content)
        status = tree.find("status").text
        message = tree.find("message").text
        if status != "000":
            logging.error(f"API error! status: {status}, message: {message}")
            raise ValueError({"status": status, "message": message})
    except ET.ParseError as e:
        jo = response.json()
        if jo["status"] != "000":
            logging.error(
                f"ET.XML Error! status: {jo['status']} message: {response.text}"
            )
            print(ValueError(response.text))

    jo = response.json()
    if "list" not in jo:
        return pd.DataFrame(), call_count
    df = pd.DataFrame(jo["list"])

    # paging
    for page in range(2, jo["total_page"] + 1):
        params["page_no"] = page
        response = make_request(url, params)
        jo = response.json()
        df = pd.concat([df, pd.DataFrame(jo["list"])])
        df = df.reset_index(drop=True)
        time.sleep(1)
    return df, call_count


# 1-2. 공시정보 - 기업개황
def company(api_key, corp_code):
    url = "https://opendart.fss.or.kr/api/company.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
    }
    r = requests.get(url, params=params)
    try:
        tree = ET.XML(r.content)
        status = (tree.find("status").text,)
        message = tree.find("message").text
        if status != "000":
            raise ValueError({"status": status, "message": message})
    except ET.ParseError as e:
        pass
    return r.json()


# 1-2. 공시정보 - 기업개황: 지정된 이름(name)을 포함하는 회사들의 corp_code 리스트를 반환
def company_by_name(api_key, corp_code_list):
    url = "https://opendart.fss.or.kr/api/company.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": "",
    }
    company_list = []
    for corp_code in corp_code_list:
        params["corp_code"] = corp_code
        r = requests.get(url, params=params)
        company_list.append(r.json())
    return company_list


# 1-3. 공시정보 - (사업보고서) 공시서류원본파일
def document(api_key, rcp_no, cache=True):
    url = "https://opendart.fss.or.kr/api/document.xml"
    params = {
        "crtfc_key": api_key,
        "rcept_no": rcp_no,
    }

    r = requests.get(url, params=params)
    try:
        tree = ET.XML(r.text)
        status = tree.find("status").text
        message = tree.find("message").text
        if status != "000":
            raise ValueError({"status": status, "message": message})
    except ET.ParseError as e:
        pass

    zf = zipfile.ZipFile(io.BytesIO(r.content))
    info_list = zf.infolist()
    fnames = sorted([info.filename for info in info_list])
    xml_data = zf.read(fnames[0])

    try:
        xml_text = xml_data.decode("euc-kr")
    except UnicodeDecodeError as e:
        xml_text = xml_data.decode("utf-8")
    except UnicodeDecodeError as e:
        xml_text = xml_data

    return xml_text


# 1-3. 공시정보 - (사업보고서, 감사보고서) 공시서류원본문서파일
def document_all(api_key, rcp_no, cache=True):
    url = "https://opendart.fss.or.kr/api/document.xml"
    params = {
        "crtfc_key": api_key,
        "rcept_no": rcp_no,
    }

    r = requests.get(url, params=params)
    try:
        tree = ET.XML(r.text)
        status = tree.find("status").text
        message = tree.find("message").text
        if status != "000":
            raise ValueError({"status": status, "message": message})
    except ET.ParseError as e:
        pass

    zf = zipfile.ZipFile(io.BytesIO(r.content))
    info_list = zf.infolist()
    fnames = sorted([info.filename for info in info_list])
    xml_text_list = []
    for fname in fnames:
        xml_data = zf.read(fname)
        try:
            xml_text = xml_data.decode("euc-kr")
        except UnicodeDecodeError as e:
            xml_text = xml_data.decode("utf-8")
        except UnicodeDecodeError as e:
            xml_text = xml_data
        xml_text_list.append(xml_text)

    return xml_text_list


# 1-4 고유번호: api/corpCode.xml
def corp_codes(api_key):
    url = "https://opendart.fss.or.kr/api/corpCode.xml"
    params = {
        "crtfc_key": api_key,
    }

    r = requests.get(url, params=params, verify=False)
    try:
        tree = ET.XML(r.content)
        status = tree.find("status").text
        message = tree.find("message").text
        if status != "000":
            raise ValueError({"status": status, "message": message})
    except ET.ParseError as e:
        pass

    zf = zipfile.ZipFile(io.BytesIO(r.content))
    xml_data = zf.read("CORPCODE.xml")

    # XML to DataFrame
    tree = ET.XML(xml_data)
    all_records = []

    element = tree.findall("list")
    for i, child in enumerate(element):
        record = {}
        for i, subchild in enumerate(child):
            record[subchild.tag] = subchild.text
        all_records.append(record)
    return pd.DataFrame(all_records)

```
##### dart_utils.py
* ```python
# -*- coding:utf-8 -*-
# 2020-2022 FinanceData.KR http://financedata.kr fb.com/financedata

import os
import re
import time
from datetime import datetime
from pandas import to_datetime
from urllib.parse import urlparse, parse_qs, quote_plus
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import difflib
import logging
import time

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.3904.108 Safari/537.36"


def _validate_dates(start, end):
    start = to_datetime(start)
    end = to_datetime(end)

    if start is None:
        start = datetime(1970, 1, 1)
    if end is None:
        end = datetime.today()
    return start, end


def _requests_get_cache(url, headers=None):
    docs_cache_dir = "docs_cache"
    if not os.path.exists(docs_cache_dir):
        os.makedirs(docs_cache_dir)

    fn = os.path.join(docs_cache_dir, quote_plus(url))
    if not os.path.isfile(fn) or os.path.getsize(fn) == 0:
        with open(fn, "wt") as f:
            r = requests.get(url, headers=headers)
            f.write(r.text)
            xhtml_text = r.text
    else:
        with open(fn, "rt") as f:
            xhtml_text = f.read()
            return xhtml_text
    return xhtml_text


def list_date_ex(date=None, cache=True):
    """
    지정한 날짜의 보고서의 목록 전체를 데이터프레임으로 반환 합니다(시간 포함)
    * date: 조회일 (기본값: 당일)
    """
    date = pd.to_datetime(date) if date else datetime.today()
    date_str = date.strftime("%Y.%m.%d")

    columns = [
        "rcept_dt",
        "corp_cls",
        "corp_name",
        "rcept_no",
        "report_nm",
        "flr_nm",
        "rm",
    ]

    df_list = []
    for page in range(1, 100):
        time.sleep(0.1)
        url = f"http://dart.fss.or.kr/dsac001/search.ax?selectDate={date_str}&pageGrouping=A&currentPage={page}"
        headers = {"User-Agent": USER_AGENT}
        xhtml_text = (
            _requests_get_cache(url, headers=headers)
            if cache
            else requests.get(url, headers).text
        )

        if "검색된 자료가 없습니다" in xhtml_text:
            if page == 1:
                return pd.DataFrame(columns=columns)
            break

        data_list = []
        soup = BeautifulSoup(xhtml_text, features="lxml")
        trs = soup.table.tbody.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            hhmm = tds[0].text.strip()
            corp_class = tds[1].span.span.text
            name = tds[1].span.a.text.strip()
            rcp_no = tds[2].a["href"].split("=")[1]
            title = " ".join(tds[2].a.text.split())
            fr_name = tds[3].text
            rcp_date = tds[4].text.replace(".", "-")
            remark = "".join([span.text for span in tds[5].find_all("span")])
            dt = date.strftime("%Y-%m-%d") + " " + hhmm
            data_list.append([dt, corp_class, name, rcp_no, title, fr_name, remark])

        df = pd.DataFrame(data_list, columns=columns)
        df["rcept_dt"] = pd.to_datetime(df["rcept_dt"])
        df_list.append(df)
    merged = pd.concat(df_list)
    merged = merged.reset_index(drop=True)
    return merged


def sub_docs(rcp_no, match=None):
    """
    지정한 URL문서에 속해있는 하위 문서 목록정보(title, url)을 데이터프레임으로 반환합니다
    * rcp_no: 접수번호를 지정합니다. rcp_no 대신 첨부문서의 URL(http로 시작)을 사용할 수 도 있습니다.
    * match: 매칭할 문자열 (문자열을 지정하면 문서 제목과 가장 유사한 순서로 소트 합니다)
    """
    if rcp_no.isdecimal():
        r = requests.get(
            f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}",
            headers={"User-Agent": USER_AGENT},
        )
    elif rcp_no.startswith("http"):
        r = requests.get(rcp_no, headers={"User-Agent": USER_AGENT})
    else:
        raise ValueError("invalid `rcp_no`(or url)")

    ## 하위 문서 URL 추출
    multi_page_re = (
        "\s+node[12]\['text'\][ =]+\"(.*?)\"\;"
        "\s+node[12]\['id'\][ =]+\"(\d+)\";"
        "\s+node[12]\['rcpNo'\][ =]+\"(\d+)\";"
        "\s+node[12]\['dcmNo'\][ =]+\"(\d+)\";"
        "\s+node[12]\['eleId'\][ =]+\"(\d+)\";"
        "\s+node[12]\['offset'\][ =]+\"(\d+)\";"
        "\s+node[12]\['length'\][ =]+\"(\d+)\";"
        "\s+node[12]\['dtd'\][ =]+\"(.*?)\";"
        "\s+node[12]\['tocNo'\][ =]+\"(\d+)\";"
    )
    matches = re.findall(multi_page_re, r.text)
    if len(matches) > 0:
        row_list = []
        for m in matches:
            doc_id = m[1]
            doc_title = m[0]
            params = f"rcpNo={m[2]}&dcmNo={m[3]}&eleId={m[4]}&offset={m[5]}&length={m[6]}&dtd={m[7]}"
            doc_url = f"http://dart.fss.or.kr/report/viewer.do?{params}"
            row_list.append([doc_title, doc_url])
        df = pd.DataFrame(row_list, columns=["title", "url"])
        if match:
            df["similarity"] = df["title"].apply(
                lambda x: difflib.SequenceMatcher(None, x, match).ratio()
            )
            df = df.sort_values("similarity", ascending=False)
        return df[[title, url]]
    else:
        single_page_re = (
            "\t\tviewDoc\('(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\S+)',''\)\;"
        )
        matches = re.findall(single_page_re, r.text)
        if len(matches) > 0:
            doc_title = BeautifulSoup(r.text, features="lxml").title.text.strip()
            m = matches[0]
            params = f"rcpNo={m[0]}&dcmNo={m[1]}&eleId={m[2]}&offset={m[3]}&length={m[4]}&dtd={m[5]}"
            doc_url = f"http://dart.fss.or.kr/report/viewer.do?{params}"
            return pd.DataFrame([[doc_title, doc_url]], columns=["title", "url"])
        else:
            raise Exception(f"{url} 하위 페이지를 포함하고 있지 않습니다")

    return pd.DataFrame(None, columns=["title", "url"])


def attach_docs(rcp_no, match=None):
    """
    첨부문서의 목록정보(title, url)을 데이터프레임으로 반환합니다. match를 지정하면 지정한 문자열과 가장 유사한 순서로 소트하여 데이터프레임을 반환 합니다.
    * rcp_no: 접수번호
    * match: 문서 제목과 가장 유사한 순서로 소트
    """
    r = requests.get(
        f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}",
        headers={"User-Agent": USER_AGENT},
    )
    soup = BeautifulSoup(r.text, features="lxml")

    row_list = []
    att = soup.find(id="att")
    if not att:
        raise Exception(f"rcp_no={rcp_no} 첨부문서를 포함하고 있지 않습니다")

    for opt in att.find_all("option"):
        if opt["value"] == "null":
            continue
        title = " ".join(opt.text.split())
        url = f'http://dart.fss.or.kr/dsaf001/main.do?{opt["value"]}'
        row_list.append([title, url])

    df = pd.DataFrame(row_list, columns=["title", "url"])
    if match:
        df["similarity"] = df.title.apply(
            lambda x: difflib.SequenceMatcher(None, x, match).ratio()
        )
        df = df.sort_values("similarity", ascending=False)
    return df[[title, url]].copy()


def attach_files(arg):  # rcp_no or URL
    """
    접수번호(rcp_no)에 속한 첨부파일 목록정보를 dict 형식으로 반환합니다.
    * rcp_no: 접수번호를 지정합니다. rcp_no 대신 첨부문서의 URL(http로 시작)을 사용할 수 도 있습니다.
    """
    url = (
        arg
        if arg.startswith("http")
        else f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={arg}"
    )
    r = requests.get(url, headers={"User-Agent": USER_AGENT})

    rcp_no = dcm_no = None
    matches = re.findall(
        "\s+node[12]\['rcpNo'\][ =]+\"(\d+)\";"
        + "\s+node[12]\['dcmNo'\][ =]+\"(\d+)\";",
        r.text,
    )
    if matches:
        rcp_no = matches[0][0]
        dcm_no = matches[0][1]

    if not dcm_no:
        print(f"{url} does not have download page. 다운로드 페이지를 포함하고 있지 않습니다.")

    download_url = (
        f"http://dart.fss.or.kr/pdf/download/main.do?rcp_no={rcp_no}&dcm_no={dcm_no}"
    )
    r = requests.get(download_url, headers={"User-Agent": USER_AGENT})
    soup = BeautifulSoup(r.text, features="lxml")
    table = soup.find("table")
    if not table:
        return dict()

    attach_files_dict = {}
    for tr in table.tbody.find_all("tr"):
        tds = tr.find_all("td")
        fname = tds[0].text
        flink = "http://dart.fss.or.kr" + tds[1].a["href"]
        attach_files_dict[fname] = flink
    return attach_files_dict


def download(url, save_path, fn=None):
    fn = fn if fn else url.split("/")[-1]
    call_count = 0

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_path = os.path.join(save_path, fn)

    def make_request(url):
        nonlocal call_count
        retries = 2
        while retries >= 0:
            try:
                response = requests.get(
                    url,
                    stream=True,
                    headers={"User-Agent": USER_AGENT},
                    timeout=30,
                    verify=False,
                )
                call_count += 1
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if retries == 0:
                    logging.error(f"Failed to download after Max retries. Error: {e}")
                    return None
                call_count += 1
                retries -= 1
                logging.info(f"Retrying...")
                time.sleep(5)

    response = make_request(url)
    if response is None:
        return None, call_count

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=4096):
            f.write(chunk) if chunk else None
    return file_path, call_count

```
##### OpenDataReader.py
* ```python
# dart.py
# -*- coding:utf-8 -*-
# 2020~2023 FinanceData.KR http://financedata.kr fb.com/financedata

import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from . import dart_list
from . import dart_utils


class OpenDartReader:
    # init corp_codes (회사 고유번호 데이터)
    def *init*(self, api_key):
        # create cache directory if not exists
        docs_cache_dir = "docs_cache"
        if not os.path.exists(docs_cache_dir):
            os.makedirs(docs_cache_dir)

        # read and return document if exists
        fn = "opendartreader_corp_codes_{}.pkl".format(
            datetime.today().strftime("%Y%m%d")
        )
        fn_cache = os.path.join(docs_cache_dir, fn)
        for fn_rm in glob.glob(
            os.path.join(docs_cache_dir, "opendartreader_corp_codes_*")
        ):
            if fn_rm == fn_cache:
                continue
            os.remove(fn_rm)
        if not os.path.exists(fn_cache):
            df = dart_list.corp_codes(api_key)
            df.to_pickle(fn_cache)

        self.corp_codes = pd.read_pickle(fn_cache)
        self.api_key = api_key

    # 1. 공시정보
    # 1-1. 공시정보 - 공시검색
    def list(
        self, corp=None, start=None, end=None, kind="", kind_detail="", final=True
    ):
        """
        DART 보고서의 목록을 DataFrame으로 반환
        * corp: 종목코드 (고유번호, 법인명도 가능)
        * start: 조회 시작일 (기본값: 1990-01-01')
        * end: 조회 종료일 (기본값: 당일)
        * kind: 보고서 종류:  A=정기공시, B=주요사항보고, C=발행공시, D=지분공시, E=기타공시,
                                        F=외부감사관련, G=펀드공시, H=자산유동화, I=거래소공시, J=공정위공시
        * final: 최종보고서 여부 (기본값: True)
        """
        if corp:
            corp_code = self.find_corp_code(corp)
            if not corp_code:
                raise ValueError(f'could not find "{corp}"')
        else:
            corp_code = ""
        return dart_list.list(
            self.api_key, corp_code, start, end, kind, kind_detail, final
        )

    def company_by_name(self, name):
        df = self.corp_codes[self.corp_codes["corp_name"].str.contains(name)]
        corp_code_list = list(df["corp_code"])
        return dart_list.company_by_name(self.api_key, corp_code_list)

    # 1-3. 공시정보 - 공시서류원본문서 (사업보고서)
    def document(self, rcp_no, cache=True):
        return dart_list.document(self.api_key, rcp_no, cache=cache)

    # 1-3. 공시정보 - 공시서류원본문서 전체 (사업보고서, 감사보고서)
    def document_all(self, rcp_no, cache=True):
        return dart_list.document_all(self.api_key, rcp_no, cache=cache)

    # 1-4. 공시정보 - 고유번호: corp(종목코드 혹은 회사이름) to 고유번호(corp_code)
    def find_corp_code(self, corp):
        if not corp.isdigit():
            df = self.corp_codes[self.corp_codes["corp_name"] == corp]
        elif corp.isdigit() and len(corp) == 6:
            df = self.corp_codes[self.corp_codes["stock_code"] == corp]
        else:
            df = self.corp_codes[self.corp_codes["corp_code"] == corp]
        return None if df.empty else df.iloc[0]["corp_code"]

    # utils: url 을 fn 으로 저장
    def download(self, url, save_path, fn):
        return dart_utils.download(url, save_path, fn)

    def retrieve(self, url, fn):
        print("retrieve() will deprecated. use download() instead")
        return dart_utils.download(url, fn)

```
#### STOCK
##### stock_api_call.py
* ```python
"""
#!/usr/bin/python
"""
"""
# Status 정보
- 000 :정상
- 010 :등록되지 않은 키입니다.
- 011 :사용할 수 없는 키입니다. 오픈API에 등록되었으나, 일시적으로 사용 중지된 키를 통하여 검색하는 경우 발생합니다.
- 012 :접근할 수 없는 IP입니다.
- 013 :조회된 데이타가 없습니다.
- 014 :파일이 존재하지 않습니다.
- 020 :요청 제한을 초과하였습니다.
       일반적으로는 10,000건 이상의 요청에 대하여 이 에러 메시지가 발생되나, 요청 제한이 다르게 설정된 경우에는 이에 준하여 발생됩니다.
- 021 :조회 가능한 회사 개수가 초과하였습니다.(최대 100건)
- 100 :필드의 부적절한 값입니다. 필드 설명에 없는 값을 사용한 경우에 발생하는 메시지입니다.
- 101 :부적절한 접근입니다.
- 800 :시스템 점검으로 인한 서비스가 중지 중입니다.
- 900 :정의되지 않은 오류가 발생하였습니다.
- 901 :사용자 계정의 개인정보 보유기간이 만료되어 사용할 수 없는 키입니다. 관리자 이메일(opendart@fss.or.kr)로 문의하시기 바랍니다.
"""

import requests
import json
import pandas as pd
import logging
from datetime import datetime, timedelta


def get_stock_price(output_file, page_count):
    """
    1. 공공데이터 포털 중 주식시세 조회

    2. Parameters:
        output_file: 저장할 파일명. 기본값은 corp_code.csv으로 main.py에서 지정.
        page_count: 한 페이지 당 건수. 모든 상장사 종가정보를 한 번에 받고 싶으면 최쇠 3000으로 설정. 다만 상장사가 늘어나면 수정해야 함.

    3. Returns:

    4. Result: save dataframe into csv file
    """
    yesterday = (datetime.now() - timedelta(1)).strftime("%Y%m%d")
    serviceKey = "wQYTTyN8nau6MaMVqoV5fSiJaU1Z8YxB1cugqVl3%2FNXhVms%2BqMxR%2FEw8%2B3dqRp%2FnkYXSyh%2BUACQ5BxnoC0Zy5A%3D%3D"
    stock_price_url = f"""https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo?serviceKey={serviceKey}&numOfRows={page_count}&pageNo=1&resultType=json"""
    print(f"url: {stock_price_url}")
    try:
        response = requests.get(stock_price_url, timeout=30)
        response.raise_for_status()
        stock_price_json = json.loads(response.text)
        items_content = (
            stock_price_json.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
        )
        stocks_dt = pd.DataFrame(items_content)
        yesterday_stocks = stocks_dt[stocks_dt["basDt"] == yesterday]
        yesterday_stocks.to_csv(output_file, index=False)

    except requests.Timeout as time_err:
        print(f"Timeout error occurred: {time_err}")
    except requests.HTTPError as http_err:
        logging.error(f"HTTP error: {http_err}")
    except requests.ConnectionError as conn_err:
        logging.error(f"Connection error: {conn_err}")
    except requests.RequestException as e:
        logging.error(f"Network error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    return

```
#### utility
##### extract_corp_code_from_files.py
* ```python
import os
import re

# Set the directory path where your files are located
directory_path = "./finance_download"

# The output file where the distinct corp_codes will be written
output_file_path = "./extracted_corp_code_from_finance_directory.txt"

# Initialize a set to store unique corp_codes
corp_codes = set()

# Regex pattern to match 'corp_code' in the file names
pattern = re.compile(r"(\w+)_\d{4}_1101._OFS.csv")

# List all files in the directory
for filename in os.listdir(directory_path):
    # Check if the filename matches the pattern
    match = pattern.match(filename)
    if match:
        # Add the corp_code to the set
        corp_codes.add(match.group(1))

# Write the distinct corp_codes to the output file
with open(output_file_path, "w") as file:
    for code in sorted(corp_codes):
        file.write(code + "\n")

print(f"Distinct corp_codes have been written to {output_file_path}")

```
##### extract_error.py
* ```python
import argparse
import re


def main(input_file_path, output_file_path):
    pattern = r"Error for corp_code: (\d+)"
    with open(input_file_path, "r", encoding="utf-8") as infile, open(
        output_file_path, "w"
    ) as outfile:
        for line in infile:
            match = re.search(pattern, line)
            if match:
                corp_code = match.group(1)
                outfile.write(f"{corp_code}\n")


if *name* == "*main*":
    parser = argparse.ArgumentParser(
        description='Extract lines containing "Error for corp_code" from an input file.'
    )
    parser.add_argument(
        "input_file_path", type=str, help="Path to the tokaicrawler log file."
    )
    parser.add_argument("output_file_path", type=str, help="Path to the output file.")

    args = parser.parse_args()
    main(args.input_file_path, args.output_file_path)

```
##### extract_modified_corp_code.py
* ```python
import csv
import argparse
from datetime import datetime, timedelta

# Initialize argparse
parser = argparse.ArgumentParser(
    description="Filter a CSV file based on the 'modify_date' field."
)
parser.add_argument("input_file", help="The input CSV file to be filtered.")
parser.add_argument(
    "start_date", help="The start date for filtering in YYYYMMDD format."
)
parser.add_argument("end_date", help="The end date for filtering in YYYYMMDD format.")
args = parser.parse_args()

# Get the start_date and end_date from the arguments
start_date = args.start_date
end_date = args.end_date

try:
    datetime.strptime(start_date, "%Y%m%d")
    datetime.strptime(end_date, "%Y%m%d")
except ValueError:
    print("Invalid date format. Please use YYYYMMDD.")
    exit(1)

# Open the input CSV file for reading
with open(args.input_file, "r", newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)

    # Create an output file name based on the input file name
    output_file_name = f"{start_date}_{end_date}_corp_code.csv"

    # Open an output CSV file for writing
    with open(output_file_name, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["corp_code", "corp_name", "stock_code", "modify_date"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        for row in reader:
            if start_date <= row["modify_date"] <= end_date:
                writer.writerow(row)

```
##### extract_stock_code.py
* ```python
import csv
import sys


def filter_rows_with_stock_code(input_file_path, output_file_path):
    with open(input_file_path, "r", newline="", encoding="utf-8") as input_csvfile:
        csv_reader = csv.DictReader(input_csvfile)

        with open(
            output_file_path, "w", newline="", encoding="utf-8"
        ) as output_csvfile:
            fieldnames = csv_reader.fieldnames
            csv_writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)

            csv_writer.writeheader()

            for row in csv_reader:
                if row["stock_code"]:
                    csv_writer.writerow(row)


if *name* == "*main*":
    if len(sys.argv) < 3:
        print("Usage: python script.py <input_file.csv> <output_file.csv>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    filter_rows_with_stock_code(input_file_path, output_file_path)

```
##### insert_corp_info_one_by_one.py
* ```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import argparse
from database.db_connection import get_session
from models.corporate import CorpInfo


def save_csv_to_db(input_csv):
    session = get_session()

    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv, dtype=str)
    df.where(pd.notna(df), None, inplace=True)

    first_header = True
    # Loop through the DataFrame and add each row to the database
    for index, row in df.iterrows():
        if first_header:
            first_header = False
        elif row["corp_code"] == "corp_code":
            continue
        try:
            # Your table class definition might differ. Make sure to match it accordingly.
            corp_info_instance = CorpInfo(
                corp_code=row["corp_code"],
                corp_name=row["corp_name"],
                corp_name_eng=row["corp_name_eng"],
                stock_name=row["stock_name"],
                stock_code=row["stock_code"],
                ceo_nm=row["ceo_nm"],
                corp_cls=row["corp_cls"],
                jurir_no=row["jurir_no"],
                bizr_no=row["bizr_no"],
                adres=row["adres"],
                hm_url=row["hm_url"],
                ir_url=row["ir_url"],
                phn_no=row["phn_no"],
                fax_no=row["fax_no"],
                induty_code=row["induty_code"],
                est_dt=row["est_dt"],
                acc_mt=row["acc_mt"],
                # logo_img_url=row['logo_img_url']  # Assuming this field is not in your CSV
            )
            session.add(corp_info_instance)
            # Commit the changes
            session.commit()
        except Exception as e:
            print("----------------------------------------------------------------")
            print(f"Error occurred while processing row {index}: {e}")
            print(f"Row data: {row}")
            print("----------------------------------------------------------------")
            session.rollback()
            return


parser = argparse.ArgumentParser(
    description="Save one-by-one from corp_info.csv to Database."
)
parser.add_argument("input_csv", help="Path to the input CSV file.")

# Run the function
if *name* == "*main*":
    args = parser.parse_args()
    save_csv_to_db(args.input_csv)

```
##### make_retry_list.py
* ```python
import sys
import csv


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python script.py <tokaicrawler.log> <split_file_#.csv> <output_file>"
        )
        sys.exit(1)

    list_of_codes_file = sys.argv[1]
    search_file = sys.argv[2]
    output_file = sys.argv[3]

    # Step 1: Read codes from the list_of_codes_file
    codes_to_search = set()
    with open(list_of_codes_file, "r", encoding="utf-8") as f:
        for line in f:
            if "Error for corp_code" in line:
                print(f"found error: {line}")
                code = line.split("corp_code: ")[1].split(" ")[0]
                codes_to_search.add(code.strip())

    print(f"found code: {codes_to_search}")
    # Step 2: Find matching codes from the search_file and save to output_file
    with open(search_file, "r", encoding="utf-8") as f, open(
        output_file, "w", encoding="utf-8", newline=""
    ) as outf:
        reader = csv.reader(f)
        writer = csv.writer(outf)

        # Write the header to the output CSV file
        header = next(reader)
        writer.writerow(header)

        for row in reader:
            corp_code = row[0]
            if corp_code in codes_to_search:
                print(f"found error corp_code: {corp_code}")
                writer.writerow(row)


if *name* == "*main*":
    main()

```
##### split_file.py
* ```python
import csv
import argparse
import os


def main(input_file, loop_count):
    output_file_prefix = (
        f"split_file_{os.path.splitext(os.path.basename(input_file))[0]}"
    )
    header = None
    row_count = 0
    file_number = 1
    current_file = None
    csv_writer = None

    # Split big file into smaller file with 9600 rows each
    with open(input_file, "r", encoding="utf-8", newline="") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if header is None:
                header = row
                continue
            if row_count == 0:
                if current_file:
                    current_file.close()
                current_file = open(
                    f"{output_file_prefix}_{file_number}.csv",
                    "w",
                    newline="",
                    encoding="utf-8",
                )
                csv_writer = csv.writer(current_file)
                csv_writer.writerow(header)
                file_number += 1

            csv_writer.writerow(row)
            row_count = (row_count + 1) % loop_count
    if current_file:
        current_file.close()


if *name* == "*main*":
    parser = argparse.ArgumentParser(description="Split a large file")
    parser.add_argument("input_file", type=str, help="Path to the input csv")
    parser.add_argument(
        "loop_count", type=int, help="Number of rows in each split file"
    )

    args = parser.parse_args()
    main(args.input_file, args.loop_count)

```
