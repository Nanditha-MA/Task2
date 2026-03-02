from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import Base, engine
from app.core.logging_config import setup_logging
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes.auth import router as auth_router
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Document Management API", lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(health_router)