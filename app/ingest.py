import json
from app.db import SessionLocal
from app.models import Product, PriceHistory
from app.normalizer import normalize_product
from app.models import Event


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def insert_product(db, data, source):

    if data.get("price") is None:
        return
    external_id = data.get("external_id")

    # check if product already exists
    existing_product = db.query(Product).filter_by(
        source=source,
        external_id=external_id
    ).first()

    if existing_product:
        # check if price changed
        if float(existing_product.current_price) != float(data.get("price")):

            # update price
            old_price = existing_product.current_price
            existing_product.current_price = data.get("price")

            db.commit()

            # add to history
            history = PriceHistory(
                product_id=existing_product.id,
                price=data.get("price")
            )
            db.add(history)
            db.commit()

            event = Event(
                product_id=existing_product.id,
                old_price=old_price,
                new_price=data.get("price"),
                status="pending"
            )

            db.add(event)
            db.commit()

            print(f"Price updated for {external_id}: {old_price} → {data.get('price')}")

        return

    # if new product → insert
    product = Product(
        name=data.get("name"),
        brand=data.get("brand"),
        category=data.get("category"),
        source=source,
        external_id=external_id,
        product_url=data.get("product_url"),
        description=data.get("description"),
        image_url=data.get("image_url"),
        current_price=data.get("price"),
        currency=data.get("currency")
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
                normalized = normalize_product(item, "1stdibs")

                if normalized:
                    insert_product(db, normalized, "1stdibs")

    print("Ingestion complete!")
    db.close()


if __name__ == "__main__":
    run_ingestion()