from pydantic import BaseModel, Field
from typing import Optional

class FileAPIDetail(BaseModel):
    factory_name: str = Field(..., description="예: 수원공장")
    system_name: str  = Field(..., description="제조 시스템 이름. 이름만 가져오세요. 예: mes, smmas")
    metric:      str  = Field(..., description="조회할 metric. 예: defects, production, inventory, energy")
    factory_id:  str  = Field(..., description="공장 ID. 예: FCT001, FCT002")
    product_code: Optional[str]  = Field(None, description="제품 코드. 예: PROD001")
    start_date: str  = Field(..., description="조회 시작일. ISO 형식 또는 '지난주', '지난달', '어제' 등 상대 표현. 예: 2025-03-04")