# AIgnition — Backend API

FastAPI backend for the AIgnition AI Marketing Decision Copilot.

---

## Architecture

```
backend/
├── app/
│   ├── main.py              ← FastAPI app factory (CORS, middleware, routers)
│   ├── config.py            ← Settings loaded from .env via pydantic-settings
│   ├── dependencies.py      ← Shared FastAPI dependency functions
│   ├── ml_interface.py      ← ⭐ ML/LLM stubs — the ONLY file ML team modifies
│   │
│   ├── routes/              ← One router per endpoint domain
│   │   ├── upload.py        → POST /api/v1/upload
│   │   ├── validate.py      → POST /api/v1/validate
│   │   ├── forecast.py      → POST /api/v1/forecast
│   │   ├── optimizer.py     → POST /api/v1/optimize
│   │   ├── risks.py         → POST /api/v1/risks
│   │   ├── summary.py       → POST /api/v1/summary
│   │   ├── report.py        → GET  /api/v1/report
│   │   └── dashboard.py     → GET  /api/v1/dashboard
│   │
│   ├── services/            ← Business logic (rules-based, ML-replaceable)
│   ├── models/              ← Pydantic request & response models
│   ├── utils/               ← Logging, exceptions, CSV and file helpers
│   └── storage/uploads/     ← Persisted CSV uploads
│
├── requirements.txt
├── .env.example
├── run.py
└── README.md
```

---

## Quick Start

### 1. Create and activate a virtual environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work out of the box)
```

### 4. Run the server

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience runner
python run.py
```

### 5. Open Swagger docs

Navigate to **http://localhost:8000/docs**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/upload` | Upload a marketing CSV (Google Ads, Meta, Microsoft, GA4, Shopify) |
| `POST` | `/api/v1/validate` | Run 7 data-quality checks, get a 0–100 quality score |
| `POST` | `/api/v1/forecast` | Generate P10/P50/P90 revenue forecast |
| `POST` | `/api/v1/optimize` | Optimise budget across channels |
| `POST` | `/api/v1/risks` | Detect risk signals (concentration, ROAS, saturation, …) |
| `POST` | `/api/v1/summary` | Generate executive summary |
| `GET` | `/api/v1/report?format=pdf` | Download PDF or CSV report |
| `GET` | `/api/v1/dashboard` | All data in one unified response |
| `GET` | `/health` | Health check |

---

## Typical Workflow

```
POST /upload        → get upload_id
POST /validate      → check data quality
POST /forecast      → generate revenue forecast
POST /optimize      → allocate budget
POST /risks         → detect risk signals
POST /summary       → executive summary
GET  /dashboard     → all of the above in one call
GET  /report        → download PDF or CSV
```

---

## ML Integration Guide

> **For the ML team:** You only need to edit **`app/ml_interface.py`**.

The file contains two placeholder functions:

```python
def predict(data: dict) -> dict:
    raise NotImplementedError("ML team will implement")

def generate_summary(data: dict) -> dict:
    raise NotImplementedError("LLM team will implement")
```

### Steps to plug in your model

1. Open `backend/app/ml_interface.py`
2. Replace `raise NotImplementedError(...)` with your implementation
3. Match the return dict shape documented in the docstring
4. Set `ML_FALLBACK_ENABLED=false` in `.env` to surface errors instead of mock data

**No other file needs to change.** All routes, services, and response models stay the same.

---

## Frontend Integration

The frontend (`aignition-copilot/src/lib/api.ts`) provides a fully typed TypeScript client:

```ts
import { api } from "@/lib/api";

// Upload
const { upload_id } = await api.upload(file);

// Validate
const validation = await api.validate(upload_id);

// Full dashboard (single call)
const dashboard = await api.dashboard(upload_id, { totalBudget: 420000 });

// Download PDF
const { url, filename } = await api.downloadReport(upload_id, "pdf");
```

Set `VITE_API_URL=http://localhost:8000/api/v1` in the frontend `.env` file.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable uvicorn auto-reload |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Allowed frontend origins |
| `MAX_UPLOAD_SIZE_MB` | `50` | Max CSV file size |
| `ML_FALLBACK_ENABLED` | `true` | Use mock data when ML is not implemented |

---

## Running Tests (manually)

```bash
# Upload a test CSV
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@sample.csv"

# Validate
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"upload_id": "<id>"}'

# Dashboard
curl "http://localhost:8000/api/v1/dashboard?upload_id=<id>&total_budget=420000"
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.115.5 | Web framework |
| `uvicorn` | 0.32.1 | ASGI server |
| `pydantic` | 2.10.3 | Data validation |
| `pydantic-settings` | 2.6.1 | `.env` config |
| `pandas` | 2.2.3 | CSV parsing & analysis |
| `numpy` | 1.26.4 | Numerical operations |
| `reportlab` | 4.2.5 | PDF generation |
| `python-multipart` | 0.0.18 | File upload support |
