import json
from app.db import SessionLocal
from app.models import Product, PriceHistory


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def insert_product(db, data, source):
    product = Product(
        name=data.get("model"),
        brand=data.get("brand"),
        category="Unknown",  # we improve later
        source=source,
        external_id=data.get("product_id"),
        product_url=data.get("product_url"),
        description=data.get("full_description"),
        image_url=data.get("main_images")[0]["url"] if data.get("main_images") else None,
        current_price=data.get("price"),
        currency="USD"
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    history = PriceHistory(
        product_id=product.id,
        price=product.current_price
    )

    db.add(history)
    db.commit()


import os

def run_ingestion():
    db = SessionLocal()

    data_folder = "data"

    for file_name in os.listdir(data_folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(data_folder, file_name)

            print(f"Processing {file_name}...")

            data = load_json(file_path)

            # handle single object or list
            if isinstance(data, dict):
                data = [data]

            for item in data:
                insert_product(db, item, "1stdibs")

    print("Ingestion complete!")


if __name__ == "__main__":
    run_ingestion()