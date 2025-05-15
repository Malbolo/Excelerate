import os
import shutil
import urllib.parse
import tempfile
import base64
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from app.utils.depend import get_minio_client
from app.utils.minio_client import MinioClient
from app.services.template import TemplateService

router = APIRouter()

@router.post("/", summary="새 엑셀 템플릿 업로드")
async def upload_template(
    template_name: str = Form(...),
    file: UploadFile = File(...),
    minio: MinioClient = Depends(get_minio_client),
):
    svc = TemplateService(minio)
    data = await file.read()
    # 1) 파일 업로드 및 중복 이름 처리
    new_name = svc.upload_template(
        template_name, data,
        file.filename, file.content_type
    )
    # 2) 응답
    return JSONResponse(status_code=201, content={"result" : "success", "data" : {"message": f"'{new_name}' 업로드 완료."}})

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

@router.get("/{template_name}/preview", summary="템플릿 첫 시트 미리보기 이미지")
async def preview_template(
    template_name: str,
    background_tasks: BackgroundTasks,
    minio: MinioClient = Depends(get_minio_client),
):
    svc = TemplateService(minio)
    tmpdir = tempfile.mkdtemp()
    try:
        png_path = await svc.generate_preview(template_name, tmpdir)
    except HTTPException:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise

    # 응답 후 임시 디렉터리 삭제 스케줄
    background_tasks.add_task(shutil.rmtree, tmpdir, True)

    with open(png_path, "rb") as f:
        img_bytes = f.read()
    encoded_str = base64.b64encode(img_bytes).decode("utf-8")

    data_uri = f"data:image/png;base64,{encoded_str}"

    return JSONResponse(status_code=200, content={"result" : "success", "data" : data_uri})

    # response = FileResponse(png_path, media_type="image/png")

    # # RFC5987 포맷으로 한글 이름을 UTF-8 URL 인코딩
    # filename = os.path.basename(png_path)  # e.g. "테스트.png"
    # quoted_fname = urllib.parse.quote(filename, safe="")  

    # # 다운로드가 아닌 인라인 뷰로
    # response.headers["Content-Disposition"] = f"inline; filename*=UTF-8''{quoted_fname}"
    # return response

@router.get("/{template_name}/download", summary="템플릿 다운로드")
async def download_template(
    template_name: str,
    background_tasks: BackgroundTasks,
    minio: MinioClient = Depends(get_minio_client),
):
    # 1) 임시 디렉토리 & 파일 경로 생성
    tmpdir = tempfile.mkdtemp()
    xlsx_path = os.path.join(tmpdir, f"{template_name}.xlsx")

    # 2) Minio에서 다운로드
    try:
        minio.download_template(template_name, xlsx_path)
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise HTTPException(status_code=404, detail=f"템플릿을 찾을 수 없습니다: {e}")

    # 3) 응답 이후 임시 디렉토리 삭제 예약
    background_tasks.add_task(shutil.rmtree, tmpdir, True)

    # 4) FileResponse로 내려주기
    response = FileResponse(
        xlsx_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    # 한글 파일명 대응
    quoted_fname = urllib.parse.quote(f"{template_name}.xlsx", safe="")
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quoted_fname}"
    return response