---
title: "streaming retrieval 분석"
created: 2023-09-11 14:53:44
updated: 2023-09-11 17:12:53
---
  * langchain 분석 필요 [[September 6th, 2023#^UDbAyTkI9|python langchain으로 streaming 구현하는 방법.]]
  * ```python
def doc_based_streaming(...)
  answer = call_retrieval_streaming_search(user_id,
                                           prompt,
                                           k, 
                                           temperature, 
                                           file_list, 
                                           search_type)
  return StreamingResponse(answer, media_type = "text/html")```
  * ```python

# 챗GPT에 문서를 기반으로 질의를 수행한다.
@print_log
def call_retrieval_streaming_search(
  user_id: str,
  prompt: str,
  k: int,
  temperature: float,
  file_list: list[str],
  search_type: str = "similarity"
) -> str:
  # clustering 결과를 요청한다.
  faiss_db = get_vectordb(user_id, filelist)
  faiss_retriever = ...

  return retrieval_streaming_search(prompt, 
                                    temperature, 
                                    faiss_retriever)
```
  * ```python
def retrieval_streaming_search(
  prompt: str, 
  temperature: float, 
  retriever: BaseRetriever
) -> object:
  _lc = RetrivalQAWrapper(get_llm(temperature=temperature, streaming=True), retriever)

  # q: SimpleQueue
  q, _thread = _lc.start_streaming(prompt, logging=False)

  while True:
    next_token = q.get(block=True)
    if next_token == JOB_END_KEY:
      break
    yield next_token

  _thread.join()```