from sqlalchemy import Column, Integer, Text, String, TIMESTAMP, func
# from app.db.db import Base

class Email(Base):
    __tablename__ = "email"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_email = Column(Text, nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
