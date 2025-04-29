import os
import logging
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

        # Milvus 벡터 스토어 설정
        URI = f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}"

        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            connection_args={"uri": URI},
        )

    async def run(self, query: str):
        """
        주어진 query를 기반으로 RAG 체인을 실행하여 응답을 생성합니다.
        """
        try:
            # # 검색기 구성: Milvus에서 k개 문서를 검색 (예제에서는 k=3)
            # retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

            # # LangChain의 RAG 체인 구성: 검색된 문서들을 이용해 답변 생성
            # qa_chain = RetrievalQA.from_chain_type(
            #     llm=self.llm, 
            #     chain_type="stuff",
            #     retriever=retriever
            # )

            # # 체인 실행: 동기 방식으로 실행 (비동기 지원 시 await qa_chain.arun(query) 사용 고려)
            # answer = qa_chain.run(query)
            answer = self.llm.invoke(query)
            return answer.content # 응답만 반환
        except Exception as e:
            logger.error("RAG 실행 중 에러 발생: %s", e)
            raise e
