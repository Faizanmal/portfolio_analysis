"""
Sentiment Analysis Model for Financial News and Reports

This module implements an NLP-based sentiment analyzer for financial documents,
news articles, and company reports using transformer models and traditional NLP.

Features:
- Multi-source sentiment analysis
- Named entity recognition
- Topic modeling
- Batch processing capabilities
"""

import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from textblob import TextBlob
import spacy
from collections import Counter
from typing import List, Dict, Tuple
from pathlib import Path
from loguru import logger
import json


class SentimentAnalyzer:
    """
    Financial sentiment analysis using transformer models and NLP.
    
    Supports multiple analysis methods:
    - FinBERT for financial-specific sentiment
    - TextBlob for quick baseline analysis
    - spaCy for entity extraction
    """
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize sentiment analyzer.
        
        Args:
            model_name: HuggingFace model name for sentiment analysis
        """
        self.model_name = model_name
        self.device = 0 if torch.cuda.is_available() else -1
        
        logger.info(f"Loading sentiment model: {model_name}")
        logger.info(f"Using device: {'GPU' if self.device == 0 else 'CPU'}")
        
        # Load FinBERT model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device
        )
        
        # Load spaCy for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        self.analysis_cache = {}
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment scores and labels
        """
        # Check cache
        if text in self.analysis_cache:
            return self.analysis_cache[text]
        
        # Truncate text if too long (FinBERT max is 512 tokens)
        max_length = 512
        inputs = self.tokenizer(text, truncation=True, max_length=max_length, return_tensors="pt")
        
        # Get FinBERT sentiment
        result = self.sentiment_pipeline(text[:512])[0]
        
        # Get TextBlob sentiment for comparison
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment
        
        analysis = {
            'finbert_label': result['label'],
            'finbert_score': float(result['score']),
            'textblob_polarity': float(textblob_sentiment.polarity),
            'textblob_subjectivity': float(textblob_sentiment.subjectivity),
            'compound_score': self._calculate_compound_score(result, textblob_sentiment)
        }
        
        # Cache result
        self.analysis_cache[text] = analysis
        
        return analysis
    
    def _calculate_compound_score(self, finbert_result: Dict, textblob_sentiment) -> float:
        """
        Calculate a compound sentiment score combining multiple methods.
        
        Args:
            finbert_result: Result from FinBERT
            textblob_sentiment: TextBlob sentiment object
            
        Returns:
            Compound score between -1 and 1
        """
        # Convert FinBERT label to score
        label_to_score = {'positive': 1.0, 'neutral': 0.0, 'negative': -1.0}
        finbert_score = label_to_score.get(finbert_result['label'].lower(), 0.0)
        finbert_weighted = finbert_score * finbert_result['score']
        
        # Combine with TextBlob (70% FinBERT, 30% TextBlob)
        compound = 0.7 * finbert_weighted + 0.3 * textblob_sentiment.polarity
        
        return float(compound)
    
    def analyze_batch(self, texts: List[str], batch_size: int = 8) -> pd.DataFrame:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            batch_size: Batch size for processing
            
        Returns:
            DataFrame with sentiment analysis results
        """
        logger.info(f"Analyzing {len(texts)} texts...")
        
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                analysis = self.analyze_sentiment(text)
                analysis['text'] = text[:100] + '...' if len(text) > 100 else text
                results.append(analysis)
        
        df = pd.DataFrame(results)
        logger.info("Batch analysis complete")
        
        return df
    
    def extract_entities(self, text: str) -> Dict:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entity types and their mentions
        """
        if self.nlp is None:
            logger.warning("spaCy not available for entity extraction")
            return {}
        
        doc = self.nlp(text)
        
        entities = {
            'organizations': [],
            'people': [],
            'locations': [],
            'money': [],
            'dates': [],
            'percentages': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            elif ent.label_ == 'PERSON':
                entities['people'].append(ent.text)
            elif ent.label_ in ['GPE', 'LOC']:
                entities['locations'].append(ent.text)
            elif ent.label_ == 'MONEY':
                entities['money'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'PERCENT':
                entities['percentages'].append(ent.text)
        
        # Remove duplicates
        entities = {k: list(set(v)) for k, v in entities.items()}
        
        return entities
    
    def analyze_document(self, text: str, extract_entities: bool = True) -> Dict:
        """
        Comprehensive document analysis.
        
        Args:
            text: Full document text
            extract_entities: Whether to extract named entities
            
        Returns:
            Complete analysis results
        """
        logger.info("Analyzing document...")
        
        # Split into sentences for detailed analysis
        blob = TextBlob(text)
        sentences = [str(s) for s in blob.sentences]
        
        # Analyze sentiment for each sentence
        sentence_sentiments = []
        for sentence in sentences:
            if len(sentence.strip()) > 10:  # Skip very short sentences
                sentiment = self.analyze_sentiment(sentence)
                sentence_sentiments.append(sentiment['compound_score'])
        
        # Overall document sentiment
        overall_sentiment = self.analyze_sentiment(text)
        
        # Extract entities
        entities = self.extract_entities(text) if extract_entities else {}
        
        # Calculate statistics
        analysis = {
            'overall_sentiment': overall_sentiment,
            'sentence_count': len(sentences),
            'analyzed_sentences': len(sentence_sentiments),
            'average_sentence_sentiment': float(np.mean(sentence_sentiments)) if sentence_sentiments else 0.0,
            'sentiment_std': float(np.std(sentence_sentiments)) if sentence_sentiments else 0.0,
            'positive_sentences': sum(1 for s in sentence_sentiments if s > 0.1),
            'negative_sentences': sum(1 for s in sentence_sentiments if s < -0.1),
            'neutral_sentences': sum(1 for s in sentence_sentiments if -0.1 <= s <= 0.1),
            'entities': entities,
            'word_count': len(text.split())
        }
        
        return analysis
    
    def analyze_news_feed(self, news_df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """
        Analyze sentiment for a news feed DataFrame.
        
        Args:
            news_df: DataFrame with news articles
            text_column: Name of column containing text
            
        Returns:
            DataFrame with added sentiment columns
        """
        logger.info(f"Analyzing {len(news_df)} news articles...")
        
        results = []
        for idx, row in news_df.iterrows():
            text = row[text_column]
            sentiment = self.analyze_sentiment(text)
            results.append(sentiment)
        
        # Add sentiment columns to original dataframe
        sentiment_df = pd.DataFrame(results)
        result_df = pd.concat([news_df, sentiment_df], axis=1)
        
        logger.info("News feed analysis complete")
        return result_df
    
    def get_trending_topics(self, texts: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Extract trending topics from texts using entity extraction.
        
        Args:
            texts: List of texts to analyze
            top_n: Number of top topics to return
            
        Returns:
            List of (topic, frequency) tuples
        """
        if self.nlp is None:
            logger.warning("spaCy not available for topic extraction")
            return []
        
        all_entities = []
        for text in texts:
            entities = self.extract_entities(text)
            # Combine all entity types
            all_entities.extend(entities.get('organizations', []))
            all_entities.extend(entities.get('people', []))
        
        # Count frequencies
        counter = Counter(all_entities)
        trending = counter.most_common(top_n)
        
        return trending
    
    def save_analysis(self, analysis: Dict, output_path: str):
        """
        Save analysis results to file.
        
        Args:
            analysis: Analysis results dictionary
            output_path: Path to save results
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Analysis saved to {output_path}")


def generate_sample_news() -> pd.DataFrame:
    """Generate sample financial news for demonstration."""
    
    news_data = {
        'date': pd.date_range('2024-01-01', periods=20, freq='D'),
        'headline': [
            'Tech stocks surge on positive earnings reports',
            'Federal Reserve maintains interest rates amid inflation concerns',
            'Major bank reports significant losses in Q4',
            'Renewable energy sector sees record investments',
            'Market volatility continues as investors await policy decisions',
            'Start-up valued at $1B after successful funding round',
            'Oil prices decline amid global oversupply concerns',
            'Cryptocurrency market experiences sharp downturn',
            'Manufacturing sector shows signs of recovery',
            'Consumer confidence reaches five-year high',
            'Trade negotiations stall, impacting market sentiment',
            'Tech giant announces massive layoffs',
            'Emerging markets attract increased foreign investment',
            'Regulatory changes benefit pharmaceutical companies',
            'Housing market shows unexpected strength',
            'Retail sales exceed expectations during holiday season',
            'Energy crisis forces industrial production cuts',
            'AI startup acquisition creates new market leader',
            'Bond yields rise as inflation expectations grow',
            'Supply chain disruptions ease, boosting logistics stocks'
        ],
        'text': [
            'Major technology companies reported better-than-expected quarterly earnings, driving significant gains across the sector. Investors showed renewed confidence in tech stocks.',
            'The Federal Reserve decided to keep interest rates unchanged following their latest meeting, citing ongoing concerns about inflation levels and economic stability.',
            'One of the country\'s largest banks disclosed substantial losses in the fourth quarter, primarily due to exposure to troubled commercial real estate loans.',
            'Investment in renewable energy projects reached record levels this quarter, with solar and wind power leading the way as costs continue to decline.',
            'Stock markets experienced heightened volatility as traders positioned themselves ahead of anticipated policy announcements from central banks.',
            'A rapidly growing technology start-up achieved unicorn status after completing a $200 million Series C funding round led by prominent venture capital firms.',
            'Global oil prices fell to multi-month lows as production increases outpaced demand growth, raising concerns about profitability for energy companies.',
            'Cryptocurrency values tumbled following regulatory crackdowns and security concerns at major exchanges, wiping billions from the market.',
            'The manufacturing sector posted its strongest growth in six months, suggesting economic recovery may be gaining momentum despite headwinds.',
            'Consumer sentiment surveys indicate growing optimism about the economy, with confidence metrics reaching their highest levels in five years.',
            'International trade talks broke down without agreement, creating uncertainty for businesses reliant on global supply chains.',
            'A leading technology company announced plans to reduce its workforce by 15%, citing the need to streamline operations and reduce costs.',
            'Emerging market economies attracted record foreign direct investment as investors sought higher returns and diversification opportunities.',
            'New regulatory frameworks are expected to benefit pharmaceutical companies by streamlining approval processes for innovative treatments.',
            'The residential real estate market demonstrated surprising resilience, with sales and prices exceeding analyst expectations.',
            'Retail sector performance during the holiday shopping period surpassed forecasts, boosting optimism for consumer-facing businesses.',
            'An ongoing energy crisis forced several industrial facilities to reduce production capacity, impacting supply chains across multiple sectors.',
            'The acquisition of a cutting-edge artificial intelligence startup by an established tech company creates a new leader in the AI services market.',
            'Government bond yields climbed to multi-year highs as markets priced in higher inflation expectations and potential policy rate increases.',
            'Improvements in global supply chain efficiency boosted shares of logistics and transportation companies after months of challenges.'
        ]
    }
    
    return pd.DataFrame(news_data)


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/sentiment_analyzer.log", rotation="10 MB")
    
    # Create output directory
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    logger.info("Initializing Sentiment Analyzer...")
    analyzer = SentimentAnalyzer()
    
    # Generate sample news
    news_df = generate_sample_news()
    news_df.to_csv("data/processed/sample_news.csv", index=False)
    logger.info("Sample news generated")
    
    # Analyze news feed
    analyzed_news = analyzer.analyze_news_feed(news_df, text_column='text')
    analyzed_news.to_csv("data/processed/analyzed_news.csv", index=False)
    
    # Display results
    logger.info("\nSentiment Analysis Results:")
    logger.info(f"Average sentiment score: {analyzed_news['compound_score'].mean():.3f}")
    logger.info(f"Positive news: {(analyzed_news['finbert_label'] == 'positive').sum()}")
    logger.info(f"Negative news: {(analyzed_news['finbert_label'] == 'negative').sum()}")
    logger.info(f"Neutral news: {(analyzed_news['finbert_label'] == 'neutral').sum()}")
    
    # Analyze a single document in detail
    sample_text = news_df.iloc[0]['text']
    doc_analysis = analyzer.analyze_document(sample_text)
    
    logger.info("\nDocument Analysis Sample:")
    logger.info(f"Overall sentiment: {doc_analysis['overall_sentiment']['finbert_label']}")
    logger.info(f"Compound score: {doc_analysis['overall_sentiment']['compound_score']:.3f}")
    logger.info(f"Entities found: {doc_analysis['entities']}")
    
    # Save detailed analysis
    analyzer.save_analysis(doc_analysis, "data/processed/sample_document_analysis.json")
    
    # Get trending topics
    trending = analyzer.get_trending_topics(news_df['text'].tolist(), top_n=5)
    logger.info(f"\nTrending topics: {trending}")
