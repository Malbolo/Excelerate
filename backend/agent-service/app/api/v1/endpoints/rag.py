import json
import uuid
import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Any

from app.core.auth import get_current_user
from app.models.query import RagSearch
from app.services.rag_service import (
    ingest_documents,
    list_documents,
    get_document,
    delete_document,
    search_documents
)

router = APIRouter()

@router.post("/ingest", response_model=Any)
async def ingest_rag(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    사용자로부터 업로드된 단일 파일( .txt, .pdf, .md, .docx )을 받아서 RAG 인덱싱을 시작합니다.
    1) 임시 경로에 파일 저장
    2) 확장자에 따라 text_utils.load_* 함수를 호출
    3) ingest_documents 호출
    """
    # 1) 확장자 확인
    original_filename = file.filename or "unknown"
    ext = original_filename.split(".")[-1].lower()
    allowed = {"txt", "md", "pdf", "docx"}
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="지원되지 않는 파일 형식입니다. (txt, md, pdf, docx)")

    # 2) 임시 디렉터리 생성 및 파일 저장
    #    /tmp/rag_upload_<UUID>_<원본이름>
    tmp_dir = tempfile.mkdtemp(prefix="rag_upload_")
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4()}.{ext}")
    try:
        contents = await file.read()
        with open(tmp_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")

    # 3) ingest_documents 호출을 위한 data_list 구성
    #    {"type": ext, "path": tmp_path} 하나짜리 리스트를 넘김
    data_entry = {"type": ext, "path": tmp_path}
    try:
        job_id = ingest_documents(current_user.id, [data_entry])
    except HTTPException as e:
        raise e
    finally:
        os.remove(tmp_path)
        os.rmdir(tmp_dir)
    return JSONResponse(
        status_code=202,
        content={"result": "success", "data": {"job_id": job_id}}
    )

@router.get("/list", response_model=List[Dict[str, Any]])
def list_rag(current_user=Depends(get_current_user)):
    """
    현재 로그인한 사용자의 RAG 문서 목록을 조회합니다.
    """
    try:
        docs = list_documents(current_user.id)
    except HTTPException as e:
        raise e
    return JSONResponse(
        status_code=200,
        content={"result": "success", "data": docs}
    )

@router.get("/documents/{doc_id}", response_model=Dict[str, Any])
def get_rag(doc_id: str, current_user=Depends(get_current_user)):
    """
    특정 문서 ID로 저장된 RAG 문서의 상세 정보를 조회합니다.
    """
    try:
        doc = get_document(current_user.id, doc_id)
    except HTTPException as e:
        raise e
    return JSONResponse(
        status_code=200,
        content={"result": "success", "data": doc}
    )

@router.delete("/documents/{doc_id}", response_model=Any)
def delete_rag(doc_id: str, current_user=Depends(get_current_user)):
    """
    특정 문서 ID를 가진 RAG 문서를 삭제하고, 인덱스에서도 제거합니다.
    """
    try:
        delete_document(current_user.id, doc_id)
    except HTTPException as e:
        raise e
    return JSONResponse(
        status_code=200,
        content={"result": "success", "data": {"deleted": True}}
    )

@router.post("/search", response_model=Dict[str, Any])
def search_rag(request: RagSearch, current_user=Depends(get_current_user)):
    """
    사용자의 자연어 질의에 대해 RAG 검색을 수행하고, LLM으로 응답을 생성합니다.
    - request: { "query": "사용자 질의", "filters": Optional[List[str]] }
    """
    try:
        result = search_documents(current_user.id, request)
    except HTTPException as e:
        raise e
    return JSONResponse(
        status_code=200,
        content={"result": "success", "data": result}
    )
