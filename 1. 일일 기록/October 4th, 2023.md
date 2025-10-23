---
title: "October 4th, 2023"
created: 2023-10-04 07:12:28
updated: 2023-10-25 10:33:42
---
  * 07:12 긴 휴일 끝에 다시 시작.
  * 14:30 LLM 스트리밍 도중 에러를 발생시키는 방법
    * 서버에서 임의로 HTTPException 발생시켜서 내가 원하는 대로 에러 메시지를 만들어서 전달할 수 있도록 에러 테스트용 코드 생성할 수 있음.
    * 서버에서 HTTPException 발생시키는 대신 스트리밍 데이터에 json 데이터 넣어서 처리하는 방식
      * 서버쪽 코드
        * 에러 발생시키는 코드
          * ```python
def inquire(self, func_name: str, **kwargs) -> Annotated[Generator, str]:
        print("에러 메시지 테스트")
        import json

        yield json.dumps({"error": True, "code": 452, "detail": "custome message"})
        ...이하 동일```
        * 원본 전체 코드
          * ```python
from langchain.adapters import openai as lc_openai
from langchain.callbacks import get_openai_callback
from typing import Annotated, Generator, List, Dict
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import (
    APIRouter,
    Form,
    UploadFile,
    Depends,
    HTTPException,
    File,
    status,
    BackgroundTasks,
    Request,
)
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, desc, join, asc, func, and_
from collections import defaultdict
from api.v1.endpoints.utils import TestType, validate_inputs
from api.common.user_exception import UnsupportedFileError
from api.common.token_count import TokenCounter
from schemas.document import EmbeddedFileDto
from schemas.chat import CompletionUserInput, RetrievalUserInput, LLMSelect
from schemas.search import UploadOption, UploadOptionSummary
from schemas.chat_history import ChatInput
from api.v1.deps import decode_auth_header, get_db
from service import (
    call_retrieval_streaming_search,
    call_retrieval_search,
    call_retrieval_qa,
)
from crud import crud_embedded_file
from service.utils import elapse_time, elapse_time_async, print_log_async, print_log
from models.chat_head import ChatHead
from models.chat_history import ChatHistory
from api.interface.vectorstore import VectorDBInterface
from service.docs_load.doc_loader import VectorDBFactory
from settings import DEFAULT_VECTOR_DB
import traceback
import shutil
import logging

router = APIRouter()

user_chat_history: Dict[str, List[Dict[str, str]]] = {}


################### LLM ###################
# streaming chat
@print_log_async
@router.get("/chat")
def chat(
    prompt: str,
    modelType: str = "azure",
    modelVersion: float = 4.0,
    streaming: bool = True,
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
):
    validate_inputs(
        [
            {
                "type": TestType.STR,
                "name": "prompt",
                "val": prompt,
                "_if": {"min_length": 5},
            },
            {
                "type": TestType.STR,
                "name": "modelType",
                "val": modelType,
                "_if": {"include": ["azure", "public"]},
            },
            {
                "type": TestType.STR,
                "name": "modelVersion",
                "val": str(modelVersion),
                "_if": {"include": ["3.5", "4.0"]},
            },
        ]
    )
    from service.llm_search import simple_chat

    # 토큰카운터 초기화
    llm_select = LLMSelect(modelType=modelType, modelVersion=modelVersion)
    TokenCounter(user_id, llm_select=llm_select, app="chat", db=db)

    try:
        return StreamingResponse(
            simple_chat(
                user_id,
                prompt,
                llm_select,
                streaming,
            ),
            media_type="text/html",
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@print_log
@router.post("/chat/qa")
def chat_on_doc(
    qa_input: RetrievalUserInput,
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
):
    # 토큰카운터 초기화
    token_counter = TokenCounter(user_id, llm_select=qa_input.llm, app="report", db=db)

    with get_openai_callback() as cb:
        # 입력한 벡터파일들을 병합하여 반환.
        try:
            doc_llm = InquiryLLM(user_id, qa_input, db)
            answer, source = doc_llm.inquire(InquiryLLM.CHAT_SEARCH)

            return JSONResponse(
                content={"result": answer, "source": source},
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
        finally:
            token_counter.set_stats(**cb.*dict*)
            token_counter.save_db(is_logging=True)
            # 사용 후 카운터 초기화
            TokenCounter.dispose_userdata(user_id)


@print_log
@router.post("/chat/retrieval")
def search_on_doc(
    qa_input: RetrievalUserInput,
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
):
    validate_inputs(
        [
            {
                "type": TestType.NUM,
                "name": "docIds",
                "val": len(qa_input.options.doc_ids),
                "_if": {"min_value": 1},
            },
        ]
    )
    # 토큰카운터 초기화
    token_counter = TokenCounter(user_id, llm_select=qa_input.llm, app="report", db=db)
    with get_openai_callback() as cb:
        try:
            doc_llm = InquiryLLM(user_id, qa_input, db)
            answer = doc_llm.inquire(InquiryLLM.KEYWORD_SEARCH)

            return JSONResponse(
                content={"result": answer}, status_code=status.HTTP_200_OK
            )

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
        finally:
            token_counter.set_stats(**cb.*dict*)
            token_counter.save_db(is_logging=True)
            # 사용 후 카운터 초기화
            TokenCounter.dispose_userdata(user_id)


@print_log
@router.post("/chat/streaming-retrieval")
def search_on_doc_streaming(
    qa_input: RetrievalUserInput,
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
):
    validate_inputs(
        [
            {
                "type": TestType.NUM,
                "name": "docIds",
                "val": len(qa_input.options.doc_ids),
                "_if": {"min_value": 1},
            },
        ]
    )
    # 토큰카운터 초기화
    TokenCounter(user_id, llm_select=qa_input.llm, app="report", db=db)
    try:
        doc_llm = InquiryLLM(user_id, qa_input, db)
        answer = doc_llm.inquire(InquiryLLM.STERAMING_SEARCH)

        return StreamingResponse(answer, media_type="text/html")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


############## 메인화면내 chat기능 ######################
# streaming chat
@router.post("/chat_chain")
async def chat_chain(
    chat_input: ChatInput,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(decode_auth_header),
    db: Session = Depends(get_db),
):
    prompt = chat_input.prompt
    print(f"prompt: {prompt}, user_id: {user_id}")

    # when chat_input.init is true, it means new chat started.
    # To save current chat later, get the new history_id.
    if chat_input.init:
        try:
            max_history_id = (
                db.query(func.max(ChatHead.history_id))
                .filter(ChatHead.user_id == user_id)
                .scalar()
            )
            if max_history_id is None:
                max_history_id = 0
            else:
                max_history_id += 1
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail="history_id error")

        new_chat_head = ChatHead(
            user_id=user_id,
            service_type=chat_input.service_type,
            history_id=max_history_id,
        )
        db.add(new_chat_head)
        db.commit()
    else:
        try:
            max_history_id = (
                db.query(func.max(ChatHead.history_id))
                .filter(ChatHead.user_id == user_id)
                .scalar()
            )
            if max_history_id is None:
                logging.error(f"max_history_id is None for {user_id}")
                raise HTTPException(status_code=500, detail="history_id error")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail="history_id error")

    return StreamingResponse(
        stream_handler(user_id, max_history_id, chat_input, db, background_tasks),
        media_type="text/plain",
    )


async def insert_chat_history(user_id, history_id, new_dict, chat_input, db):
    new_chat_history = ChatHistory(
        user_id=user_id,
        service_type=chat_input.service_type,
        history_id=history_id,
        role=new_dict["role"],
        content=new_dict["content"],
        regen=chat_input.regen,
    )
    db.add(new_chat_history)
    db.commit()


def stream_handler(user_id, history_id, chat_input: ChatInput, db, background_tasks):
    if chat_input.init or user_id not in user_chat_history:
        user_chat_history[user_id] = []

    new_data = {"role": "user", "content": chat_input.prompt}
    user_chat_history[user_id].append(new_data)
    background_tasks.add_task(
        insert_chat_history, user_id, history_id, new_data, chat_input, db
    )

    lc_result = lc_openai.ChatCompletion.create(
        messages=user_chat_history[user_id],
        model=chat_input.model,
        temperature=1.0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stream=True,
    )

    final_result = ""
    for chunk in lc_result:
        content = chunk["choices"][0].get("delta", {}).get("content")
        # logging.info(f'{content}')
        if content is not None:
            final_result += content
            yield content
        else:
            new_data = {"role": "system", "content": final_result}
            user_chat_history[user_id].append(new_data)
            background_tasks.add_task(
                insert_chat_history, user_id, history_id, new_data, chat_input, db
            )


@router.api_route("/chat_history", methods=["GET", "DELETE"])
async def chat_history(
    request: Request,
    user_id: str = Depends(decode_auth_header),
    db: Session = Depends(get_db),
):
    method = request.method

    if method == "GET":
        logging.debug("GET")
        service_type = request.query_params.get("service_type")
        stmt = (
            select(ChatHistory, ChatHead)
            .select_from(
                join(
                    ChatHistory,
                    ChatHead,
                    and_(
                        ChatHistory.history_id == ChatHead.history_id,
                        ChatHistory.user_id == ChatHead.user_id,
                    ),
                )
            )
            .where(ChatHistory.user_id == user_id)
            .where(ChatHistory.service_type == service_type)
            .order_by(desc(ChatHead.create_dt), asc(ChatHistory.create_dt))
        )
        result = db.execute(stmt)
        chat_history = result.fetchall()
        # print(f"chat_history: {chat_history}")

        grouped_chat = defaultdict(list)

        for record in chat_history:
            chat_head = record.ChatHead
            chat_history = record.ChatHistory
            grouped_chat[chat_head.history_id].append(
                {"chatHistory": chat_history, "updateAt": chat_head.create_dt}
            )

        formatted_records = []
        for historyId, items in grouped_chat.items():
            chat_history_formatted = [
                {
                    "role": item["chatHistory"].role,
                    "content": item["chatHistory"].content,
                }
                for item in items
            ]
            create_dt = items[0]["updateAt"]
            formatted_records.append(
                {
                    "historyId": historyId,
                    "serviceType": chat_history.service_type,
                    "chatHistory": chat_history_formatted,
                    "updateAt": create_dt.isoformat(),
                }
            )

        print(f"chat_history: {formatted_records}")
        return {"chat_history": formatted_records}
    elif method == "DELETE":
        try:
            form_data = await request.json()

            history_id = form_data.get("history_id")
            service_type = form_data.get("service_type")
            stmt = delete(ChatHead).where(
                (ChatHead.user_id == user_id)
                & (ChatHead.service_type == service_type)
                & (ChatHead.history_id == history_id)
            )
            db.execute(stmt)
            db.commit()
        except:
            raise HTTPException(status_code=400, detail="Invalid request body")

        return {"message": "chat history deleted"}
    else:
        return {"message": "Method not supported"}


############### 문서관리 + 프롬프트 + 문서요약 ########################


@router.post("/completion")
@print_log
def prompt(
    user_input: CompletionUserInput,
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
):
    from crud.crud_dart import get_emb_list
    from service.llm_search import simple_chat

    answer = None
    shared_docs_seqs = []
    corp_code = None
    # 회사코드가 들어오면 해당 임베딩문서 ID목록을 취득한다.
    if user_input.references.company and user_input.references.company.company_code:
        corp_code = user_input.references.company.company_code

        if corp_code:
            shared_docs_seqs = list(map(lambda e: e.seq, get_emb_list(corp_code, db)))

    # 토큰카운터 초기화
    token_counter = TokenCounter(
        user_id, llm_select=user_input.llm, app="report", db=db
    )

    # userDoc가 있거나 임베딩 공유파일이 존재할 때
    try:
        if user_input.references.userdoc or len(shared_docs_seqs) > 0:
            token_counter.set_app("report")
            # docIds는 타API에서 사용되고있음.
            # userDocs를 docIds에 추가한다.
            emb_id_list = user_input.references.userdoc
            if emb_id_list:
                emb_id_list += shared_docs_seqs
            else:
                emb_id_list = shared_docs_seqs
            # 동일 문서번호가 일을 경우대비 병합.
            # 참고) 개인, 공유는 별개로 일련번호가 생성되므로 가능성은 없음.
            user_input.options.doc_ids = list(set(emb_id_list))

            doc_llm = InquiryLLM(user_id, user_input, db)
            answer = doc_llm.inquire(InquiryLLM.STERAMING_SEARCH)

        else:
            token_counter.set_app("chat")

            prompt = user_input.prompt
            answer = simple_chat(user_id, prompt, user_input.llm, streaming=True)

        return StreamingResponse(answer, media_type="text/html")

    except ValueError as err:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    except FileNotFoundError as err:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))

    except Exception as err:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        )


# 문서요약
@router.post("/doc/summary")
async def summarize_docs(
    chain_type: str = "map_reduce",
    temperature: float = 0.5,
    llm_select: LLMSelect = Depends(LLMSelect.as_form),
    upload_option: UploadOptionSummary = Depends(UploadOptionSummary.as_form),
    file: UploadFile = File(),
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
) -> JSONResponse:
    validate_inputs(
        [
            {
                "type": TestType.LIST,
                "name": "files",
                "val": [file],
            },
            {
                "type": TestType.STR,
                "name": "chain_type",
                "val": chain_type,
                "_if": {"include": ["map_reduce", "stuff", "refine"]},
            },
            {
                "type": TestType.NUM,
                "name": "temperature",
                "val": temperature,
                "_if": {"min_value": 0, "max_value": 1},
            },
        ]
    )
    from service.llm_search import summarize_docs
    from service.utils import upload_files

    # 업로드파일을 저장한다.
    dir_path = await upload_files([file])

    # 토큰카운터 초기화
    token_counter = TokenCounter(user_id, llm_select=llm_select, app="summary", db=db)

    with get_openai_callback() as cb:
        try:
            summary = await summarize_docs(
                user_id, chain_type, temperature, dir_path, upload_option
            )

            return JSONResponse(
                content={"result": summary}, status_code=status.HTTP_200_OK
            )
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        finally:
            # 원본파일을 삭제한다.
            shutil.rmtree(dir_path)

            if cb.total_tokens > 0:
                token_counter.set_stats(**cb.*dict*)
                token_counter.save_db(is_logging=True)
            # 사용 후 카운터 초기화
            TokenCounter.dispose_userdata(user_id)


# 임베딩 k건 조회
@router.get("/doc/query")
@elapse_time
def search_on_similarity(
    query: str,
    sourcefiles: str,
    top: int = 3,
    modelType: str = "azure",
    modelVersion: float = 4.0,
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
) -> JSONResponse:
    validate_inputs(
        [
            {
                "type": TestType.STR,
                "name": "query",
                "val": query,
                "_if": {"min_length": 5},
            },
            {"type": TestType.STRS_NUM, "name": "sourcefiles", "val": sourcefiles},
            {"type": TestType.NUM, "name": "top", "val": top, "_if": {"min_value": 1}},
            {
                "type": TestType.STR,
                "name": "modelType",
                "val": modelType,
                "_if": {"include": ["azure", "public"]},
            },
            {
                "type": TestType.STR,
                "name": "modelVersion",
                "val": str(modelVersion),
                "_if": {"include": ["3.5", "4.0"]},
            },
        ]
    )

    from crud import crud_embedded_file

    k = top
    ref_doc_seqs = list(map(lambda s: int(s), sourcefiles.split(",")))
    query = query
    answer = []

    # 참고문서목록을 취득한다.
    docs_list = crud_embedded_file.get_documents_by_seqs(db, user_id, ref_doc_seqs)
    if len(docs_list) > 0:
        vectorstore: VectorDBInterface = VectorDBFactory.create(DEFAULT_VECTOR_DB)
        # 벡터스토어에서 관련정보를 취득한다.
        llm_search = LLMSelect(model_type=modelType, model_version=modelVersion)

        try:
            # 입력한 벡터파일들을 병합하여 반환.
            answer: dict[str, any] = vectorstore.search_query(
                query, k, docs_list, llm_search
            )
            return JSONResponse(content=str(answer), status_code=status.HTTP_200_OK)

        except FileNotFoundError as err:
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
            )
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    else:
        err_message = "입력한 자료에 대한 조회권한이 없습니다."
        logging.error(err_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err_message),
        )


@router.get("/doc/{seq_id}")
async def get_document(
    seq_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
):
    validate_inputs(
        [
            {
                "type": TestType.NUM,
                "name": "seq_id",
                "val": seq_id,
                "_if": {"min_value": 1},
            },
        ]
    )
    from crud.crud_embedded_file import get_document_by_seq
    from schemas.document import EmbeddedFileDto
    from service.utils import datetime_handler, filter_columns

    try:
        doc: EmbeddedFileDto = get_document_by_seq(db, seq_id)
        doc = datetime_handler(doc)
        doc = filter_columns(doc, ["embedding_filename"])

        return JSONResponse(
            content={"document": doc.*dict*}, status_code=status.HTTP_200_OK
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/doc/{seq_id}")
def delete_document(
    seq_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
):
    validate_inputs(
        [
            {
                "type": TestType.NUM,
                "name": "seq_id",
                "val": seq_id,
                "_if": {"min_value": 1},
            },
        ]
    )
    from crud.crud_embedded_file import delete_document_by_seq

    vectorstore: VectorDBInterface = VectorDBFactory.create(DEFAULT_VECTOR_DB)
    try:
        document_name = delete_document_by_seq(db, user_id, seq_id)

        if document_name:
            # vector file을 삭제한다.
            vectorstore.delete(user_id, document_name)
            db.commit()

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return JSONResponse(
        content={"document": document_name}, status_code=status.HTTP_200_OK
    )


# 문서목록 조회
@router.get("/docs")
@print_log
def get_documents(
    db: Session = Depends(get_db), user_id: str = Depends(decode_auth_header)
):
    from crud.crud_embedded_file import get_documents_by_user_id
    from schemas.document import EmbeddedFileDto
    from service.utils import datetime_handler, filter_columns

    doc_list = []
    try:
        embedding_list: list[EmbeddedFileDto] = get_documents_by_user_id(db, user_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    for doc in embedding_list:
        dup_doc = datetime_handler(doc)
        dup_doc = filter_columns(dup_doc, exclude_columns=["embedding_filename"])
        doc_list.append(dup_doc.*dict*)

    return JSONResponse(content={"documents": doc_list}, status_code=status.HTTP_200_OK)


# 문서업로드
@router.post("/docs")
@elapse_time_async
@print_log_async
async def upload_documents(
    upload_option: UploadOption = Depends(UploadOption.as_form),
    llm_select: LLMSelect = Depends(LLMSelect.as_form),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(decode_auth_header),
) -> JSONResponse:
    validate_inputs(
        [
            {
                "type": TestType.FILE,
                "name": "files",
                "val": files,
            },
        ]
    )
    # from service.faiss_search import create_vectordb
    from crud import crud_embedded_file
    from service.utils import upload_files
    from service.docs_load.doc_loader import DocumentManager

    # 토큰카운터 초기화
    token_counter = TokenCounter(user_id, llm_select=llm_select, app="embedding", db=db)
    token_counter.set_embedding_mode(True)
    try:
        # 업로드 처리 후 저장위치 취득
        upload_tmp_dir = await upload_files(files)

        # 벡터db 선택
        vectordb: VectorDBInterface = VectorDBFactory.create(DEFAULT_VECTOR_DB)

        doc_manager = DocumentManager(
            user_id, vectordb, llm_select, upload_tmp_dir, upload_option
        )

        # 임베딩 사용토큰 계산, 임베딩파일 저장을 수행.
        upload_docs = await doc_manager.execute()

        # 문서목록에 등록한다.
        crud_embedded_file.register_documents(db, upload_docs)

        crud_embedded_file.commit(db)

        return JSONResponse(
            content={"documents": upload_docs}, status_code=status.HTTP_200_OK
        )

    except UnsupportedFileError as e:
        # 파일확장자에 대한 처리로직이 없을 때
        traceback.print_exc()
        raise HTTPException(status_code=e.state_code, detail=str(e.message))

    except Exception as e:
        # 카운팅된 토큰 처리.
        token_counter.save_db(is_logging=True)
        TokenCounter.dispose_userdata(user_id)

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    finally:
        # 원본파일을 삭제한다.
        shutil.rmtree(upload_tmp_dir)


# 문서기반 검색 클래스
# 공통 입력파라미터 유효성 및 발생 에러처리
class InquiryLLM:
    KEYWORD_SEARCH = "_search_keyword"
    STERAMING_SEARCH = "_search_streaming"
    CHAT_SEARCH = "_chat_keyword"

    def *init*(
        self, user_id: str, qa_input: CompletionUserInput, db: Session
    ) -> None:
        self.user_id = user_id
        self.k = qa_input.options.top
        self.temperature = qa_input.options.temperature
        self.id_list = qa_input.options.doc_ids
        self.search_type = qa_input.options.search_type
        self.prompt = qa_input.prompt
        self.llm_select = qa_input.llm
        self.db = db

    def inquire(self, func_name: str, **kwargs) -> Annotated[Generator, str]:
        if not hasattr(self, func_name):
            raise ValueError(f"존재하지 않는 기능을 호출하였습니다.[기능명:{func_name}]")
        # 참조문서목록 생성
        self._make_filelist()

        return getattr(self, func_name)(**kwargs)

    def _make_filelist(self) -> None:
        # 참고문서목록을 취득한다.
        docs_list: list[EmbeddedFileDto] = crud_embedded_file.get_documents_by_seqs(
            self.db, self.user_id, self.id_list
        )

        if len(docs_list) < len(self.id_list):
            raise ValueError("유효하지 않는 문서가 포함되어 있습니다.")

        vectorstore: VectorDBInterface = VectorDBFactory.create(DEFAULT_VECTOR_DB)
        # 입력한 벡터파일들을 병합하여 반환.
        self.vector_db = vectorstore.get(docs_list)

    def _search_keyword(self, **kwargs) -> str:
        _streaming = kwargs["streaming"] if "streaming" in kwargs else False
        return call_retrieval_search(
            self.user_id,
            self.prompt,
            self.k,
            self.temperature,
            self.vector_db,
            self.search_type,
            self.llm_select,
        )

    def _search_streaming(self, **kwargs) -> Generator:
        return call_retrieval_streaming_search(
            self.user_id,
            self.prompt,
            self.k,
            self.temperature,
            self.vector_db,
            self.search_type,
            self.llm_select,
        )

    def _chat_keyword(self, **kwargs) -> str:
        return call_retrieval_qa(
            self.user_id,
            self.prompt,
            self.k,
            self.temperature,
            self.vector_db,
            self.llm_select,
        )```
      * 클라이언트쪽 코드
        * 아래처럼 코드를 추가하고 if (!response.ok) 블럭을 막는다.
        * ```javascript
        const chunk = new TextDecoder().decode(value);
        const parsedChunk = JSON.parse(chunk);
        console.log('parseChunk: ', parsedChunk);
        if (parsedChunk.error) {
          console.error('Error code:', parsedChunk.code);
          console.error('Error detail:', parsedChunk.detail);
          onError && onError(parsedChunk.code, parsedChunk.detail);
          finish();

          console.log('streaming done', done);
          onDone(buffer);
          return;
        }```
  * [x] 기업명 입력하는 데서 401,403에러가 날 경우 처리 [[October 5th, 2023]]