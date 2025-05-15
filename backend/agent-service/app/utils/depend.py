from fastapi import Request
from app.services.llmtest import LLMTest
from app.services.code_gen.graph import CodeGenerator
from app.services.data_load.datachain import FileAPIClient
from app.utils.minio_client import minio_client, MinioClient

# 의존성 주입 함수: 요청마다 app.state에 등록된 서비스를 가져오기 위해 사용
def get_llm_service(request: Request) -> LLMTest:
    return request.app.state.llm_service

def get_data_load(request: Request) -> FileAPIClient:
    return request.app.state.data_load

def get_code_gen(request: Request) -> CodeGenerator:
    return request.app.state.code_gen

def get_minio_client() -> MinioClient:
    """
    DI를 통해 전역 minio_client 인스턴스를 주입합니다.
    """
    return minio_client