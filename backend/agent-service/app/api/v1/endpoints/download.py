from itsdangerous import TimestampSigner, BadSignature, SignatureExpired
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from app.utils.minio_client import MinioClient
from app.utils.depend import get_minio_client
from app.core.config import settings

router = APIRouter()

@router.get("", summary="토큰 검증 후 스트리밍 다운로드")
async def download_proxy(
    token: str = Query(..., description="서명된 download token"),
    minio: MinioClient = Depends(get_minio_client),
):
    signer = TimestampSigner(settings.TOKEN_SECRET_KEY)
    try:
        # 최대 1시간(3600초) 유효
        object_key = signer.unsign(token, max_age=3600).decode()
    except SignatureExpired:
        raise HTTPException(403, "토큰이 만료되었습니다.")
    except BadSignature:
        raise HTTPException(403, "유효하지 않은 토큰입니다.")

    # MinIO에서 스트리밍
    try:
        resp = minio.client.get_object(minio.bucket, object_key)
    except Exception:
        raise HTTPException(404, "파일을 찾을 수 없습니다.")

    # 파일명 한글/특수문자 처리
    filename = object_key.split("/")[-1]
    quoted   = quote(filename, safe="")
    cd       = f"attachment; filename*=UTF-8''{quoted}"

    return StreamingResponse(
        resp.stream(32 * 1024),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": cd},
    )
