# Product Price Monitoring System

##  Overview

This project is a **Product Price Monitoring System** that collects product data from multiple marketplaces, tracks price changes over time, and provides APIs and a web interface for monitoring and analysis.

It supports:

* Multi-source product ingestion (1stdibs, extensible to others)
* Price history tracking
* Event-driven notifications for price changes
* Authenticated API access
* Interactive frontend dashboard

---

##  Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd price-monitor
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL

* Create a database named `price_monitor`
* Update DB credentials in `app/db.py`

### 5. Run the application

```bash
python main.py
uvicorn main:app --reload
```

### 6. Generate API key

```bash
python create_user.py
```

---

##  Running End-to-End

1. Run ingestion to load data:

python -m app.ingest

2. Start API server:

uvicorn main:app --reload

3. Open frontend:

Open `index.html` in browser

4. (Optional) Process notifications:

python -m app.worker


##  API Documentation

All endpoints require an API key:

```
api-key: YOUR_API_KEY
```

### Endpoints

* `GET /products`

  * List products
  * Supports filters:

    * `source`
    * `min_price`
    * `max_price`

* `GET /products/{id}`

  * Get product details with price history

* `GET /analytics`

  * Returns:

    * total products
    * average price
    * products grouped by source

### Example Response

GET /products

[
  {
    "id": 1,
    "name": "Chanel Belt",
    "brand": "Chanel",
    "price": 2500,
    "source": "1stdibs"
  }
]   

---

##  System Architecture

### 1. Ingestion Pipeline

* Reads JSON data from multiple sources
* Uses normalization layer to standardize data
* Inserts into database
* Detects price changes

### 2. Price History

* Stored in separate table (`price_history`)
* Linked via `product_id`
* Efficient for large-scale queries

### 3. Event-Driven Notifications

* Price changes generate events
* Events stored in `events` table
* Background worker processes events
* Ensures non-blocking ingestion

### 4. API Layer

* Built using FastAPI
* Supports filtering, analytics, and history
* Secured using API key authentication

### 5. Frontend

* Simple HTML + JavaScript UI
* Displays dashboard, products, and history

---

##  Design Decisions

### 🔹 Price History Scaling

Price history is stored in a dedicated table with indexing on `product_id` and timestamps. This allows efficient querying even when the table grows to millions of rows.

---

### 🔹 Scaling Considerations   ← ✅ ADD HERE

- Price history table can grow to millions of rows
- Indexed on `product_id` and `timestamp`
- Queries use filtering to avoid full table scans
- Can be improved using:
  - Table partitioning
  - Archival of old data
  - Read replicas for heavy analytics

---


### 🔹 Notification System

An event-driven architecture is used:

* Price changes create events
* Worker processes events asynchronously
* Ensures reliability and avoids blocking ingestion

---

### 🔹 Handling Multiple Sources

A normalization layer (`normalizer.py`) standardizes input data.

To add a new source:

* Implement a new normalization function
* Reuse ingestion pipeline

---

##  Testing

Run tests using:

```bash
python -m pytest
```

Tests cover:

* Authentication
* API endpoints
* Edge cases
* Filtering
* Invalid inputs

---

##  Known Limitations

* No real external notification integration (webhook/email simulated)
* Basic frontend UI (not styled)
* No pagination for large datasets
* No caching layer

---

##  Future Improvements

* Add Redis caching
* Integrate message queue (Kafka/RabbitMQ)
* Improve frontend UI (React/Vue)
* Add pagination and sorting
* Add real-time updates via WebSockets

---

##  Project Structure

```
price-monitor/
│
├── app/
│   ├── models.py
│   ├── db.py
│   ├── ingest.py
│   ├── normalizer.py
│   ├── worker.py
│   ├── auth.py
│   └── dependencies.py
│
├── data/
├── tests/
├── main.py
├── index.html
├── create_user.py
├── requirements.txt
└── README.md
```

---

##  Conclusion

This system demonstrates:

* Scalable backend design
* Event-driven architecture
* Clean API design
* End-to-end data flow
* Real-world engineering practices

---
