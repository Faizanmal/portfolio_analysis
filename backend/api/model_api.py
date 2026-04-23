"""
FastAPI Model Serving API

REST API for serving ML models and providing prediction endpoints.

Features:
- Risk prediction endpoint
- Sentiment analysis endpoint
- Portfolio optimization endpoint
- Model metadata and health checks
- API documentation (Swagger/OpenAPI)
- Mobile PWA support
- Social Trading platform
- Predictive Analytics
- Real-time Collaboration
- Conversational AI Assistant
- Personalized Learning
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger
import pandas as pd

from models.risk_predictor import RiskPredictor
from models.sentiment_analyzer import SentimentAnalyzer
from models.portfolio_optimizer import PortfolioOptimizer


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    models_loaded: Optional[Dict[str, bool]] = None
    version: Optional[str] = None

# Import new feature modules
try:
    from mobile.pwa_app import MobileAPIService
except ImportError:
    MobileAPIService = None

try:
    from social.social_trading import SocialTradingPlatform
except ImportError:
    SocialTradingPlatform = None

try:
    from analytics.predictive_analytics import PredictiveAnalyticsPlatform
except ImportError:
    PredictiveAnalyticsPlatform = None

try:
    from collaboration.real_time_collaboration import CollaborationPlatform
except ImportError:
    CollaborationPlatform = None

try:
    from assistant.conversational_ai import ConversationalAI
except ImportError:
    ConversationalAI = None

try:
    from learning.personalized_learning import PersonalizedLearningPlatform
except ImportError:
    PersonalizedLearningPlatform = None


# Initialize FastAPI app
app = FastAPI(
    title="AI Portfolio Analysis API",
    description="""REST API for AI-powered portfolio analysis and predictions.
    
## Features
- 📊 Risk Prediction & Portfolio Optimization
- 📱 Mobile PWA Support
- 👥 Social Trading Platform
- 📈 Predictive Analytics
- 🤝 Real-time Collaboration
- 🤖 Conversational AI Assistant
- 📚 Personalized Learning
    """,
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
risk_model = None
sentiment_analyzer = None
portfolio_optimizer = None

# New feature platform instances
mobile_service = None
social_platform = None
analytics_platform = None
collaboration_platform = None
ai_assistant = None
learning_platform = None


# Pydantic models for request/response
class CompanyFinancials(BaseModel):
    """Financial data for risk prediction."""
    company_id: int
    revenue: float
    cogs: float
    net_income: float
    total_assets: float
    total_debt: float
    total_equity: float
    current_assets: float
    current_liabilities: float
    cash: float
    inventory: float
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class RiskPredictionResponse(BaseModel):
    """Risk prediction response."""
    risk_level: str
    confidence: float
    probabilities: Dict[str, float]
    timestamp: str


class SentimentRequest(BaseModel):
    """Sentiment analysis request."""
    text: str = Field(..., min_length=10, max_length=5000)
    extract_entities: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The company reported strong quarterly earnings with revenue growth of 25% year-over-year.",
                "extract_entities": True
            }
        }


class SentimentResponse(BaseModel):
    """Sentiment analysis response."""
    sentiment_label: str
    sentiment_score: float
    compound_score: float
    entities: Optional[Dict] = None
    timestamp: str


class PortfolioRequest(BaseModel):
    """Portfolio optimization request."""
    assets: List[str]
    returns_data: List[List[float]]
    optimization_method: str = Field(default="max_sharpe", pattern="^(max_sharpe|min_volatility|risk_parity)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "assets": ["AAPL", "GOOGL", "MSFT"],
                "returns_data": [[0.001, 0.002, -0.001], [0.002, 0.001, 0.003]],
                "optimization_method": "max_sharpe"
            }
        }


class PortfolioResponse(BaseModel):
    """Portfolio optimization response."""
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    timestamp: str


logger.info("Loading models...")

try:
    # Load risk prediction model
    risk_model = RiskPredictor()
    model_path = Path("data/models/risk_predictor.pkl")
    if model_path.exists():
        risk_model.load_model()
        logger.info("Risk model loaded successfully")
    else:
        logger.warning("Risk model not found, will need to train first")

    # Load sentiment analyzer
    sentiment_analyzer = SentimentAnalyzer()
    logger.info("Sentiment analyzer loaded successfully")

    # Initialize portfolio optimizer
    portfolio_optimizer = PortfolioOptimizer()
    logger.info("Portfolio optimizer initialized")

    logger.info("All models loaded successfully")

except Exception as e:
    logger.error(f"Error loading models: {str(e)}")

# Initialize new feature platforms
platform_config = {}

try:
    if MobileAPIService:
        mobile_service = MobileAPIService(platform_config)
        app.include_router(mobile_service.get_api_routes())
        logger.info("Mobile PWA service initialized")
except Exception as e:
    logger.warning(f"Mobile service not available: {e}")

try:
    if SocialTradingPlatform:
        social_platform = SocialTradingPlatform(platform_config)
        app.include_router(social_platform.get_api_routes())
        logger.info("Social trading platform initialized")
except Exception as e:
    logger.warning(f"Social platform not available: {e}")

try:
    if PredictiveAnalyticsPlatform:
        analytics_platform = PredictiveAnalyticsPlatform(platform_config)
        app.include_router(analytics_platform.get_api_routes())
        logger.info("Predictive analytics platform initialized")
except Exception as e:
    logger.warning(f"Analytics platform not available: {e}")

try:
    if CollaborationPlatform:
        collaboration_platform = CollaborationPlatform(platform_config)
        app.include_router(collaboration_platform.get_api_routes())
        logger.info("Collaboration platform initialized")
except Exception as e:
    logger.warning(f"Collaboration platform not available: {e}")

try:
    if ConversationalAI:
        ai_assistant = ConversationalAI(platform_config)
        app.include_router(ai_assistant.get_api_routes())
        logger.info("Conversational AI assistant initialized")
except Exception as e:
    logger.warning(f"AI assistant not available: {e}")

try:
    if PersonalizedLearningPlatform:
        learning_platform = PersonalizedLearningPlatform(platform_config)
        app.include_router(learning_platform.get_api_routes())
        logger.info("Learning platform initialized")
except Exception as e:
    logger.warning(f"Learning platform not available: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down API server...")


# API Endpoints

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "message": "AI Portfolio Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        models_loaded={
            "risk_model": risk_model is not None and risk_model.model is not None,
            "sentiment_analyzer": sentiment_analyzer is not None,
            "portfolio_optimizer": portfolio_optimizer is not None
        },
        version="2.0.0"
    )


@app.get("/api/v1/features", tags=["Health"])
async def list_features():
    """List all available feature modules."""
    return {
        "features": {
            "core_models": {
                "risk_predictor": risk_model is not None,
                "sentiment_analyzer": sentiment_analyzer is not None,
                "portfolio_optimizer": portfolio_optimizer is not None
            },
            "mobile_pwa": mobile_service is not None,
            "social_trading": social_platform is not None,
            "predictive_analytics": analytics_platform is not None,
            "collaboration": collaboration_platform is not None,
            "ai_assistant": ai_assistant is not None,
            "learning_platform": learning_platform is not None
        },
        "api_routes": [route.path for route in app.routes],
        "version": "2.0.0"
    }


@app.post("/api/v1/predict/risk", response_model=RiskPredictionResponse, tags=["Predictions"])
async def predict_risk(financials: CompanyFinancials):
    """
    Predict financial risk level for a company.
    
    Returns risk classification (Low, Medium, High) with confidence scores.
    """
    if risk_model is None or risk_model.model is None:
        raise HTTPException(status_code=503, detail="Risk model not available")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame([financials.dict()])
        
        # Get predictions
        prediction = risk_model.predict(df)[0]
        probabilities = risk_model.predict_proba(df)[0]
        
        # Get probability for each class
        classes = risk_model.model.classes_
        prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
        
        # Get confidence for predicted class
        confidence = float(max(probabilities))
        
        return RiskPredictionResponse(
            risk_level=prediction,
            confidence=confidence,
            probabilities=prob_dict,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Risk prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/api/v1/analyze/sentiment", response_model=SentimentResponse, tags=["Analysis"])
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of financial text.
    
    Supports news articles, reports, and financial documents.
    """
    if sentiment_analyzer is None:
        raise HTTPException(status_code=503, detail="Sentiment analyzer not available")
    
    try:
        # Analyze sentiment
        sentiment = sentiment_analyzer.analyze_sentiment(request.text)
        
        # Extract entities if requested
        entities = None
        if request.extract_entities:
            entities = sentiment_analyzer.extract_entities(request.text)
        
        return SentimentResponse(
            sentiment_label=sentiment['finbert_label'],
            sentiment_score=sentiment['finbert_score'],
            compound_score=sentiment['compound_score'],
            entities=entities,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/v1/optimize/portfolio", response_model=PortfolioResponse, tags=["Optimization"])
async def optimize_portfolio(request: PortfolioRequest):
    """
    Optimize portfolio allocation.
    
    Supports multiple optimization methods:
    - max_sharpe: Maximum Sharpe ratio
    - min_volatility: Minimum volatility
    - risk_parity: Equal risk contribution
    """
    if portfolio_optimizer is None:
        raise HTTPException(status_code=503, detail="Portfolio optimizer not available")
    
    try:
        # Convert returns data to DataFrame
        returns_df = pd.DataFrame(request.returns_data, columns=request.assets)
        
        # Load data into optimizer
        portfolio_optimizer.load_data(returns_df)
        
        # Optimize based on method
        if request.optimization_method == "max_sharpe":
            result = portfolio_optimizer.optimize_max_sharpe()
        elif request.optimization_method == "min_volatility":
            result = portfolio_optimizer.optimize_min_volatility()
        elif request.optimization_method == "risk_parity":
            result = portfolio_optimizer.risk_parity_optimization()
        else:
            raise ValueError(f"Unknown optimization method: {request.optimization_method}")
        
        if not result['success']:
            raise HTTPException(status_code=400, detail="Optimization failed to converge")
        
        return PortfolioResponse(
            weights=result['weights'],
            expected_return=result['metrics']['return'],
            volatility=result['metrics']['volatility'],
            sharpe_ratio=result['metrics']['sharpe_ratio'],
            timestamp=datetime.now().isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Portfolio optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/api/v1/models/info", tags=["Models"])
async def get_models_info():
    """
    Get information about loaded models.
    
    Returns model metadata, performance metrics, and feature information.
    """
    models_info = {}
    
    # Risk model info
    if risk_model and risk_model.model:
        models_info['risk_predictor'] = {
            'loaded': True,
            'features': risk_model.feature_names,
            'metrics': risk_model.metrics
        }
    else:
        models_info['risk_predictor'] = {'loaded': False}
    
    # Sentiment analyzer info
    if sentiment_analyzer:
        models_info['sentiment_analyzer'] = {
            'loaded': True,
            'model': sentiment_analyzer.model_name
        }
    else:
        models_info['sentiment_analyzer'] = {'loaded': False}
    
    # Portfolio optimizer info
    if portfolio_optimizer:
        models_info['portfolio_optimizer'] = {
            'loaded': True,
            'risk_free_rate': portfolio_optimizer.risk_free_rate
        }
    else:
        models_info['portfolio_optimizer'] = {'loaded': False}
    
    return models_info


@app.post("/api/v1/batch/sentiment", tags=["Batch Processing"])
async def batch_sentiment_analysis(texts: List[str], background_tasks: BackgroundTasks):
    """
    Batch sentiment analysis for multiple texts.
    
    Processes multiple texts and returns aggregated results.
    """
    if sentiment_analyzer is None:
        raise HTTPException(status_code=503, detail="Sentiment analyzer not available")
    
    if len(texts) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 texts per batch")
    
    try:
        # Analyze batch
        results_df = sentiment_analyzer.analyze_batch(texts, batch_size=8)
        
        # Convert to dict
        results = results_df.to_dict('records')
        
        return {
            "total_texts": len(texts),
            "results": results,
            "summary": {
                "average_compound_score": float(results_df['compound_score'].mean()),
                "positive_count": int((results_df['finbert_label'] == 'positive').sum()),
                "negative_count": int((results_df['finbert_label'] == 'negative').sum()),
                "neutral_count": int((results_df['finbert_label'] == 'neutral').sum())
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch sentiment analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Configure logging
    logger.add("logs/api.log", rotation="10 MB")
    
    # Run server
    logger.info("Starting API server...")
    uvicorn.run(
        "model_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
