import requests
import pandas as pd
import logging
import time
from datetime import date

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_milvus import Milvus
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.transform import TransformChain
from pymilvus import connections, utility
from fastapi import HTTPException

from app.models.log import LogDetail
from app.models.structure import FileAPIDetail

from app.utils.memory_logger import MemoryLogger

from app.core.config import settings
from app.services.data_load.data_util import make_entity_extraction_prompt, make_date_code_template, is_iso_date
from app.utils.api_utils import get_log_queue

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
            k: int = 3,
            model_name: str = "gpt-4.1-nano",
            base_url: str = settings.FILESYSTEM_URL,
    ):
        # 임베딩 초기화
        self.emb = OpenAIEmbeddings()

        self.mlogger = MemoryLogger()
        # Milvus 초기화 시도
        self.store = self._initialize_milvus(host, port, collection_name)

        if self.store:
            self.retriever = self.store.as_retriever(
                search_type="similarity", search_kwargs={"k": k}
            )
        else:
            logger.warning("Milvus 연결 실패. 검색 기능이 제한됩니다.")
            self.retriever = None

        # Entity extractor chain
        prompt = make_entity_extraction_prompt()
        self.llm = ChatOpenAI(model_name=model_name, temperature=0, callbacks=[self.mlogger])
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
        self.extractor_chain = today_chain | flatten | prompt | structured
        self.base_url = base_url

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
                raise ValueError(f"{q.factory_name}의 factory_id '{q.factory_id}'가 유효하지 않습니다.")
            if q.metric not in valid_metrics:
                raise ValueError(f"{q.factory_name}는 metric '{q.metric}'을 지원하지 않습니다.")
            if q.product_code and q.product_code not in valid_prods:
                raise ValueError(f"{q.factory_name}에는 product_code '{q.product_code}'가 없습니다.")
        except Exception as e:
            logger.error(f"검증 중 오류 발생: {e}")
            raise HTTPException(status_code=400, detail=f"Data fetch failed: {e}")

    def _assemble_url(self, q: FileAPIDetail) -> str:
        # 예시 URL: /{system_name}/factory-data/{metric}?product_code=...&start_date=...
        path = f"/{q.system_name}/factory-data/{q.metric}"
        query = (
            f"?factory_id={q.factory_id}"
            f"&start_date={q.start_date}"
        )
        if q.product_code:
            query += f"&product_code={q.product_code}"
        return self.base_url + path + query

    def run(self, user_input: str, stream_id: str) -> tuple[str, pd.DataFrame, list[LogDetail], FileAPIDetail]:
        self.mlogger.set_name("LLM Call: Extract DataCall Params")
        self.mlogger.reset()

        q = get_log_queue(stream_id)

        python_code = None

        # 1) 엔티티 추출
        if self.retriever:
            result = create_retrieval_chain(self.retriever, self.extractor_chain).invoke({
                "input": user_input
            })
            entities: FileAPIDetail = result['answer']
        else:
            # retriever가 없는 경우 직접 추출
            result = self.extractor_chain.invoke({
                "context": "",
                "input": user_input
            })
            entities: FileAPIDetail = result

        entity_logs: list[LogDetail] = self.mlogger.get_logs()
        # 로그 스트리밍
        q.put_nowait({"type": "log", "content": entity_logs[-1].model_dump_json()})

        if entities.start_date is None:
            raise HTTPException(status_code=400, detail=f"Start date is required")

        # 2) start_date가 ISO 포맷이 아니면 → LLM으로 코드 생성 후 exec
        if not is_iso_date(entities.start_date):
            self.mlogger.set_name("LLM Call: Transfrom Date Param")
            # 2-1) 날짜 계산용 템플릿 꺼내기
            prompt = make_date_code_template()
            date_chain = prompt | self.llm

            # 2-2) expr 에 원본 텍스트 넣고 코드 스니펫 받기
            code_snippet: str = date_chain.invoke({"expr": entities.start_date}).content
            # 2-3) exec 으로 실행해서 namespace 에서 startdate 꺼내기
            namespace: dict = {}
            exec(code_snippet, namespace)
            entities.start_date = namespace["startdate"]
            python_code = code_snippet

            entity_logs: list[LogDetail] = self.mlogger.get_logs()
            # 로그 스트리밍
            q.put_nowait({"type": "code", "content": python_code})
            q.put_nowait({"type": "log", "content": entity_logs[-1].model_dump_json()})

        # 2) 검증
        self._validate(entities)

        # 3) URL 생성 & 호출
        url = self._assemble_url(entities)
        logger.info(f"API 호출 URL: {url}")

        try:
            raw = self.fetch_data(url)
        except Exception as e:
            logger.warning(f"API 호출 실패: {e}")
            raise HTTPException(status_code=404, detail=f"Data fetch failed: {e}")

        dataframe = pd.DataFrame(raw["data"])
        q.put_nowait({"type": "data", "content": dataframe.to_dict(orient="records")})

        # 4) DataFrame 반환
        return url, pd.DataFrame(raw["data"]), entity_logs, python_code, entities
