from fastapi import FastAPI

from app.api.routes.auth import router as auth_router

app = FastAPI(title="UPA Nordeste API")

app.include_router(auth_router)
