"""
Conversational AI Assistant
===========================

Enterprise-grade conversational AI for portfolio analysis with:
- Natural language queries ("Should I buy more Apple stock?")
- Voice-powered portfolio reviews with spoken explanations
- Contextual recommendations based on user behavior patterns
- Educational explanations for complex financial concepts
- Multi-language support for global users

Makes complex financial data accessible to non-experts.
"""

import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging


class IntentType(Enum):
    """User intent categories"""
    # Portfolio queries
    PORTFOLIO_STATUS = "portfolio_status"
    PORTFOLIO_PERFORMANCE = "portfolio_performance"
    PORTFOLIO_ALLOCATION = "portfolio_allocation"
    PORTFOLIO_RISK = "portfolio_risk"
    
    # Stock queries
    STOCK_PRICE = "stock_price"
    STOCK_ANALYSIS = "stock_analysis"
    STOCK_NEWS = "stock_news"
    STOCK_RECOMMENDATION = "stock_recommendation"
    
    # Trading queries
    BUY_RECOMMENDATION = "buy_recommendation"
    SELL_RECOMMENDATION = "sell_recommendation"
    TRADE_EXECUTION = "trade_execution"
    TRADE_HISTORY = "trade_history"
    
    # Market queries
    MARKET_OVERVIEW = "market_overview"
    MARKET_NEWS = "market_news"
    SECTOR_ANALYSIS = "sector_analysis"
    
    # Educational
    EXPLAIN_CONCEPT = "explain_concept"
    STRATEGY_EXPLANATION = "strategy_explanation"
    RISK_EDUCATION = "risk_education"
    
    # Alerts and notifications
    SET_ALERT = "set_alert"
    CHECK_ALERTS = "check_alerts"
    MANAGE_ALERTS = "manage_alerts"
    
    # General
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"


class ResponseStyle(Enum):
    """Response styles for different user preferences"""
    CONCISE = "concise"
    DETAILED = "detailed"
    TECHNICAL = "technical"
    SIMPLE = "simple"
    EDUCATIONAL = "educational"


@dataclass
class ConversationContext:
    """Context for ongoing conversation"""
    session_id: str
    user_id: str
    language: Language = Language.ENGLISH
    response_style: ResponseStyle = ResponseStyle.DETAILED
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    # Conversation history
    messages: List[Dict[str, Any]] = field(default_factory=list)
    
    # Current context
    current_topic: Optional[str] = None
    mentioned_symbols: List[str] = field(default_factory=list)
    mentioned_concepts: List[str] = field(default_factory=list)
    
    # User preferences learned during conversation
    learned_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Intent:
    """Parsed user intent"""
    intent_type: IntentType
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""


@dataclass
class AIResponse:
    """AI assistant response"""
    response_id: str
    text: str
    spoken_text: Optional[str] = None
    intent: Optional[Intent] = None
    data: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    educational_note: Optional[str] = None
    follow_up_questions: List[str] = field(default_factory=list)
    language: Language = Language.ENGLISH
    created_at: datetime = field(default_factory=datetime.now)
    
    # For voice responses
    audio_url: Optional[str] = None
    ssml: Optional[str] = None


@dataclass
class EducationalContent:
    """Educational content for financial concepts"""
    concept_id: str
    concept_name: str
    category: str
    
    # Explanations at different levels
    simple_explanation: str
    detailed_explanation: str
    technical_explanation: str
    
    # Examples and analogies
    examples: List[str] = field(default_factory=list)
    analogies: List[str] = field(default_factory=list)
    
    # Related concepts
    related_concepts: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    
    # Multi-language support
    translations: Dict[str, Dict[str, str]] = field(default_factory=dict)


@dataclass
class UserBehaviorPattern:
    """Learned user behavior pattern"""
    user_id: str
    pattern_type: str
    frequency: int = 0
    last_occurrence: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Pattern strength (0-1)
    confidence: float = 0.0


class IntentClassifier:
    """
    Classifies user intents from natural language.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Intent patterns (regex-based, would use ML in production)
        self.intent_patterns = self._load_intent_patterns()
        
        # Entity extractors
        self.entity_extractors = self._setup_entity_extractors()
    
    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Load intent classification patterns"""
        return {
            IntentType.PORTFOLIO_STATUS: [
                r"(how('s| is)|what('s| is))?\s*(my )?(portfolio|holdings?|positions?)",
                r"show( me)? (my )?portfolio",
                r"portfolio (status|overview|summary)",
                r"what do i (own|hold|have)"
            ],
            IntentType.PORTFOLIO_PERFORMANCE: [
                r"(how is|how's) my portfolio (doing|performing)",
                r"portfolio (performance|returns?|gains?|losses?)",
                r"(am i|are we) (making|losing) money",
                r"what('s| is) my (return|gain|loss|pnl|p&l)"
            ],
            IntentType.STOCK_PRICE: [
                r"(what('s| is)|how much is) (the price of )?([\w]+)( stock)?( trading)?( at)?",
                r"([\w]+) (stock )?(price|quote|value)",
                r"current price (of|for) ([\w]+)"
            ],
            IntentType.STOCK_ANALYSIS: [
                r"(analyze|analysis)( of)? ([\w]+)",
                r"what do you think (of|about) ([\w]+)",
                r"(tell me|give me|show) (more )?(about|info|information) (on|about) ([\w]+)",
                r"([\w]+) (stock )?(analysis|outlook|prospects)"
            ],
            IntentType.BUY_RECOMMENDATION: [
                r"should i (buy|purchase|invest in|get)( more)? ([\w]+)",
                r"is ([\w]+) (a )?(good )?buy",
                r"(recommend|suggest) (something|stocks?) to buy",
                r"what should i (buy|invest in|purchase)"
            ],
            IntentType.SELL_RECOMMENDATION: [
                r"should i (sell|exit|get rid of|dump) ([\w]+)",
                r"is it time to sell ([\w]+)",
                r"should i take profits (on|in) ([\w]+)"
            ],
            IntentType.MARKET_OVERVIEW: [
                r"(how is|how's|what's happening in) the market",
                r"market (overview|summary|update|news)",
                r"how (are|is) (the )?(markets?|stocks?) (doing|today)"
            ],
            IntentType.EXPLAIN_CONCEPT: [
                r"(what is|what's|explain|define)( a| an)?( the)? ([\w\s]+)",
                r"(can you |please )?(explain|tell me about|help me understand) ([\w\s]+)",
                r"(i don't understand|what does)( the)?( term)? ([\w\s]+)( mean)?"
            ],
            IntentType.SET_ALERT: [
                r"(set|create|add) (a |an )?(price |)alert (for|on|when) ([\w]+)",
                r"alert me (when|if) ([\w]+)",
                r"notify me (when|if)"
            ],
            IntentType.PORTFOLIO_RISK: [
                r"(what('s| is)|how much) (is )?(my )?(portfolio )?risk",
                r"(am i|are we) (at |)risk",
                r"risk (analysis|assessment|level|exposure)"
            ],
            IntentType.GREETING: [
                r"^(hi|hello|hey|good morning|good afternoon|good evening)",
                r"^(what's up|howdy|greetings)"
            ],
            IntentType.HELP: [
                r"(help|assist|support)",
                r"what can you (do|help with)",
                r"(how do i|how can i)"
            ]
        }
    
    def _setup_entity_extractors(self) -> Dict[str, Callable]:
        """Setup entity extraction functions"""
        return {
            "stock_symbol": self._extract_stock_symbol,
            "number": self._extract_number,
            "percentage": self._extract_percentage,
            "date": self._extract_date,
            "financial_concept": self._extract_financial_concept
        }
    
    async def classify(self, text: str, context: Optional[ConversationContext] = None) -> Intent:
        """Classify user intent from text"""
        text_lower = text.lower().strip()
        
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        matched_groups = []
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Calculate confidence based on match quality
                    match_ratio = len(match.group()) / len(text_lower)
                    confidence = min(0.95, 0.5 + match_ratio * 0.5)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent_type
                        matched_groups = list(match.groups())
        
        # Extract entities
        entities = await self._extract_entities(text, best_intent, matched_groups)
        
        # Consider conversation context
        if context and best_confidence < 0.6:
            # Check if user is continuing previous topic
            adjusted_intent, adjusted_confidence = self._adjust_for_context(
                text, best_intent, best_confidence, context
            )
            if adjusted_confidence > best_confidence:
                best_intent = adjusted_intent
                best_confidence = adjusted_confidence
        
        return Intent(
            intent_type=best_intent,
            confidence=best_confidence,
            entities=entities,
            raw_text=text
        )
    
    async def _extract_entities(
        self,
        text: str,
        intent_type: IntentType,
        matched_groups: List[str]
    ) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {}
        
        # Extract stock symbols
        symbols = self._extract_stock_symbol(text)
        if symbols:
            entities["symbols"] = symbols
        
        # Extract numbers
        numbers = self._extract_number(text)
        if numbers:
            entities["numbers"] = numbers
        
        # Extract percentages
        percentages = self._extract_percentage(text)
        if percentages:
            entities["percentages"] = percentages
        
        # Extract dates
        dates = self._extract_date(text)
        if dates:
            entities["dates"] = dates
        
        # For explain_concept, extract the concept
        if intent_type == IntentType.EXPLAIN_CONCEPT:
            concept = self._extract_financial_concept(text)
            if concept:
                entities["concept"] = concept
        
        return entities
    
    def _extract_stock_symbol(self, text: str) -> List[str]:
        """Extract stock symbols from text"""
        # Common stock symbols
        known_symbols = {
            "apple": "AAPL", "google": "GOOGL", "amazon": "AMZN",
            "microsoft": "MSFT", "tesla": "TSLA", "nvidia": "NVDA",
            "meta": "META", "netflix": "NFLX", "amd": "AMD",
            "intel": "INTC", "disney": "DIS", "coca-cola": "KO"
        }
        
        symbols = []
        text_lower = text.lower()
        
        # Check for company names
        for name, symbol in known_symbols.items():
            if name in text_lower:
                symbols.append(symbol)
        
        # Check for ticker patterns (2-5 uppercase letters)
        ticker_pattern = r'\b([A-Z]{2,5})\b'
        matches = re.findall(ticker_pattern, text.upper())
        for match in matches:
            if match not in symbols:
                symbols.append(match)
        
        return symbols
    
    def _extract_number(self, text: str) -> List[float]:
        """Extract numbers from text"""
        numbers = []
        
        # Match various number formats
        patterns = [
            r'\$?([\d,]+\.?\d*)\s*(million|m|billion|b|thousand|k)?',
            r'([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    num_str = match[0].replace(',', '')
                    multiplier = match[1] if len(match) > 1 else ''
                else:
                    num_str = match.replace(',', '')
                    multiplier = ''
                
                try:
                    num = float(num_str)
                    if multiplier in ['million', 'm']:
                        num *= 1_000_000
                    elif multiplier in ['billion', 'b']:
                        num *= 1_000_000_000
                    elif multiplier in ['thousand', 'k']:
                        num *= 1_000
                    numbers.append(num)
                except ValueError:
                    continue
        
        return numbers
    
    def _extract_percentage(self, text: str) -> List[float]:
        """Extract percentages from text"""
        pattern = r'([\d.]+)\s*(%|percent)'
        matches = re.findall(pattern, text.lower())
        return [float(m[0]) for m in matches]
    
    def _extract_date(self, text: str) -> List[str]:
        """Extract dates from text"""
        dates = []
        
        # Relative dates
        if "today" in text.lower():
            dates.append(datetime.now().strftime("%Y-%m-%d"))
        if "yesterday" in text.lower():
            dates.append((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
        
        # Pattern matching for dates
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{2})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates
    
    def _extract_financial_concept(self, text: str) -> Optional[str]:
        """Extract financial concept to explain"""
        concepts = [
            "sharpe ratio", "beta", "alpha", "volatility", "var", "value at risk",
            "diversification", "portfolio", "hedge", "derivative", "option",
            "put", "call", "strike price", "dividend", "yield", "p/e ratio",
            "market cap", "eps", "earnings", "revenue", "profit margin",
            "rsi", "macd", "moving average", "support", "resistance",
            "bull market", "bear market", "correction", "crash"
        ]
        
        text_lower = text.lower()
        for concept in concepts:
            if concept in text_lower:
                return concept
        
        return None
    
    def _adjust_for_context(
        self,
        text: str,
        current_intent: IntentType,
        current_confidence: float,
        context: ConversationContext
    ) -> Tuple[IntentType, float]:
        """Adjust intent based on conversation context"""
        # If user mentioned symbols recently and asks follow-up
        if context.mentioned_symbols and current_intent == IntentType.UNKNOWN:
            follow_up_words = ["more", "else", "also", "what about", "and"]
            if any(word in text.lower() for word in follow_up_words):
                return IntentType.STOCK_ANALYSIS, 0.7
        
        return current_intent, current_confidence


class ResponseGenerator:
    """
    Generates natural language responses.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Response templates
        self.templates = self._load_response_templates()
        
        # Educational content
        self.educational_content = self._load_educational_content()
    
    def _load_response_templates(self) -> Dict[IntentType, Dict[ResponseStyle, str]]:
        """Load response templates for different intents and styles"""
        return {
            IntentType.PORTFOLIO_STATUS: {
                ResponseStyle.CONCISE: "Your portfolio is worth ${total_value:,.2f}, {change_direction} {change_pct:.2f}% today.",
                ResponseStyle.DETAILED: """📊 **Portfolio Summary**
                
Your portfolio is currently valued at **${total_value:,.2f}**, which is {change_direction} **{change_pct:.2f}%** ({change_direction_symbol}${change_amount:,.2f}) today.

**Top Holdings:**
{top_holdings}

**Asset Allocation:**
{allocation}

Your portfolio has {num_positions} positions across {num_sectors} sectors.""",
                ResponseStyle.SIMPLE: "You have ${total_value:,.2f} in your portfolio. It went {change_direction} {change_pct:.2f}% today."
            },
            IntentType.PORTFOLIO_PERFORMANCE: {
                ResponseStyle.CONCISE: "Portfolio return: {total_return:.2f}% all-time, {ytd_return:.2f}% YTD.",
                ResponseStyle.DETAILED: """📈 **Performance Report**

**Overall Performance:**
- Total Return: **{total_return:.2f}%**
- Year-to-Date: **{ytd_return:.2f}%**
- Monthly Return: **{monthly_return:.2f}%**

**Risk Metrics:**
- Sharpe Ratio: {sharpe_ratio:.2f}
- Max Drawdown: {max_drawdown:.2f}%
- Volatility: {volatility:.2f}%

**Benchmark Comparison:**
You're {benchmark_comparison} the S&P 500 by {benchmark_diff:.2f}%."""
            },
            IntentType.STOCK_ANALYSIS: {
                ResponseStyle.DETAILED: """📊 **{symbol} Analysis**

**Current Price:** ${price:.2f} ({change_direction}{change_pct:.2f}%)

**Technical Analysis:**
- Trend: {trend}
- RSI: {rsi:.1f} ({rsi_signal})
- 50-Day MA: ${ma_50:.2f}
- 200-Day MA: ${ma_200:.2f}

**Fundamental Analysis:**
- P/E Ratio: {pe_ratio:.1f}
- Market Cap: ${market_cap}
- Revenue Growth: {revenue_growth:.1f}%

**AI Recommendation:** {recommendation}
Confidence: {confidence:.0f}%

{additional_insight}"""
            },
            IntentType.BUY_RECOMMENDATION: {
                ResponseStyle.DETAILED: """🤔 **Should You Buy {symbol}?**

Based on my analysis, here's my assessment:

**Recommendation: {recommendation}**
Confidence: {confidence:.0f}%

**Reasons to consider:**
{pros}

**Risks to consider:**
{cons}

**Your portfolio context:**
{portfolio_context}

Remember: This is AI-generated advice. Consider consulting with a financial advisor for major investment decisions."""
            },
            IntentType.MARKET_OVERVIEW: {
                ResponseStyle.DETAILED: """🌍 **Market Overview**

**Major Indices:**
- S&P 500: {sp500_value:,.2f} ({sp500_change:+.2f}%)
- Nasdaq: {nasdaq_value:,.2f} ({nasdaq_change:+.2f}%)
- Dow Jones: {dow_value:,.2f} ({dow_change:+.2f}%)

**Market Sentiment:** {sentiment}

**Key Movers:**
{top_movers}

**Today's Headlines:**
{headlines}"""
            }
        }
    
    def _load_educational_content(self) -> Dict[str, EducationalContent]:
        """Load educational content for financial concepts"""
        return {
            "sharpe ratio": EducationalContent(
                concept_id="sharpe_ratio",
                concept_name="Sharpe Ratio",
                category="risk_metrics",
                simple_explanation="The Sharpe Ratio tells you how much extra return you're getting for the risk you're taking. A higher number means you're getting better returns for the amount of risk.",
                detailed_explanation="""The Sharpe Ratio measures risk-adjusted return. It's calculated as (Portfolio Return - Risk-Free Rate) / Portfolio Standard Deviation.

A Sharpe Ratio of 1.0 is considered good, 2.0 is very good, and 3.0 is excellent. Negative values mean you'd be better off in risk-free investments.""",
                technical_explanation="""Sharpe Ratio = (Rp - Rf) / σp

Where:
- Rp = Portfolio return
- Rf = Risk-free rate (typically Treasury yield)
- σp = Standard deviation of portfolio returns

This metric assumes returns are normally distributed, which may not hold during market stress.""",
                examples=[
                    "If your portfolio returned 12%, the risk-free rate is 2%, and your volatility is 10%, your Sharpe Ratio is (12-2)/10 = 1.0",
                    "A portfolio with higher returns but much higher volatility might have a lower Sharpe Ratio than a conservative portfolio"
                ],
                analogies=[
                    "Think of it like miles per gallon for investments - it measures how much 'return' you get per unit of 'risk fuel' you burn."
                ],
                related_concepts=["sortino ratio", "volatility", "risk-adjusted return"],
                translations={
                    "es": {
                        "simple": "El Ratio de Sharpe te dice cuánto rendimiento extra estás obteniendo por el riesgo que estás tomando."
                    }
                }
            ),
            "diversification": EducationalContent(
                concept_id="diversification",
                concept_name="Diversification",
                category="portfolio_management",
                simple_explanation="Diversification means not putting all your eggs in one basket. By spreading your investments across different assets, you reduce the risk of losing everything if one investment fails.",
                detailed_explanation="""Diversification is a risk management strategy that mixes a variety of investments within a portfolio. The rationale is that a portfolio of different kinds of investments will, on average, yield higher returns and pose a lower risk than any individual investment.

Key aspects:
- Asset class diversification (stocks, bonds, real estate)
- Geographic diversification (domestic, international)
- Sector diversification (tech, healthcare, finance)
- Time diversification (different investment periods)""",
                technical_explanation="""Diversification reduces unsystematic (company-specific) risk while systematic (market) risk remains.

Portfolio variance: σ²p = Σᵢ Σⱼ wᵢwⱼσᵢⱼ

With more uncorrelated assets, the portfolio variance decreases. The correlation coefficient (ρ) between assets determines diversification benefits.""",
                examples=[
                    "Instead of investing $10,000 in one stock, investing $1,000 each in 10 different stocks across various sectors",
                    "A portfolio with 60% stocks, 30% bonds, and 10% real estate is more diversified than 100% stocks"
                ],
                analogies=[
                    "Like having multiple income streams - if you lose your job, you still have rental income and investments"
                ],
                related_concepts=["correlation", "asset allocation", "systematic risk"]
            ),
            "volatility": EducationalContent(
                concept_id="volatility",
                concept_name="Volatility",
                category="risk_metrics",
                simple_explanation="Volatility measures how much an investment's price jumps around. High volatility means the price can change a lot quickly, while low volatility means prices are more stable.",
                detailed_explanation="""Volatility is a statistical measure of the dispersion of returns for a given security or market index. Higher volatility means higher risk, as the price can change dramatically in either direction.

Types:
- Historical volatility: Based on past price movements
- Implied volatility: Derived from options prices, reflects market expectations
- Realized volatility: Actual volatility observed over a period""",
                technical_explanation="""Volatility (σ) is typically calculated as the standard deviation of returns:

σ = √(Σ(rᵢ - μ)² / (n-1))

Where rᵢ are individual returns and μ is the mean return.

Annualized volatility = Daily volatility × √252 (trading days)""",
                examples=[
                    "A stock that moves 5% daily has higher volatility than one that moves 0.5% daily",
                    "The VIX index measures expected volatility in the S&P 500"
                ],
                analogies=[
                    "Like weather - some places have calm, predictable weather (low volatility) while others have frequent storms and temperature swings (high volatility)"
                ],
                related_concepts=["standard deviation", "VIX", "risk", "beta"]
            )
        }
    
    async def generate_response(
        self,
        intent: Intent,
        context: ConversationContext,
        data: Dict[str, Any]
    ) -> AIResponse:
        """Generate a natural language response"""
        # Get template for intent and style
        templates = self.templates.get(intent.intent_type, {})
        template = templates.get(context.response_style, templates.get(ResponseStyle.DETAILED, ""))
        
        # Generate response based on intent
        if intent.intent_type == IntentType.EXPLAIN_CONCEPT:
            return await self._generate_educational_response(intent, context)
        elif intent.intent_type == IntentType.GREETING:
            return self._generate_greeting_response(context)
        elif intent.intent_type == IntentType.HELP:
            return self._generate_help_response(context)
        elif intent.intent_type == IntentType.UNKNOWN:
            return self._generate_fallback_response(intent, context)
        
        # Format template with data
        try:
            text = template.format(**data)
        except KeyError as e:
            self.logger.warning(f"Missing data for template: {e}")
            text = "I found the information you requested, but encountered an issue formatting the response."
        
        # Generate spoken version if needed
        spoken_text = self._generate_spoken_text(text)
        
        # Generate follow-up suggestions
        follow_ups = self._generate_follow_up_questions(intent, context, data)
        
        # Check if educational note should be added
        educational_note = None
        if context.response_style == ResponseStyle.EDUCATIONAL:
            educational_note = self._get_contextual_education(intent, data)
        
        return AIResponse(
            response_id=secrets.token_urlsafe(16),
            text=text,
            spoken_text=spoken_text,
            intent=intent,
            data=data,
            suggestions=self._generate_suggestions(intent, context),
            follow_up_questions=follow_ups,
            educational_note=educational_note,
            language=context.language
        )
    
    async def _generate_educational_response(
        self,
        intent: Intent,
        context: ConversationContext
    ) -> AIResponse:
        """Generate educational explanation"""
        concept = intent.entities.get("concept", "")
        
        content = self.educational_content.get(concept.lower())
        
        if content:
            # Choose explanation level based on style
            if context.response_style == ResponseStyle.SIMPLE:
                explanation = content.simple_explanation
            elif context.response_style == ResponseStyle.TECHNICAL:
                explanation = content.technical_explanation
            else:
                explanation = content.detailed_explanation
            
            # Add examples
            text = f"📚 **{content.concept_name}**\n\n{explanation}"
            
            if content.examples:
                text += "\n\n**Examples:**\n"
                for ex in content.examples[:2]:
                    text += f"• {ex}\n"
            
            if content.analogies and context.response_style == ResponseStyle.SIMPLE:
                text += f"\n**Think of it this way:** {content.analogies[0]}"
            
            if content.related_concepts:
                text += f"\n\n**Related concepts:** {', '.join(content.related_concepts)}"
            
            return AIResponse(
                response_id=secrets.token_urlsafe(16),
                text=text,
                spoken_text=content.simple_explanation,
                intent=intent,
                suggestions=[f"Explain {c}" for c in content.related_concepts[:3]],
                follow_up_questions=[
                    f"Would you like more detail on {content.related_concepts[0]}?",
                    "Would you like a technical explanation?",
                    "How does this apply to your portfolio?"
                ],
                language=context.language
            )
        
        # Concept not found
        return AIResponse(
            response_id=secrets.token_urlsafe(16),
            text=f"I don't have a detailed explanation for '{concept}' yet, but I can help you with many financial concepts like Sharpe ratio, diversification, volatility, and more.",
            suggestions=["Explain Sharpe ratio", "What is diversification?", "What is volatility?"],
            language=context.language
        )
    
    def _generate_greeting_response(self, context: ConversationContext) -> AIResponse:
        """Generate greeting response"""
        hour = datetime.now().hour
        
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        text = f"""👋 {greeting}! I'm your AI portfolio assistant.

I can help you with:
• 📊 Portfolio analysis and performance
• 📈 Stock research and recommendations
• 🌍 Market updates and news
• 📚 Financial education
• 🔔 Price alerts and notifications

What would you like to know about today?"""
        
        return AIResponse(
            response_id=secrets.token_urlsafe(16),
            text=text,
            spoken_text=f"{greeting}! I'm your AI portfolio assistant. How can I help you today?",
            suggestions=[
                "How is my portfolio doing?",
                "Show me market overview",
                "Analyze AAPL stock"
            ],
            language=context.language
        )
    
    def _generate_help_response(self, context: ConversationContext) -> AIResponse:
        """Generate help response"""
        text = """🤖 **How I Can Help You**

**Portfolio Questions:**
• "How is my portfolio doing?"
• "What's my portfolio performance?"
• "Show me my risk analysis"

**Stock Research:**
• "Should I buy Apple stock?"
• "Analyze Tesla"
• "What's the price of GOOGL?"

**Market Information:**
• "How is the market today?"
• "What are the top movers?"
• "Show me sector performance"

**Learning:**
• "Explain Sharpe ratio"
• "What is diversification?"
• "Teach me about options"

**Alerts:**
• "Set an alert for AAPL at $200"
• "Show my alerts"

Just ask naturally - I understand conversational language!"""
        
        return AIResponse(
            response_id=secrets.token_urlsafe(16),
            text=text,
            spoken_text="I can help with portfolio analysis, stock research, market updates, and financial education. Just ask me anything!",
            suggestions=[
                "How is my portfolio?",
                "Market overview",
                "Help me learn about investing"
            ],
            language=context.language
        )
    
    def _generate_fallback_response(self, intent: Intent, context: ConversationContext) -> AIResponse:
        """Generate fallback response for unknown intents"""
        text = """I'm not quite sure I understood that. Here's what I can help with:

• Portfolio analysis and performance
• Stock research and recommendations
• Market updates
• Financial education

Could you rephrase your question, or try one of the suggestions below?"""
        
        return AIResponse(
            response_id=secrets.token_urlsafe(16),
            text=text,
            spoken_text="I'm not sure I understood that. Could you try rephrasing your question?",
            intent=intent,
            suggestions=[
                "How is my portfolio?",
                "Analyze AAPL",
                "Market overview"
            ],
            language=context.language
        )
    
    def _generate_spoken_text(self, text: str) -> str:
        """Generate spoken version of text (remove markdown, simplify)"""
        # Remove markdown formatting
        spoken = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        spoken = re.sub(r'\*([^*]+)\*', r'\1', spoken)
        spoken = re.sub(r'#+\s*', '', spoken)
        spoken = re.sub(r'[📊📈🌍📚🔔👋🤖🤔]', '', spoken)
        spoken = re.sub(r'\n{2,}', '. ', spoken)
        spoken = re.sub(r'\n', ' ', spoken)
        spoken = re.sub(r'\s{2,}', ' ', spoken)
        
        return spoken.strip()
    
    def _generate_follow_up_questions(
        self,
        intent: Intent,
        context: ConversationContext,
        data: Dict[str, Any]
    ) -> List[str]:
        """Generate contextual follow-up questions"""
        follow_ups = []
        
        if intent.intent_type == IntentType.PORTFOLIO_STATUS:
            follow_ups = [
                "Would you like to see the performance breakdown?",
                "Should I analyze the risk in your portfolio?",
                "Would you like recommendations to rebalance?"
            ]
        elif intent.intent_type == IntentType.STOCK_ANALYSIS:
            symbols = intent.entities.get("symbols", [])
            if symbols:
                symbol = symbols[0]
                follow_ups = [
                    f"Should I compare {symbol} with competitors?",
                    f"Would you like to see {symbol}'s recent news?",
                    f"Should I run a 'what-if' scenario for buying {symbol}?"
                ]
        elif intent.intent_type == IntentType.MARKET_OVERVIEW:
            follow_ups = [
                "Would you like sector-specific analysis?",
                "Should I show how this affects your portfolio?",
                "Would you like to see international markets?"
            ]
        
        return follow_ups
    
    def _generate_suggestions(
        self,
        intent: Intent,
        context: ConversationContext
    ) -> List[str]:
        """Generate quick action suggestions"""
        suggestions = []
        
        if intent.intent_type in [IntentType.PORTFOLIO_STATUS, IntentType.PORTFOLIO_PERFORMANCE]:
            suggestions = ["Portfolio risk", "Rebalancing suggestions", "Tax optimization"]
        elif intent.intent_type in [IntentType.STOCK_ANALYSIS, IntentType.BUY_RECOMMENDATION]:
            suggestions = ["Compare with sector", "View technicals", "See fundamentals"]
        else:
            suggestions = ["Portfolio overview", "Market update", "Learn something new"]
        
        return suggestions
    
    def _get_contextual_education(self, intent: Intent, data: Dict[str, Any]) -> Optional[str]:
        """Get educational note relevant to the context"""
        if intent.intent_type == IntentType.PORTFOLIO_RISK:
            return "💡 **Learning Note:** The Sharpe Ratio shown above measures risk-adjusted return. A value above 1.0 is generally considered good."
        elif intent.intent_type == IntentType.STOCK_ANALYSIS:
            return "💡 **Learning Note:** RSI (Relative Strength Index) above 70 typically indicates overbought conditions, while below 30 indicates oversold."
        return None


class BehaviorAnalyzer:
    """
    Analyzes user behavior patterns for contextual recommendations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.patterns: Dict[str, List[UserBehaviorPattern]] = {}
    
    async def track_behavior(
        self,
        user_id: str,
        action: str,
        context: Dict[str, Any]
    ):
        """Track user behavior"""
        if user_id not in self.patterns:
            self.patterns[user_id] = []
        
        # Find or create pattern
        pattern = next(
            (p for p in self.patterns[user_id] if p.pattern_type == action),
            None
        )
        
        if pattern:
            pattern.frequency += 1
            pattern.last_occurrence = datetime.now()
            pattern.confidence = min(1.0, pattern.frequency / 10)
        else:
            pattern = UserBehaviorPattern(
                user_id=user_id,
                pattern_type=action,
                frequency=1,
                context=context
            )
            self.patterns[user_id].append(pattern)
    
    async def get_recommendations(self, user_id: str) -> List[str]:
        """Get personalized recommendations based on behavior"""
        patterns = self.patterns.get(user_id, [])
        recommendations = []
        
        # Sort by frequency and recency
        sorted_patterns = sorted(
            patterns,
            key=lambda p: (p.frequency, p.last_occurrence),
            reverse=True
        )
        
        for pattern in sorted_patterns[:3]:
            if pattern.pattern_type == "portfolio_check":
                recommendations.append("Check your portfolio performance")
            elif pattern.pattern_type == "stock_analysis":
                symbols = pattern.context.get("symbols", [])
                if symbols:
                    recommendations.append(f"Update on {symbols[0]}")
            elif pattern.pattern_type == "market_overview":
                recommendations.append("See today's market summary")
        
        return recommendations


class MultiLanguageSupport:
    """
    Multi-language support for global users.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Common phrases translations
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[Language, str]]:
        """Load common translations"""
        return {
            "greeting_morning": {
                Language.ENGLISH: "Good morning",
                Language.SPANISH: "Buenos días",
                Language.FRENCH: "Bonjour",
                Language.GERMAN: "Guten Morgen",
                Language.PORTUGUESE: "Bom dia",
                Language.CHINESE: "早上好",
                Language.JAPANESE: "おはようございます",
            },
            "portfolio_summary": {
                Language.ENGLISH: "Portfolio Summary",
                Language.SPANISH: "Resumen del Portafolio",
                Language.FRENCH: "Résumé du Portefeuille",
                Language.GERMAN: "Portfolio-Zusammenfassung",
            },
            "up": {
                Language.ENGLISH: "up",
                Language.SPANISH: "subió",
                Language.FRENCH: "en hausse",
                Language.GERMAN: "gestiegen",
            },
            "down": {
                Language.ENGLISH: "down",
                Language.SPANISH: "bajó",
                Language.FRENCH: "en baisse",
                Language.GERMAN: "gefallen",
            }
        }
    
    async def translate(self, text: str, target_language: Language) -> str:
        """Translate text to target language"""
        if target_language == Language.ENGLISH:
            return text
        
        # In production, use translation API
        # For now, return original with note
        return f"{text}\n\n[Translation to {target_language.value} pending]"
    
    async def detect_language(self, text: str) -> Language:
        """Detect language of input text"""
        # Simple detection based on character patterns
        # In production, use language detection API
        
        if any(ord(c) > 0x4E00 and ord(c) < 0x9FFF for c in text):
            return Language.CHINESE
        if any(ord(c) > 0x3040 and ord(c) < 0x30FF for c in text):
            return Language.JAPANESE
        
        # Default to English
        return Language.ENGLISH


class ConversationalAI:
    """
    Main conversational AI system integrating all components.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.intent_classifier = IntentClassifier(config)
        self.response_generator = ResponseGenerator(config)
        self.behavior_analyzer = BehaviorAnalyzer(config)
        self.language_support = MultiLanguageSupport(config)
        
        # Active sessions
        self.sessions: Dict[str, ConversationContext] = {}
        
        # Data providers (would be injected in production)
        self.data_providers: Dict[str, Callable] = {}
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None
    ) -> AIResponse:
        """Process a user message and generate response"""
        # Get or create session
        context = await self._get_or_create_session(user_id, session_id)
        
        # Detect language
        detected_language = await self.language_support.detect_language(message)
        if detected_language != Language.ENGLISH:
            context.language = detected_language
        
        # Classify intent
        intent = await self.intent_classifier.classify(message, context)
        
        # Fetch required data based on intent
        data = await self._fetch_data_for_intent(intent, context)
        
        # Generate response
        response = await self.response_generator.generate_response(intent, context, data)
        
        # Update context
        await self._update_context(context, message, intent, response)
        
        # Track behavior
        await self.behavior_analyzer.track_behavior(
            user_id,
            intent.intent_type.value,
            {"symbols": intent.entities.get("symbols", [])}
        )
        
        return response
    
    async def _get_or_create_session(
        self,
        user_id: str,
        session_id: Optional[str]
    ) -> ConversationContext:
        """Get existing session or create new one"""
        if session_id and session_id in self.sessions:
            context = self.sessions[session_id]
            context.last_activity = datetime.now()
            return context
        
        # Create new session
        new_session_id = session_id or secrets.token_urlsafe(16)
        context = ConversationContext(
            session_id=new_session_id,
            user_id=user_id
        )
        self.sessions[new_session_id] = context
        return context
    
    async def _fetch_data_for_intent(
        self,
        intent: Intent,
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Fetch data required to respond to intent"""
        data = {}
        
        # Mock data - in production, fetch from real sources
        if intent.intent_type == IntentType.PORTFOLIO_STATUS:
            data = {
                "total_value": 125000.00,
                "change_direction": "up",
                "change_direction_symbol": "+",
                "change_pct": 1.25,
                "change_amount": 1543.21,
                "num_positions": 15,
                "num_sectors": 8,
                "top_holdings": "• AAPL: 15% (+2.3%)\n• MSFT: 12% (+1.1%)\n• GOOGL: 10% (-0.5%)",
                "allocation": "• Technology: 45%\n• Healthcare: 20%\n• Financials: 15%\n• Other: 20%"
            }
        elif intent.intent_type == IntentType.PORTFOLIO_PERFORMANCE:
            data = {
                "total_return": 32.5,
                "ytd_return": 15.2,
                "monthly_return": 2.3,
                "sharpe_ratio": 1.45,
                "max_drawdown": 8.2,
                "volatility": 14.5,
                "benchmark_comparison": "outperforming",
                "benchmark_diff": 3.2
            }
        elif intent.intent_type == IntentType.STOCK_ANALYSIS:
            symbols = intent.entities.get("symbols", ["AAPL"])
            symbol = symbols[0] if symbols else "AAPL"
            data = {
                "symbol": symbol,
                "price": 175.50,
                "change_direction": "+",
                "change_pct": 1.25,
                "trend": "Bullish 📈",
                "rsi": 62.5,
                "rsi_signal": "Neutral",
                "ma_50": 172.30,
                "ma_200": 165.80,
                "pe_ratio": 28.5,
                "market_cap": "2.8T",
                "revenue_growth": 5.2,
                "recommendation": "BUY 📈",
                "confidence": 72,
                "additional_insight": "Strong momentum with positive earnings revisions. Watch for resistance at $180."
            }
        elif intent.intent_type == IntentType.BUY_RECOMMENDATION:
            symbols = intent.entities.get("symbols", ["AAPL"])
            symbol = symbols[0] if symbols else "AAPL"
            data = {
                "symbol": symbol,
                "recommendation": "MODERATE BUY 📈",
                "confidence": 68,
                "pros": "• Strong brand and ecosystem\n• Consistent revenue growth\n• Services segment expanding",
                "cons": "• Premium valuation\n• Smartphone market saturation\n• Regulatory risks in EU",
                "portfolio_context": f"Adding {symbol} would increase your Technology exposure to 50%. Consider if this aligns with your diversification goals."
            }
        elif intent.intent_type == IntentType.MARKET_OVERVIEW:
            data = {
                "sp500_value": 4782.53,
                "sp500_change": 0.85,
                "nasdaq_value": 15123.45,
                "nasdaq_change": 1.20,
                "dow_value": 38254.32,
                "dow_change": 0.45,
                "sentiment": "Cautiously Bullish 📈",
                "top_movers": "📈 NVDA +4.2% | TSLA +3.1%\n📉 BA -2.3% | JNJ -1.8%",
                "headlines": "• Fed signals rate decision coming\n• Tech earnings beat expectations\n• Oil prices stabilize"
            }
        
        return data
    
    async def _update_context(
        self,
        context: ConversationContext,
        message: str,
        intent: Intent,
        response: AIResponse
    ):
        """Update conversation context"""
        # Add to message history
        context.messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        context.messages.append({
            "role": "assistant",
            "content": response.text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update mentioned symbols
        new_symbols = intent.entities.get("symbols", [])
        for symbol in new_symbols:
            if symbol not in context.mentioned_symbols:
                context.mentioned_symbols.append(symbol)
        
        # Update current topic
        context.current_topic = intent.intent_type.value
        
        # Limit history
        if len(context.messages) > 50:
            context.messages = context.messages[-50:]
    
    def get_api_routes(self):
        """Get FastAPI routes for conversational AI endpoints"""
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
        
        router = APIRouter(prefix="/assistant", tags=["AI Assistant"])
        
        class MessageRequest(BaseModel):
            message: str
            session_id: Optional[str] = None
        
        class VoiceRequest(BaseModel):
            audio_base64: Optional[str] = None
            transcribed_text: Optional[str] = None
            session_id: Optional[str] = None
        
        class PreferencesRequest(BaseModel):
            language: str = "en"
            response_style: str = "detailed"
        
        @router.post("/chat")
        async def chat(request: MessageRequest, user_id: str = "demo_user"):
            response = await self.process_message(
                user_id=user_id,
                message=request.message,
                session_id=request.session_id
            )
            return {
                "response_id": response.response_id,
                "text": response.text,
                "spoken_text": response.spoken_text,
                "suggestions": response.suggestions,
                "follow_up_questions": response.follow_up_questions,
                "educational_note": response.educational_note,
                "data": response.data
            }
        
        @router.post("/voice")
        async def voice_chat(request: VoiceRequest, user_id: str = "demo_user"):
            # In production, transcribe audio first
            text = request.transcribed_text or ""
            
            response = await self.process_message(
                user_id=user_id,
                message=text,
                session_id=request.session_id
            )
            
            return {
                "response_id": response.response_id,
                "text": response.text,
                "spoken_text": response.spoken_text,
                "ssml": response.ssml,
                "suggestions": response.suggestions
            }
        
        @router.get("/session/{session_id}")
        async def get_session(session_id: str):
            context = self.sessions.get(session_id)
            if not context:
                raise HTTPException(status_code=404, detail="Session not found")
            
            return {
                "session_id": context.session_id,
                "user_id": context.user_id,
                "language": context.language.value,
                "message_count": len(context.messages),
                "current_topic": context.current_topic,
                "mentioned_symbols": context.mentioned_symbols
            }
        
        @router.post("/preferences")
        async def update_preferences(request: PreferencesRequest, user_id: str = "demo_user"):
            # Find user's sessions and update preferences
            for session in self.sessions.values():
                if session.user_id == user_id:
                    session.language = Language(request.language)
                    session.response_style = ResponseStyle(request.response_style)
            
            return {"status": "updated"}
        
        @router.get("/recommendations")
        async def get_recommendations(user_id: str = "demo_user"):
            recommendations = await self.behavior_analyzer.get_recommendations(user_id)
            return {"recommendations": recommendations}
        
        @router.get("/concepts/{concept}")
        async def explain_concept(concept: str):
            content = self.response_generator.educational_content.get(concept.lower())
            if not content:
                raise HTTPException(status_code=404, detail="Concept not found")
            
            return {
                "concept": content.concept_name,
                "category": content.category,
                "simple": content.simple_explanation,
                "detailed": content.detailed_explanation,
                "technical": content.technical_explanation,
                "examples": content.examples,
                "related": content.related_concepts
            }
        
        return router


# Export main components
__all__ = [
    'ConversationalAI',
    'IntentClassifier',
    'ResponseGenerator',
    'BehaviorAnalyzer',
    'MultiLanguageSupport',
    'IntentType',
    'Language',
    'ResponseStyle'
]
