from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, BigInteger, Date
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship

from db.database import Base
from schemas.job_create_schema import JobCreateRequest


class Job(Base):
    __tablename__ = "jobs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    user_name = Column(String(50), nullable=False)
    user_department = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    data_load_command = Column(Text, nullable=False)
    data_load_url = Column(String(255), nullable=False)
    data_load_code = Column(LONGTEXT)
    code = Column(LONGTEXT, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    source_data = relationship("JobSourceData", back_populates="job", uselist=False, cascade="all, delete")
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

class JobSourceData(Base):
    __tablename__ = "job_source_data"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    factory_name = Column(String(20))
    system_name = Column(String(10))
    metric = Column(String(15))
    factory_id = Column(String(30))
    product_code = Column(String(30))
    start_date = Column(Date)
    end_date = Column(Date)

    job = relationship("Job", back_populates="source_data")

class JobCommand(Base):
    __tablename__ = "job_commands"

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)

    job = relationship("Job", back_populates="commands")