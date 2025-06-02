# app/services/rag_service.py

import json
import uuid
import os
from typing import List, Dict, Any

from fastapi import HTTPException
from pymilvus import connections, utility, Collection, DataType, FieldSchema, CollectionSchema

from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from app.core.config import settings
from app.models.query import RagSearch
from app.utils.text_utils import (
    load_txt_or_md,
    load_pdf,
    load_docx,
    split_text_into_chunks
)

# ─────────────────────────────────────────────────────────────────────────────
# 1) Milvus 컬렉션 초기화(싱글톤)
# ─────────────────────────────────────────────────────────────────────────────
def get_or_init_rag_collection(collection_name: str = "rag_chunks"):
    """
    - Milvus에 이미 'rag_chunks' 컬렉션이 있으면 반환
    - 없으면 <chunk_id(int auto), user_id(str), doc_id(str), text(str), embedding(vector)> 스키마로 생성
    - embedding dim은 settings.EMBEDDING_DIM (예: 1536 혹은 768) 로 가정
    """
    connections.connect(alias="default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
    if not utility.has_collection(collection_name):
        # 컬렉션이 없다면 새로 생성
        fields = [
            FieldSchema(name="chunk_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=36),
            FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
            FieldSchema(name="created_at", dtype=DataType.INT64)  # timestamp 용(선택)
        ]
        schema = CollectionSchema(fields, description="RAG document chunks for all users")
        Collection(name=collection_name, schema=schema)
        col = Collection(collection_name)
        col.create_index(field_name="embedding", 
                         index_params={
                            "index_type": "HNSW",
                            "metric_type": "L2",
                            "params": { "M": 16, "efConstruction": 200}
                        })
        col.load()
        return col
    else:
        col = Collection(collection_name)
        col.load()
        return col

# 싱글톤 변수(모듈 로드 시 초기화)
_RAG_COLLECTION = get_or_init_rag_collection()


# ─────────────────────────────────────────────────────────────────────────────
# 2) 문서(단일 JSON or 텍스트) → 청크로 분해 → Milvus 업로드
# ─────────────────────────────────────────────────────────────────────────────
def ingest_documents(user_id: str, data_list: List[Dict[str, Any]]) -> str:
    """
    - data_list: List of dict. 각 dict는 'type'과 'path' 또는 'content'를 포함합니다.
      예시: 
      [
        {"type": "json", "content": {...}}, 
        {"type": "txt", "path": "/tmp/hello.txt"}, 
        {"type": "pdf", "path": "/tmp/report.pdf"}, 
        {"type": "docx", "path": "/tmp/doc.docx"},
      ]
    - 사용자가 업로드한 문서를 파싱(parsers 사용)한 뒤, 
      chunk 단위로 분리(split_text_into_chunks 사용), 
      벡터 임베딩 → Milvus 저장
    - 저장 완료 후, job_id(UUID)를 반환하고, 
      job_id를 통해 상태 조회를 확장 가능
    """

    # 1) 고유 job_id 발급 (단순 UUID)
    job_id = str(uuid.uuid4())

    # 2) “문서 단위”로 각각 doc_id 부여 → 청크 생성·업로드
    for raw_doc in data_list:
        # 2.1) doc_id 발급
        doc_id = str(uuid.uuid4())
        file_name = os.path.basename(file_path)

        # 2.2) “실제 텍스트” 얻기: text_utils의 load_*/parse_* 호출
        doc_type = raw_doc.get("type")
        if doc_type in ("txt", "md"):
            file_path = raw_doc.get("path")
            text = load_txt_or_md(file_path)
        elif doc_type == "pdf":
            file_path = raw_doc.get("path")
            text = load_pdf(file_path)
        elif doc_type == "docx":
            file_path = raw_doc.get("path")
            text = load_docx(file_path)
        elif doc_type == "json":
            content = raw_doc.get("content")
            text = json.dumps(content, ensure_ascii=False)
        else:
            raise HTTPException(status_code=400, detail=f"지원되지 않는 문서 형식: {doc_type}")

        # 2.3) 텍스트가 비어있으면 건너뜀
        if not text:
            continue

        # 2.4) 청크 분할 (split_text_into_chunks 사용)
        #      – 기본 chunk_size=1000, overlap=200 기준
        chunks = split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200)

        # 2.5) 벡터 임베딩 생성 (OpenAIEmbeddings)
        embedder = OpenAIEmbeddings()  # 내부적으로 settings.OPENAI_API_KEY 사용
        embeddings = embedder.embed_documents(chunks)  # List[List[float]]

        # 2.6) Milvus 컬렉션에 한꺼번에 업로드
        milvus_col = _RAG_COLLECTION

        # Bulk insert 준비: 각 field별 list 형태로 준비
        #      스키마 순서: [chunk_id(auto), user_id, doc_id, text, embedding, created_at]
        user_ids = [user_id] * len(chunks)
        doc_ids = [doc_id] * len(chunks)
        file_names = [file_name or ""] * len(chunks)
        texts = chunks
        vectors = embeddings
        timestamps = [int(os.path.getmtime(raw_doc.get("path"))) if raw_doc.get("path") and os.path.exists(raw_doc.get("path")) else 0 for _ in range(len(chunks))]

        entities = [user_ids, doc_ids, file_names, texts, vectors, timestamps]
        milvus_col.insert(entities)

    # 3) Job ID 반환
    return job_id


# ─────────────────────────────────────────────────────────────────────────────
# 3) 사용자의 문서 목록 조회
# ─────────────────────────────────────────────────────────────────────────────
def list_documents(user_id: str) -> List[Dict[str, Any]]:
    """
    - Milvus에서 user_id 필터링 후 고유 doc_id 및 file_name 목록 반환
    - 반환 예시: [{"doc_id":"xxx", "file_name":"hello.txt", "status":"indexed"}, ...]
    """
    milvus_col = _RAG_COLLECTION
    expr = f'user_id == "{user_id}"'

    # doc_id와 file_name 필드를 같이 가져옵니다 (limit=0 → 모두)
    res = milvus_col.query(expr=expr, output_fields=["doc_id", "file_name"], limit=0)

    # Milvus가 청크 단위로 리턴하므로, 중복된 doc_id마다 file_name이 같다는 가정 하에 집계
    unique = {}
    for r in res:
        did = r["doc_id"]
        fname = r["file_name"]
        # 이미 등록된 doc_id는 건너뛰어 첫 번째 file_name만 저장
        if did not in unique:
            unique[did] = fname

    result = []
    for did, fname in unique.items():
        result.append({"doc_id": did, "file_name": fname, "status": "indexed"})
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 4) 특정 문서 상세 조회
# ─────────────────────────────────────────────────────────────────────────────
def get_document(user_id: str, doc_id: str) -> Dict[str, Any]:
    """
    - user_id+doc_id 필터 → Milvus에서 해당 문서(=여러 청크)의 metadata 조회
    - 반환 예시: {
    #     "doc_id": "...",
    #     "file_name": "hello.txt",
    #     "chunk_count": N,
    #     "preview": "...첫 번째 청크...",
    #     "status": "indexed"
    # }
    """
    milvus_col = _RAG_COLLECTION
    expr = f'user_id == "{user_id}" && doc_id == "{doc_id}"'

    # 첫 번째 청크의 텍스트(Preview)와 file_name 동시에 가져오기
    docs = milvus_col.query(expr=expr, output_fields=["text", "file_name"], limit=1)
    if not docs:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    preview = docs[0]["text"]
    file_name = docs[0]["file_name"]

    # 전체 청크 개수
    all_chunks = milvus_col.query(expr=expr, output_fields=["chunk_id"], limit=0)
    chunk_count = len(all_chunks)

    return {
        "doc_id": doc_id,
        "file_name": file_name,
        "chunk_count": chunk_count,
        "preview": preview,
        "status": "indexed",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5) 특정 문서 삭제
# ─────────────────────────────────────────────────────────────────────────────
def delete_document(user_id: str, doc_id: str) -> None:
    """
    - Milvus에서 user_id==... AND doc_id==... 조건을 만족하는 모든 청크 레코드를 삭제합니다.
    """
    milvus_col = _RAG_COLLECTION
    expr = f'user_id == "{user_id}" && doc_id == "{doc_id}"'
    milvus_col.delete(expr=expr)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 6) RAG 검색 및 LLM 호출
# ─────────────────────────────────────────────────────────────────────────────
def search_documents(user_id: str, request_data: RagSearch) -> Dict[str, Any]:
    """
    - request_data: {"query": "질의문", "filters": Optional[List[str]]}
    - 1) query embedding 생성 → 2) Milvus 벡터 검색 → 3) top_k 청크 추출 → 
      4) LLM에 컨텍스트 프롬프트 전송 → 5) 응답 반환
    """
    milvus_col = _RAG_COLLECTION

    query_text = request_data.query
    if not query_text:
        raise HTTPException(status_code=400, detail="검색할 쿼리를 입력하세요.")

    # 1) embedding 생성 (OpenAIEmbeddings)
    embedder = OpenAIEmbeddings()
    query_vector = embedder.embed_query(query_text)

    # 2) Milvus 유사도 검색
    filter_docs = request_data.filters    # Optional[List[str]]
    k = request_data.k or 5
    expr = f'user_id == "{user_id}"'
    if filter_docs:
        or_clauses = " OR ".join([f'doc_id == "{did}"' for did in filter_docs])
        expr = f'{expr} && ({or_clauses})'

    search_params = {"metric_type": "L2", "params": { "M": 16, "efConstruction": 200}}
    results = milvus_col.search(
        data=[query_vector],
        anns_field="embedding",
        param=search_params,
        limit=k,
        expr=expr,
        output_fields=["doc_id", "text"],    # ★ 반드시 이 두 필드를 리턴받아야 함
    )
    hits = results[0]  # top-k 결과

    # 3) 검색된 청크 텍스트를 순서대로 모아 context 생성
    retrieved_snippets = []
    for hit in hits:
        text_val = hit.entity.get("text") or ""
        snippet = {"text": text_val, "doc_id": hit.entity.get("doc_id"), "distance": hit.distance}
        retrieved_snippets.append(snippet)

    # 4) LLM 호출: ChatOpenAI + 간단한 PromptTemplate
    llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0)
    context = "\n\n".join([s["text"] for s in retrieved_snippets])
    prompt = f"""
You are a helpful assistant. Use the following document snippets to answer the user question:

{context}

Question: {query_text}
"""
    llm_response = llm.invoke(prompt)  # .invoke() 예시
    answer = llm_response.content

    # 5) 결과 반환: answer + sources (doc_id 리스트 + distance)
    sources = [{"doc_id": s["doc_id"], "distance": s["distance"]} for s in retrieved_snippets]

    return {"query": query_text, "answer": answer, "sources": sources}

