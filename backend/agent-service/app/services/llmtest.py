import os
import logging
import time
from app.core.config import settings
# LangChain 관련 라이브러리 임포트
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_milvus import Milvus
from langchain_core.documents import Document
from langchain_experimental.tools.python.tool import PythonREPLTool
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMTest:
    def __init__(self):
        """
        LLM 연결 테스트용 서비스
        """

        self.llm = ChatOpenAI(
            temperature=0.3,
            max_tokens=1024,
            model_name="gpt-4o-mini"
        )

        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small") # 차후 필요 시 더 고급 임베딩 모델 사용

        # Milvus 초기화 시도
        self._initialize_milvus()

    def _initialize_milvus(self):
        """Milvus 연결을 초기화하는 메서드, 실패 시 백업 방법 제공"""

        self.vector_store = None

        host = settings.MILVUS_HOST
        port = settings.MILVUS_PORT
        collection = settings.MILVUS_COLLECTION
        logger.warning(f"Milvus 연결 시도: {host}:{port}")

        try:
            from pymilvus import connections, utility

            max_retries = 5
            retry_interval = 3  # 초

            for attempt in range(max_retries):
                try:
                    logger.warning(f"Milvus 연결 시도 {attempt+1}/{max_retries}: {host}:{port}")

                    # pymilvus 연결 (alias 없이)
                    connections.connect(
                        uri=f"tcp://{host}:{port}"
                    )

                    # 연결 테스트
                    collection_list = utility.list_collections()
                    logger.info(f"사용 가능한 컬렉션 목록: {collection_list}")

                    collection_exists = collection in collection_list
                    logger.info(f"Milvus 컬렉션 '{collection}' 존재 여부: {collection_exists}")

                    # LangChain Milvus 초기화
                    logger.info("LangChain Milvus 래퍼 초기화 중...")
                    self.vector_store = Milvus(
                        embedding_function=self.embeddings,
                        connection_args={
                            "uri": f"tcp://{host}:{port}"
                        },
                        collection_name=collection,
                        vector_field="vector"
                    )

                    logger.info("Milvus 연결 성공!")

                    if not collection_exists:
                        logger.warning(f"컬렉션 '{collection}'이 없습니다. 먼저 create_collection.py 스크립트를 실행하세요.")

                    return

                except Exception as e:
                    logger.warning(f"Milvus 연결 시도 {attempt+1} 실패: {e}")
                    if attempt < max_retries - 1:
                        logger.info(f"{retry_interval}초 후 재시도...")
                        time.sleep(retry_interval)
                    else:
                        logger.error(f"Milvus 연결 모두 실패 ({max_retries}회 시도)")
                        self.vector_store = None

        except Exception as e:
            logger.error(f"Milvus 연결 모듈 로드 또는 초기화 실패: {e}")
            self.vector_store = None

        logger.warning("Milvus 없이 LLM만 사용하는 모드로 전환합니다.")
