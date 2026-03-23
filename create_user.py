from app.db import SessionLocal
from app.models import User
import uuid

db = SessionLocal()

api_key = str(uuid.uuid4())

user = User(
    api_key=api_key
)

db.add(user)
db.commit()

print("Your API key:", api_key)