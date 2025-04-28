from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.utils.docs import CodeGenDocs
from app.models.query import CommandRequest
from app.services.code_gen.graph import CodeGenerator
from app.utils.depend import get_code_gen
from langchain_core.messages import HumanMessage


import pandas as pd
from app.services.code_gen.sample import sample_data

router = APIRouter()
docs = CodeGenDocs()
df = pd.DataFrame(sample_data["data"])

# FastAPI 엔드포인트: 사용자의 질의를 받고 graph를 통해 답변 생성
@router.post("/command")
async def command_code(
    request: CommandRequest = docs.base["data"],
    code_gen: CodeGenerator = Depends(get_code_gen)
):
    try:
        graph = code_gen.build()

        query = {
                'messages': [HumanMessage(request.command_list)],
                'python_code': '',
                'command_list': request.command_list,
                'dataframe': [df],
                'retry_count': 0
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
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"code": answer["python_code"], "dataframe": serialized})