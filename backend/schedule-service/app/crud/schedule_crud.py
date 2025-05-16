# app/crud/schedule.py

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.schedule_models import Schedule, ScheduleJob, ScheduleRun, ScheduleRunTask
from app.schemas.schedule_schema import ScheduleCreateRequest, ScheduleUpdateRequest


def create_schedule(db: Session, dag_id: str, data: Dict[str, Any], user_id: int) -> Schedule:
    """스케줄 DB 레코드 생성"""
    db_schedule = Schedule(
        dag_id=dag_id,
        title=data["title"],
        description=data.get("description", ""),
        frequency=data["frequency"],
        frequency_cron=data["cron_expression"],
        execution_time=data.get("execution_time"),
        start_date=data["start_date"],
        end_date=data.get("end_date"),
        success_emails=data.get("success_emails", []),
        failure_emails=data.get("failure_emails", []),
        owner=data["owner"],
        created_by=user_id
    )

    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    # Job 연결 정보 저장
    for idx, job_id in enumerate(data["job_ids"]):
        db_job = ScheduleJob(
            schedule_id=db_schedule.id,
            job_id=job_id,
            order=idx
        )
        db.add(db_job)

    db.commit()
    return db_schedule


def get_schedule_by_dag_id(db: Session, dag_id: str) -> Optional[Schedule]:
    """DAG ID로 스케줄 조회"""
    return db.query(Schedule).filter(Schedule.dag_id == dag_id).first()


def update_schedule(db: Session, dag_id: str, data: Dict[str, Any]) -> Optional[Schedule]:
    """스케줄 업데이트"""
    db_schedule = get_schedule_by_dag_id(db, dag_id)
    if not db_schedule:
        return None

    # 업데이트할 필드 지정
    update_data = {}
    if "title" in data:
        update_data["title"] = data["title"]
    if "description" in data:
        update_data["description"] = data["description"]
    if "frequency" in data:
        update_data["frequency"] = data["frequency"]
    if "cron_expression" in data:
        update_data["frequency_cron"] = data["cron_expression"]
    if "execution_time" in data:
        update_data["execution_time"] = data["execution_time"]
    if "start_date" in data:
        update_data["start_date"] = data["start_date"]
    if "end_date" in data:
        update_data["end_date"] = data["end_date"]
    if "success_emails" in data:
        update_data["success_emails"] = data["success_emails"]
    if "failure_emails" in data:
        update_data["failure_emails"] = data["failure_emails"]
    if "is_paused" in data:
        update_data["is_paused"] = data["is_paused"]

    # 업데이트 실행
    for key, value in update_data.items():
        setattr(db_schedule, key, value)

    # Job 연결 정보 업데이트
    if "job_ids" in data:
        # 기존 연결 삭제
        db.query(ScheduleJob).filter(ScheduleJob.schedule_id == db_schedule.id).delete()

        # 새 연결 생성
        for idx, job_id in enumerate(data["job_ids"]):
            db_job = ScheduleJob(
                schedule_id=db_schedule.id,
                job_id=job_id,
                order=idx
            )
            db.add(db_job)

    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def delete_schedule(db: Session, dag_id: str) -> bool:
    """스케줄 삭제"""
    db_schedule = get_schedule_by_dag_id(db, dag_id)
    if not db_schedule:
        return False

    db.delete(db_schedule)
    db.commit()
    return True


def get_all_schedules(db: Session, skip: int = 0, limit: int = 100) -> List[Schedule]:
    """모든 스케줄 조회"""
    return db.query(Schedule).order_by(desc(Schedule.created_at)).offset(skip).limit(limit).all()


# 실행 이력 관련 함수들
def create_schedule_run(db: Session, dag_id: str, run_id: str, status: str) -> ScheduleRun:
    """스케줄 실행 이력 추가"""
    db_schedule = get_schedule_by_dag_id(db, dag_id)
    if not db_schedule:
        return None

    db_run = ScheduleRun(
        schedule_id=db_schedule.id,
        run_id=run_id,
        status=status,
        start_time=datetime.utcnow()
    )

    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run


def update_schedule_run(db: Session, run_id: str, data: Dict[str, Any]) -> Optional[ScheduleRun]:
    """스케줄 실행 이력 업데이트"""
    db_run = db.query(ScheduleRun).filter(ScheduleRun.run_id == run_id).first()
    if not db_run:
        return None

    for key, value in data.items():
        setattr(db_run, key, value)

    db.commit()
    db.refresh(db_run)
    return db_run


def get_schedule_metadata(db: Session, dag_id: str) -> Dict[str, Any]:
    """DAG ID로 스케줄 메타데이터 조회"""
    schedule = get_schedule_by_dag_id(db, dag_id)
    if not schedule:
        # 기본 빈 메타데이터 반환 (기존 get_dag_metadata와 같은 형식)
        return {
            "job_ids": [],
            "start_date": None,
            "end_date": None,
            "success_emails": [],
            "failure_emails": [],
            "execution_time": None,
            "title": None,
            "description": None
        }

    # 스케줄 모델에서 관련 데이터 추출
    schedule_jobs = db.query(ScheduleJob).filter(ScheduleJob.schedule_id == schedule.id).order_by(
        ScheduleJob.order).all()
    job_ids = [job.job_id for job in schedule_jobs]

    return {
        "job_ids": job_ids,
        "start_date": schedule.start_date.isoformat() if schedule.start_date else None,
        "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
        "success_emails": schedule.success_emails or [],
        "failure_emails": schedule.failure_emails or [],
        "execution_time": schedule.execution_time,
        "title": schedule.title,
        "description": schedule.description
    }


def update_schedule_metadata(db: Session, dag_id: str, data: Dict[str, Any]) -> bool:
    """스케줄 메타데이터 업데이트"""
    db_schedule = get_schedule_by_dag_id(db, dag_id)
    if not db_schedule:
        return False

    # 업데이트할 필드들
    for key, value in data.items():
        if key == "job_ids":
            # 기존 job 연결 삭제
            db.query(ScheduleJob).filter(ScheduleJob.schedule_id == db_schedule.id).delete()

            # 새 job 연결 추가
            for idx, job_id in enumerate(value):
                db_job = ScheduleJob(
                    schedule_id=db_schedule.id,
                    job_id=job_id,
                    order=idx
                )
                db.add(db_job)
        elif hasattr(db_schedule, key):
            setattr(db_schedule, key, value)

    db.commit()
    return True

def get_schedules_in_range(db: Session, min_id: str, max_id: str) -> List[Schedule]:
    """특정 ID 범위에 속하는 스케줄 조회 (id는 ULID 형식)"""
    return db.query(Schedule).filter(
        Schedule.id >= min_id,
        Schedule.id <= max_id
    ).order_by(desc(Schedule.id)).all()

def get_schedule_jobs_by_schedule_ids(db: Session, schedule_ids: List[str]) -> List[ScheduleJob]:
    """특정 스케줄 ID 목록에 해당하는 job 정보 조회"""
    if not schedule_ids:
        return []

    return db.query(ScheduleJob).filter(
        ScheduleJob.schedule_id.in_(schedule_ids)
    ).order_by(ScheduleJob.schedule_id, ScheduleJob.order).all()