# User Guide

## AI-Powered Portfolio Analysis Platform

Welcome to the comprehensive user guide for the AI-Powered Portfolio Analysis Platform. This guide will help you get started and make the most of all features.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Usage](#dashboard-usage)
3. [Model Training](#model-training)
4. [Automation Setup](#automation-setup)
5. [API Integration](#api-integration)
6. [Document Analysis](#document-analysis)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection for API integrations

### Installation

1. **Navigate to the project directory:**
   ```powershell
   cd "e:\Machine Learning Models\New folder"
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Download spaCy model:**
   ```powershell
   python -m spacy download en_core_web_sm
   ```

5. **Configure environment variables:**
   ```powershell
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
   - `ALPHA_VANTAGE_API_KEY`: For financial data (optional)

### First Run

**Train the risk prediction model:**
```powershell
python models/risk_predictor.py
```

**Start the dashboard:**
```powershell
streamlit run dashboard/app.py
```

Access the dashboard at: `http://localhost:8501`

---

## Dashboard Usage

### Overview Page

The overview page provides a high-level summary of your portfolio:

- **Key Metrics**: Total value, returns, active investments, risk level
- **Performance Chart**: Historical portfolio value
- **Asset Allocation**: Pie chart showing distribution
- **Risk Distribution**: Bar chart of companies by risk level

**Tips:**
- Refresh data by reloading the page
- Use filters to focus on specific time periods
- Export charts as images for presentations

### Risk Prediction

Predict financial risk for companies:

1. Navigate to "🎯 Risk Prediction"
2. Enter financial data:
   - Revenue, costs, income
   - Assets, debt, equity
   - Cash and inventory
3. Click "🔍 Predict Risk"
4. Review results:
   - Risk level (Low/Medium/High)
   - Confidence scores
   - Probability distribution

**Use Cases:**
- Due diligence for new investments
- Monitoring existing portfolio companies
- Quarterly risk assessments

### Sentiment Analysis

Analyze sentiment of financial text:

1. Navigate to "💭 Sentiment Analysis"
2. Paste text (news articles, reports, etc.)
3. Enable entity extraction if needed
4. Click "🔍 Analyze Sentiment"
5. Review:
   - Sentiment label and score
   - Compound sentiment score
   - Extracted entities (companies, people, amounts)

**Best Practices:**
- Use recent news for real-time sentiment
- Combine multiple sources for better accuracy
- Track sentiment trends over time

### Portfolio Optimization

Optimize asset allocation:

1. Navigate to "⚖️ Portfolio Optimization"
2. Choose data source:
   - Use sample data for testing
   - Upload CSV with returns data
3. Select optimization method:
   - **Maximum Sharpe Ratio**: Best risk-adjusted returns
   - **Minimum Volatility**: Lowest risk
   - **Risk Parity**: Equal risk contribution
4. Click "🎯 Optimize Portfolio"
5. Review:
   - Optimal weights
   - Expected return and volatility
   - Sharpe ratio

**CSV Format:**
```csv
Asset_1,Asset_2,Asset_3
0.001,0.002,-0.001
0.002,0.001,0.003
-0.001,0.0015,0.002
```

### Document Analysis

Analyze financial documents with AI:

1. Navigate to "📄 Document Analysis"
2. Upload document (PDF, DOCX, TXT)
3. Click "🔍 Analyze Document"
4. Review:
   - Document summary
   - Extracted financial metrics
   - Ask questions about the document

**Supported Documents:**
- Annual reports
- Quarterly earnings reports
- Investment memorandums
- Due diligence documents

---

## Model Training

### Risk Prediction Model

**Train from scratch:**
```python
from models.risk_predictor import RiskPredictor
import pandas as pd

# Load your data
df = pd.read_csv('your_financial_data.csv')

# Train model
predictor = RiskPredictor()
metrics = predictor.train(df, optimize=True)

# Save model
predictor.save_model()

print(f"Test Accuracy: {metrics['test_accuracy']:.2%}")
```

**Data Format:**

Required columns:
- `company_id`: Unique identifier
- `revenue`: Company revenue
- `cogs`: Cost of goods sold
- `net_income`: Net income
- `total_assets`: Total assets
- `total_debt`: Total debt
- `total_equity`: Total equity
- `current_assets`: Current assets
- `current_liabilities`: Current liabilities
- `cash`: Cash and equivalents
- `inventory`: Inventory value
- `risk_level`: Target (Low/Medium/High)

### Sentiment Analyzer

The sentiment analyzer uses pre-trained models and doesn't require training. However, you can fine-tune:

```python
from models.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyze single text
result = analyzer.analyze_sentiment("Your text here")

# Batch analysis
import pandas as pd
news_df = pd.read_csv('news_data.csv')
analyzed = analyzer.analyze_news_feed(news_df, text_column='article_text')
```

---

## Automation Setup

### Data Pipeline

The automated data pipeline extracts, transforms, and loads data:

**Run manually:**
```python
from automation.data_pipeline import DataPipeline, create_pipeline_config

pipeline = DataPipeline(data_dir="data")
config = create_pipeline_config()

# Customize config
config['tickers'] = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
config['period'] = '1y'

results = pipeline.run_full_pipeline(config)
```

**Schedule automatic runs:**
```python
from automation.scheduler import AutomationScheduler

scheduler = AutomationScheduler()
scheduler.setup_default_schedule()
scheduler.start()

# Runs automatically:
# - Daily data pipeline at 6 AM
# - Weekly reports on Mondays at 8 AM
# - Monthly model retraining on 1st at 2 AM
```

### Report Generation

**Generate reports programmatically:**
```python
from automation.report_generator import ReportGenerator

generator = ReportGenerator(output_dir="reports")

# Prepare report data
data = {
    'title': 'Q4 2024 Portfolio Report',
    'period': 'Q4 2024',
    'portfolio_data': portfolio_df,
    'summary_data': summary_dict,
    'analysis_data': analysis_dict
}

report_path = generator.generate_complete_report(data)
print(f"Report saved to: {report_path}")
```

**Schedule automatic reports:**
Reports are automatically generated weekly when the scheduler is running.

---

## API Integration

### Starting the API Server

```powershell
# Development mode (with auto-reload)
uvicorn api.model_api:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn api.model_api:app --host 0.0.0.0 --port 8000 --workers 4
```

Access:
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Using the API

See [API Documentation](API_DOCUMENTATION.md) for detailed endpoint information.

**Quick Example:**
```python
import requests

# Predict risk
response = requests.post(
    'http://localhost:8000/api/v1/predict/risk',
    json={
        'company_id': 1,
        'revenue': 50000000,
        'net_income': 5000000,
        # ... other fields
    }
)

risk_result = response.json()
print(f"Risk Level: {risk_result['risk_level']}")
```

---

## Document Analysis

### Using the Document Analyzer

**Analyze a single document:**
```python
from nlp.document_analyzer import DocumentAnalyzer

analyzer = DocumentAnalyzer()

# Load and analyze
results = analyzer.analyze_document_complete('path/to/document.pdf')

# Access results
print(results['summary'])
print(results['financial_metrics'])
print(results['due_diligence'])
```

**Batch processing:**
```python
file_paths = [
    'reports/company1.pdf',
    'reports/company2.pdf',
    'reports/company3.pdf'
]

results = analyzer.batch_analyze_documents(file_paths)

for result in results:
    print(f"{result['file_name']}: {result['summary'][:100]}...")
```

### Question Answering

Ask questions about documents:
```python
text = analyzer.load_document('report.pdf')

questions = [
    "What was the company's revenue?",
    "What are the main risk factors?",
    "What is the growth strategy?"
]

for question in questions:
    answer = analyzer.answer_question(text, question)
    print(f"Q: {question}")
    print(f"A: {answer}\n")
```

---

## Troubleshooting

### Common Issues

**1. Models not loading**
- Ensure models are trained: `python models/risk_predictor.py`
- Check file exists: `data/models/risk_predictor.pkl`
- Review logs: `logs/risk_predictor.log`

**2. API returns 503 errors**
- Models may not be loaded
- Restart the API server
- Check logs: `logs/api.log`

**3. Dashboard shows errors**
- Verify all dependencies installed
- Check Python version (3.9+)
- Clear Streamlit cache: Settings → Clear Cache

**4. Sentiment analysis fails**
- Download spaCy model: `python -m spacy download en_core_web_sm`
- Check internet connection (for FinBERT download)
- Review logs: `logs/sentiment_analyzer.log`

**5. OpenAI features not working**
- Set `OPENAI_API_KEY` in `.env`
- Check API key validity
- Verify internet connection

### Performance Optimization

**1. Speed up model predictions:**
- Use batch prediction for multiple items
- Cache frequently used predictions
- Consider GPU acceleration (install `tensorflow-gpu`)

**2. Reduce memory usage:**
- Process documents in chunks
- Clear cache regularly
- Use smaller batch sizes

**3. Improve dashboard performance:**
- Enable caching: `@st.cache_data`
- Reduce data visualization points
- Optimize data loading

### Getting Help

**Check logs:**
- General: `logs/app.log`
- Models: `logs/risk_predictor.log`, `logs/sentiment_analyzer.log`
- API: `logs/api.log`
- Pipeline: `logs/data_pipeline.log`

**Debug mode:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Best Practices

### Data Management

1. **Regular backups**: Backup `data/` folder regularly
2. **Version control**: Track model versions
3. **Data validation**: Always validate input data
4. **Clean old files**: Use automated cleanup

### Model Management

1. **Regular retraining**: Retrain models monthly
2. **Monitor performance**: Track accuracy metrics
3. **A/B testing**: Test new models before deployment
4. **Document changes**: Keep model change log

### Security

1. **API keys**: Never commit API keys to version control
2. **Access control**: Implement authentication in production
3. **Data privacy**: Encrypt sensitive data
4. **Regular updates**: Keep dependencies updated

### Monitoring

1. **Set up alerts**: Monitor for errors and anomalies
2. **Track metrics**: Monitor model performance
3. **Log analysis**: Review logs regularly
4. **User feedback**: Collect and act on feedback

---

## Advanced Features

### Custom Model Integration

Add your own models:

```python
# models/custom_model.py
class CustomPredictor:
    def __init__(self):
        self.model = load_your_model()
    
    def predict(self, data):
        return self.model.predict(data)

# Integrate into API
from models.custom_model import CustomPredictor

custom_model = CustomPredictor()

@app.post("/api/v1/predict/custom")
async def custom_prediction(data: CustomInput):
    result = custom_model.predict(data)
    return {"prediction": result}
```

### Extending the Dashboard

Add custom pages:

```python
# dashboard/pages/custom_page.py
import streamlit as st

def show_custom_page():
    st.title("Custom Analysis")
    # Your custom code here

# dashboard/app.py
from pages.custom_page import show_custom_page

# Add to navigation
if page == "Custom":
    show_custom_page()
```

---

## Next Steps

1. **Customize**: Adapt models to your specific use case
2. **Integrate**: Connect with your existing systems
3. **Scale**: Deploy to cloud for production use
4. **Expand**: Add more features and models
5. **Monitor**: Set up monitoring and alerts

---

For more information, see:
- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Project README.md
