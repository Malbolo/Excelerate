from fastapi import FastAPI
from app.api.email_api import router as email_router

# app = FastAPI()


app = FastAPI(docs_url="/api/notification/docs", redoc_url=None, openapi_url="/api/notification/openapi.json")
# app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None) # 배포 시 docs 비활성화

app.include_router(email_router)
