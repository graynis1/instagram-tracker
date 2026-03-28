import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables, engine
from scheduler import get_scheduler
from routes.accounts import router as accounts_router
from routes.history import router as history_router
from routes.devices import router as devices_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _apply_runtime_migrations():
    """
    Alembic migration'ın çalışmadığı durumlar için güvenlik ağı.
    check_interval_hours → check_interval_minutes dönüşümünü sütun bazında kontrol eder.
    """
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            # Hızlı sütun varlık kontrolü — information_schema sorgusu
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'tracked_accounts'
                  AND column_name IN ('check_interval_hours', 'check_interval_minutes')
            """))
            existing = {row[0] for row in result}
            has_old = 'check_interval_hours' in existing
            has_new = 'check_interval_minutes' in existing

            if not has_old and not has_new:
                return  # Tablo henüz yok, create_tables() halleder

            if has_old and not has_new:
                conn.execute(text(
                    'ALTER TABLE tracked_accounts '
                    'RENAME COLUMN check_interval_hours TO check_interval_minutes'
                ))
                conn.commit()
                logger.info("Runtime migration: check_interval_hours → check_interval_minutes")
            elif has_old and has_new:
                conn.execute(text(
                    'UPDATE tracked_accounts '
                    'SET check_interval_minutes = check_interval_hours * 60 '
                    'WHERE check_interval_minutes IS NULL OR check_interval_minutes = 0'
                ))
                conn.execute(text(
                    'ALTER TABLE tracked_accounts DROP COLUMN check_interval_hours'
                ))
                conn.commit()
                logger.info("Runtime migration: check_interval_hours sütunu kaldırıldı")
    except Exception as e:
        logger.warning(f"Runtime migration kontrolü atlandı: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Başlangıç
    logger.info("Uygulama başlatılıyor...")
    _apply_runtime_migrations()
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
