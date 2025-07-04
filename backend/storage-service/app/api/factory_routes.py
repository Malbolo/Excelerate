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

                # 중첩된 defect_types 구조를 평면화
                flat_data = {
                    "product_id": pid,
                    "factory_id": factory_id,
                    "date": date,
                    "product_category": PRODUCTS[pid]["category"],
                    "product_name": pdata.get("product_name", ""),
                    "defect_rate": pdata.get("defect_rate", 0),
                    "total_inspected": pdata.get("total_inspected", 0),
                    "defect_count": pdata.get("defect_count", 0)
                }

                # defect_types 객체의 각 항목을 평면화된 구조에 추가
                for defect_name, defect_count in pdata.get("defect_types", {}).items():
                    flat_data[defect_name] = defect_count

                result.append(flat_data)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")

    result = filter_common(result, product_id, product_category)

    # defect_type 필터 로직 수정 - 이제 평면화된 구조이므로 직접 접근
    if defect_type:
        result = [r for r in result if r.get(defect_type, 0) > 0]
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
                    # 기본 레코드 정보
                    flattened_record = {
                        "factory_id": factory_id,
                        "product_id": pid,
                        "product_category": PRODUCTS[pid]["category"],
                        "date": record.get("date", ""),
                        "time": record.get("time", ""),
                        "product_name": record.get("product_name", ""),
                        "inspection_type": record.get("inspection_type", ""),
                        "inspector": record.get("inspector", ""),
                        "total_samples": record.get("total_samples", 0),
                        "total_pass": record.get("total_pass", 0),
                        "total_fail": record.get("total_fail", 0),
                        "pass_rate": record.get("pass_rate", 0)
                    }

                    # detailed_results 평면화
                    if "detailed_results" in record:
                        for category, items in record["detailed_results"].items():
                            for item_name, item_data in items.items():
                                # 키 이름 형식: '카테고리_항목명_속성'
                                prefix = f"{category}_{item_name}"
                                for metric, value in item_data.items():
                                    flattened_record[f"{prefix}_{metric}"] = value

                    result.append(flattened_record)
            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
                continue

    result = filter_common(result, product_id, product_category)
    if inspection_type:
        result = [r for r in result if r["inspection_type"] == inspection_type]

    return BaseResponse(success=True, data=result)