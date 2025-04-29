from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_milvus import Milvus

def build_catalog_documents() -> list[Document]:
    location_map = {
        "vietnam": {"groups": ["DX", "DA"], "products": ["A", "B"]},
        "china":   {"groups": ["MX", "SDS"], "products": ["C", "D"]},
        "japan":   {"groups": ["DX", "MX"], "products": ["A", "C"]},
        "korea":   {"groups": ["DA", "SDS"], "products": ["B", "D"]},
        "usa":     {"groups": ["MX", "DA"], "products": ["A", "D"]},
    }
    metric_list = ["불량률", "production", "sales_report", "kpi_report"]

    docs: list[Document] = []
    for loc, info in location_map.items():
        docs.append(Document(
            page_content=f"{loc} 지사 → 그룹: {','.join(info['groups'])}; 제품: {','.join(info['products'])}",
            metadata={
                "type":     "location_info",
                "location": loc,
                "groups":   ",".join(info["groups"]),
                "products": ",".join(info["products"]),
            }
        ))
    docs.append(Document(
        page_content="metric 목록 → " + ", ".join(metric_list),
        metadata={
            "type":    "metric_info",
            "metrics": ",".join(metric_list),
        }
    ))
    return docs

class CatalogIngestor:
    """
    build_catalog_documents()로 생성된 docs를 Milvus에 업로드합니다.
    .run() 호출만으로 자동으로 문서 생성→임베딩→저장 과정을 처리합니다.
    """
    def __init__(
        self,
        *,
        connection_args: dict = {"host": "localhost", "port": 19530},
        collection_name: str = "catalog_docs",
        index_params: dict = {"index_type": "HNSW", "metric_type": "L2"},
        drop_old: bool = True
    ):
        self.connection_args = connection_args
        self.collection_name = collection_name
        self.index_params = index_params
        self.drop_old = drop_old
        self.embedding = OpenAIEmbeddings()

    def run(self) -> Milvus:
        # 1. 문서 생성
        docs = build_catalog_documents()

        all_keys = set().union(*(doc.metadata.keys() for doc in docs))
        for doc in docs:
            for key in all_keys:
                doc.metadata.setdefault(key, "")

        # 2. Milvus에 저장
        store = Milvus.from_documents(
            documents=docs,
            embedding=self.embedding,
            connection_args=self.connection_args,
            collection_name=self.collection_name,
            index_params=self.index_params,
            drop_old=self.drop_old,
        )
        return store
