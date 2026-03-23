from app.db import SessionLocal
from app.models import Event


def process_events():
    db = SessionLocal()

    events = db.query(Event).filter(Event.status == "pending").all()

    for event in events:
        try:
            print(f"Processing event for product {event.product_id}")
            print(f"Price changed: {event.old_price} → {event.new_price}")

            # simulate notification (webhook/email/etc)
            event.status = "sent"

            db.commit()

        except Exception:
            event.status = "failed"
            db.commit()

    db.close()


if __name__ == "__main__":
    process_events()