from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.utils.docs import CodeGenDocs
from app.models.query import CommandRequest
from app.services.code_gen.graph import CodeGenerator
from app.utils.depend import get_code_gen
from langchain_core.messages import HumanMessage
from fastapi.encoders import jsonable_encoder


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
                "error_msg": None,
                "logs": []
            }

        answer = graph.invoke(query)

        # answer["dataframe"] 가 이제 List[pd.DataFrame] 라면…
        df_list = answer["dataframe"]

        # 1) 레코드 목록 리스트로 직렬화
        serialized = [
            single_df.to_dict(orient="records")
            # single_df.to_dict()
            for single_df in df_list
        ]

        payload = {
            "code":      answer["python_code"],
            "dataframe": serialized,      # 여전히 to_dict 직후의 리스트
            "error_msg": answer["error_msg"],
            "logs":      answer["logs"],
        }
        # logs는 redis에 따로 저장하는 것을 고려

        # # 디버깅 (저장된 df list 확인)
        # for one in df_list:
        #     print(one)
        #     print("\n")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content=jsonable_encoder(payload))