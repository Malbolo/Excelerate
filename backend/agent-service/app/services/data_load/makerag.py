import json
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_milvus import Milvus
from app.core.config import settings
from typing import List, Dict
from pymilvus import connections, utility
import logging
import time

# 로깅 설정
logger = logging.getLogger(__name__)

def build_catalog_documents(catalog: List[Dict]) -> List[Document]:
    """
    catalog: List of dicts, each containing factory_name, system_name, factory_id, product, metric_list, etc.
    [
      {
        "factory_name": "수원공장",
        "system_name": "mes",
        "factory_id": "FCT001",
        "product": { ... },
        "metric_list": [ ... ]
      },
      ...
    ]
    """
    docs: List[Document] = []
    for info in catalog:
        factory_name = info.get("factory_name", "")
        # page_content엔 전체 엔트리 JSON 직렬화
        content = json.dumps(info, ensure_ascii=False)
        # metadata엔 검색·검증용 필드만
        metadata = {
            "type":         "factory_info",
            "factory_name": factory_name,
            "system_name":  info.get("system_name", ""),
            "factory_id":   info.get("factory_id", ""),
            # product 딕셔너리 키 목록을 쉼표로 연결
            "product_list": ",".join(info.get("product", {}).keys()),
            # metric_list를 쉼표로 연결
            "metric_list":  ",".join(info.get("metric_list", [])),
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


class CatalogIngestor:
    def __init__(
        self,
        catalog_data: List[Dict],
        *,
        connection_args: dict     = {"host": settings.MILVUS_HOST, "port": settings.MILVUS_PORT},
        collection_name: str      = "factory_catalog",
        index_params: dict        = {"index_type": "HNSW", "metric_type": "L2", "params": { "M": 16, "efConstruction": 200}},
        drop_old: bool            = True
    ):
        self.catalog_data   = catalog_data
        self.connection_args = connection_args
        self.collection_name = collection_name
        self.index_params    = index_params
        self.drop_old        = drop_old
        self.embedding       = OpenAIEmbeddings()

    def run(self) -> Milvus:
        docs = build_catalog_documents(self.catalog_data)
        # 메타데이터 키 통일
        all_keys = set().union(*(d.metadata.keys() for d in docs))
        for d in docs:
            for k in all_keys:
                d.metadata.setdefault(k, "")

        max_retries = 5
        retry_interval = 3  # 초

        host=self.connection_args["host"]
        port=self.connection_args["port"]

        for attempt in range(max_retries):
            try:
                logger.info(f"Milvus 연결 시도 {attempt+1}/{max_retries}: {host}:{port}")

                # pymilvus 연결 (TCP URI 사용)
                connections.connect(
                    uri=f"tcp://{host}:{port}"
                )

                # LangChain Milvus 초기화
                logger.info("LangChain Milvus 래퍼 초기화 중...")
                store = Milvus.from_documents(
                    documents=docs,
                    embedding=self.embedding,
                    connection_args={
                        "uri": f"tcp://{host}:{port}"
                    },
                    collection_name=self.collection_name,
                    index_params=self.index_params,
                    drop_old=self.drop_old,
                )

                logger.info("Milvus 연결 성공!")
                return store

            except Exception as e:
                logger.warning(f"Milvus 연결 시도 {attempt+1} 실패: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"{retry_interval}초 후 재시도...")
                    time.sleep(retry_interval)

        logger.error(f"Milvus 연결 모두 실패 ({max_retries}회 시도)")

        return None
