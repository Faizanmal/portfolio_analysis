# Quick Start Guide

## Get Up and Running in 5 Minutes

This guide will help you quickly set up and run the AI Portfolio Analysis Platform.

---

## Step 1: Installation (2 minutes)

Open PowerShell and run:

```powershell
# Navigate to project directory
cd "e:\Machine Learning Models\New folder"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

---

## Step 2: Train Models (2 minutes)

```powershell
# Train the risk prediction model
python models\risk_predictor.py

# This will:
# - Generate sample data
# - Train the model
# - Save the model to data/models/
# - Display performance metrics
```

Expected output:
```
Training accuracy: 0.9200
Testing accuracy: 0.8700
Model saved to data\models\risk_predictor.pkl
```

---

## Step 3: Choose Your Interface (1 minute)

### Option A: Interactive Dashboard (Recommended for beginners)

```powershell
streamlit run dashboard\app.py
```

The dashboard will open in your browser at `http://localhost:8501`

**Features:**
- 📊 Portfolio overview
- 🎯 Risk prediction interface
- 💭 Sentiment analysis
- ⚖️ Portfolio optimization
- 📄 Document analysis

### Option B: REST API (For developers)

```powershell
uvicorn api.model_api:app --reload
```

Access:
- API: `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`

**Test the API:**
```powershell
# In a new PowerShell window
curl http://localhost:8000/health
```

---

## Step 4: Try It Out!

### Using the Dashboard

1. **Navigate to Risk Prediction**
   - Enter sample financial data
   - Click "Predict Risk"
   - View results

2. **Try Sentiment Analysis**
   - Paste: "Company reports record-breaking revenue growth of 35%"
   - Click "Analyze Sentiment"
   - See sentiment score and entities

3. **Optimize a Portfolio**
   - Use sample data
   - Select "Maximum Sharpe Ratio"
   - Click "Optimize Portfolio"

### Using the API

**Python example:**
```python
import requests

# Test risk prediction
response = requests.post(
    'http://localhost:8000/api/v1/predict/risk',
    json={
        'company_id': 1,
        'revenue': 50000000,
        'cogs': 30000000,
        'net_income': 5000000,
        'total_assets': 100000000,
        'total_debt': 30000000,
        'total_equity': 70000000,
        'current_assets': 40000000,
        'current_liabilities': 20000000,
        'cash': 15000000,
        'inventory': 5000000
    }
)

print(response.json())
```

---

## Optional: Enable Advanced Features

### OpenAI Integration (for document analysis)

1. Get an API key from [OpenAI](https://platform.openai.com/)

2. Create `.env` file:
   ```powershell
   cp .env.example .env
   ```

3. Edit `.env` and add your key:
   ```
   OPENAI_API_KEY=your_key_here
   ```

4. Restart the application

Now you can use:
- Advanced document summarization
- Q&A on documents
- Investment memo generation

---

## Common Quick Start Issues

### "ModuleNotFoundError"
**Solution:** Make sure virtual environment is activated:
```powershell
.\venv\Scripts\activate
```

### "spaCy model not found"
**Solution:** Download the model:
```powershell
python -m spacy download en_core_web_sm
```

### Dashboard won't start
**Solution:** Check if port 8501 is available:
```powershell
netstat -ano | findstr :8501
```

### Models not loading
**Solution:** Train the models first:
```powershell
python models\risk_predictor.py
```

---

## Quick Command Reference

```powershell
# Activate environment
.\venv\Scripts\activate

# Run dashboard
streamlit run dashboard\app.py

# Run API
uvicorn api.model_api:app --reload

# Run data pipeline
python automation\data_pipeline.py

# Generate report
python automation\report_generator.py

# Train models
python models\risk_predictor.py
python models\sentiment_analyzer.py

# Start scheduler
python automation\scheduler.py
```

---

## Next Steps

✅ **You're all set!** Here's what to explore next:

1. **Read the User Guide** → `docs/USER_GUIDE.md`
   - Learn all features in detail
   - Customize for your needs

2. **Explore the API** → `docs/API_DOCUMENTATION.md`
   - Integrate with your applications
   - Build custom workflows

3. **Run Automation** → `automation/scheduler.py`
   - Schedule automated tasks
   - Generate reports automatically

4. **Customize Models** → `models/`
   - Train with your own data
   - Adjust parameters

5. **Deploy to Production** → `docs/DEPLOYMENT_GUIDE.md`
   - Docker deployment
   - Cloud deployment

---

## Getting Help

**Check these resources:**
- 📖 Full documentation in `docs/` folder
- 🔍 Search logs in `logs/` folder
- 💡 Review example notebooks in `notebooks/`
- 🌐 Visit API docs at `http://localhost:8000/docs`

**Still stuck?**
- Review error messages in terminal
- Check log files for details
- Verify all dependencies are installed
- Ensure Python version is 3.9+

---

## Quick Demo Script

Run this complete workflow:

```powershell
# 1. Setup
python models\risk_predictor.py

# 2. Start dashboard (in new terminal)
streamlit run dashboard\app.py

# 3. Start API (in another terminal)
uvicorn api.model_api:app --reload

# 4. Run data pipeline
python automation\data_pipeline.py

# 5. Generate report
python automation\report_generator.py
```

Now you have:
✓ Trained models
✓ Interactive dashboard running
✓ REST API running
✓ Sample data processed
✓ Report generated

---

**Congratulations! You're ready to use the AI Portfolio Analysis Platform! 🎉**

For detailed information, see the complete documentation in the `docs/` folder.
