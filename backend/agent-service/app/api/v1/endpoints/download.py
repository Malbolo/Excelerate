from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from app.utils.minio_client import MinioClient
from app.utils.depend import get_minio_client

router = APIRouter()

@router.get(
    "/{file_key}",
    summary="프록시 스트리밍 다운로드"
)
async def download_proxy(
    file_key: str,
    minio: MinioClient = Depends(get_minio_client),
):
    object_key = f"outputs/{file_key}"
    try:
        resp = minio.client.get_object(minio.bucket, object_key)
    except Exception:
        raise HTTPException(404, "파일을 찾을 수 없습니다.")

    # 파일명에 유니코드가 포함될 수 있으므로 RFC5987 인코딩 적용
    quoted_filename = quote(file_key, safe="")
    content_disposition = f"attachment; filename*=UTF-8''{quoted_filename}"

    return StreamingResponse(
        resp.stream(32 * 1024),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": content_disposition}
    )