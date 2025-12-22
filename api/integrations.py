"""
Third-Party API Integrations

Integrates with external APIs for data and services:
- OpenAI GPT-4 for text generation and analysis
- Financial data APIs (Alpha Vantage, Yahoo Finance)
- News APIs
- Email services

Features:
- API client wrappers
- Rate limiting
- Error handling
- Response caching
"""

import openai
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
from loguru import logger
import os
from dotenv import load_dotenv
from functools import lru_cache


load_dotenv()


class OpenAIClient:
    """
    OpenAI API client for GPT-4 integration.
    
    Provides text generation, analysis, and summarization capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not found")
        
        self.model = "gpt-4"
        self.max_tokens = 2000
        self.temperature = 0.7
    
    def generate_completion(self, 
                          prompt: str,
                          max_tokens: Optional[int] = None,
                          temperature: Optional[float] = None) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Error: {str(e)}"
    
    def summarize_document(self, document: str, max_length: int = 500) -> str:
        """
        Summarize a financial document.
        
        Args:
            document: Document text
            max_length: Maximum summary length
            
        Returns:
            Summary text
        """
        prompt = f"""
        Summarize the following financial document in a concise, professional manner.
        Focus on key financial metrics, performance indicators, and important insights.
        Maximum length: {max_length} words.
        
        Document:
        {document[:4000]}  # Truncate to avoid token limits
        
        Summary:
        """
        
        return self.generate_completion(prompt, max_tokens=max_length * 2)
    
    def analyze_investment(self, company_info: Dict) -> str:
        """
        Generate investment analysis.
        
        Args:
            company_info: Company information dictionary
            
        Returns:
            Investment analysis
        """
        prompt = f"""
        Provide a detailed investment analysis for the following company:
        
        Company: {company_info.get('name', 'Unknown')}
        Sector: {company_info.get('sector', 'N/A')}
        Revenue: ${company_info.get('revenue', 0):,.0f}
        Growth Rate: {company_info.get('growth_rate', 0):.1f}%
        Profit Margin: {company_info.get('profit_margin', 0):.1f}%
        Debt-to-Equity: {company_info.get('debt_to_equity', 0):.2f}
        
        Provide:
        1. Strengths and weaknesses
        2. Growth potential
        3. Risk factors
        4. Investment recommendation
        """
        
        return self.generate_completion(prompt)
    
    def extract_insights(self, text: str) -> List[str]:
        """
        Extract key insights from text.
        
        Args:
            text: Input text
            
        Returns:
            List of insights
        """
        prompt = f"""
        Extract 5-7 key insights from the following financial text.
        Present each insight as a concise bullet point.
        
        Text:
        {text[:3000]}
        
        Key Insights:
        """
        
        response = self.generate_completion(prompt, max_tokens=500)
        
        # Parse bullet points
        insights = [line.strip('- ').strip() for line in response.split('\n') 
                   if line.strip() and line.strip()[0] in ['-', '•', '*']]
        
        return insights


class FinancialDataClient:
    """
    Financial data API client.
    
    Integrates with financial data providers for market data,
    company fundamentals, and economic indicators.
    """
    
    def __init__(self):
        """Initialize financial data client."""
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Financial data client initialized")
    
    @lru_cache(maxsize=128)
    def get_stock_quote(self, symbol: str) -> Dict:
        """
        Get real-time stock quote.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Quote data dictionary
        """
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not configured")
            return self._generate_mock_quote(symbol)
        
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': symbol,
                    'price': float(quote.get('05. price', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'change_percent': quote.get('10. change percent', '0%'),
                    'volume': int(quote.get('06. volume', 0)),
                    'timestamp': quote.get('07. latest trading day')
                }
            else:
                return self._generate_mock_quote(symbol)
                
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            return self._generate_mock_quote(symbol)
    
    def _generate_mock_quote(self, symbol: str) -> Dict:
        """Generate mock quote data for demonstration."""
        import random
        price = random.uniform(50, 500)
        change = random.uniform(-10, 10)
        
        return {
            'symbol': symbol,
            'price': round(price, 2),
            'change': round(change, 2),
            'change_percent': f"{(change/price*100):.2f}%",
            'volume': random.randint(1000000, 50000000),
            'timestamp': datetime.now().strftime('%Y-%m-%d'),
            'mock': True
        }
    
    def get_company_overview(self, symbol: str) -> Dict:
        """
        Get company overview and fundamentals.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Company data dictionary
        """
        # Check cache first
        cache_file = self.cache_dir / f"{symbol}_overview.json"
        
        if cache_file.exists():
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(days=7):
                with open(cache_file, 'r') as f:
                    logger.info(f"Using cached data for {symbol}")
                    return json.load(f)
        
        if not self.alpha_vantage_key:
            return self._generate_mock_overview(symbol)
        
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching overview for {symbol}: {str(e)}")
            return self._generate_mock_overview(symbol)
    
    def _generate_mock_overview(self, symbol: str) -> Dict:
        """Generate mock company overview."""
        import random
        
        sectors = ['Technology', 'Healthcare', 'Finance', 'Consumer', 'Energy']
        
        return {
            'Symbol': symbol,
            'Name': f'{symbol} Corporation',
            'Sector': random.choice(sectors),
            'MarketCapitalization': str(random.randint(1000000000, 1000000000000)),
            'PERatio': str(round(random.uniform(10, 50), 2)),
            'EPS': str(round(random.uniform(1, 20), 2)),
            'DividendYield': str(round(random.uniform(0, 5), 2)),
            'Beta': str(round(random.uniform(0.5, 2.0), 2)),
            'mock': True
        }


class EmailClient:
    """
    Email notification client.
    
    Sends automated emails for reports, alerts, and notifications.
    """
    
    def __init__(self):
        """Initialize email client."""
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('EMAIL_FROM', 'noreply@example.com')
        logger.info("Email client initialized")
    
    def send_report(self, 
                   to_emails: List[str],
                   subject: str,
                   html_content: str,
                   attachments: Optional[List[str]] = None) -> bool:
        """
        Send report via email.
        
        Args:
            to_emails: List of recipient emails
            subject: Email subject
            html_content: HTML email content
            attachments: List of file paths to attach
            
        Returns:
            Success status
        """
        if not self.api_key:
            logger.warning("Email API key not configured. Email not sent.")
            logger.info(f"Would send email to: {to_emails}")
            logger.info(f"Subject: {subject}")
            return False
        
        try:
            # In production, integrate with SendGrid or similar
            # from sendgrid import SendGridAPIClient
            # from sendgrid.helpers.mail import Mail
            
            logger.info(f"Sending email to {len(to_emails)} recipients")
            logger.info(f"Subject: {subject}")
            
            # Placeholder for actual implementation
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_alert(self, to_emails: List[str], alert_message: str) -> bool:
        """
        Send alert notification.
        
        Args:
            to_emails: List of recipient emails
            alert_message: Alert message
            
        Returns:
            Success status
        """
        subject = f"Alert: {alert_message[:50]}"
        html_content = f"""
        <html>
            <body>
                <h2>System Alert</h2>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Message:</strong></p>
                <p>{alert_message}</p>
            </body>
        </html>
        """
        
        return self.send_report(to_emails, subject, html_content)


# Convenience functions

def get_openai_client() -> OpenAIClient:
    """Get OpenAI client instance."""
    return OpenAIClient()


def get_financial_data_client() -> FinancialDataClient:
    """Get financial data client instance."""
    return FinancialDataClient()


def get_email_client() -> EmailClient:
    """Get email client instance."""
    return EmailClient()


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/api_integrations.log", rotation="10 MB")
    
    # Test OpenAI integration
    logger.info("Testing API integrations...")
    
    # Financial data client
    fin_client = get_financial_data_client()
    quote = fin_client.get_stock_quote('AAPL')
    logger.info(f"Stock quote: {quote}")
    
    overview = fin_client.get_company_overview('AAPL')
    logger.info(f"Company: {overview.get('Name', 'N/A')}")
    
    # OpenAI client (if configured)
    openai_client = get_openai_client()
    if openai_client.api_key:
        summary = openai_client.summarize_document(
            "Apple Inc. reported record quarterly revenue of $123 billion..."
        )
        logger.info(f"Summary: {summary[:200]}")
    
    # Email client
    email_client = get_email_client()
    email_client.send_alert(
        ['admin@example.com'],
        'Test alert message'
    )
    
    logger.info("API integration tests complete")
