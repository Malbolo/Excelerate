from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.log_config import logger

# 데이터베이스 URL 설정
DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy 엔진 생성
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    logger.info(f"Database engine created with URL: {DATABASE_URL}")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 베이스 클래스
Base = declarative_base()

def get_db():
    """요청마다 새로운 DB 세션을 제공하고 요청 종료 후 세션을 닫음"""
    db = SessionLocal()
    try:
        yield db
        logger.debug("Database session yielded")
    finally:
        db.close()
        logger.debug("Database session closed")