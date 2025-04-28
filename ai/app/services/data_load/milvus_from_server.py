import requests

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_milvus import Milvus
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.transform import TransformChain

from pydantic import BaseModel, Field

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
def init_vectorstore():
    """
    기존에 삽입해 둔 'catalog_docs' 컬렉션을 Milvus 서버에서 불러와
    그대로 검색에만 사용합니다. 문서 재삽입은 하지 않습니다.
    """
    emb = OpenAIEmbeddings()
    store = Milvus(
        embedding_function=emb,                      # 임베딩 함수
        connection_args={"host": "localhost",        # Milvus 서버 접속 정보
                         "port": 19530},
        collection_name="catalog_docs"               # 이미 생성·삽입해 둔 컬렉션 이름
    )
    return store

def init_retriever(vectorstore, k=3):
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})

# ─────────────────────────────────────────────────────────────────────────────
# 3. Entity Extractor - Structure data version 구성 (prompt | llm)
# ─────────────────────────────────────────────────────────────────────────────
def init_entity_extractor():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "주어진 자연어 요청을 기반으로 context로 부터 다음 필드를 추출하세요: location, startdate, enddate, group, product, metric"),
        ("system", "값이 없으면 null로 두세요."),
        ("system", "<context>\n{context}\n{metric_list}\n</context>"),
        ("human", "{input}")
    ])
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(FileAPIDetail)
    
    # Context flattening chain
    # (context: list[Document] → context: str)
    flatten_chain = TransformChain(
        input_variables=["context"],
        output_variables=["context"],
        transform=lambda inputs: {
            "context": "\n".join(d.page_content for d in inputs["context"])
        }
    )
    
    qa_chain = flatten_chain | prompt | structured_llm

    return qa_chain


# ─────────────────────────────────────────────────────────────────────────────
# 4. 유효성 검증
# ─────────────────────────────────────────────────────────────────────────────
def validate_entities(entities, retriever):
    # location → groups/products
    loc_doc = next(
        d for d in retriever.invoke(entities["location"])
        if d.metadata["type"] == "location_info"
    )
    groups = loc_doc.metadata["groups"].split(",")
    prods = loc_doc.metadata["products"].split(",")
    if entities["group"] not in groups:
        raise ValueError(f"{entities['group']} 그룹은 {entities['location']} 지사에 없습니다.")
    if entities["product"] not in prods:
        raise ValueError(f"{entities['product']} 제품은 {entities['location']} 지사에 없습니다.")

    met_doc = next(
        d for d in retriever.invoke("metric 목록")
        if d.metadata["type"] == "metric_info"
    )
    metrics = met_doc.metadata["metrics"].split(",")
    if entities["metric"] not in metrics:
        raise ValueError(f"{entities['metric']} 는 지원되지 않는 metric 입니다.")

# ─────────────────────────────────────────────────────────────────────────────
# 5. URL 조합
# ─────────────────────────────────────────────────────────────────────────────
def assemble_url(entities, base_url="https://filesystem.com"):
    path = "/api/v1/{location}/{group}/{product}/{metric}".format(**entities)
    query = f"?startdate={entities['startdate']}&enddate={entities['enddate']}"
    return base_url + path + query

# ─────────────────────────────────────────────────────────────────────────────
# 6. 데이터 호출
# ─────────────────────────────────────────────────────────────────────────────
def fetch_data(url: str) -> dict:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

# ─────────────────────────────────────────────────────────────────────────────
# 7. 요청 핸들러
# ─────────────────────────────────────────────────────────────────────────────
def handle_request(user_input: str, retriever, extractor) -> str:
    # 7-0. 쿼리 분할
    # 쿼리가 다중 API 호출이 필요한 경우, 쿼리를 분할하여 처리해야 함
    # 분할 하여 처리 후 각각의 결과를 조합하는 로직 필요
    # 예시 : 한국 지사의 DA 그룹 B, D 제품의 kpi 보고서를 2025-03-01부터 2025-04-22까지 가져와
    # → 한국 지사의 DA 그룹 B 제품의 kpi 보고서를 2025-03-01부터 2025-04-22까지 가져와
    # → 한국 지사의 DA 그룹 D 제품의 kpi 보고서를 2025-03-01부터 2025-04-22까지 가져와
    # 실제 파일 시스템이 한번에 여러 그룹의 제품 정보를 한번에 호출할 수 있는 지 확인 필요.

    # 7-1. 엔티티 추출
    # metric list 호출
    met_doc = next(
        d for d in retriever.invoke("metric 목록")
        if d.metadata["type"] == "metric_info"
    )
    metrics = met_doc.metadata["metrics"].split(",")
    
    # rag 체인 생성, invoke
    rag_chain = create_retrieval_chain(retriever,  extractor)

    file_params: FileAPIDetail = rag_chain.invoke({
        "metric_list": "metric 목록 → " + ", ".join(metrics),
        "input":   user_input
    })
    print("=======================================")
    print(f"체인 실행 결과: \n{file_params['answer']}")  # 디버깅용
    print("=======================================")
    entities = file_params['answer'].model_dump()
    # 7-2. 유효성 검증
    validate_entities(entities, retriever)
    # 7-3. URL 생성 & 호출
    url = assemble_url(entities)
    # raw = fetch_data(url)
    return url
    # 7-4. DataFrame 반환
    # return pd.DataFrame(raw["data"])

# ─────────────────────────────────────────────────────────────────────────────
# 8. 초기화 & 실행 예시
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    store      = init_vectorstore()
    retriever  = init_retriever(store)
    extractor  = init_entity_extractor()

    query      = "베트남 지사의 DX 그룹 A 제품 불량률을 2025-01-01부터 2025-03-31까지 가져와"
    # query      = "한국 지사의 DA 그룹 D 제품 kpi 보고서를 2025-03-01부터 2025-04-22까지 가져와"
    # query      = "한국 지사의 DA 그룹 A 제품 kpi 보고서를 2025-03-01부터 2025-04-22까지 가져와"

    # df         = handle_request(query, retriever, extractor)
    # print(df.head())
    url = handle_request(query, retriever, extractor)
    print(url)