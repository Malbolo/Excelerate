import requests
import pandas as pd

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_milvus import Milvus
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.transform import TransformChain

from app.models.structure import FileAPIDetail

from app.services.code_gen.sample import sample_data
from app.core.config import settings

# ─────────────────────────────────────────────────────────────────────────────
# 2. VectorDB & Retriever 초기화
# ─────────────────────────────────────────────────────────────────────────────
class FileAPIClient:
    def __init__(
        self,
        host: str = settings.MILVUS_HOST,
        port: int = settings.MILVUS_PORT,
        collection_name: str = "factory_catalog",
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
            ("system", "다음 필드를 추출하세요: factory_name, system_name, metric, factory_id, start_date"),
            ("system", "해당하는 값이 없으면 null로 두세요."),
            ("system", "<context>\n{context}\n</context>"),
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

    def _validate(self, q: FileAPIDetail):
        # 1) factory_info 문서 가져오기
        docs     = list(self.retriever.invoke(q.factory_name))
        fact_doc = next(d for d in docs if d.metadata["type"] == "factory_info")

        # 2) metadata 로부터 유효값 파싱
        valid_ids     = [fact_doc.metadata["factory_id"]]
        valid_metrics = fact_doc.metadata["metric_list"].split(",")
        # valid_prods   = fact_doc.metadata["product_list"].split(",") # prod 값 추출 시 이것도 체크

        if q.factory_id not in valid_ids:
            raise ValueError(f"{q.factory_name}의 factory_id '{q.factory_id}'가 유효하지 않습니다.")
        if q.metric not in valid_metrics:
            raise ValueError(f"{q.factory_name}는 metric '{q.metric}'을 지원하지 않습니다.")

    def _assemble_url(self, q: FileAPIDetail) -> str:
        # 예시 URL: /{system_name}/factory-data/{metric}?product_code=...&start_date=...
        path  = f"/{q.system_name}/factory-data/{q.metric}"
        query = f"?factory_id={q.factory_id}&start_date={q.start_date}"
        return self.base_url + path + query

    def run(self, user_input: str) -> pd.DataFrame:
        # 1) 쿼리 분할
        # 쿼리가 다중 API 호출이 필요한 경우, 쿼리를 분할하여 처리해야 함
        # 분할 하여 처리 후 각각의 결과를 조합하는 로직 필요
        # 예시 : 한국 지사의 DA 그룹 B, D 제품의 kpi 보고서를 2025-03-01부터 2025-04-22까지 가져와
        # → 한국 지사의 DA 그룹 B 제품의 kpi 보고서를 2025-03-01부터 2025-04-22까지 가져와
        # → 한국 지사의 DA 그룹 D 제품의 kpi 보고서를 2025-03-01부터 2025-04-22까지 가져와
        # 실제 파일 시스템이 한번에 여러 그룹의 제품 정보를 한번에 호출할 수 있는 지 확인 필요.


        # 2) 엔티티 추출
        result = create_retrieval_chain(self.retriever, self.extractor_chain).invoke({
            "input": user_input
        })
        entities : FileAPIDetail = result['answer']
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