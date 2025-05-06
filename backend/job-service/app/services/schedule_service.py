from typing import Optional
import uuid
import json
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from starlette.responses import JSONResponse
from sqlalchemy import func, and_, or_

from app.db.database import get_db
from app.models.models import Schedule, ScheduleJob, ScheduleExecution, Job, JobCommand
from app.schemas.schedule_create_schema import ScheduleCreateRequest, ScheduleCreateResponse
from app.services import airflow_integration

async def create_schedule(request: ScheduleCreateRequest, user_id: int) -> JSONResponse:
    """스케줄 생성 서비스"""
    db = next(get_db())
    try:
        # 고유한 스케줄 ID 생성
        schedule_id = f"schedule_{uuid.uuid4().hex[:6]}"
        
        # 이메일 리스트를 JSON 문자열로 변환
        success_emails = json.dumps(request.success_emails) if request.success_emails else None
        failure_emails = json.dumps(request.failure_emails) if request.failure_emails else None
        
        # 스케줄 생성
        db_schedule = Schedule(
            id=schedule_id,
            title=request.title,
            description=request.description,
            user_id=user_id,
            start_date=request.start_date,
            end_date=request.end_date,
            execution_time=request.execution_time,
            frequency=request.frequency,
            success_emails=success_emails,
            failure_emails=failure_emails,
            status="pending"
        )
        db.add(db_schedule)
        
        # 관련 Job 연결 및 정보 수집
        jobs_info = []
        for job_ref in request.jobs:
            # Job이 존재하는지 확인
            job = db.query(Job).filter(Job.id == job_ref.id, Job.user_id == user_id).first()
            if not job:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Job ID {job_ref.id}를 찾을 수 없습니다."
                )
            
            db_schedule_job = ScheduleJob(
                schedule_id=schedule_id,
                job_id=job_ref.id,
                order=job_ref.order
            )
            db.add(db_schedule_job)
            
            # Airflow DAG 생성을 위한 Job 정보 수집
            commands = db.query(JobCommand).filter(JobCommand.job_id == job.id).order_by(JobCommand.order).all()
            job_info = {
                "id": job.id,
                "name": job.name,
                "order": job_ref.order,
                "data_load_command": job.data_load_command,
                "data_load_url": job.data_load_url,
                "code": job.code,
                "commands": [{"content": cmd.content, "order": cmd.order} for cmd in commands]
            }
            jobs_info.append(job_info)
        
        db.commit()
        
        # Airflow DAG 생성
        success_emails_list = request.success_emails or []
        failure_emails_list = request.failure_emails or []
        
        try:
            airflow_integration.create_schedule_dag(
                schedule_id, 
                request.title,
                request.description,
                request.frequency,
                request.start_date,
                request.end_date,
                jobs_info,
                success_emails_list,
                failure_emails_list
            )
        except Exception as e:
            print(f"Airflow DAG 생성 실패: {e}")
            # 오류가 있더라도 스케줄은 생성하고 경고만 로그에 남김
        
        created_at = datetime.now()
        
        return ScheduleCreateResponse(
            result="success",
            data={
                "schedule_id": schedule_id,
                "created_at": created_at.isoformat()
            }
        )
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        print(f"스케줄 생성 중 오류 발생: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"스케줄 생성에 실패했습니다: {str(e)}"
        )

async def get_monthly_statistics(db: Session, user_id: int, year: int, month: int) -> JSONResponse:
    """월별 스케줄 조회 서비스"""
    try:
        # 해당 월의 일수 계산
        if month in [1, 3, 5, 7, 8, 10, 12]:
            days_in_month = 31
        elif month in [4, 6, 9, 11]:
            days_in_month = 30
        elif month == 2:
            # 윤년 계산
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                days_in_month = 29
            else:
                days_in_month = 28
        else:
            return JSONResponse(
                status_code=400, 
                content={"result": "fail", "message": "유효하지 않은 월입니다."}
            )
        
        statistics = []
        for day in range(1, days_in_month + 1):
            # 해당 일자의 스케줄 실행 통계 조회
            day_start = datetime(year, month, day, 0, 0, 0)
            day_end = datetime(year, month, day, 23, 59, 59)
            
            pending_count = db.query(func.count(ScheduleExecution.id)).join(Schedule).\
                filter(Schedule.user_id == user_id,
                      ScheduleExecution.status == "pending",
                      ScheduleExecution.execution_date.between(day_start, day_end)).scalar()
            
            success_count = db.query(func.count(ScheduleExecution.id)).join(Schedule).\
                filter(Schedule.user_id == user_id,
                      ScheduleExecution.status == "success",
                      ScheduleExecution.execution_date.between(day_start, day_end)).scalar()
            
            fail_count = db.query(func.count(ScheduleExecution.id)).join(Schedule).\
                filter(Schedule.user_id == user_id,
                      ScheduleExecution.status == "fail",
                      ScheduleExecution.execution_date.between(day_start, day_end)).scalar()
            
            statistics.append({
                "day": day,
                "pending": pending_count,
                "success": success_count,
                "fail": fail_count
            })
        
        return JSONResponse(content={
            "result": "success",
            "data": {
                "statistics": statistics
            }
        })
    except Exception as e:
        print(f"월별 통계 조회 중 오류 발생: {e}")
        return JSONResponse(
            status_code=500, 
            content={"result": "fail", "message": "월별 통계 조회에 실패했습니다."}
        )

async def get_daily_schedules(db: Session, user_id: int, year: int, month: int, day: int) -> JSONResponse:
    """일별 스케줄 목록 조회 서비스"""
    try:
        # 해당 일자의 스케줄 목록 조회
        day_start = datetime(year, month, day, 0, 0, 0)
        day_end = datetime(year, month, day, 23, 59, 59)
        
        # 해당 날짜에 실행 예정인 스케줄 조회
        # 1. 매일 실행 스케줄
        # 2. 매주 특정 요일 실행 스케줄 (해당 일자가 지정된 요일인 경우)
        # 3. 매월 특정 일자 실행 스케줄 (해당 일자가 지정된 일자인 경우)
        # 4. 매년 특정 월/일 실행 스케줄 (해당 일자가 지정된 월/일인 경우)
        
        # 간단한 구현: 해당 일자에 실행 시간이 있는 스케줄 조회
        schedules = db.query(Schedule).\
            filter(Schedule.user_id == user_id,
                  Schedule.start_date <= day_end,
                  or_(
                      Schedule.end_date.is_(None),
                      Schedule.end_date >= day_start
                  )).all()
        
        # 스케줄 목록 가공
        schedule_list = []
        for schedule in schedules:
            # 주어진 날짜에 이 스케줄이 실행되는지 확인
            # (실제로는 빈도(frequency)에 따라 계산 필요)
            schedule_list.append({
                "id": schedule.id,
                "title": schedule.title,
                "description": schedule.description,
                "status": schedule.status
            })
        
        return JSONResponse(content={
            "result": "success",
            "data": {
                "schedules": schedule_list
            }
        })
    except Exception as e:
        print(f"일별 스케줄 조회 중 오류 발생: {e}")
        return JSONResponse(
            status_code=500, 
            content={"result": "fail", "message": "일별 스케줄 조회에 실패했습니다."}
        )

async def get_schedule_detail(db: Session, schedule_id: str) -> JSONResponse:
    """스케줄 상세 조회 서비스"""
    try:
        # 스케줄 상세 정보 조회
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return JSONResponse(
                status_code=404, 
                content={"result": "fail", "message": "스케줄을 찾을 수 없습니다."}
            )
        
        # 관련 Job 정보 조회
        schedule_jobs = db.query(ScheduleJob).filter(ScheduleJob.schedule_id == schedule_id).\
            order_by(ScheduleJob.order).all()
        
        jobs_detail = []
        for schedule_job in schedule_jobs:
            job = db.query(Job).filter(Job.id == schedule_job.job_id).first()
            if job:
                commands = db.query(JobCommand).filter(JobCommand.job_id == job.id).\
                    order_by(JobCommand.order).all()
                
                command_details = []
                for cmd in commands:
                    command_details.append({
                        "content": cmd.content,
                        "status": schedule_job.status,  # 또는 명령어별 상태가 있다면 해당 상태
                        "order": cmd.order
                    })
                
                jobs_detail.append({
                    "id": job.id,
                    "name": job.name,
                    "order": schedule_job.order,
                    "commands": command_details
                })
        
        # 사용자 정보 조회
        # 실제로는 사용자 테이블에서 사용자명을 조회해야 함
        username = f"user_{schedule.user_id}"
        
        return JSONResponse(content={
            "result": "success",
            "data": {
                "id": schedule.id,
                "title": schedule.title,
                "description": schedule.description,
                "created_at": schedule.created_at.isoformat(),
                "userId": username,
                "status": schedule.status,
                "jobs": jobs_detail
            }
        })
    except Exception as e:
        print(f"스케줄 상세 조회 중 오류 발생: {e}")
        return JSONResponse(
            status_code=500, 
            content={"result": "fail", "message": "스케줄 상세 조회에 실패했습니다."}
        )
    
async def update_schedule_status(db: Session, schedule_id: str, status: str) -> dict:
    """스케줄 상태 업데이트 서비스"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            raise HTTPException(
                status_code=404, 
                detail="스케줄을 찾을 수 없습니다."
            )
        
        # 상태 업데이트
        schedule.status = status
        schedule.updated_at = datetime.now()
        
        # 상태가 running이면 실행 기록 추가
        if status == "running":
            schedule_execution = ScheduleExecution(
                schedule_id=schedule_id,
                status=status,
                execution_date=datetime.now()
            )
            db.add(schedule_execution)
        
        # 상태가 success 또는 fail이면 실행 기록 업데이트
        elif status in ["success", "fail"]:
            schedule_execution = db.query(ScheduleExecution).filter(
                ScheduleExecution.schedule_id == schedule_id,
                ScheduleExecution.status == "running"
            ).order_by(ScheduleExecution.created_at.desc()).first()
            
            if schedule_execution:
                schedule_execution.status = status
                schedule_execution.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "result": "success",
            "data": {
                "schedule_id": schedule_id,
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
        }
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        print(f"스케줄 상태 업데이트 중 오류 발생: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"스케줄 상태 업데이트에 실패했습니다: {str(e)}"
        )

async def toggle_schedule(db: Session, schedule_id: str, user_id: int, is_active: bool) -> dict:
    """스케줄 활성화/비활성화 서비스"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id, Schedule.user_id == user_id).first()
        if not schedule:
            raise HTTPException(
                status_code=404, 
                detail="스케줄을 찾을 수 없습니다."
            )
        
        # 스케줄 활성화 상태 업데이트
        schedule.is_active = is_active
        schedule.updated_at = datetime.now()
        
        db.commit()
        
        # Airflow API를 통해 DAG 활성화/비활성화
        try:
            if is_active:
                airflow_integration._unpause_dag_api(schedule_id)
            else:
                airflow_integration._pause_dag_api(schedule_id)
        except Exception as e:
            print(f"Airflow DAG 상태 변경 중 오류 발생: {e}")
        
        return {
            "result": "success",
            "data": {
                "schedule_id": schedule_id,
                "is_active": is_active,
                "updated_at": datetime.now().isoformat()
            }
        }
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        print(f"스케줄 활성화/비활성화 중 오류 발생: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"스케줄 활성화/비활성화에 실패했습니다: {str(e)}"
        )