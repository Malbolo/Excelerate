from fastapi import FastAPI
from app.api.job_api import router as job_router
from app.db.database import Base, engine

# app = FastAPI()
app = FastAPI(docs_url="/api/jobs/docs", redoc_url=None, openapi_url="/api/jobs/openapi.json")

Base.metadata.create_all(bind=engine)

app.include_router(job_router)
