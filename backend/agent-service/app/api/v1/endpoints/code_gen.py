from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.utils.docs import CodeGenDocs
from app.models.query import CommandRequest
from app.services.code_gen.graph import CodeGenerator
from app.utils.depend import get_code_gen
from langchain_core.messages import HumanMessage
from fastapi.encoders import jsonable_encoder

from app.utils.redis_client import generate_log_id, save_logs_to_redis, save_states_to_redis, get_states_from_redis
from uuid import uuid4

import pandas as pd
import requests

router = APIRouter()
docs = CodeGenDocs()

# FastAPI 엔드포인트: 사용자의 질의를 받고 graph를 통해 답변 생성
@router.post("/generate")
async def command_code(
    request: CommandRequest = docs.base["data"],
    code_gen: CodeGenerator = Depends(get_code_gen)
):
    try:
        graph = code_gen.build()

        checkdata = requests.get(request.url).json()
        checkdata = checkdata["data"]
        # 이후 동일 url로 온 적이 있는 요청은 캐시해서 들고 있을 것. 아니면 dataload 요청 시 저장된 값을 활용하도록 할 것
        # 또는 url 필드에 파일 시스템 파일 경로를 받아 조작하도록 할 것. 그럼 필드는 유지될 것으로 보임

        query = {
                'messages': [HumanMessage(request.command_list)],
                'python_code': '',
                'python_codes_list': [],
                'command_list': request.command_list,
                'classified_cmds': [],
                'current_unit': {},
                'queue_idx': 0,
                'dataframe': [pd.DataFrame(checkdata)],
                'retry_count': 0,
                'error_msg': None,
                'logs': [],
                'download_token': ''
            } # initial state 생성기 분리

        user_id = request.user_id or "guest" # user_id는 추후 jwt등으로 체크
        if request.uid:
            uid = request.uid
            session_id = f"sessions:{user_id}:{uid}"
            old_state = get_states_from_redis(session_id)
            print(old_state.keys())
            # q_check = query
            # q_check.update(old_state)
            # print(q_check)
            raise
        else:
            uid = uuid4().hex

        answer = graph.invoke(query)

        # answer["dataframe"] 가 이제 List[pd.DataFrame] 라면…
        df_list = answer["dataframe"]

        # 레코드 목록 리스트로 직렬화
        serialized = [
            single_df.to_dict(orient="records")
            # single_df.to_dict()
            for single_df in df_list
        ]

        # logs는 redis에 따로 저장하는 것을 고려
        # log_id = generate_log_id(user_id)
        log_id = f"logs:{user_id}:{uid}"
        save_logs_to_redis(log_id, answer["logs"])

        session_id = f"sessions:{user_id}:{uid}"
        save_states_to_redis(session_id, answer)

        payload = {
            "codes":      answer["python_codes_list"],
            "dataframe": serialized,      # 여전히 to_dict 직후의 리스트
            "error_msg": answer["error_msg"],
            "download_token":answer["download_token"],
            # "logs":      answer["logs"], # 이제 로그는 log_id만 보내기
            "log_id": uid
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"result" : "success", "data" : jsonable_encoder(payload)})