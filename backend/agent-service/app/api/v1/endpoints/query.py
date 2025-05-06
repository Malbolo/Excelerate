from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.utils.docs import QueryDocs
from app.models.query import QueryRequest
from app.utils.depend import get_llm_service
from app.services.llmtest import LLMTest

router = APIRouter()
docs = QueryDocs()

# FastAPI 엔드포인트: 사용자의 질의를 받고 RAG 체인을 통해 답변 생성
@router.post("/query")
async def query_rag(
    request: QueryRequest,
    llm_test: LLMTest = Depends(get_llm_service)
):
    try:
        answer = await llm_test.run(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200, content={"result" : "success", "data" : {"answer": answer}})