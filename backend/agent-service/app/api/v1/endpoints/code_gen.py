from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.query import CommandRequest
from app.services.code_gen.graph import CodeGenerator
from fastapi.encoders import jsonable_encoder

from fastapi.concurrency import run_in_threadpool

from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np

from app.core import auth

from app.utils.depend import get_code_gen
from app.utils.docs import CodeGenDocs
from app.utils.redis_client import generate_log_id, save_logs_to_redis, save_states_to_redis, get_states_from_redis
from app.utils.api_utils import make_initial_query, get_log_queue, strip_excel_block
from uuid import uuid4

router = APIRouter()
docs = CodeGenDocs()

# FastAPI 엔드포인트: 사용자의 질의를 받고 graph를 통해 답변 생성
@router.post("/generate")
async def command_code(
    req: Request,
    request: CommandRequest = docs.base["data"],
    code_gen: CodeGenerator = Depends(get_code_gen)
):
    try:
        api_start = datetime.now(ZoneInfo("Asia/Seoul"))
        graph = code_gen.build()

        # 나중엔 Optional이 아닌 필수로 연결하도록 요청
        if request.stream_id:
            stream_id = request.stream_id
        else:
            stream_id = "check" # 확인용 

        q = get_log_queue(stream_id)
        q.put_nowait({"type": "notice", "content": "CodeGenerator를 호출합니다."})

        # 그래프 호출을 위한 기본 쿼리 생성
        query = make_initial_query(request.url, request.command_list, stream_id)

        # user_id와 user_name 인증정보로 부터 가져오기. 없으면 "guest"
        try:
            user_id = auth.get_user_id_from_header(req) or "guest"
            profile = auth.get_user_info(user_id)
            if profile and isinstance(profile, dict):
                user_name = profile.get("name") or "guest"
            else:
                user_name = "guest"
        except:
            user_id = "guest"
            user_name = "guest"

        # 세션을 불러와 관리하는 기능 - 필요하면 사용. 다만 커맨드를 edit할 경우 애매해짐
        if request.uid:
            uid = request.uid
            session_id = f"sessions:{user_id}:{uid}"
            old_state = get_states_from_redis(session_id)
            query.update(old_state)
        else:
            uid = uuid4().hex
        
        # Edit 모드여서 기존 코드가 있으면 excel 조작부를 제거하고 반영
        if request.original_code:
            query['original_code'] = strip_excel_block(request.original_code)

        # graph 별도의 쓰레드에서 실행행
        answer = await run_in_threadpool(graph.invoke, query)

        # answer["dataframe"] 가 이제 List[pd.DataFrame] 라면…
        df_list = answer["dataframe"]

        # df list의 각 df의 결측치 제거
        for df in df_list:
            # NaN, inf 처리를 한 번에
            df = df.replace([np.nan, np.inf, -np.inf], None)

        # 레코드 목록 리스트로 직렬화
        serialized = [
            single_df.to_dict(orient="records")
            # single_df.to_dict()
            for single_df in df_list
        ]

        log_id = generate_log_id(user_name, uid)

        api_end = datetime.now(ZoneInfo("Asia/Seoul"))
        api_latency = (api_end - api_start).total_seconds()
        
        q.put_nowait({"type": "notice", "content": "Log를 저장 중입니다..."})
        save_logs_to_redis(log_id, answer["logs"], metadata={
            "agent_name":  "Code Generetor",
            "log_detail":  "코드를 생성합니다.",
            "total_latency": api_latency
        })

        session_id = f"sessions:{user_id}:{uid}"
        save_states_to_redis(session_id, answer)

        payload = {
            "codes":      [answer["python_code"]],
            "dataframe": serialized,
            "error_msg": answer["error_msg"],
            "download_token":answer["download_token"],
            "log_id": uid
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    q.put_nowait({"type": "stop", "content": "API 호출이 정상 종료되었습니다."})
    return JSONResponse(status_code=200, content={"result" : "success", "data" : jsonable_encoder(payload)})