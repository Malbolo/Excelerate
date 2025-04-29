from pydantic import BaseModel, Field, RootModel
from typing import Dict, List

class OldFileAPIDetail(BaseModel):
    location: str = Field(description="파일을 불러올 지사 정보. 지사를 붙이지 말고 이름만 가져오세요. 예: vietnam, china")
    startdate: str = Field(description="파일을 불러올 시작일. 예: 2025-01-01")
    enddate: str = Field(description="파일을 불러올 종료일. 예: 2025-03-31")
    group: str = Field(description="파일을 불러올 그룹 정보. 예: DX, DA")
    product: str = Field(description="파일을 불러올 제품 정보. 예: A, B")
    metric: str = Field(description="파일을 불러올 metric 정보. 예: 불량률, production")

class FileAPIDetail(BaseModel):
    system_name: str  = Field(..., description="제조 시스템 이름. 이름만 가져오세요. 예: mes, smmas")
    metric:      str  = Field(..., description="조회할 metric. 예: defects, production, inventory, energy")
    factory_id:  str  = Field(..., description="공장 ID. 예: FCT001, FCT002")
    start_date:  str  = Field(..., description="조회 시작일. 예: 2025-04-01")


class ProductInfo(BaseModel):
    name: str     = Field(..., description="제품명. 예: 스마트폰A")
    category: str = Field(..., description="카테고리. 예: 전자기기")

class FactoryInfo(BaseModel):
    factory_id:    str                      = Field(..., description="공장 ID. 예: FCT001")
    product:       Dict[str, ProductInfo]   = Field(..., description="제품 코드 → 상세정보 매핑")
    metric_list:   List[str]                = Field(..., description="지원 metric 리스트. 예: ['defects','production']")

class FactoryCatalog(RootModel[Dict[str, FactoryInfo]]):
    """
    root: { 공장명: FactoryInfo, ... }
    """
    pass
    # 최상위 키(공장명)를 arbitrary하게 매핑