from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_milvus import Milvus
from app.models.structure import FactoryCatalog

def build_catalog_documents(catalog: FactoryCatalog) -> list[Document]:
    docs: list[Document] = []
    for factory_name, info in catalog.root.items():
        # 1) 공장 단위 요약 문서
        docs.append(Document(
            page_content=(
                f"{factory_name}({info.factory_id}) → "
                f"제품코드: {', '.join(info.product.keys())}; "
                f"metrics: {', '.join(info.metric_list)}"
            ),
            metadata={
                "type":         "factory_info",
                "factory_name": factory_name,
                "factory_id":   info.factory_id,
                "products":     ",".join(info.product.keys()),
                "metrics":      ",".join(info.metric_list),
            }
        ))
        # 2) 개별 제품 문서 (옵션)
        for code, prod in info.product.items():
            docs.append(Document(
                page_content=(
                    f"{factory_name} - {prod.name} (코드: {code}), "
                    f"카테고리: {prod.category}"
                ),
                metadata={
                    "type":          "product_info",
                    "factory_name":  factory_name,
                    "factory_id":    info.factory_id,
                    "product_code":  code,
                    "product_name":  prod.name,
                    "category":      prod.category,
                }
            ))
    return docs


class CatalogIngestor:
    def __init__(
        self,
        catalog_data: dict,
        *,
        connection_args: dict     = {"host": "localhost", "port": 19530},
        collection_name: str      = "factory_catalog",
        index_params: dict        = {"index_type": "HNSW", "metric_type": "L2"},
        drop_old: bool            = True
    ):
        # raw dict → Pydantic 모델
        self.catalog: FactoryCatalog = FactoryCatalog.parse_obj(catalog_data)
        self.connection_args = connection_args
        self.collection_name = collection_name
        self.index_params    = index_params
        self.drop_old        = drop_old
        self.embedding       = OpenAIEmbeddings()

    def run(self) -> Milvus:
        # 1) Document 생성
        docs = build_catalog_documents(self.catalog)
        print(docs)

        # 2) metadata 키 통일 (optional)
        all_keys = set().union(*(d.metadata.keys() for d in docs))
        for d in docs:
            for k in all_keys:
                d.metadata.setdefault(k, "")

        # 3) Milvus에 업로드
        store = Milvus.from_documents(
            documents=docs,
            embedding=self.embedding,
            connection_args=self.connection_args,
            collection_name=self.collection_name,
            index_params=self.index_params,
            drop_old=self.drop_old,
        )
        return store
