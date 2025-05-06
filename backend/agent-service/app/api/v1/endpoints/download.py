from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("", summary="Presigned URL 리다이렉트 (GET)")
async def download_url(
    url: str = Query(..., description="presigned URL"),
):
    # 302: GET → GET 리다이렉트
    return RedirectResponse(url, status_code=302)