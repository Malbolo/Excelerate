import json
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_milvus import Milvus
from app.core.config import settings
from typing import List, Dict

def build_catalog_documents(catalog: List[Dict]) -> List[Document]:
    """
    catalog: List of dicts, each mapping factory_name to its info dict:
    [
      {"수원공장": {"system_name":..., "factory_id":..., ...}},
      {"서울공장": {...}},
      ...
    ]
    """
    docs: List[Document] = []
    for entry in catalog:
        # 각 entry는 {factory_name: info_dict}
        for factory_name, info in entry.items():
            # 전체 JSON 구조 저장
            content = json.dumps({factory_name: info}, ensure_ascii=False)
            # metadata에는 검색 및 검증 필드만
            metadata = {
                "type":         "factory_info",
                "factory_name": factory_name,
                "system_name":  info.get("system_name", ""),
                "factory_id":   info.get("factory_id", ""),
                "product_list": ",".join(info.get("product", {}).keys()),
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

        store = Milvus.from_documents(
            documents=docs,
            embedding=self.embedding,
            connection_args=self.connection_args,
            collection_name=self.collection_name,
            index_params=self.index_params,
            drop_old=self.drop_old,
        )
        return store
