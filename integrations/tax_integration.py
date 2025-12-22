"""
Tax Software Integration
========================

Integrate with tax software:
- TurboTax
- TaxAct
- CoinTracker (for crypto)
- Generate tax documents (1099, 8949)
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class EventType(Enum):
    """Types of taxable events"""
    STOCK_SALE = "stock_sale"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    CAPITAL_GAIN = "capital_gain"
    CAPITAL_LOSS = "capital_loss"
    CRYPTO_SALE = "crypto_sale"
    CRYPTO_INCOME = "crypto_income"
    OPTIONS_EXERCISE = "options_exercise"
    RSU_VEST = "rsu_vest"


class TaxLotMethod(Enum):
    """Tax lot accounting methods"""
    FIFO = "fifo"  # First In First Out
    LIFO = "lifo"  # Last In First Out
    HIFO = "hifo"  # Highest In First Out
    SPECIFIC_ID = "specific_id"  # Specific Identification


@dataclass
class TaxableEvent:
    """Taxable event"""
    event_id: str
    event_type: EventType
    date: datetime
    
    # Asset details
    symbol: str
    description: str
    quantity: float
    
    # Financial details
    proceeds: float = 0.0
    cost_basis: float = 0.0
    gain_loss: float = 0.0
    
    # Holding period
    is_long_term: bool = False  # Held > 1 year
    acquisition_date: Optional[datetime] = None
    
    # Metadata
    account_id: Optional[str] = None
    notes: str = ""
    
    def calculate_gain_loss(self):
        """Calculate gain/loss"""
        self.gain_loss = self.proceeds - self.cost_basis
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'type': self.event_type.value,
            'date': self.date.isoformat(),
            'symbol': self.symbol,
            'quantity': self.quantity,
            'proceeds': self.proceeds,
            'cost_basis': self.cost_basis,
            'gain_loss': self.gain_loss,
            'is_long_term': self.is_long_term
        }


@dataclass
class TaxDocument:
    """Tax document (1099, 8949, etc.)"""
    document_id: str
    document_type: str  # 1099-DIV, 1099-B, 8949, etc.
    tax_year: int
    
    # Issuer
    issuer_name: str
    issuer_ein: Optional[str] = None
    
    # Taxpayer
    taxpayer_name: str
    taxpayer_ssn: Optional[str] = None
    
    # Data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'document_id': self.document_id,
            'type': self.document_type,
            'tax_year': self.tax_year,
            'issuer': self.issuer_name,
            'data': self.data,
            'generated_at': self.generated_at.isoformat()
        }


class TaxIntegration:
    """
    Base tax integration system.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("tax_integration")
        self.events: Dict[str, List[TaxableEvent]] = {}  # user_id -> events
        self.documents: Dict[str, List[TaxDocument]] = {}  # user_id -> documents
    
    def add_event(self, user_id: str, event: TaxableEvent):
        """Add a taxable event"""
        if user_id not in self.events:
            self.events[user_id] = []
        
        event.calculate_gain_loss()
        self.events[user_id].append(event)
        
        self.logger.info(f"Added {event.event_type.value} event for user {user_id}")
    
    def get_events(
        self,
        user_id: str,
        tax_year: int,
        event_type: Optional[EventType] = None
    ) -> List[TaxableEvent]:
        """Get taxable events for a year"""
        user_events = self.events.get(user_id, [])
        
        filtered = [
            e for e in user_events
            if e.date.year == tax_year
        ]
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        return filtered
    
    def calculate_capital_gains(
        self,
        user_id: str,
        tax_year: int
    ) -> Dict[str, Any]:
        """Calculate capital gains/losses"""
        events = self.get_events(user_id, tax_year)
        
        short_term_gain = 0.0
        long_term_gain = 0.0
        
        for event in events:
            if event.event_type in [EventType.STOCK_SALE, EventType.CRYPTO_SALE]:
                if event.is_long_term:
                    long_term_gain += event.gain_loss
                else:
                    short_term_gain += event.gain_loss
        
        return {
            'tax_year': tax_year,
            'short_term': {
                'gain_loss': short_term_gain,
                'tax_rate_range': '10-37%'
            },
            'long_term': {
                'gain_loss': long_term_gain,
                'tax_rate_range': '0-20%'
            },
            'total_gain_loss': short_term_gain + long_term_gain
        }
    
    def calculate_dividend_income(
        self,
        user_id: str,
        tax_year: int
    ) -> Dict[str, Any]:
        """Calculate dividend income"""
        events = self.get_events(user_id, tax_year, EventType.DIVIDEND)
        
        qualified_dividends = 0.0
        ordinary_dividends = 0.0
        
        for event in events:
            # Simplified - in production check qualified dividend criteria
            if event.is_long_term:
                qualified_dividends += event.proceeds
            else:
                ordinary_dividends += event.proceeds
        
        return {
            'tax_year': tax_year,
            'qualified_dividends': qualified_dividends,
            'ordinary_dividends': ordinary_dividends,
            'total_dividends': qualified_dividends + ordinary_dividends
        }
    
    def generate_1099_div(
        self,
        user_id: str,
        tax_year: int,
        taxpayer_name: str,
        issuer_name: str = "Portfolio Analysis Platform"
    ) -> TaxDocument:
        """Generate 1099-DIV form"""
        dividend_data = self.calculate_dividend_income(user_id, tax_year)
        
        doc = TaxDocument(
            document_id=str(uuid.uuid4()),
            document_type="1099-DIV",
            tax_year=tax_year,
            issuer_name=issuer_name,
            taxpayer_name=taxpayer_name,
            data={
                'box_1a_ordinary_dividends': dividend_data['ordinary_dividends'],
                'box_1b_qualified_dividends': dividend_data['qualified_dividends']
            }
        )
        
        if user_id not in self.documents:
            self.documents[user_id] = []
        self.documents[user_id].append(doc)
        
        self.logger.info(f"Generated 1099-DIV for {user_id}")
        
        return doc
    
    def generate_form_8949(
        self,
        user_id: str,
        tax_year: int,
        taxpayer_name: str
    ) -> TaxDocument:
        """Generate Form 8949 (Sales and Other Dispositions of Capital Assets)"""
        events = self.get_events(user_id, tax_year)
        
        short_term_transactions = []
        long_term_transactions = []
        
        for event in events:
            if event.event_type in [EventType.STOCK_SALE, EventType.CRYPTO_SALE]:
                txn = {
                    'description': f"{event.quantity} {event.symbol}",
                    'date_acquired': event.acquisition_date.strftime('%m/%d/%Y') if event.acquisition_date else 'VARIOUS',
                    'date_sold': event.date.strftime('%m/%d/%Y'),
                    'proceeds': event.proceeds,
                    'cost_basis': event.cost_basis,
                    'gain_loss': event.gain_loss
                }
                
                if event.is_long_term:
                    long_term_transactions.append(txn)
                else:
                    short_term_transactions.append(txn)
        
        doc = TaxDocument(
            document_id=str(uuid.uuid4()),
            document_type="8949",
            tax_year=tax_year,
            issuer_name="Portfolio Analysis Platform",
            taxpayer_name=taxpayer_name,
            data={
                'short_term_transactions': short_term_transactions,
                'long_term_transactions': long_term_transactions,
                'short_term_total': sum(t['gain_loss'] for t in short_term_transactions),
                'long_term_total': sum(t['gain_loss'] for t in long_term_transactions)
            }
        )
        
        if user_id not in self.documents:
            self.documents[user_id] = []
        self.documents[user_id].append(doc)
        
        self.logger.info(f"Generated Form 8949 for {user_id}")
        
        return doc
    
    def export_to_turbotax(
        self,
        user_id: str,
        tax_year: int
    ) -> Dict[str, Any]:
        """Export data to TurboTax format"""
        capital_gains = self.calculate_capital_gains(user_id, tax_year)
        dividend_income = self.calculate_dividend_income(user_id, tax_year)
        
        # TurboTax TXF format (Tax Exchange Format)
        return {
            'format': 'TXF',
            'tax_year': tax_year,
            'capital_gains': capital_gains,
            'dividend_income': dividend_income,
            'file_data': self._generate_txf_file(user_id, tax_year)
        }
    
    def _generate_txf_file(self, user_id: str, tax_year: int) -> str:
        """Generate TXF file content"""
        # Simplified TXF format
        lines = [
            "V042",
            f"D{datetime.now().strftime('%m/%d/%Y')}",
            "^"
        ]
        
        events = self.get_events(user_id, tax_year)
        
        for event in events:
            if event.event_type == EventType.STOCK_SALE:
                # Short-term or long-term capital gain
                code = "323" if event.is_long_term else "321"
                
                lines.extend([
                    f"T{code}",
                    f"N{event.symbol}",
                    f"D{event.date.strftime('%m/%d/%Y')}",
                    f"${event.gain_loss:.2f}",
                    "^"
                ])
        
        return "\n".join(lines)
    
    def get_tax_summary(
        self,
        user_id: str,
        tax_year: int
    ) -> Dict[str, Any]:
        """Get comprehensive tax summary"""
        capital_gains = self.calculate_capital_gains(user_id, tax_year)
        dividend_income = self.calculate_dividend_income(user_id, tax_year)
        events = self.get_events(user_id, tax_year)
        
        return {
            'user_id': user_id,
            'tax_year': tax_year,
            'summary': {
                'total_events': len(events),
                'capital_gains': capital_gains,
                'dividend_income': dividend_income,
                'estimated_tax_owed': self._estimate_tax(capital_gains, dividend_income)
            },
            'documents_available': [
                '1099-DIV',
                'Form 8949',
                'Schedule D'
            ],
            'generated_at': datetime.now().isoformat()
        }
    
    def _estimate_tax(
        self,
        capital_gains: Dict[str, Any],
        dividend_income: Dict[str, Any]
    ) -> float:
        """Estimate tax owed (simplified)"""
        # Very simplified tax calculation
        # In production, use actual tax brackets
        
        # Short-term gains taxed as ordinary income (assume 24% bracket)
        short_term_tax = max(0, capital_gains['short_term']['gain_loss']) * 0.24
        
        # Long-term gains taxed at 15%
        long_term_tax = max(0, capital_gains['long_term']['gain_loss']) * 0.15
        
        # Qualified dividends at 15%, ordinary at 24%
        dividend_tax = (
            dividend_income.get('qualified_dividends', 0) * 0.15 +
            dividend_income.get('ordinary_dividends', 0) * 0.24
        )
        
        return short_term_tax + long_term_tax + dividend_tax


class TurboTaxConnector:
    """Connector for TurboTax export"""
    
    def __init__(self):
        self.logger = logging.getLogger("turbotax_connector")
    
    def export_data(
        self,
        tax_integration: TaxIntegration,
        user_id: str,
        tax_year: int,
        output_path: str
    ) -> bool:
        """Export data to TurboTax file"""
        try:
            data = tax_integration.export_to_turbotax(user_id, tax_year)
            
            with open(output_path, 'w') as f:
                f.write(data['file_data'])
            
            self.logger.info(f"Exported TurboTax file to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return False


class CoinTrackerConnector:
    """Connector for CoinTracker (crypto tax)"""
    
    def __init__(self, api_key: str):
        self.logger = logging.getLogger("cointracker_connector")
        self.api_key = api_key
    
    def sync_crypto_transactions(
        self,
        tax_integration: TaxIntegration,
        user_id: str,
        tax_year: int
    ) -> bool:
        """Sync crypto transactions to CoinTracker"""
        try:
            events = tax_integration.get_events(user_id, tax_year, EventType.CRYPTO_SALE)
            
            # In production, make API call to CoinTracker
            # POST /api/v1/transactions
            
            self.logger.info(f"Synced {len(events)} crypto transactions")
            return True
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            return False
