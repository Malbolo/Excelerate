from fastapi import FastAPI
import app.api.job_api

app = FastAPI()

app.include_router(api.job_api.router)
