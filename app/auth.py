from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate(api_key: str = Header(None), db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key missing")

    user = db.query(User).filter(User.api_key == api_key).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # track usage
    user.usage_count += 1
    db.commit()

    return user