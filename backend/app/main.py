from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.pacientes import router as pacientes_router
from app.api.routes.prescricao import router as prescricao_router
from app.api.routes.prontuario import router as prontuario_router
from app.api.routes.triagem import router as triagem_router

app = FastAPI(title="UPA Nordeste API")

app.include_router(auth_router)
app.include_router(pacientes_router)
app.include_router(triagem_router)
app.include_router(prontuario_router)
app.include_router(prescricao_router)
