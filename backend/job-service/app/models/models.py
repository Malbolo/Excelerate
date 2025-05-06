from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from app.db.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String, nullable=False)
    user_department = Column(String, nullable=False)
    type = Column(String(50))
    title = Column(String(100))
    description = Column(Text)
    data_load_command = Column(Text)
    data_load_url = Column(String(255))
    code = Column(LONGTEXT)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    commands = relationship("JobCommand", back_populates="job", cascade="all, delete")


class JobCommand(Base):
    __tablename__ = "job_commands"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    content = Column(Text)
    order = Column(Integer)

    job = relationship("Job", back_populates="commands")

# schedule
class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(String(100), primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    execution_time = Column(DateTime, nullable=False)
    frequency = Column(String(50), nullable=False)
    success_emails = Column(Text, nullable=True)
    failure_emails = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, running, success, fail
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ScheduleJob(Base):
    __tablename__ = "schedule_jobs"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String(100), ForeignKey("schedules.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    order = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")  # pending, running, success, fail
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    schedule = relationship("Schedule", backref="schedule_jobs")
    job = relationship("Job")


class ScheduleExecution(Base):
    __tablename__ = "schedule_executions"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String(100), ForeignKey("schedules.id", ondelete="CASCADE"))
    status = Column(String(20), default="pending")  # pending, success, fail
    execution_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    schedule = relationship("Schedule")

    