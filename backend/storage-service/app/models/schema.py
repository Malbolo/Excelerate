from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class BaseResponse(BaseModel):
    success: bool = Field(True, description="요청 성공 여부")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="응답 데이터")
