from langchain_core.messages import HumanMessage
import pandas as pd
import requests
from typing import List, Dict, Any

import re
import asyncio


def strip_excel_block(code: str) -> str:
    """
    "# Excel 작업 시작"부터 "# Excel 작업 끝"까지
    해당 블록 전체를 제거합니다.
    """
    pattern = r"(?s)#\s*Excel 작업 시작.*?#\s*Excel 작업 끝"
    return re.sub(pattern, "", code)

def make_initial_query(url: str, command_list: List[str], stream_id: str) -> Dict[str, Any]:
    """
    그래프 첫 실행을 위한 초기 query 객체를 생성합니다.
    - url에서 원본 데이터를 불러와 DataFrame으로 래핑
    - 실행에 필요한 모든 필드를 빈 값/초기값으로 세팅
    - stream_id가 있으면 상태에 포함
    """
    resp = requests.get(url)
    resp.raise_for_status()
    raw_data = resp.json().get("data", [])

    query = {
        "messages":          [HumanMessage(command_list)],
        "python_code":       "",
        "python_codes_list": [],
        "command_list":      command_list,
        "classified_cmds":   [],
        "current_unit":      {},
        "queue_idx":         0,
        "dataframe":         [pd.DataFrame(raw_data)],
        "retry_count":       0,
        "error_msg":         None,
        "logs":              [],
        "download_token":    "",
        "stream_id":         stream_id,
        "original_code":     None
    }

    return query

_LOG_QUEUES: Dict[str, asyncio.Queue] = {}
_DF_QUEUES: Dict[str, asyncio.Queue]  = {}
_DF_SENDER_TASKS: Dict[str, asyncio.Task] = {}

def get_log_queue(stream_id: str) -> asyncio.Queue:
    if stream_id not in _LOG_QUEUES:
        _LOG_QUEUES[stream_id] = asyncio.Queue()
    return _LOG_QUEUES[stream_id]

def get_df_queue(stream_id: str) -> asyncio.Queue:
    if stream_id not in _DF_QUEUES:
        _DF_QUEUES[stream_id] = asyncio.Queue()
    return _DF_QUEUES[stream_id]

async def _df_sender(stream_id: str):
    df_q  = get_df_queue(stream_id)
    log_q = get_log_queue(stream_id)
    try:
        while True:
            df = await df_q.get()
            log_q.put_nowait({"type": "data", "content": df.to_dict(orient="records")})
            await asyncio.sleep(0.3) # 0.3초
    except asyncio.CancelledError:
        # 태스크가 취소될 때 조용히 종료
        return

def ensure_df_sender_task(stream_id: str):
    """
    stream_id당 하나의 _df_sender 태스크만 생성하고 레지스트리에 저장
    """
    task = _DF_SENDER_TASKS.get(stream_id)
    if task is None or task.done():
        # 현재 루프에 태스크 생성
        task = asyncio.create_task(_df_sender(stream_id))
        _DF_SENDER_TASKS[stream_id] = task
    return task