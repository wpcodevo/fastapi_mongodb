from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth

app = FastAPI(title="Microsserviço de Autenticação")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Auth"], prefix="/api/auth")


@app.get("/api/healthchecker")
def root():
    return {"status": "ok", "message": "Microsserviço de Autenticação ativo"}