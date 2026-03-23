def normalize_product(data, source):
    if source == "1stdibs":
        return {
            "name": data.get("model"),
            "brand": data.get("brand"),
            "category": "Accessories",  # improve later
            "external_id": data.get("product_id"),
            "product_url": data.get("product_url"),
            "description": data.get("full_description"),
            "image_url": data.get("main_images")[0]["url"] if data.get("main_images") else None,
            "price": data.get("price"),
            "currency": "USD"
        }

    # future sources:
    # elif source == "grailed":
    #     ...

    return None