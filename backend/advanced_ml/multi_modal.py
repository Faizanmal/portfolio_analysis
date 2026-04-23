"""
Multi-Modal AI Analysis
=======================

Multi-modal AI for comprehensive analysis:
- Document processing (PDFs, filings)
- Image analysis (charts, documents)
- Audio transcription (earnings calls)
- Multi-modal fusion
"""

import numpy as np
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging


class DocumentType(Enum):
    """Types of documents"""
    SEC_FILING = "sec_filing"
    EARNINGS_REPORT = "earnings_report"
    ANNUAL_REPORT = "annual_report"
    RESEARCH_NOTE = "research_note"
    NEWS_ARTICLE = "news_article"
    PRESS_RELEASE = "press_release"
    REGULATORY = "regulatory"
    CONTRACT = "contract"


class ImageType(Enum):
    """Types of images"""
    CHART = "chart"
    TABLE = "table"
    LOGO = "logo"
    DOCUMENT_SCAN = "document_scan"
    SCREENSHOT = "screenshot"


class SentimentLevel(Enum):
    """Sentiment levels"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


@dataclass
class ExtractedEntity:
    """Entity extracted from text"""
    entity_type: str
    text: str
    confidence: float
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentAnalysis:
    """Analysis results for a document"""
    document_id: str
    document_type: DocumentType
    
    # Text analysis
    word_count: int = 0
    summary: str = ""
    key_topics: List[str] = field(default_factory=list)
    entities: List[ExtractedEntity] = field(default_factory=list)
    
    # Sentiment
    sentiment: SentimentLevel = SentimentLevel.NEUTRAL
    sentiment_score: float = 0.0
    
    # Financial metrics extracted
    financial_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Risk factors
    risk_factors: List[str] = field(default_factory=list)
    
    # Confidence
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'document_id': self.document_id,
            'document_type': self.document_type.value,
            'summary': self.summary,
            'key_topics': self.key_topics,
            'sentiment': self.sentiment.value,
            'sentiment_score': self.sentiment_score,
            'financial_metrics': self.financial_metrics,
            'risk_factors': self.risk_factors,
            'entity_count': len(self.entities)
        }


@dataclass
class ChartAnalysis:
    """Analysis results for a chart image"""
    chart_type: str  # line, bar, candlestick, pie, etc.
    title: str = ""
    
    # Extracted data
    data_points: List[Dict[str, Any]] = field(default_factory=list)
    trend: str = ""  # up, down, sideways
    
    # Pattern detection
    patterns_detected: List[str] = field(default_factory=list)
    support_levels: List[float] = field(default_factory=list)
    resistance_levels: List[float] = field(default_factory=list)
    
    confidence: float = 0.0


class DocumentProcessor:
    """
    Processes and analyzes financial documents.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("document_processor")
        
        # Financial keywords for extraction
        self.financial_patterns = {
            'revenue': r'revenue[s]?\s*(?:of|:)?\s*\$?([\d,\.]+)\s*(million|billion|M|B)?',
            'net_income': r'net\s+income\s*(?:of|:)?\s*\$?([\d,\.]+)\s*(million|billion|M|B)?',
            'eps': r'(?:earnings|EPS)\s+(?:per\s+share)?\s*(?:of|:)?\s*\$?([\d\.]+)',
            'margin': r'(?:gross|net|operating)?\s*margin[s]?\s*(?:of|:)?\s*([\d\.]+)\s*%',
            'growth': r'(?:revenue|earnings|sales)\s+growth\s*(?:of|:)?\s*([\d\.]+)\s*%'
        }
        
        # Sentiment words
        self.positive_words = {
            'growth', 'increase', 'positive', 'strong', 'exceeded', 'beat',
            'outperform', 'optimistic', 'bullish', 'upside', 'improve',
            'success', 'profitable', 'record', 'momentum', 'accelerate'
        }
        
        self.negative_words = {
            'decline', 'decrease', 'negative', 'weak', 'missed', 'below',
            'underperform', 'pessimistic', 'bearish', 'downside', 'deteriorate',
            'loss', 'challenge', 'headwind', 'slowdown', 'risk'
        }
    
    def analyze_document(
        self,
        text: str,
        document_type: DocumentType,
        document_id: str = None
    ) -> DocumentAnalysis:
        """Analyze a document"""
        document_id = document_id or f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        analysis = DocumentAnalysis(
            document_id=document_id,
            document_type=document_type,
            word_count=len(text.split())
        )
        
        # Extract financial metrics
        analysis.financial_metrics = self._extract_financial_metrics(text)
        
        # Extract entities
        analysis.entities = self._extract_entities(text)
        
        # Analyze sentiment
        sentiment_score = self._analyze_sentiment(text)
        analysis.sentiment_score = sentiment_score
        analysis.sentiment = self._score_to_sentiment(sentiment_score)
        
        # Extract topics
        analysis.key_topics = self._extract_topics(text)
        
        # Generate summary
        analysis.summary = self._generate_summary(text)
        
        # Extract risk factors
        analysis.risk_factors = self._extract_risk_factors(text)
        
        analysis.confidence = 0.85  # Placeholder
        
        self.logger.info(f"Analyzed document: {document_id}")
        return analysis
    
    def _extract_financial_metrics(self, text: str) -> Dict[str, float]:
        """Extract financial metrics from text"""
        metrics = {}
        
        for metric_name, pattern in self.financial_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    value_str = matches[0][0] if isinstance(matches[0], tuple) else matches[0]
                    value = float(value_str.replace(',', ''))
                    
                    # Handle multipliers
                    if isinstance(matches[0], tuple) and len(matches[0]) > 1:
                        multiplier = matches[0][1].lower()
                        if multiplier in ['billion', 'b']:
                            value *= 1e9
                        elif multiplier in ['million', 'm']:
                            value *= 1e6
                    
                    metrics[metric_name] = value
                except (ValueError, IndexError):
                    pass
        
        return metrics
    
    def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract named entities from text"""
        entities = []
        
        # Company names (simplified - in production use NER)
        company_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|Ltd|LLC|Company|Co)\.?)\b'
        for match in re.finditer(company_pattern, text):
            entities.append(ExtractedEntity(
                entity_type='COMPANY',
                text=match.group(1),
                confidence=0.8,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        # Ticker symbols
        ticker_pattern = r'\b([A-Z]{1,5})\b(?:\s*\((?:NYSE|NASDAQ|AMEX)\))?'
        for match in re.finditer(ticker_pattern, text):
            if len(match.group(1)) >= 2:
                entities.append(ExtractedEntity(
                    entity_type='TICKER',
                    text=match.group(1),
                    confidence=0.6,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        # Dates
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})\b'
        for match in re.finditer(date_pattern, text):
            entities.append(ExtractedEntity(
                entity_type='DATE',
                text=match.group(1),
                confidence=0.9,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        # Money amounts
        money_pattern = r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B))?'
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            entities.append(ExtractedEntity(
                entity_type='MONEY',
                text=match.group(),
                confidence=0.95,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text, returns score from -1 to 1"""
        words = text.lower().split()
        
        positive_count = sum(1 for w in words if w in self.positive_words)
        negative_count = sum(1 for w in words if w in self.negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def _score_to_sentiment(self, score: float) -> SentimentLevel:
        """Convert sentiment score to level"""
        if score > 0.3:
            return SentimentLevel.VERY_POSITIVE
        elif score > 0.1:
            return SentimentLevel.POSITIVE
        elif score > -0.1:
            return SentimentLevel.NEUTRAL
        elif score > -0.3:
            return SentimentLevel.NEGATIVE
        else:
            return SentimentLevel.VERY_NEGATIVE
    
    def _extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """Extract key topics from text"""
        # Simplified topic extraction using keyword frequency
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Filter common words
        stopwords = {'this', 'that', 'with', 'from', 'have', 'will', 'been', 'were', 'they'}
        words = [w for w in words if w not in stopwords]
        
        # Count frequencies
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        
        # Get top topics
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_words[:max_topics]]
    
    def _generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate summary of text"""
        # Simple extractive summary
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return ""
        
        # Score sentences by importance
        scored = []
        for sent in sentences:
            score = 0
            words = sent.lower().split()
            
            # Boost for financial terms
            financial_terms = ['revenue', 'earnings', 'profit', 'growth', 'market']
            score += sum(2 for w in words if w in financial_terms)
            
            # Boost for numbers
            score += len(re.findall(r'\d+', sent))
            
            scored.append((sent, score))
        
        # Get top sentences
        scored.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in scored[:max_sentences]]
        
        return '. '.join(top_sentences) + '.'
    
    def _extract_risk_factors(self, text: str) -> List[str]:
        """Extract risk factors from text"""
        risk_keywords = [
            'risk', 'uncertainty', 'challenge', 'threat', 'volatile',
            'regulatory', 'compliance', 'litigation', 'competition'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        risk_sentences = []
        
        for sent in sentences:
            if any(kw in sent.lower() for kw in risk_keywords):
                sent = sent.strip()
                if len(sent) > 20:
                    risk_sentences.append(sent[:200])  # Truncate long sentences
        
        return risk_sentences[:10]  # Max 10 risk factors


class ImageAnalyzer:
    """
    Analyzes financial images (charts, tables, documents).
    """
    
    def __init__(self):
        self.logger = logging.getLogger("image_analyzer")
    
    def analyze_chart(
        self,
        image_data: np.ndarray,
        chart_type: str = None
    ) -> ChartAnalysis:
        """Analyze a chart image"""
        # In production, use computer vision models
        # This is a placeholder implementation
        
        analysis = ChartAnalysis(
            chart_type=chart_type or 'unknown'
        )
        
        # Simulate chart analysis
        if chart_type == 'candlestick':
            analysis.patterns_detected = ['potential_breakout', 'support_test']
            analysis.trend = 'up'
            analysis.support_levels = [100.0, 95.0]
            analysis.resistance_levels = [110.0, 115.0]
        elif chart_type == 'line':
            analysis.trend = 'sideways'
            analysis.patterns_detected = ['consolidation']
        
        analysis.confidence = 0.7
        
        return analysis
    
    def extract_table_data(
        self,
        image_data: np.ndarray
    ) -> Dict[str, Any]:
        """Extract data from table image"""
        # Placeholder - in production use OCR + table detection
        return {
            'rows': [],
            'columns': [],
            'confidence': 0.0
        }
    
    def classify_image(
        self,
        image_data: np.ndarray
    ) -> Tuple[ImageType, float]:
        """Classify image type"""
        # Placeholder - in production use image classification
        return ImageType.CHART, 0.8


class AudioProcessor:
    """
    Processes audio content (earnings calls, interviews).
    """
    
    def __init__(self):
        self.logger = logging.getLogger("audio_processor")
    
    def transcribe(
        self,
        audio_path: str
    ) -> str:
        """Transcribe audio to text"""
        # Placeholder - in production use speech-to-text API
        return "Transcription placeholder"
    
    def analyze_tone(
        self,
        audio_path: str
    ) -> Dict[str, float]:
        """Analyze speaker tone/emotion"""
        # Placeholder - in production use audio analysis
        return {
            'confidence': 0.5,
            'stress': 0.3,
            'enthusiasm': 0.4
        }


class MultiModalAnalyzer:
    """
    Combines multiple modalities for comprehensive analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("multimodal_analyzer")
        self.document_processor = DocumentProcessor()
        self.image_analyzer = ImageAnalyzer()
        self.audio_processor = AudioProcessor()
    
    def analyze_earnings_release(
        self,
        press_release: str,
        financial_tables: List[np.ndarray] = None,
        earnings_call_audio: str = None
    ) -> Dict[str, Any]:
        """Comprehensive analysis of earnings release"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'modalities_analyzed': []
        }
        
        # Analyze press release
        doc_analysis = self.document_processor.analyze_document(
            press_release,
            DocumentType.EARNINGS_REPORT
        )
        results['document_analysis'] = doc_analysis.to_dict()
        results['modalities_analyzed'].append('text')
        
        # Analyze financial tables if provided
        if financial_tables:
            table_data = []
            for table in financial_tables:
                table_data.append(self.image_analyzer.extract_table_data(table))
            results['table_analysis'] = table_data
            results['modalities_analyzed'].append('image')
        
        # Analyze earnings call if provided
        if earnings_call_audio:
            transcript = self.audio_processor.transcribe(earnings_call_audio)
            tone = self.audio_processor.analyze_tone(earnings_call_audio)
            
            results['audio_analysis'] = {
                'transcript_summary': transcript[:500],
                'tone_analysis': tone
            }
            results['modalities_analyzed'].append('audio')
        
        # Fuse signals
        results['fused_analysis'] = self._fuse_signals(results)
        
        return results
    
    def _fuse_signals(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Fuse signals from multiple modalities"""
        signals = {
            'overall_sentiment': 0.0,
            'confidence': 0.0,
            'key_insights': [],
            'risk_level': 'medium'
        }
        
        weights = {'text': 0.5, 'image': 0.3, 'audio': 0.2}
        total_weight = 0
        
        # Text sentiment
        if 'document_analysis' in results:
            doc = results['document_analysis']
            signals['overall_sentiment'] += doc.get('sentiment_score', 0) * weights['text']
            total_weight += weights['text']
            signals['key_insights'].extend(doc.get('key_topics', []))
        
        # Audio tone
        if 'audio_analysis' in results:
            tone = results['audio_analysis'].get('tone_analysis', {})
            # Convert tone to sentiment-like score
            audio_sentiment = tone.get('enthusiasm', 0.5) - tone.get('stress', 0.5)
            signals['overall_sentiment'] += audio_sentiment * weights['audio']
            total_weight += weights['audio']
        
        if total_weight > 0:
            signals['overall_sentiment'] /= total_weight
        
        signals['confidence'] = total_weight / sum(weights.values())
        
        # Determine risk level
        if signals['overall_sentiment'] < -0.3:
            signals['risk_level'] = 'high'
        elif signals['overall_sentiment'] > 0.3:
            signals['risk_level'] = 'low'
        
        return signals
    
    def generate_research_report(
        self,
        company_name: str,
        documents: List[str],
        charts: List[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive research report"""
        report = {
            'company': company_name,
            'generated_at': datetime.now().isoformat(),
            'sections': {}
        }
        
        # Analyze all documents
        all_metrics = {}
        all_topics = []
        all_risks = []
        overall_sentiment = 0
        
        for i, doc in enumerate(documents):
            analysis = self.document_processor.analyze_document(
                doc,
                DocumentType.RESEARCH_NOTE,
                document_id=f"doc_{i}"
            )
            
            all_metrics.update(analysis.financial_metrics)
            all_topics.extend(analysis.key_topics)
            all_risks.extend(analysis.risk_factors)
            overall_sentiment += analysis.sentiment_score
        
        if documents:
            overall_sentiment /= len(documents)
        
        # Analyze charts
        if charts:
            chart_insights = []
            for chart in charts:
                chart_analysis = self.image_analyzer.analyze_chart(chart)
                chart_insights.append({
                    'type': chart_analysis.chart_type,
                    'trend': chart_analysis.trend,
                    'patterns': chart_analysis.patterns_detected
                })
            report['sections']['technical_analysis'] = chart_insights
        
        report['sections']['financial_metrics'] = all_metrics
        report['sections']['key_themes'] = list(set(all_topics))[:10]
        report['sections']['risk_factors'] = all_risks[:10]
        report['overall_sentiment'] = {
            'score': overall_sentiment,
            'level': self.document_processor._score_to_sentiment(overall_sentiment).value
        }
        
        return report
