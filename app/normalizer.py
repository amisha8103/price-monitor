# def normalize_product(data, source):
#     if source == "1stdibs":
#         return {
#             "name": data.get("model"),
#             "brand": data.get("brand"),
#             "category": "Accessories",  # improve later
#             "external_id": data.get("product_id"),
#             "product_url": data.get("product_url"),
#             "description": data.get("full_description"),
#             "image_url": data.get("main_images")[0]["url"] if data.get("main_images") else None,
#             "price": data.get("price"),
#             "currency": "USD"
#         }

#     # future sources:
#     # elif source == "grailed":
#     #     ...

#     return None


def normalize_product(data, source):

    # common fields
    price = data.get("price")
    if price is None:
        return None

    # image handling
    image_url = None
    if data.get("main_images"):
        image_url = data["main_images"][0].get("url")
    elif data.get("image_url"):
        image_url = data.get("image_url")

    # description handling (diff per source)
    description = None

    if source == "1stdibs":
        description = data.get("full_description")

    elif source == "fashionphile":
        description = data.get("metadata", {}).get("description")

    elif source == "grailed":
        description = data.get("metadata", {}).get("full_product_description")

    # # category (simple mapping)
    # if source == "1stdibs":
    #     category = "Accessories"
    # elif source == "fashionphile":
    #     category = "Jewelry"
    # elif source == "grailed":
    #     category = "Apparel"
    # else:
    #     category = "Unknown"

    name = data.get("model", "").lower()

    if "belt" in name:
        category = "Belts"

    elif "earring" in name:
        category = "Earrings"

    elif "necklace" in name or "pendant" in name:
        category = "Necklace"

    elif "ring" in name:
        category = "Rings"

    elif "jacket" in name:
        category = "Jackets"

    elif "shirt" in name or "tee" in name:
        category = "Shirts"

    elif "pants" in name or "jeans" in name:
        category = "Pants"

    else:
        category = "Other"

    return {
        "name": data.get("model"),
        "brand": data.get("brand"),
        "category": category,
        "price": price,
        "external_id": data.get("product_id"),
        "product_url": data.get("product_url"),
        "description": description,
        "image_url": image_url,
        "currency": data.get("currency", "USD")
    }