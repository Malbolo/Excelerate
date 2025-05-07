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