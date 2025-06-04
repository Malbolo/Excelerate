# app/utils/document_utils.py

import os
from typing import List

from fastapi import HTTPException

from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_txt_or_md(file_path: str) -> str:
    """
    '.txt' 또는 '.md' 파일을 TextLoader로 읽어서 전체 텍스트를 반환합니다.
    :param file_path: 텍스트/마크다운 파일 경로
    :return: 파일 내 모든 텍스트 문자열
    """
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {file_path}")
    try:
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()  # List[Document]
        # 여러 개의 Document가 있을 수 있지만, 대부분 TextLoader는 한 덩어리로 반환됩니다.
        return "\n".join([doc.page_content for doc in docs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트/마크다운 로드 오류: {e}")


def load_pdf(file_path: str) -> str:
    """
    '.pdf' 파일을 PyPDFLoader로 읽어서 전체 텍스트를 반환합니다.
    PyPDFLoader가 페이지별로 Document를 생성하므로, 모든 페이지를 합쳐서 반환합니다.
    :param file_path: PDF 파일 경로
    :return: 파일 내 모든 텍스트 문자열
    """
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"PDF 파일을 찾을 수 없습니다: {file_path}")
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()  # List[Document], 각 Document.page_content는 한 페이지 텍스트
        return "\n".join([doc.page_content for doc in docs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 로드 오류: {e}")


def load_docx(file_path: str) -> str:
    """
    '.docx' 파일을 Docx2txtLoader로 읽어서 전체 텍스트를 반환합니다.
    :param file_path: DOCX 파일 경로
    :return: 파일 내 모든 텍스트 문자열
    """
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"DOCX 파일을 찾을 수 없습니다: {file_path}")
    try:
        loader = Docx2txtLoader(file_path)
        docs = loader.load()  # List[Document]
        return "\n".join([doc.page_content for doc in docs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX 로드 오류: {e}")


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[str]:
    """
    주어진 텍스트를 지정된 크기와 오버랩으로 청크로 분할하여 반환합니다.
    langchain_text_splitters의 RecursiveCharacterTextSplitter를 사용합니다.
    :param text: 전체 텍스트 문자열
    :param chunk_size: 청크 크기(문자 단위)
    :param chunk_overlap: 청크 간 중첩 크기(문자 단위)
    :return: 텍스트 청크 리스트
    """
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        return splitter.split_text(text)
    except Exception as e:
        raise RuntimeError(f"텍스트 분할 오류: {e}")
