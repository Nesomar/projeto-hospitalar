from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.pacientes import router as pacientes_router

app = FastAPI(title="UPA Nordeste API")

app.include_router(auth_router)
app.include_router(pacientes_router)
