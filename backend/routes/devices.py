import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, User
from models import DeviceRegister

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.post("/register", status_code=200)
def register_device(
    body: DeviceRegister,
    db: Session = Depends(get_db),
):
    try:
        uid = uuid.UUID(body.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz user_id formatı")

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        user = User(id=uid, device_token=body.device_token)
        db.add(user)
    else:
        user.device_token = body.device_token

    db.commit()
    return {"message": "Cihaz kaydedildi", "user_id": str(uid)}
