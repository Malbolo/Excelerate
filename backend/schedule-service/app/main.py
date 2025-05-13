from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.api.schedule_api import router as schedule_router

# app = FastAPI()
app = FastAPI(docs_url="/api/schedulers/docs", redoc_url=None, openapi_url="/api/schedulers/openapi.json")

# Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(schedule_router)
