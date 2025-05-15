from app.db.database import Base
from app.schemas.job_create_schema import JobCreateRequest
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship


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
    def create(cls, request: JobCreateRequest, user_id: int, user_name: str, department: str):
        return Job(
        user_id=user_id,
        user_name=user_name,
        user_department=department,
        type=request.type,
        title=request.title,
        description=request.description,
        data_load_command=request.data_load_command,
        data_load_url=request.data_load_url,
        data_load_code=request.data_load_code,
        code=request.code
    )

class JobCommand(Base):
    __tablename__ = "job_commands"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)

    job = relationship("Job", back_populates="commands")