from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.schemas.job.job_create_schema import JobCreateRequest


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String, nullable=False)
    user_department = Column(String, nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    data_load_command = Column(Text, nullable=False)
    data_load_url = Column(String(255), nullable=False)
    data_load_code = Column(LONGTEXT)
    code = Column(LONGTEXT, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    commands = relationship("JobCommand", back_populates="job", cascade="all, delete")

    @classmethod
    def create(cls, job: JobCreateRequest, user_id: int, user_name: str, department: str):
        return Job(
        user_id=user_id,
        user_name=user_name,
        user_department=department,
        type=job.type,
        title=job.title,
        description=job.description,
        data_load_command=job.data_load_command,
        data_load_url=job.data_load_url,
        data_load_code=job.data_load_code,
        code=job.code
    )

class JobCommand(Base):
    __tablename__ = "job_commands"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)

    job = relationship("Job", back_populates="commands")