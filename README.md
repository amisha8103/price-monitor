#  Product Price Monitoring System

##  Overview

This project is a **Product Price Monitoring System** that ingests product data from multiple marketplaces, tracks price changes over time, and provides APIs and a web interface for monitoring.

It demonstrates:

* Data ingestion & normalization
* Price history tracking
* Event-driven notifications
* Authenticated API access with usage tracking
* Aggregate analytics
* Functional frontend dashboard

---

#  How to Run (Step-by-Step)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd price-monitor
```

---

### 2. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Setup PostgreSQL

* Create database: `price_monitor`
* Update credentials in `app/db.py`

---

### 5. Start the API server (creates tables)

```bash
uvicorn main:app --reload
```

Keep this running, or start it once to create tables and then stop it.

---

### 6. Create API key (in a new terminal)

```bash
python create_user.py
```

---

### 7. Run ingestion

```bash
python -m app.ingest
```

---

### 8. Run frontend

```bash
python -m http.server 5500
```

Open:

```
http://localhost:5500/index.html
```

Note: the dashboard needs the API server running.

---

### 9. Run worker (notifications)

```bash
python app/worker.py
```

If you are not in the repo root, use:

```bash
python -m app.worker
```

---

### 10. Run tests

```bash
python -m pytest
```

---

#  Authentication

All API endpoints require:

```
api-key: YOUR_API_KEY
```

---

#  API Documentation

---

## 🔹 GET /products

Retrieve products with optional filters.

### Query Parameters:

* `source`
* `category`
* `min_price`
* `max_price`

### Example:

```
GET /products?min_price=1000&source=grailed
```

### Response:

```json
[
  {
    "id": 1,
    "name": "Product Name",
    "brand": "Brand",
    "price": 1200.0,
    "source": "grailed"
  }
]
```

---

## 🔹 GET /products/{id}

Get product details along with price history.

### Example:

```
GET /products/1
```

### Response:

```json
{
  "id": 1,
  "name": "Product Name",
  "brand": "Brand",
  "price": 1200.0,
  "source": "grailed",
  "history": [
    {
      "price": 1000.0,
      "timestamp": "2026-03-01T10:00:00"
    }
  ]
}
```

---

## 🔹 GET /analytics

Returns global and filtered aggregate statistics.

### Query Parameters:

* `source` (optional)
* `category` (optional)

### Response:

```json
{
  "total_products": 90,
  "average_price": 2184.0,

  "products_by_source": [
    {"source": "grailed", "count": 30}
  ],

  "source_summary": [
    {
      "source": "grailed",
      "count": 30,
      "avg_price": 2100.0
    }
  ],

  "average_price_by_category": [
    {
      "category": "Earrings",
      "avg_price": 2500.0,
      "count": 10
    }
  ],

  "filtered_total": 5,
  "filtered_avg": 2400.0
}
```

---

## 🔹 POST /refresh

Triggers data ingestion asynchronously.

### Response:

```json
{
  "message": "Data refresh started"
}
```

 Note: This endpoint runs ingestion in the background and does not wait for completion. It reads JSON files from `data/`.

---

#  Error Handling

The API validates inputs and returns appropriate errors:

| Status Code | Meaning                                              |
| ----------- | ---------------------------------------------------- |
| 400         | Invalid input (e.g., negative price, empty category) |
| 401         | Missing or invalid API key                           |
| 404         | Product not found                                    |

### Example:

```json
{
  "detail": "min_price must be >= 0"
}
```

---

#  Design Decisions

---

## 🔹 Price History Scaling

Price history is stored in a separate table (`price_history`) linked by `product_id`.

### Why this scales:

* Append-only writes
* Indexed by `product_id`
* Efficient for millions of rows

### Future improvements:

* Table partitioning by time
* Archiving old records
* Using time-series databases

---

## 🔹 Notification System

An **event-driven architecture** is used:

### Flow:

1. Price change detected during ingestion
2. Event stored in `events` table (`pending`)
3. Worker processes events asynchronously
4. Status updated (`sent` / `failed`)

### Why this approach:

* Non-blocking ingestion
* Reliable (events stored in DB)
* Supports retry of failed events

Notifications are simulated via logs but can be extended to webhooks or messaging systems. Failed events are retried in subsequent worker runs.

---

## 🔹 Handling Multiple Sources

A normalization layer standardizes different input formats.

### Benefits:

* Easy to add new sources
* Decoupled ingestion logic

### Scaling to 100+ sources:

* Add new parser per source
* Plug into ingestion pipeline
* No change required in API/database

---

#  System Architecture

### Components:

1. **Ingestion Layer**

   * Reads data
   * Detects price changes
   * Stores products & history

2. **Database**

   * Products
   * Price history
   * Events
   * API usage logs

3. **Worker**

   * Processes events asynchronously
   * Handles failures & retries

4. **API (FastAPI)**

   * Filtering
   * Analytics
   * Authentication
   * Usage tracking

5. **Frontend**

   * Dashboard
   * Product listing
   * Product detail with history

---

#  Testing

Tests are located in tests/test_api.py

Run:

```bash
python -m pytest
```

Covers:

* Authentication
* API responses
* Edge cases
* Error handling
* Filters

---

#  Known Limitations

* No real notification integration (email/webhook simulated)
* No pagination for large datasets
* No caching layer
* Worker runs manually (not scheduled)
* Basic frontend (no styling)
* No rate limiting

---

#  Future Improvements

* Add Redis caching
* Implement pagination
* Add real-time updates (WebSockets)
* Integrate message queue (Kafka/RabbitMQ)
* Improve frontend (React + charts)
* Add retry backoff for events
* Deploy with Docker & CI/CD

---

#  Project Structure

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
├── tests/
├── data/
├── main.py
├── index.html
├── create_user.py
├── requirements.txt
└── README.md
```

---

#  Conclusion

This project demonstrates:

* End-to-end backend system design
* Event-driven architecture
* Scalable data handling
* Clean API design
* Real-world engineering practices

---
