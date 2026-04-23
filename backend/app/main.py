from fastapi import FastAPI
from app.core.database import engine, Base
from app.core.seed_data import seed_hcps
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed demo HCPs (idempotent — only inserts if table is empty)
    seed_hcps()
    yield

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach routes
from app.routes.auth_route import router as auth_router
from app.routes.hcp_route import router as hcp_router
from app.routes.interaction_route import router as interaction_router
from app.routes.chat_route import router as chat_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(hcp_router, prefix="/api/v1")
app.include_router(interaction_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")

@app.get("/test")
def test():
    return {"message": "Hello World pusing in the ubantu server through the github action !!"}