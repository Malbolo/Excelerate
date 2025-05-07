from langchain_core.messages import HumanMessage
import pandas as pd
import requests
from typing import List, Dict, Any

def make_initial_query(url: str, command_list: List[str]) -> Dict[str, Any]:
    """
    그래프 첫 실행을 위한 초기 query 객체를 생성합니다.
    - url에서 원본 데이터를 불러와 DataFrame으로 래핑
    - 실행에 필요한 모든 필드를 빈 값/초기값으로 세팅
    """
    resp = requests.get(url)
    resp.raise_for_status()
    raw_data = resp.json().get("data", [])

    return {
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
        "download_token":    ""
    }
