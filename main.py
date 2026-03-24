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
from app.models import APIUsage
from fastapi import HTTPException

def log_usage(db, api_key, endpoint):

    print(f"Logging usage: {api_key} called {endpoint}")
    usage = APIUsage(
        api_key=api_key,
        endpoint=endpoint
    )
    db.add(usage)
    db.commit()

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
    log_usage(db, user.api_key, "/products") 

    # ❌ BAD INPUT CHECK
    if min_price is not None and min_price < 0:
        raise HTTPException(status_code=400, detail="min_price must be >= 0")

    if max_price is not None and max_price < 0:
        raise HTTPException(status_code=400, detail="max_price must be >= 0")

    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")
    
    query = db.query(Product)

    if source:
        query = query.filter(Product.source == source)
    
    if category:
        query = query.filter(func.lower(Product.category) == category.lower())

    if min_price is not None:
        query = query.filter(Product.current_price >= min_price)

    if max_price is not None:
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
    log_usage(db, user.api_key, f"/products/{product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")    

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

# @app.get("/analytics")
# def get_analytics(user = Depends(authenticate), db: Session = Depends(get_db)):
#     total_products = db.query(Product).count()

#     avg_price = db.query(func.avg(Product.current_price)).scalar()

#     source_counts = db.query(
#         Product.source, func.count(Product.id)
#     ).group_by(Product.source).all()

#     return {
#         "total_products": total_products,
#         "average_price": float(avg_price) if avg_price else 0,
#         "products_by_source": [
#             {"source": s, "count": c} for s, c in source_counts
#         ]
#     }

# @app.get("/analytics")
# def get_analytics(
#     user = Depends(authenticate),
#     db: Session = Depends(get_db),
#     source: str = None,
#     category: str = None
# ):

#     query = db.query(Product)

#     # apply filters
#     if source:
#         query = query.filter(Product.source == source)

#     if category:
#         from sqlalchemy import func
#         query = query.filter(func.lower(Product.category) == category.lower())

#     # total products
#     total_products = query.count()

#     # average price
#     avg_price = query.with_entities(func.avg(Product.current_price)).scalar()

#     # products by source (respecting filters)
#     source_counts = db.query(
#         Product.source, func.count(Product.id)
#     )

#     if source:
#         source_counts = source_counts.filter(Product.source == source)

#     if category:
#         source_counts = source_counts.filter(
#             func.lower(Product.category) == category.lower()
#         )

#     source_counts = source_counts.group_by(Product.source).all()

#     # average by category (respecting filters)
#     category_avg = db.query(
#         Product.category, func.avg(Product.current_price)
#     )

#     if source:
#         category_avg = category_avg.filter(Product.source == source)

#     if category:
#         category_avg = category_avg.filter(
#             func.lower(Product.category) == category.lower()
#         )

#     category_avg = category_avg.group_by(Product.category).all()

#     return {
#         "total_products": total_products,
#         "average_price": float(avg_price) if avg_price else 0,

#         "products_by_source": [
#             {"source": s, "count": c} for s, c in source_counts
#         ],

#         "average_price_by_category": [
#             {"category": cat, "avg_price": float(avg)}
#             for cat, avg in category_avg
#         ]
#     }

@app.get("/analytics")
def get_analytics(
    user = Depends(authenticate),
    db: Session = Depends(get_db),
    source: str = None,
    category: str = None
):
    log_usage(db, user.api_key, "/analytics")

    # 🔥 GLOBAL (NO FILTERS)
    total_products = db.query(Product).count()
    avg_price = db.query(func.avg(Product.current_price)).scalar()

    if source and source.strip() == "":
        raise HTTPException(status_code=400, detail="Source cannot be empty")
    if category and category.strip() == "":
        raise HTTPException(status_code=400, detail="Category cannot be empty")
    if total_products == 0:
        raise HTTPException(status_code=400, detail="No products in database")
    

    # 🟢 GLOBAL SOURCE SUMMARY
    global_source_counts = db.query(
        Product.source, func.count(Product.id), func.avg(Product.current_price)
    ).group_by(Product.source).all()
    
    # 🔵 FILTERED QUERY
    query = db.query(Product)

    if source:
        query = query.filter(Product.source == source)

    if category:
        query = query.filter(func.lower(Product.category) == category.lower())

    # products by source (filtered)
    source_counts = query.with_entities(
        Product.source, func.count(Product.id)
    ).group_by(Product.source).all()

    # avg by category (filtered)
    category_avg = query.with_entities(
        Product.category,
        func.avg(Product.current_price),
        func.count(Product.id)
    ).group_by(Product.category).all()

    filtered_total = query.count()
    filtered_avg = query.with_entities(func.avg(Product.current_price)).scalar()

    return {
        "total_products": total_products,
        "average_price": float(avg_price) if avg_price else 0,

        "products_by_source": [
            {"source": s, "count": c} for s, c, _ in global_source_counts
        ],

        "source_summary": [
            {
                "source": s,
                "count": c,
                "avg_price": float(avg)
            }
            for s, c, avg in global_source_counts
        ], 

        "average_price_by_category": [
            {
                "category": cat,
                "avg_price": float(avg),
                "count": count
            }
            for cat, avg, count in category_avg
        ],

        "filtered_total": filtered_total,
        "filtered_avg": float(filtered_avg) if filtered_avg else 0,
    }



@app.post("/refresh")
def refresh_data(user = Depends(authenticate), db: Session = Depends(get_db)):
    log_usage(db, user.api_key, "/refresh")
    try:
        subprocess.Popen([sys.executable, "-m", "app.ingest"])
        return {"message": "Data refresh started"}
    except Exception as e:
        return {"error": str(e)}

print(models.Event)