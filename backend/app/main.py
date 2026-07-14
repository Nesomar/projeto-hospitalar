from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.pacientes import router as pacientes_router
from app.api.routes.painel import router as painel_router
from app.api.routes.prescricao import router as prescricao_router
from app.api.routes.prontuario import router as prontuario_router
from app.api.routes.triagem import router as triagem_router

app = FastAPI(title="UPA Nordeste API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(pacientes_router)
app.include_router(triagem_router)
app.include_router(prontuario_router)
app.include_router(prescricao_router)
app.include_router(painel_router)
