from langchain_core.messages import HumanMessage
import pandas as pd
import requests
from typing import List, Dict, Any

import asyncio

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
        "stream_id":         stream_id
    }

    return query

_LOG_QUEUES: Dict[str, asyncio.Queue] = {}

def get_log_queue(stream_id: str) -> asyncio.Queue:
    """
    stream_id별로 하나의 Queue를 생성·반환.
    Graph 실행 코드에서 새 로그를 여기로 put 하고,
    SSE 핸들러에서는 이 Queue를 get하며 스트리밍합니다.
    """
    if stream_id not in _LOG_QUEUES:
        _LOG_QUEUES[stream_id] = asyncio.Queue()
    return _LOG_QUEUES[stream_id]