"""
Banking API Integrations
========================

Connect to banking platforms for:
- Account aggregation
- Transaction sync
- Net worth tracking
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging


class BankType(Enum):
    """Banking platform types"""
    PLAID = "plaid"
    YODLEE = "yodlee"
    FINICITY = "finicity"
    MX = "mx"


class AccountType(Enum):
    """Bank account types"""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    INVESTMENT = "investment"


class TransactionCategory(Enum):
    """Transaction categories"""
    INCOME = "income"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    PURCHASE = "purchase"
    ATM = "atm"
    FEE = "fee"
    INTEREST = "interest"


@dataclass
class BankAccount:
    """Bank account information"""
    account_id: str
    institution_name: str
    account_type: AccountType
    account_number_last4: str
    
    # Balances
    current_balance: float = 0.0
    available_balance: float = 0.0
    limit: Optional[float] = None  # For credit cards/loans
    
    # Metadata
    currency: str = "USD"
    is_active: bool = True
    last_synced: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'account_id': self.account_id,
            'institution': self.institution_name,
            'type': self.account_type.value,
            'last4': self.account_number_last4,
            'current_balance': self.current_balance,
            'available_balance': self.available_balance,
            'currency': self.currency
        }


@dataclass
class Transaction:
    """Bank transaction"""
    transaction_id: str
    account_id: str
    
    # Transaction details
    date: datetime
    amount: float
    description: str
    merchant_name: Optional[str] = None
    
    # Classification
    category: TransactionCategory = TransactionCategory.PURCHASE
    subcategory: Optional[str] = None
    
    # Status
    pending: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'transaction_id': self.transaction_id,
            'date': self.date.isoformat(),
            'amount': self.amount,
            'description': self.description,
            'merchant': self.merchant_name,
            'category': self.category.value,
            'pending': self.pending
        }


class BankingConnection(ABC):
    """
    Base class for banking API connections.
    """
    
    def __init__(
        self,
        client_id: str,
        secret: str,
        bank_type: BankType
    ):
        self.logger = logging.getLogger(f"banking_{bank_type.value}")
        self.client_id = client_id
        self.secret = secret
        self.bank_type = bank_type
        self.is_connected = False
    
    @abstractmethod
    def create_link_token(self, user_id: str) -> str:
        """Create a link token for user authentication"""
        pass
    
    @abstractmethod
    def exchange_public_token(self, public_token: str) -> str:
        """Exchange public token for access token"""
        pass
    
    @abstractmethod
    def get_accounts(self, access_token: str) -> List[BankAccount]:
        """Get user's bank accounts"""
        pass
    
    @abstractmethod
    def get_transactions(
        self,
        access_token: str,
        account_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get transactions"""
        pass
    
    @abstractmethod
    def get_balance(self, access_token: str, account_id: str) -> float:
        """Get account balance"""
        pass


class PlaidConnector(BankingConnection):
    """
    Plaid banking API connector.
    """
    
    def __init__(
        self,
        client_id: str,
        secret: str,
        environment: str = "sandbox"
    ):
        super().__init__(client_id, secret, BankType.PLAID)
        self.environment = environment  # sandbox, development, production
    
    def create_link_token(self, user_id: str) -> str:
        """Create Plaid Link token"""
        # In production, use plaid-python library
        # from plaid.api import plaid_api
        # from plaid.model.link_token_create_request import LinkTokenCreateRequest
        # request = LinkTokenCreateRequest(...)
        # response = client.link_token_create(request)
        
        self.logger.info(f"Created link token for user {user_id}")
        return f"link-{uuid.uuid4()}"
    
    def exchange_public_token(self, public_token: str) -> str:
        """Exchange public token for access token"""
        # In production:
        # from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
        # request = ItemPublicTokenExchangeRequest(public_token=public_token)
        # response = client.item_public_token_exchange(request)
        
        access_token = f"access-{uuid.uuid4()}"
        self.logger.info("Exchanged public token")
        return access_token
    
    def get_accounts(self, access_token: str) -> List[BankAccount]:
        """Get Plaid accounts"""
        # Placeholder - in production call Plaid API
        return [
            BankAccount(
                account_id="plaid_checking_123",
                institution_name="Chase",
                account_type=AccountType.CHECKING,
                account_number_last4="4321",
                current_balance=5000.0,
                available_balance=4800.0,
                last_synced=datetime.now()
            ),
            BankAccount(
                account_id="plaid_savings_456",
                institution_name="Chase",
                account_type=AccountType.SAVINGS,
                account_number_last4="8765",
                current_balance=15000.0,
                available_balance=15000.0,
                last_synced=datetime.now()
            )
        ]
    
    def get_transactions(
        self,
        access_token: str,
        account_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get Plaid transactions"""
        # Placeholder
        return [
            Transaction(
                transaction_id="txn_1",
                account_id=account_id or "plaid_checking_123",
                date=datetime.now(),
                amount=-45.67,
                description="Amazon.com",
                merchant_name="Amazon",
                category=TransactionCategory.PURCHASE
            )
        ]
    
    def get_balance(self, access_token: str, account_id: str) -> float:
        """Get account balance from Plaid"""
        accounts = self.get_accounts(access_token)
        for account in accounts:
            if account.account_id == account_id:
                return account.current_balance
        return 0.0
    
    def get_liabilities(self, access_token: str) -> Dict[str, Any]:
        """Get liabilities (credit cards, loans)"""
        # In production:
        # from plaid.model.liabilities_get_request import LiabilitiesGetRequest
        # request = LiabilitiesGetRequest(access_token=access_token)
        # response = client.liabilities_get(request)
        
        return {
            'credit_cards': [],
            'student_loans': [],
            'mortgages': []
        }


class YodleeConnector(BankingConnection):
    """
    Yodlee banking API connector.
    """
    
    def __init__(
        self,
        client_id: str,
        secret: str
    ):
        super().__init__(client_id, secret, BankType.YODLEE)
    
    def create_link_token(self, user_id: str) -> str:
        """Create Yodlee FastLink token"""
        return f"yodlee-link-{uuid.uuid4()}"
    
    def exchange_public_token(self, public_token: str) -> str:
        """Exchange token"""
        return f"yodlee-access-{uuid.uuid4()}"
    
    def get_accounts(self, access_token: str) -> List[BankAccount]:
        """Get Yodlee accounts"""
        return []
    
    def get_transactions(
        self,
        access_token: str,
        account_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get Yodlee transactions"""
        return []
    
    def get_balance(self, access_token: str, account_id: str) -> float:
        """Get account balance"""
        return 0.0


class NetWorthTracker:
    """
    Tracks net worth across all connected accounts.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("net_worth_tracker")
        self.connections: Dict[str, BankingConnection] = {}
        self.user_tokens: Dict[str, Dict[str, str]] = {}  # user_id -> {bank_type -> access_token}
    
    def add_connection(
        self,
        user_id: str,
        bank_type: BankType,
        access_token: str,
        connection: BankingConnection
    ):
        """Add a banking connection for a user"""
        conn_key = f"{user_id}_{bank_type.value}"
        self.connections[conn_key] = connection
        
        if user_id not in self.user_tokens:
            self.user_tokens[user_id] = {}
        self.user_tokens[user_id][bank_type.value] = access_token
        
        self.logger.info(f"Added {bank_type.value} connection for user {user_id}")
    
    def calculate_net_worth(self, user_id: str) -> Dict[str, Any]:
        """Calculate user's net worth"""
        total_assets = 0.0
        total_liabilities = 0.0
        
        accounts_by_type = {
            'checking': [],
            'savings': [],
            'investment': [],
            'credit_cards': [],
            'loans': []
        }
        
        tokens = self.user_tokens.get(user_id, {})
        
        for bank_type_str, access_token in tokens.items():
            conn_key = f"{user_id}_{bank_type_str}"
            connection = self.connections.get(conn_key)
            
            if not connection:
                continue
            
            try:
                accounts = connection.get_accounts(access_token)
                
                for account in accounts:
                    balance = account.current_balance
                    
                    if account.account_type in [AccountType.CHECKING, AccountType.SAVINGS, AccountType.INVESTMENT]:
                        total_assets += balance
                        
                        if account.account_type == AccountType.CHECKING:
                            accounts_by_type['checking'].append(account.to_dict())
                        elif account.account_type == AccountType.SAVINGS:
                            accounts_by_type['savings'].append(account.to_dict())
                        else:
                            accounts_by_type['investment'].append(account.to_dict())
                    
                    elif account.account_type in [AccountType.CREDIT_CARD, AccountType.LOAN, AccountType.MORTGAGE]:
                        total_liabilities += abs(balance)
                        
                        if account.account_type == AccountType.CREDIT_CARD:
                            accounts_by_type['credit_cards'].append(account.to_dict())
                        else:
                            accounts_by_type['loans'].append(account.to_dict())
            
            except Exception as e:
                self.logger.error(f"Error getting accounts from {bank_type_str}: {e}")
        
        net_worth = total_assets - total_liabilities
        
        return {
            'user_id': user_id,
            'net_worth': net_worth,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'accounts': accounts_by_type,
            'calculated_at': datetime.now().isoformat()
        }
    
    def get_spending_analysis(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze spending patterns"""
        category_totals = {}
        merchant_totals = {}
        total_spent = 0.0
        
        tokens = self.user_tokens.get(user_id, {})
        
        for bank_type_str, access_token in tokens.items():
            conn_key = f"{user_id}_{bank_type_str}"
            connection = self.connections.get(conn_key)
            
            if not connection:
                continue
            
            try:
                transactions = connection.get_transactions(
                    access_token,
                    start_date=start_date,
                    end_date=end_date
                )
                
                for txn in transactions:
                    if txn.amount < 0:  # Spending
                        amount = abs(txn.amount)
                        total_spent += amount
                        
                        # By category
                        category = txn.category.value
                        category_totals[category] = category_totals.get(category, 0) + amount
                        
                        # By merchant
                        if txn.merchant_name:
                            merchant_totals[txn.merchant_name] = merchant_totals.get(txn.merchant_name, 0) + amount
            
            except Exception as e:
                self.logger.error(f"Error getting transactions: {e}")
        
        # Sort
        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:10]
        top_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'user_id': user_id,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_spent': total_spent,
            'by_category': dict(top_categories),
            'by_merchant': dict(top_merchants),
            'transaction_count': sum(1 for _ in category_totals)
        }
