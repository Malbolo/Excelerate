from typing import List
import requests
import pandas as pd
import logging
import time
from datetime import date

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_milvus import Milvus
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.transform import TransformChain
from pymilvus import connections, utility
from fastapi import HTTPException

from app.core.config import settings
from app.models.log import LogDetail
from app.models.structure import FileAPIDetail

from app.services.data_load.data_util import is_iso_date

from app.utils.memory_logger import MemoryLogger
from app.utils.api_utils import get_log_queue
from app.utils.chatprompt.redis_chatprompt import load_chat_template
from app.services.code_gen.graph_util import log_filter

# 로깅 설정
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# 2. VectorDB & Retriever 초기화
# ─────────────────────────────────────────────────────────────────────────────
class FileAPIClient:
    def __init__(
            self,
            host: str = settings.MILVUS_HOST,
            port: int = settings.MILVUS_PORT,
            collection_name: str = "factory_catalog",
            k: int = 2,
            model_name: str = "gpt-4.1-mini",
            base_url: str = settings.FILESYSTEM_URL,
    ):
        self.mlogger = MemoryLogger()
        self.llm = ChatOpenAI(model_name=model_name, temperature=0, callbacks=[self.mlogger])
        self.emb = OpenAIEmbeddings()
        # Milvus 초기화 시도
        self.store = self._initialize_milvus(host, port, collection_name)

        if self.store:
            self.retriever = self.store.as_retriever(
                search_type="similarity", search_kwargs={"k": k}
            )
        else:
            logger.warning("Milvus 연결 실패. 검색 기능이 제한됩니다.")
            self.retriever = None
        
        self.base_url = base_url
        self.logs : List[LogDetail] = []

    def _initialize_milvus(self, host, port, collection_name):
        """Milvus 연결을 초기화하는 메서드, 실패 시 None 반환"""
        logger.info(f"Milvus 연결 시도: {host}:{port}, 컬렉션: {collection_name}")

        max_retries = 5
        retry_interval = 3  # 초

        for attempt in range(max_retries):
            try:
                logger.info(f"Milvus 연결 시도 {attempt+1}/{max_retries}: {host}:{port}")

                # pymilvus 연결 (TCP URI 사용)
                connections.connect(
                    uri=f"tcp://{host}:{port}"
                )

                # 연결 테스트
                collection_list = utility.list_collections()
                logger.info(f"사용 가능한 컬렉션 목록: {collection_list}")

                collection_exists = collection_name in collection_list
                logger.info(f"Milvus 컬렉션 '{collection_name}' 존재 여부: {collection_exists}")

                if not collection_exists:
                    logger.warning(f"컬렉션 '{collection_name}'이 없습니다.")

                # LangChain Milvus 초기화
                logger.info("LangChain Milvus 래퍼 초기화 중...")
                store = Milvus(
                    embedding_function=self.emb,
                    connection_args={
                        "uri": f"tcp://{host}:{port}"
                    },
                    collection_name=collection_name,
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
    
    def _available_params(self) -> str:
        guide = "유효한 파라미터 목록:\n\n"
        if not self.retriever:
            guide += "Milvus 연결이 없습니다. 검색 기능이 제한됩니다.\n"
            return guide
        try:
            # 1) 호출 직전에 k 값을 충분히 크게 설정
            self.retriever.search_kwargs["k"] = 10
            # 2) factory_info 문서 가져오기 (이제 최대 10개까지 가져옴)
            docs = list(self.retriever.invoke("factory_info"))
            self.retriever.search_kwargs["k"] = 2 # 원래 k 값으로 복원
            if not docs:
                guide += "등록된 factory_info 문서가 없습니다.\n"
                return guide
            
            for doc in docs:
                metadata = doc.metadata
                factory_name = metadata.get("factory_name", "알 수 없음")
                factory_id = metadata.get("factory_id", "알 수 없음")
                metric_list = metadata.get("metric_list", "").split(",")
                product_list = metadata.get("product_list", "").split(",")
                guide += f"Factory: {factory_name} (ID: {factory_id})\n"
                guide += f"  - 지원 Metric: {', '.join(metric_list) if metric_list else '없음'}\n"
                guide += f"  - 지원 Product: {', '.join(product_list) if product_list else '없음'}\n\n"
            guide += "사용법 예시:\n"
            guide += "  - '2025년 2월부터' : 시작 날짜를 지정합니다.\n"
            guide += "  - '2025년 2월부터 3월까지' : 시작 및 종료 날짜를 지정합니다.\n"
            guide += "  - '공장 A의 metric X' : 특정 공장과 메트릭을 지정합니다.\n"
            guide += "ex) 2025년 2월부터 3월까지 공장 A의 metric X 데이터 가져와\n"
        except Exception as e:
            logger.error(f"파라미터 목록 추출 중 오류 발생: {e}")
            guide += "파라미터 목록을 가져오는 중 오류가 발생했습니다. Milvus 연결을 확인해주세요."

        return guide

    def extract_params_chain(self):
        # Entity extractor chain
        prompt = load_chat_template("Data Loader:Extract DataCall Params")
        structured = self.llm.with_structured_output(FileAPIDetail)
        
        today_chain = TransformChain(
            input_variables=[],
            output_variables=["today"],
            transform=lambda _: {"today": date.today().isoformat()}
        )
        
        flatten = TransformChain(
            input_variables=["context"],
            output_variables=["context"],
            transform=lambda i: {"context": "\n".join(d.page_content for d in i["context"])}
        )
        extractor_chain = today_chain | flatten | prompt | structured
        return extractor_chain

    def fetch_data(self, url: str) -> dict:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def _validate(self, q: FileAPIDetail):
        if not self.retriever:
            logger.warning("Milvus 연결이 없어 검증을 건너뜁니다.")
            return

        try:
            # 1) factory_info 문서 가져오기
            docs = list(self.retriever.invoke(q.factory_name))
            fact_doc = next((d for d in docs if d.metadata.get("type") == "factory_info"), None)

            if not fact_doc:
                logger.warning(f"'{q.factory_name}' 관련 factory_info 문서를 찾을 수 없습니다.")
                return

            # 2) metadata 로부터 유효값 파싱
            valid_ids = [fact_doc.metadata.get("factory_id", "")]
            valid_metrics = fact_doc.metadata.get("metric_list", "").split(",")
            valid_prods = fact_doc.metadata.get("product_list", "").split(",")

            if q.factory_id not in valid_ids:
                raise  ValueError(f"{q.factory_name}의 factory_id '{q.factory_id}'가 유효하지 않습니다.")
            if q.metric not in valid_metrics:
                raise  ValueError(f"{q.factory_name}는 metric '{q.metric}'을 지원하지 않습니다.")
            if q.product_code and q.product_code not in valid_prods:
                raise  ValueError(f"{q.factory_name}에는 product_code '{q.product_code}'가 없습니다.")
        except Exception as e:
            logger.error(f"검증 중 오류 발생: {e}")
            data_guide = self._available_params()
            raise HTTPException(status_code=400, detail=f"Data fetch failed: {e}\n\n{data_guide}")

    def _transform_date_field(self, start_expr: str, end_expr: str, q, queue):       
        queue.put_nowait({"type":"notice","content":f"날짜 표현을 ISO-7801으로 변환 중"})
        self.mlogger.set_name(f"LLM Call: Transform Date Params")

        # 2-1) 날짜 계산용 템플릿 꺼내기
        prompt = load_chat_template("Data Loader:Transform Date Params")
        date_chain = prompt | self.llm

        # 2-2) expr 에 원본 텍스트 넣고 코드 스니펫 받기
        code_snippet: str = date_chain.invoke({"start_expr": start_expr, "end_expr": end_expr}).content

        # 2-3) exec 으로 실행해서 namespace 에서 startdate 꺼내기
        namespace: dict = {}
        exec(code_snippet, namespace)
        setattr(q, "start_date", namespace["startdate"])
        setattr(q, "end_date", namespace["enddate"])

        llm_entry = self.mlogger.get_logs()[-1] if self.mlogger.get_logs() else None
        self.logs.append(llm_entry)
        log = log_filter(llm_entry)

        queue.put_nowait({"type":"code","content": code_snippet})
        queue.put_nowait({"type":"log","content": log})
        return code_snippet

    def _assemble_url(self, q: FileAPIDetail) -> str:
        # 예시 URL: /{system_name}/factory-data/{metric}?product_code=...&start_date=...
        path = f"/{q.system_name}/factory-data/{q.metric}"
        query = (
            f"?factory_id={q.factory_id}"
            f"&start_date={q.start_date}"
        )
        if q.end_date:
            query += f"&end_date={q.end_date}"
        if q.product_code:
            query += f"&product_code={q.product_code}"
        return self.base_url + path + query

    def run(self, user_input: str, stream_id: str) -> tuple[str, pd.DataFrame, list[LogDetail], FileAPIDetail]:
        self.mlogger.set_name("LLM Call: Extract DataCall Params")
        self.mlogger.reset()
        self.logs = []

        q = get_log_queue(stream_id)
        q.put_nowait({"type": "notice", "content": "요청으로부터 파라미터를 추출중입니다."})

        python_code = None

        extract_chain = self.extract_params_chain()

        # 1) 엔티티 추출
        if self.retriever:
            result = create_retrieval_chain(self.retriever, extract_chain).invoke({"input": user_input})
            entities: FileAPIDetail = result['answer']
        else:
            # retriever가 없는 경우 직접 추출
            result = extract_chain.invoke({"context": "", "input": user_input})
            entities: FileAPIDetail = result

        llm_entry = self.mlogger.get_logs()[-1] if self.mlogger.get_logs() else None
        self.logs.append(llm_entry)
        log = log_filter(llm_entry)
        # 로그 스트리밍
        q.put_nowait({"type": "log", "content": log})

        if entities.start_date is "":
            raise HTTPException(status_code=400, detail=f"데이터 호출을 위해선 start_date가 필요합니다. 질의에 날짜를 포함해주세요.\n\n ex) '2025년 2월부터', '지난달 부터' 등")

        # 2) date가 ISO 포맷이 아니면 → LLM으로 코드 생성 후 exec
        if not is_iso_date(entities.start_date) or (entities.end_date and not is_iso_date(entities.end_date)):
            python_code = self._transform_date_field(entities.start_date, entities.end_date, entities, q)

        # 3) 검증
        self._validate(entities)

        # 4) URL 생성 & 호출
        url = self._assemble_url(entities)
        logger.info(f"API 호출 URL: {url}")
        q.put_nowait({"type": "notice", "content": "서버에서 데이터를 불러오는 중..."})

        try:
            raw = self.fetch_data(url)
        except Exception as e:
            logger.warning(f"API 호출 실패: {e}")
            data_guide = self._available_params()
            raise HTTPException(status_code=404, detail=f"API 호출에 실패했습니다. URL: {url}, 에러: {str(e)}\n\n존재하지 않는 파라미터 입니다. 유효한 파라미터는 다음과 같습니다.\n\n{data_guide}")

        dataframe = pd.DataFrame(raw["data"])
        q.put_nowait({"type": "data", "content": dataframe.to_dict(orient="records")})
        q.put_nowait({"type": "notice", "content": "data를 불러왔습니다."})

        # 5) DataFrame 반환
        return url, pd.DataFrame(raw["data"]), self.logs, python_code, entities
