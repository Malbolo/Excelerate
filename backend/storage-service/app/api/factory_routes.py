from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta
from app.core.minio_client import minio_client
from app.models.schema import BaseResponse
import logging

logger = logging.getLogger("factory-routes")

# 제품 정보 (카테고리 조회용)
PRODUCTS = {
    "PROD001": {"name": "스마트폰A", "category": "전자기기"},
    "PROD002": {"name": "스마트폰B", "category": "전자기기"},
    "PROD003": {"name": "태블릿C", "category": "전자기기"},
    "PROD004": {"name": "노트북D", "category": "컴퓨터"},
    "PROD005": {"name": "데스크탑E", "category": "컴퓨터"},
}

router = APIRouter()


def get_date_range(start_date: str, end_date: Optional[str] = None):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date is None:
        end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # 오늘 날짜의 00:00:00
    else:
        end = datetime.strptime(end_date, "%Y-%m-%d")

    if start > end:
        return [start_date]
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]


def filter_common(data, product_id, product_category):
    if product_id:
        data = [r for r in data if r["product_id"] == product_id]
    if product_category:
        data = [r for r in data if r.get("product_category") == product_category]
    return data



@router.get("/factory-data/defects", response_model=BaseResponse, summary="제품별 불량률 데이터 조회")
def get_defect_data(
    factory_id: str = Query(..., description="공장 ID(예: FCT001)"),
    start_date: str = Query(..., description="조회 시작일 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="조회 종료일 (YYYY-MM-DD)"),
    product_id: Optional[str] = Query(None, description="제품 ID (예: PROD001)"),
    product_category: Optional[str] = Query(None, description="제품 카테고리 (예: 전자기기, 컴퓨터)"),
    defect_type: Optional[str] = Query(None, description="불량 유형 필터 (예: 외관불량)"),
    defect_rate_min: Optional[float] = Query(None, description="최소 불량률 (%)"),
    defect_rate_max: Optional[float] = Query(None, description="최대 불량률 (%)"),
):
    result = []
    for date in get_date_range(start_date, end_date):
        path = f"quality/defect_rates/{factory_id}/{date}.json"
        logger.debug(f"Loading from: {path}")
        try:
            raw = minio_client.get_data(path)
            logger.debug(f"Successfully loaded: {path}")
            for pid, pdata in raw["data"].items():
                if pid not in PRODUCTS:
                    logger.debug(f"Unknown product_id: {pid}")
                    continue
                pdata.update({
                    "product_id": pid,
                    "factory_id": factory_id,
                    "date": date,
                    "product_category": PRODUCTS[pid]["category"]
                })
                result.append(pdata)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")

    result = filter_common(result, product_id, product_category)

    if defect_type:
        result = [r for r in result if r["defect_types"].get(defect_type, 0) > 0]
    if defect_rate_min is not None:
        result = [r for r in result if r["defect_rate"] >= defect_rate_min]
    if defect_rate_max is not None:
        result = [r for r in result if r["defect_rate"] <= defect_rate_max]

    return BaseResponse(success=True, data=result)


@router.get("/factory-data/production", response_model=BaseResponse, summary="공장별 생산량 데이터 조회")
def get_production_data(
        factory_id: str = Query(..., description="공장 ID(예: FCT001)"),
        start_date: str = Query(..., description="조회 시작일 (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="조회 종료일 (YYYY-MM-DD)"),
        product_id: Optional[str] = Query(None, description="제품 ID (예: PROD001)"),
        product_category: Optional[str] = Query(None, description="제품 카테고리 (예: 전자기기, 컴퓨터)"),
):
    result = []
    for date in get_date_range(start_date, end_date):
        path = f"production/daily/{factory_id}/{date}.json"
        try:
            raw = minio_client.get_data(path)
            for pid, pdata in raw["data"].items():
                pdata.update({
                    "product_id": pid,
                    "factory_id": factory_id,
                    "date": date,
                    "product_category": PRODUCTS[pid]["category"]
                })
                result.append(pdata)
        except Exception:
            continue

    result = filter_common(result, product_id, product_category)
    return BaseResponse(success=True, data=result)


@router.get("/factory-data/inventory", response_model=BaseResponse, summary="공장별 재고 현황 조회")
def get_inventory_data(
        factory_id: str = Query(..., description="공장 ID(예: FCT001)"),
        start_date: str = Query(..., description="조회 시작일 (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="조회 종료일 (YYYY-MM-DD)"),
        product_id: Optional[str] = Query(None, description="제품 ID (예: PROD001)"),
        product_category: Optional[str] = Query(None, description="제품 카테고리 (예: 전자기기, 컴퓨터)"),
):
    result = []
    for date in get_date_range(start_date, end_date):
        path = f"inventory/status/{factory_id}/{date}.json"
        try:
            raw = minio_client.get_data(path)
            product_data = raw["data"].get("products", {})
            for pid, pdata in product_data.items():
                pdata.update({
                    "product_id": pid,
                    "factory_id": factory_id,
                    "date": date,
                    "product_category": PRODUCTS[pid]["category"]
                })
                result.append(pdata)
        except Exception:
            continue

    result = filter_common(result, product_id, product_category)
    return BaseResponse(success=True, data=result)


@router.get("/factory-data/energy", response_model=BaseResponse, summary="공장별 에너지 사용량 조회")
def get_energy_data(
        factory_id: str = Query(..., description="공장 ID(예: FCT001)"),
        week: str = Query(..., description="조회 주차 (예: 2025_W17)"),
):
    path = f"energy/consumption/{factory_id}/{week}.json"
    try:
        raw = minio_client.get_data(path)
        result = []
        for energy_type, info in raw["data"].items():
            result.append({
                "factory_id": factory_id,
                "week": week,
                "energy_type": energy_type,
                **info
            })
        return BaseResponse(success=True, data=result)
    except Exception as e:
        return {"error": f"데이터 조회 실패: {e}"}


@router.get("/factory-data/equipment", response_model=BaseResponse, summary="설비 가동률 및 상태 조회")
def get_equipment_data(
        factory_id: str = Query(..., description="공장 ID(예: FCT001)"),
        start_date: str = Query(..., description="조회 시작일 (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="조회 종료일 (YYYY-MM-DD)"),
        line_id: Optional[str] = Query(None, description="라인 ID 필터 (예: LINE01)"),
        eq_type: Optional[str] = Query(None, description="설비 타입 필터 (예: ASSY, TEST 등)"),
):
    result = []
    for date in get_date_range(start_date, end_date):
        path = f"equipment/utilization/{factory_id}/{date}.json"
        try:
            raw = minio_client.get_data(path)
            for lid, equipments in raw["data"].items():
                if line_id and lid != line_id:
                    continue
                for eq_id, edata in equipments.items():
                    equipment_entry = {
                        "factory_id": factory_id,
                        "line_id": lid,
                        "equipment_id": eq_id,
                        "date": date,
                        **edata
                    }
                    if eq_type and not eq_id.startswith(f"{lid}_{eq_type}_"):
                        continue
                    result.append(equipment_entry)
        except Exception:
            continue

    return BaseResponse(success=True, data=result)


@router.get("/factory-data/quality-inspection", response_model=BaseResponse, summary="품질 검사 결과 조회")
def get_quality_inspection_data(
        factory_id: str = Query(..., description="공장 ID(예: FCT001)"),
        start_date: str = Query(..., description="조회 시작일 (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="조회 종료일 (YYYY-MM-DD)"),
        product_id: Optional[str] = Query(None, description="제품 ID (예: PROD001)"),
        product_category: Optional[str] = Query(None, description="제품 카테고리 (예: 전자기기, 컴퓨터)"),
        inspection_type: Optional[str] = Query(None, description="검사 유형 필터 (예: 최종검사)"),
):
    result = []
    for date in get_date_range(start_date, end_date):
        for pid in PRODUCTS:
            path = f"quality/inspections/{factory_id}/{pid}/{date}.json"
            try:
                raw = minio_client.get_data(path)
                for record in raw["records"]:
                    record.update({
                        "factory_id": factory_id,
                        "product_id": pid,
                        "product_category": PRODUCTS[pid]["category"]
                    })
                    result.append(record)
            except Exception:
                continue

    result = filter_common(result, product_id, product_category)
    if inspection_type:
        result = [r for r in result if r["inspection_type"] == inspection_type]

    return BaseResponse(success=True, data=result)