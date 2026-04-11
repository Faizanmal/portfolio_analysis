# API Documentation

## AI Portfolio Analysis API

RESTful API for AI-powered portfolio analysis, risk prediction, sentiment analysis, and portfolio optimization.

**Base URL:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## Authentication

Currently, the API is open for demonstration purposes. In production, implement API key authentication:

```python
headers = {
    'Authorization': 'Bearer YOUR_API_KEY'
}
```

---

## Endpoints

### Health Check

#### GET `/health`

Check API health status and model availability.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-28T10:30:00",
  "models_loaded": {
    "risk_model": true,
    "sentiment_analyzer": true,
    "portfolio_optimizer": true
  },
  "version": "1.0.0"
}
```

---

### Risk Prediction

#### POST `/api/v1/predict/risk`

Predict financial risk level for a company based on financial metrics.

**Request Body:**
```json
{
  "company_id": 1,
  "revenue": 50000000,
  "cogs": 30000000,
  "net_income": 5000000,
  "total_assets": 100000000,
  "total_debt": 30000000,
  "total_equity": 70000000,
  "current_assets": 40000000,
  "current_liabilities": 20000000,
  "cash": 15000000,
  "inventory": 5000000
}
```

**Response:**
```json
{
  "risk_level": "Medium",
  "confidence": 0.87,
  "probabilities": {
    "Low": 0.15,
    "Medium": 0.72,
    "High": 0.13
  },
  "timestamp": "2024-10-28T10:30:00"
}
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/api/v1/predict/risk"
data = {
    "company_id": 1,
    "revenue": 50000000,
    "cogs": 30000000,
    "net_income": 5000000,
    "total_assets": 100000000,
    "total_debt": 30000000,
    "total_equity": 70000000,
    "current_assets": 40000000,
    "current_liabilities": 20000000,
    "cash": 15000000,
    "inventory": 5000000
}

response = requests.post(url, json=data)
print(response.json())
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/predict/risk" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "revenue": 50000000,
    "net_income": 5000000,
    ...
  }'
```

---

### Sentiment Analysis

#### POST `/api/v1/analyze/sentiment`

Analyze sentiment of financial text using FinBERT and advanced NLP.

**Request Body:**
```json
{
  "text": "The company reported strong quarterly earnings with revenue growth of 25% year-over-year.",
  "extract_entities": true
}
```

**Response:**
```json
{
  "sentiment_label": "positive",
  "sentiment_score": 0.95,
  "compound_score": 0.78,
  "entities": {
    "organizations": [],
    "people": [],
    "money": [],
    "dates": [],
    "percentages": ["25%"]
  },
  "timestamp": "2024-10-28T10:30:00"
}
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/api/v1/analyze/sentiment"
data = {
    "text": "Apple reported record quarterly earnings exceeding analyst expectations.",
    "extract_entities": True
}

response = requests.post(url, json=data)
result = response.json()
print(f"Sentiment: {result['sentiment_label']}")
print(f"Score: {result['compound_score']}")
```

---

### Portfolio Optimization

#### POST `/api/v1/optimize/portfolio`

Optimize portfolio allocation using modern portfolio theory.

**Request Body:**
```json
{
  "assets": ["AAPL", "GOOGL", "MSFT"],
  "returns_data": [
    [0.001, 0.002, -0.001],
    [0.002, 0.001, 0.003],
    [-0.001, 0.0015, 0.002]
  ],
  "optimization_method": "max_sharpe"
}
```

**Optimization Methods:**
- `max_sharpe`: Maximum Sharpe Ratio
- `min_volatility`: Minimum Volatility
- `risk_parity`: Equal Risk Contribution

**Response:**
```json
{
  "weights": {
    "AAPL": 0.35,
    "GOOGL": 0.40,
    "MSFT": 0.25
  },
  "expected_return": 0.125,
  "volatility": 0.18,
  "sharpe_ratio": 0.58,
  "timestamp": "2024-10-28T10:30:00"
}
```

**Example (Python):**
```python
import requests
import numpy as np

url = "http://localhost:8000/api/v1/optimize/portfolio"

# Generate sample returns
returns = np.random.normal(0.001, 0.02, (100, 3)).tolist()

data = {
    "assets": ["AAPL", "GOOGL", "MSFT"],
    "returns_data": returns,
    "optimization_method": "max_sharpe"
}

response = requests.post(url, json=data)
result = response.json()
print(f"Optimal Weights: {result['weights']}")
print(f"Expected Return: {result['expected_return']:.2%}")
print(f"Sharpe Ratio: {result['sharpe_ratio']:.3f}")
```

---

### Batch Sentiment Analysis

#### POST `/api/v1/batch/sentiment`

Analyze sentiment for multiple texts in a single request.

**Request Body:**
```json
[
  "Stock prices surged on positive earnings reports.",
  "Company faces regulatory challenges ahead.",
  "New product launch exceeded expectations."
]
```

**Response:**
```json
{
  "total_texts": 3,
  "results": [
    {
      "text": "Stock prices surged on positive earnings...",
      "finbert_label": "positive",
      "compound_score": 0.82
    },
    ...
  ],
  "summary": {
    "average_compound_score": 0.45,
    "positive_count": 2,
    "negative_count": 1,
    "neutral_count": 0
  },
  "timestamp": "2024-10-28T10:30:00"
}
```

**Limits:**
- Maximum 100 texts per batch

---

### Model Information

#### GET `/api/v1/models/info`

Get information about loaded models, including metadata and performance metrics.

**Response:**
```json
{
  "risk_predictor": {
    "loaded": true,
    "features": ["debt_to_equity", "current_ratio", "profit_margin", ...],
    "metrics": {
      "train_accuracy": 0.92,
      "test_accuracy": 0.87,
      "trained_at": "2024-10-28T08:00:00"
    }
  },
  "sentiment_analyzer": {
    "loaded": true,
    "model": "ProsusAI/finbert"
  },
  "portfolio_optimizer": {
    "loaded": true,
    "risk_free_rate": 0.02
  }
}
```

---

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable (model not loaded)

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently not implemented. In production, consider:
- 1000 requests per hour per IP
- 100 requests per minute per endpoint

---

## Best Practices

1. **Batch Processing**: Use batch endpoints when analyzing multiple items
2. **Caching**: Cache results for frequently requested data
3. **Error Handling**: Always implement proper error handling
4. **Timeouts**: Set reasonable timeouts for API calls
5. **Validation**: Validate input data before sending requests

---

## Example: Complete Workflow

```python
import requests
import pandas as pd

BASE_URL = "http://localhost:8000"

# 1. Check API health
health = requests.get(f"{BASE_URL}/health").json()
print(f"API Status: {health['status']}")

# 2. Predict risk for a company
risk_data = {
    "company_id": 1,
    "revenue": 50000000,
    "net_income": 5000000,
    # ... other financials
}
risk_result = requests.post(
    f"{BASE_URL}/api/v1/predict/risk",
    json=risk_data
).json()
print(f"Risk Level: {risk_result['risk_level']}")

# 3. Analyze sentiment of news
news_text = "Company reports record-breaking quarterly revenue."
sentiment_result = requests.post(
    f"{BASE_URL}/api/v1/analyze/sentiment",
    json={"text": news_text, "extract_entities": True}
).json()
print(f"Sentiment: {sentiment_result['sentiment_label']}")

# 4. Optimize portfolio
portfolio_data = {
    "assets": ["AAPL", "GOOGL", "MSFT"],
    "returns_data": [[0.001, 0.002, -0.001]] * 100,
    "optimization_method": "max_sharpe"
}
opt_result = requests.post(
    f"{BASE_URL}/api/v1/optimize/portfolio",
    json=portfolio_data
).json()
print(f"Optimal Weights: {opt_result['weights']}")
```

---

## Support

For issues or questions:
- Check the interactive documentation at `/docs`
- Review error messages for debugging
- Consult the project README for setup instructions
