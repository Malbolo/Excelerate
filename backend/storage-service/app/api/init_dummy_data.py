import random
from datetime import datetime, timedelta
from app.core.minio_client import minio_client


def create_comprehensive_factory_data():
    """공장 시스템에 필요한 다양한 더미 데이터 생성"""
    # 기본 정보 정의
    factories = ["FCT001", "FCT002", "FCT003"]  # 공장 코드
    factory_names = {"FCT001": "수원공장", "FCT002": "평택공장", "FCT003": "구미공장"}

    production_lines = ["LINE01", "LINE02", "LINE03", "LINE04"]

    products = {
        "PROD001": {"name": "스마트폰A", "category": "전자기기"},
        "PROD002": {"name": "스마트폰B", "category": "전자기기"},
        "PROD003": {"name": "태블릿C", "category": "전자기기"},
        "PROD004": {"name": "노트북D", "category": "컴퓨터"},
        "PROD005": {"name": "데스크탑E", "category": "컴퓨터"}
    }

    # 오늘 날짜
    today = datetime.now()

    # 1. 제품별 불량률 데이터 생성 (이미 DB에 있다고 가정하는 데이터)
    create_defect_rate_data(factories, products, today)

    # 2. 생산량 데이터 생성
    create_production_data(factories, products, production_lines, today)

    # 3. 설비 가동률 데이터 생성
    create_equipment_utilization_data(factories, production_lines, today)

    # 4. 재고 현황 데이터 생성
    create_inventory_data(factories, products, today)

    # 5. 에너지 사용량 데이터 생성
    create_energy_consumption_data(factories, today)

    # 6. 공장별 기본 정보 생성
    create_factory_basic_info(factories, factory_names)

    # 7. 제품별 기본 정보 생성
    create_product_basic_info(products)

    # 8. 품질 상세 지표 데이터 생성
    create_quality_detail_data(factories, products, today)

def create_defect_rate_data(factories, products, today):
    """제품별 불량률 데이터 생성"""
    # 최근 90일간의 데이터 생성
    for i in range(90):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        for factory_id in factories:
            defect_data = {}

            for product_id, product_info in products.items():
                # 각 제품별 일일 불량률 데이터
                # 불량률은 0.5%에서 3% 사이로 설정
                defect_rate = round(random.uniform(0.5, 3.0), 2)

                # 날짜가 최근일수록 개선되는 경향 추가 (현실감)
                if i < 30:  # 최근 30일
                    defect_rate = max(0.3, defect_rate - 0.5)

                total_inspected = random.randint(800, 1500)
                defect_count = int(total_inspected * defect_rate / 100)

                # 불량 유형별 분포
                defect_types = {
                    "외관불량": random.randint(0, defect_count),
                    "기능불량": random.randint(0, defect_count),
                    "치수이상": random.randint(0, defect_count),
                    "기타": random.randint(0, defect_count)
                }

                # 합계가 defect_count가 되도록 조정
                total_by_type = sum(defect_types.values())
                if total_by_type > 0:
                    factor = defect_count / total_by_type
                    for key in defect_types:
                        defect_types[key] = int(defect_types[key] * factor)

                # 데이터 추가
                defect_data[product_id] = {
                    "product_name": product_info["name"],
                    "date": date_str,
                    "defect_rate": defect_rate,
                    "total_inspected": total_inspected,
                    "defect_count": defect_count,
                    "defect_types": defect_types
                }

            # MinIO에 저장
            object_name = f"quality/defect_rates/{factory_id}/{date_str}.json"
            minio_client.save_data(object_name, {"data": defect_data})


def create_production_data(factories, products, production_lines, today):
    """생산량 데이터 생성"""
    # 최근 90일간의 데이터 생성
    for i in range(90):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        for factory_id in factories:
            production_data = {}

            for product_id, product_info in products.items():
                # 공장별로 특정 제품만 생산한다고 가정
                if (factory_id == "FCT001" and product_id in ["PROD001", "PROD002", "PROD003"]) or \
                        (factory_id == "FCT002" and product_id in ["PROD002", "PROD004"]) or \
                        (factory_id == "FCT003" and product_id in ["PROD003", "PROD005"]):

                    daily_production = {}
                    total_daily = 0

                    # 라인별 생산량
                    assigned_lines = random.sample(production_lines, random.randint(1, 3))
                    for line in assigned_lines:
                        # 기본 생산량
                        line_production = random.randint(200, 500)

                        # 주말은 생산량 감소
                        if date.weekday() >= 5:  # 5=토요일, 6=일요일
                            line_production = int(line_production * 0.6)

                        daily_production[line] = line_production
                        total_daily += line_production

                    production_data[product_id] = {
                        "product_name": product_info["name"],
                        "date": date_str,
                        "total_production": total_daily,
                        "line_production": daily_production,
                        "target_production": random.randint(total_daily - 100, total_daily + 300),
                    }

            # MinIO에 저장
            object_name = f"production/daily/{factory_id}/{date_str}.json"
            minio_client.save_data(object_name, {"data": production_data})


def create_equipment_utilization_data(factories, production_lines, today):
    """설비 가동률 데이터 생성"""
    # 설비 정의
    equipment_types = {
        "ASSY": ["ASSY01", "ASSY02", "ASSY03"],
        "TEST": ["TEST01", "TEST02"],
        "PACK": ["PACK01", "PACK02"]
    }

    # 최근 90일간의 데이터 생성
    for i in range(90):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        for factory_id in factories:
            equipment_data = {}

            for line_id in production_lines:
                line_equipment = {}

                for eq_type, equipments in equipment_types.items():
                    for eq_id in equipments:
                        # 가동률 (70%~95%)
                        utilization = round(random.uniform(70, 95), 1)

                        # 주말이나 특정 날짜에는 가동률 감소
                        if date.weekday() >= 5:  # 주말
                            utilization = round(utilization * 0.7, 1)

                        # 다운타임 (분 단위)
                        downtime = random.randint(0, int((100 - utilization) * 0.6 * 24))

                        # 고장 횟수
                        failures = random.randint(0, 3)

                        equipment_id = f"{line_id}_{eq_type}_{eq_id}"
                        line_equipment[equipment_id] = {
                            "utilization_rate": utilization,
                            "downtime_minutes": downtime,
                            "failure_count": failures,
                            "maintenance_due": random.choice([True, False]),
                            "status": random.choice(["정상", "점검필요", "경고"]) if utilization > 85 else "점검필요"
                        }

                equipment_data[line_id] = line_equipment

            # MinIO에 저장
            object_name = f"equipment/utilization/{factory_id}/{date_str}.json"
            minio_client.save_data(object_name, {"data": equipment_data})

def create_inventory_data(factories, products, today):
    """재고 현황 데이터 생성"""
    # 자재 정의
    materials = {
        "MAT001": "PCB기판",
        "MAT002": "디스플레이",
        "MAT003": "배터리",
        "MAT004": "케이스",
        "MAT005": "카메라모듈",
        "MAT006": "메모리칩",
        "MAT007": "프로세서"
    }

    # 최근 30일간의 데이터 생성
    for i in range(30):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        for factory_id in factories:
            # 원자재 재고
            material_inventory = {}
            for mat_id, mat_name in materials.items():
                # 재고량
                quantity = random.randint(1000, 5000)

                # 안전 재고
                safety_stock = 1000

                # 재고 상태
                if quantity < safety_stock:
                    status = "부족"
                elif quantity < safety_stock * 1.2:
                    status = "경고"
                else:
                    status = "정상"

                material_inventory[mat_id] = {
                    "name": mat_name,
                    "quantity": quantity,
                    "safety_stock": safety_stock,
                    "status": status,
                    "last_restock_date": (date - timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d"),
                    "unit_price": round(random.uniform(10, 500), 2)
                }

            # 제품 재고
            product_inventory = {}
            for product_id, product_info in products.items():
                # 공장별로 특정 제품만 생산한다고 가정
                if (factory_id == "FCT001" and product_id in ["PROD001", "PROD002", "PROD003"]) or \
                        (factory_id == "FCT002" and product_id in ["PROD002", "PROD004"]) or \
                        (factory_id == "FCT003" and product_id in ["PROD003", "PROD005"]):
                    # 완제품 재고
                    finished_qty = random.randint(200, 2000)

                    # WIP (진행 중인 작업) 재고
                    wip_qty = random.randint(50, 500)

                    product_inventory[product_id] = {
                        "name": product_info["name"],
                        "finished_quantity": finished_qty,
                        "wip_quantity": wip_qty,
                        "reorder_point": 300,
                        "status": "정상" if finished_qty > 300 else "재생산필요",
                        "last_production_date": date_str
                    }

            # MinIO에 저장
            inventory_data = {
                "date": date_str,
                "materials": material_inventory,
                "products": product_inventory
            }
            object_name = f"inventory/status/{factory_id}/{date_str}.json"
            minio_client.save_data(object_name, {"data": inventory_data})


def create_energy_consumption_data(factories, today):
    """에너지 사용량 데이터 생성"""
    # 에너지 유형
    energy_types = ["전기", "가스", "수도", "증기"]

    # 최근 90일간의 데이터 생성
    for i in range(90):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        # 주단위로 저장
        if date.weekday() == 0 or i == 0:  # 월요일이거나 오늘
            for factory_id in factories:
                weekly_data = {}

                for energy_type in energy_types:
                    # 기본 사용량
                    if energy_type == "전기":
                        base_usage = random.randint(5000, 8000)  # kWh
                        unit = "kWh"
                    elif energy_type == "가스":
                        base_usage = random.randint(800, 1500)  # m³
                        unit = "m³"
                    elif energy_type == "수도":
                        base_usage = random.randint(300, 700)  # m³
                        unit = "m³"
                    else:  # 증기
                        base_usage = random.randint(1000, 2500)  # kg
                        unit = "kg"

                    # 계절에 따른 변동 (간단한 시뮬레이션)
                    month = date.month
                    if energy_type == "전기" and month in [6, 7, 8]:  # 여름
                        base_usage = int(base_usage * 1.2)  # 냉방으로 인한 증가
                    elif energy_type == "가스" and month in [12, 1, 2]:  # 겨울
                        base_usage = int(base_usage * 1.3)  # 난방으로 인한 증가

                    # 주말은 사용량 감소
                    weekend_usage = int(base_usage * 0.6)

                    # 일별 사용량 (7일)
                    daily_usage = {}
                    for j in range(7):
                        day_date = date + timedelta(days=j)
                        if day_date > today:
                            continue

                        day_str = day_date.strftime("%Y-%m-%d")
                        if day_date.weekday() >= 5:  # 주말
                            usage = int(weekend_usage * random.uniform(0.9, 1.1))
                        else:
                            usage = int(base_usage * random.uniform(0.9, 1.1))

                        daily_usage[day_str] = usage

                    weekly_data[energy_type] = {
                        "unit": unit,
                        "total_usage": sum(daily_usage.values()),
                        "daily_usage": daily_usage,
                        "average_daily": round(sum(daily_usage.values()) / len(daily_usage), 2),
                        "peak_day": max(daily_usage.items(), key=lambda x: x[1])[0],
                        "peak_usage": max(daily_usage.values())
                    }

                # 주차 계산
                week_num = date.isocalendar()[1]

                # MinIO에 저장
                object_name = f"energy/consumption/{factory_id}/{date.year}_W{week_num}.json"
                minio_client.save_data(object_name, {"data": weekly_data})


def create_factory_basic_info(factories, factory_names):
    """공장 기본 정보 생성"""
    factory_info = {}

    for factory_id in factories:
        info = {
            "name": factory_names[factory_id],
            "location": random.choice(["경기도 수원시", "경기도 평택시", "경상북도 구미시"]),
            "size": f"{random.randint(5000, 20000)}m²",
            "established_year": random.randint(1990, 2010),
            "employee_count": random.randint(500, 2000),
            "production_lines": random.randint(3, 8),
            "main_products": random.sample(["스마트폰", "태블릿", "노트북", "데스크탑", "가전제품"], k=random.randint(2, 4))
        }
        factory_info[factory_id] = info

    # MinIO에 저장
    minio_client.save_data("factory/basic_info.json", {"data": factory_info})


def create_product_basic_info(products):
    """제품 기본 정보 생성"""
    product_info = {}

    for product_id, basic_info in products.items():
        # 기본 정보 확장
        info = {
            "name": basic_info["name"],
            "category": basic_info["category"],
            "launch_date": f"20{random.randint(18, 23)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "price": round(random.uniform(500, 2000) * 1000),  # 가격 (원)
            "weight": round(random.uniform(0.2, 3.0), 2),  # 무게 (kg)
            "dimensions": f"{random.randint(10, 40)}x{random.randint(10, 30)}x{random.randint(1, 5)}cm",
            "production_cost": round(random.uniform(200, 1000) * 1000),  # 생산 원가 (원)
            "lead_time": random.randint(2, 10),  # 생산 소요일
            "materials": random.sample(["PCB기판", "디스플레이", "배터리", "케이스", "카메라모듈", "메모리칩", "프로세서"],
                                       k=random.randint(4, 7))
        }
        product_info[product_id] = info

    # MinIO에 저장
    minio_client.save_data("product/basic_info.json", {"data": product_info})


def create_quality_detail_data(factories, products, today):
    """품질 상세 지표 데이터 생성"""
    # 품질 검사 유형
    inspection_types = ["최종검사", "공정검사", "수입검사"]

    # 검사 항목
    inspection_items = {
        "외관": ["스크래치", "변색", "이물질", "조립불량"],
        "치수": ["길이", "두께", "폭", "무게"],
        "기능": ["전원", "신호", "속도", "반응성"],
        "내구성": ["충격", "진동", "온도", "습도"]
    }

    # 최근 90일간의 데이터 생성
    for i in range(90):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        for factory_id in factories:
            for product_id, product_info in products.items():
                # 공장별로 특정 제품만 생산한다고 가정
                if not ((factory_id == "FCT001" and product_id in ["PROD001", "PROD002", "PROD003"]) or
                        (factory_id == "FCT002" and product_id in ["PROD002", "PROD004"]) or
                        (factory_id == "FCT003" and product_id in ["PROD003", "PROD005"])):
                    continue

                daily_inspection_records = []

                # 하루에 여러 번 품질 검사 실시
                for _ in range(random.randint(2, 5)):
                    inspection_type = random.choice(inspection_types)
                    inspection_time = f"{random.randint(8, 18):02d}:{random.randint(0, 59):02d}"

                    # 검사 항목별 결과
                    inspection_results = {}
                    total_pass = 0
                    total_fail = 0

                    for category, items in inspection_items.items():
                        category_results = {}
                        for item in items:
                            # 품질 검사 결과 (합격률 90~99%)
                            sample_size = random.randint(30, 100)
                            pass_rate = random.uniform(0.90, 0.99)
                            pass_count = int(sample_size * pass_rate)
                            fail_count = sample_size - pass_count

                            category_results[item] = {
                                "sample_size": sample_size,
                                "pass": pass_count,
                                "fail": fail_count,
                                "pass_rate": round(pass_count / sample_size * 100, 2)
                            }

                            total_pass += pass_count
                            total_fail += fail_count

                        inspection_results[category] = category_results

                    # 종합 결과
                    total_samples = total_pass + total_fail
                    total_pass_rate = round(total_pass / total_samples * 100, 2) if total_samples > 0 else 0

                    record = {
                        "date": date_str,
                        "time": inspection_time,
                        "product_id": product_id,
                        "product_name": product_info["name"],
                        "inspection_type": inspection_type,
                        "inspector": f"검사원{random.randint(1, 10)}",
                        "total_samples": total_samples,
                        "total_pass": total_pass,
                        "total_fail": total_fail,
                        "pass_rate": total_pass_rate,
                        "detailed_results": inspection_results
                    }

                    daily_inspection_records.append(record)

                # MinIO에 저장
                object_name = f"quality/inspections/{factory_id}/{product_id}/{date_str}.json"
                minio_client.save_data(object_name, {"records": daily_inspection_records})