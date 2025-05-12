# app/api/v1/endpoints/templates.py

import os
import uuid
import tempfile
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.utils.depend import get_minio_client
from app.utils.minio_client import MinioClient

router = APIRouter()

@router.post("/", summary="새 엑셀 템플릿 업로드")
async def upload_template(
    template_name: str = Form(...),
    file: UploadFile = File(...),
    minio: MinioClient = Depends(get_minio_client),
):
    # --- 0) 파일 확장자/콘텐츠 타입 검사 ---
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext != ".xlsx":
        raise HTTPException(
            status_code=400,
            detail="지원되지 않는 파일 형식입니다. ‘.xlsx’ 파일만 업로드 가능합니다."
        )

    # (선택) 추가로 헤더 레벨에서 content_type 검사
    if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        raise HTTPException(
            status_code=400,
            detail=f"잘못된 콘텐츠 타입입니다: {file.content_type}"
        )
    # ------------------------------------------

    # 1) OS에 맞는 임시 디렉터리 생성
    with tempfile.TemporaryDirectory() as tmpdir:
        suffix = os.path.splitext(file.filename)[1] or ".xlsx"
        tmp_path = os.path.join(tmpdir, f"{uuid.uuid4().hex}{suffix}")

        # 2) 업로드된 파일을 임시 디렉터리에 저장
        try:
            contents = await file.read()
            with open(tmp_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")

        # 3) MinIO에 템플릿 업로드
        try:
            minio.upload_template(template_name, tmp_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"템플릿 업로드 실패: {e}")

    # with 블록 벗어나면 tmpdir 전체가 자동 삭제됩니다
    return JSONResponse(status_code=201, content={"result" : "success", "data" : {"message": f"'{template_name}' 업로드 완료."}})

@router.get("/", summary="등록된 템플릿 목록 조회")
async def list_templates(
    minio: MinioClient = Depends(get_minio_client),
):
    try:
        templates = minio.list_templates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 조회 실패: {e}")
    return JSONResponse(status_code=200, content={"result" : "success", "data" : {"templates": templates}})

@router.delete("/{template_name}", summary="특정 템플릿 삭제")
async def delete_template(
    template_name: str,
    minio: MinioClient = Depends(get_minio_client),
):
    try:
        minio.delete_template(template_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 삭제 실패: {e}")
    return JSONResponse(status_code=200, content={"result" : "success", "data" : {"message": f"'{template_name}' 삭제 완료."}})
