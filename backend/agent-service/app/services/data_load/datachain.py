import requests
import pandas as pd

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_milvus import Milvus
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.transform import TransformChain

from pydantic import BaseModel, Field
from app.services.code_gen.sample import sample_data

class FileAPIDetail(BaseModel):
    location: str = Field(description="파일을 불러올 지사 정보. 지사를 붙이지 말고 이름만 가져오세요. 예: vietnam, china")
    startdate: str = Field(description="파일을 불러올 시작일. 예: 2025-01-01")
    enddate: str = Field(description="파일을 불러올 종료일. 예: 2025-03-31")
    group: str = Field(description="파일을 불러올 그룹 정보. 예: DX, DA")
    product: str = Field(description="파일을 불러올 제품 정보. 예: A, B")
    metric: str = Field(description="파일을 불러올 metric 정보. 예: 불량률, production")

# ─────────────────────────────────────────────────────────────────────────────
# 2. VectorDB & Retriever 초기화
# ─────────────────────────────────────────────────────────────────────────────
class FileAPIClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 19530,
        collection_name: str = "catalog_docs",
        k: int = 3,
        model_name: str = "gpt-4o-mini",
        base_url: str = "https://filesystem.com",
    ):
        # VectorDB + Retriever
        emb = OpenAIEmbeddings()
        store = Milvus(
            embedding_function=emb,
            connection_args={"host": host, "port": port},
            collection_name=collection_name,
        )
        self.retriever = store.as_retriever(
            search_type="similarity", search_kwargs={"k": k}
        )
        # Entity extractor chain
        prompt = ChatPromptTemplate.from_messages([
            ("system", "다음 필드를 추출하세요: location, startdate, enddate, group, product, metric"),
            ("system", "값 없으면 null로 두세요."),
            ("system", "<context>\n{context}\n{metric_list}\n</context>"),
            ("human", "{input}")
        ])
        llm = ChatOpenAI(model_name=model_name, temperature=0)
        structured = llm.with_structured_output(FileAPIDetail)
        flatten = TransformChain(
            input_variables=["context"],
            output_variables=["context"],
            transform=lambda i: {"context": "\n".join(d.page_content for d in i["context"])}
        )
        self.extractor_chain = flatten | prompt | structured
        self.base_url = base_url

    def fetch_data(self, url: str) -> dict:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def _validate(self, e: dict):
        # location → groups/products 검증
        docs = list(self.retriever.invoke(e["location"]))
        loc_doc = next(d for d in docs if d.metadata["type"] == "location_info")
        groups = loc_doc.metadata["groups"].split(",")
        prods  = loc_doc.metadata["products"].split(",")
        if e["group"] not in groups:
            raise ValueError(f"{e['group']} 그룹은 {e['location']} 지사에 없습니다.")
        if e["product"] not in prods:
            raise ValueError(f"{e['product']} 제품은 {e['location']} 지사에 없습니다.")
        # metric 검증
        met_doc = next(d for d in self.retriever.invoke("metric 목록") if d.metadata["type"] == "metric_info")
        metrics = met_doc.metadata["metrics"].split(",")
        if e["metric"] not in metrics:
            raise ValueError(f"{e['metric']} 는 지원되지 않는 metric 입니다.")

    def _assemble_url(self, e: dict) -> str:
        path  = f"/api/v1/{e['location']}/{e['group']}/{e['product']}/{e['metric']}"
        query = f"?startdate={e['startdate']}&enddate={e['enddate']}"
        return self.base_url + path + query

    def run(self, user_input: str) -> pd.DataFrame:
        # 1) metric 목록 조회
        met_doc = next(d for d in self.retriever.invoke("metric 목록") if d.metadata["type"] == "metric_info")
        metrics = met_doc.metadata["metrics"].split(",")
        metric_list = "metric 목록 → " + ", ".join(metrics)

        # 2) 엔티티 추출
        result = create_retrieval_chain(self.retriever, self.extractor_chain).invoke({
            "context": [],
            "metric_list": metric_list,
            "input": user_input
        })
        entities: FileAPIDetail = result['answer'].model_dump()

        # 3) 검증
        self._validate(entities)

        # 4) URL 생성 & 호출
        url = self._assemble_url(entities)
        print(url) # url 체크
        try:
            raw = self.fetch_data(url)
        except:
            print("아직 API 연결이 안됐어요")
            raw = sample_data

        # 5) DataFrame 반환
        return url, pd.DataFrame(raw["data"])