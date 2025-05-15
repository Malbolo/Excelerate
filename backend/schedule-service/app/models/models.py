from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime

from app.db.database import Base


class Schedule(Base):
    """스케줄 정보 모델"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    dag_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(String(50), nullable=False)  # daily, weekly, monthly 등
    frequency_cron = Column(String(100), nullable=False)  # cron 표현식
    execution_time = Column(String(10), nullable=True)  # HH:MM 형식
    is_paused = Column(Boolean, default=False)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    success_emails = Column(JSON, nullable=True)  # ['example@example.com', ...] 형식
    failure_emails = Column(JSON, nullable=True)

    owner = Column(String(100), nullable=False)
    created_by = Column(Integer, nullable=False)  # 사용자 ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 정의
    jobs = relationship("ScheduleJob", back_populates="schedule", cascade="all, delete-orphan")
    runs = relationship("ScheduleRun", back_populates="schedule", cascade="all, delete-orphan")

class ScheduleJob(Base):
    """스케줄에 포함된 Job 모델"""
    __tablename__ = "schedule_jobs"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    job_id = Column(String(50), nullable=False)  # Job 서비스의 job ID
    order = Column(Integer, default=0)  # 실행 순서

    schedule = relationship("Schedule", back_populates="jobs")

class ScheduleRun(Base):
    """스케줄 실행 이력 모델"""
    __tablename__ = "schedule_runs"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    run_id = Column(String(255), nullable=False)  # Airflow dag_run_id
    status = Column(String(50), nullable=False)  # success, failed, running, etc.
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    execution_date = Column(DateTime, nullable=True)

    schedule = relationship("Schedule", back_populates="runs")
    tasks = relationship("ScheduleRunTask", back_populates="run", cascade="all, delete-orphan")

class ScheduleRunTask(Base):
    """스케줄 실행 작업 모델"""
    __tablename__ = "schedule_run_tasks"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("schedule_runs.id"), nullable=False)
    task_id = Column(String(255), nullable=False)  # Airflow task_id
    job_id = Column(String(50), nullable=False)  # Job 서비스의 job ID
    status = Column(String(50), nullable=False)  # success, failed, running, etc.
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    error_trace = Column(LONGTEXT, nullable=True)

    run = relationship("ScheduleRun", back_populates="tasks")