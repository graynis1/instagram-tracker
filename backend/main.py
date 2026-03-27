import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables
from scheduler import get_scheduler
from routes.accounts import router as accounts_router
from routes.history import router as history_router
from routes.devices import router as devices_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Başlangıç
    logger.info("Uygulama başlatılıyor...")
    create_tables()
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("Scheduler başlatıldı")
    yield
    # Kapanış
    scheduler.stop()
    logger.info("Scheduler durduruldu")


app = FastAPI(
    title="Instagram Tracker API",
    version="1.0.0",
    description="Instagram hesap değişikliklerini takip eden API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts_router)
app.include_router(history_router)
app.include_router(devices_router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "instagram-tracker-api"}
