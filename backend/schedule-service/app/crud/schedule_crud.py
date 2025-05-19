# app/crud/schedule.py

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.schedule_models import Schedule, ScheduleJob, ScheduleRun, ScheduleRunTask
from app.schemas.schedule_schema import ScheduleCreateRequest, ScheduleUpdateRequest

def create_schedule(db: Session, id:str, data: Dict[str, Any], user_id: int) -> Schedule:
    """스케줄 DB 레코드 생성"""
    db_schedule = Schedule(
        id=id,
        title=data["title"],
        description=data.get("description", ""),
        frequency=data["frequency"],
        cron_expression=data["cron_expression"],
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

def get_schedule_by_id(db: Session, id: str) -> Optional[Schedule]:
    """DAG ID로 스케줄 조회"""
    return db.query(Schedule).filter(Schedule.id == id).first()

def delete_schedule(db: Session, id: str) -> bool:
    """스케줄 삭제"""
    db_schedule = get_schedule_by_id(db, id)
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
    db_schedule = get_schedule_by_id(db, dag_id)
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

def update_schedule(db: Session, id: str, data: Dict[str, Any]) -> bool:
    """스케줄 메타데이터 업데이트"""
    db_schedule = get_schedule_by_id(db, id)
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


def get_schedules_by_ids(db: Session, schedule_ids: List[str]) -> List[Schedule]:
    """특정 ID 목록에 해당하는 스케줄 조회"""
    if not schedule_ids:
        return []

    return db.query(Schedule).filter(
        Schedule.id.in_(schedule_ids)
    ).all()


def get_schedule_ids_by_filters(db: Session, title: str = "", owner: str = "", frequency: str = "") -> List[str]:
    """제목, 소유자, 주기 필터 조건에 맞는 스케줄 ID 목록 조회"""
    query = db.query(Schedule.id).order_by(desc(Schedule.id))

    if title:
        query = query.filter(Schedule.title.ilike(f"%{title}%"))
    if owner:
        query = query.filter(Schedule.owner.ilike(f"%{owner}%"))
    if frequency:
        query = query.filter(Schedule.frequency == frequency)

    schedules = query.all()
    return [schedule.id for schedule in schedules]