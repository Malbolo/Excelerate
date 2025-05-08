from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.utils.docs import CodeGenDocs
from app.models.query import CommandRequest
from app.services.code_gen.graph import CodeGenerator
from app.utils.depend import get_code_gen
from app.utils.api_utils import make_initial_query
from fastapi.encoders import jsonable_encoder
from app.core import auth

from app.utils.redis_client import generate_log_id, save_logs_to_redis, save_states_to_redis, get_states_from_redis
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
        graph = code_gen.build()

        query = make_initial_query(request.url, request.command_list)

        user_id = auth.get_user_id_from_header(req) 
        if user_id is None:
            user_id = "guest"

        if request.uid:
            uid = request.uid
            session_id = f"sessions:{user_id}:{uid}"
            old_state = get_states_from_redis(session_id)
            query.update(old_state)
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

        try:
            user_name = auth.get_user_info(user_id)
        except:
            user_name = "guest"
        log_id = generate_log_id(user_name)
        
        save_logs_to_redis(log_id, answer["logs"], metadata={
            "agent_name":  "Code Generetor",
            "log_detail":  "코드를 생성합니다."
        })

        session_id = f"sessions:{user_id}:{uid}"
        save_states_to_redis(session_id, answer)

        payload = {
            "codes":      [answer["python_code"]],
            "dataframe": serialized,      # 여전히 to_dict 직후의 리스트
            "error_msg": answer["error_msg"],
            "download_token":answer["download_token"],
            # "logs":      answer["logs"], # 이제 로그는 log_id만 보내기
            "log_id": uid
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"result" : "success", "data" : jsonable_encoder(payload)})