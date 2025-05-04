from fastapi import FastAPI
import api.job_api

app = FastAPI()

app.include_router(api.job_api.router)
