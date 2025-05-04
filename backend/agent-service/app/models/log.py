from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class LogDetail(BaseModel):
    name:       str      = Field(..., description="로그 이름")
    input:      str      = Field(..., description="입력")
    output:     str      = Field(..., description="출력")
    timestamp:  datetime = Field(..., description="생성 시간")
    metadata:   dict     = Field(default_factory=dict, description="메타데이터")
    sub_events:  List["LogDetail"] = Field(default_factory=list, description="하위 로그")

    # 자기참조 필드 순환 처리
    model_config = {"arbitrary_types_allowed": True}

LogDetail.model_rebuild()
