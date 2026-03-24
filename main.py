from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.db import engine, Base
from app import models
from app.models import Product
from app.models import PriceHistory
from sqlalchemy import func
from app.auth import authenticate
import subprocess
import sys

# create tables
Base.metadata.create_all(bind=engine)

print("Tables created successfully!")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Price Monitoring API is running"}



@app.get("/products")
def get_products(
    user = Depends(authenticate),
    db: Session = Depends(get_db),
    source: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None
):
    query = db.query(Product)

    if source:
        query = query.filter(Product.source == source)
    
    if category:
        query = query.filter(Product.category == category)

    if min_price:
        query = query.filter(Product.current_price >= min_price)

    if max_price:
        query = query.filter(Product.current_price <= max_price)

    products = query.all()

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

@app.get("/products/{product_id}")
def get_product(product_id: int,user = Depends(authenticate), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return {"error": "Product not found"}

    history = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id
    ).all()

    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "price": float(product.current_price),
        "source": product.source,
        "history": [
            {
                "price": float(h.price),
                "timestamp": h.timestamp
            }
            for h in history
        ]
    }

@app.get("/analytics")
def get_analytics(user = Depends(authenticate), db: Session = Depends(get_db)):
    total_products = db.query(Product).count()

    avg_price = db.query(func.avg(Product.current_price)).scalar()

    source_counts = db.query(
        Product.source, func.count(Product.id)
    ).group_by(Product.source).all()

    return {
        "total_products": total_products,
        "average_price": float(avg_price) if avg_price else 0,
        "products_by_source": [
            {"source": s, "count": c} for s, c in source_counts
        ]
    }

@app.post("/refresh")
def refresh_data(user = Depends(authenticate)):
    try:
        subprocess.Popen([sys.executable, "-m", "app.ingest"])
        return {"message": "Data refresh started"}
    except Exception as e:
        return {"error": str(e)}

print(models.Event)