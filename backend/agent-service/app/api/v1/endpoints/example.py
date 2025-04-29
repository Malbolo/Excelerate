# app/api/v1/endpoints/example.py

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.utils.docs import ExampleDocs
from app.core.config import settings

router = APIRouter()
docs = ExampleDocs()


# @router.post(
#     "/",
#     summary="요약 설명",
#     description="API 상세 설명",
#     response_description="응답 설명",
#     responses=docs.base["res"],
# )
# async def example_endpoint(request: Request, data: Ingredients = docs.base["data"]):
#     try:
#         query_maker = QueryMaker(data.ingredients, data.main_ingredients,
#                                  data.preferred_ingredients, data.disliked_ingredients,
#                                  data.categories, data.dietaries, data.allergies)
#         # 비동기로 전체 프로세스 실행
#         result = await query_maker.run()
#         return JSONResponse(status_code=200, content=result)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="레시피 생성 중 오류가 발생했습니다.")
