# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
#
# load_dotenv()
#
# user = os.getenv("DB_USER")
# password = os.getenv("DB_PASSWORD")
# host = os.getenv("DB_HOST")
# port = os.getenv("DB_PORT")
# name = os.getenv("DB_NAME")
#
# DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
#
# engine = create_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     except Exception as e:
#         db.rollback()  # 예외 발생 시 롤백
#         raise e  # 예외를 상위로 전달
#     finally:
#         db.close()