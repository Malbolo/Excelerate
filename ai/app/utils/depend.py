from fastapi import Request
from app.services.llmtest import LLMTest
from app.services.code_gen.graph import CodeGenerator

# 의존성 주입 함수: 요청마다 app.state에 등록된 서비스를 가져오기 위해 사용
def get_llm_service(request: Request) -> LLMTest:
    return request.app.state.llm_service

def get_code_gen(request: Request) -> CodeGenerator:
    return request.app.state.code_gen