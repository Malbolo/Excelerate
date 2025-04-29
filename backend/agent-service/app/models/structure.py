from pydantic import BaseModel, Field

class FileAPIDetail(BaseModel):
    location: str = Field(description="파일을 불러올 지사 정보. 지사를 붙이지 말고 이름만 가져오세요. 예: vietnam, china")
    startdate: str = Field(description="파일을 불러올 시작일. 예: 2025-01-01")
    enddate: str = Field(description="파일을 불러올 종료일. 예: 2025-03-31")
    group: str = Field(description="파일을 불러올 그룹 정보. 예: DX, DA")
    product: str = Field(description="파일을 불러올 제품 정보. 예: A, B")
    metric: str = Field(description="파일을 불러올 metric 정보. 예: 불량률, production")