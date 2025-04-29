import json
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_milvus import Milvus
from app.core.config import settings

def build_catalog_documents(catalog: dict) -> list[Document]:
    docs: list[Document] = []
    for factory_name, info in catalog.items():
        # 1) page_content: JSON 문자열(혹은 사람이 읽기 편한 포맷)으로 통째로 기록
        content = json.dumps({factory_name: info}, ensure_ascii=False)

        # 2) metadata: RAG 검색·검증에 필요한 키만 뽑아서 저장
        docs.append(Document(
            page_content=content,
            metadata={
                "type":          "factory_info",
                "factory_name":  factory_name,
                "system_name":   info["system_name"],
                "factory_id":    info["factory_id"],
                "product_list":  ",".join(info["product"].keys()),
                "metric_list":   ",".join(info["metric_list"]),
            }
        ))

    return docs


class CatalogIngestor:
    def __init__(
        self,
        catalog_data: dict,
        *,
        connection_args: dict     = {"host": settings.MILVUS_HOST, "port": settings.MILVUS_PORT},
        collection_name: str      = "factory_catalog",
        index_params: dict        = {"index_type": "HNSW", "metric_type": "L2"},
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
        print(docs)
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
