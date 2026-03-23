from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import Product

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Price Monitoring API is running"}


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "price": float(p.current_price),
            "source": p.source
        }
        for p in products
    ]