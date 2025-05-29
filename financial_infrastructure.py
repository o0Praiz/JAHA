# JAH Agency - Financial Infrastructure System
# Version 1.0 | Autonomous Financial Management Framework

import logging
import threading
import time
import hashlib
import hmac
from collections import defaultdict, deque
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import sqlite3
import csv
from pathlib import Path

class AccountType(Enum):
    PRIMARY_REVENUE = "primary_revenue"
    OPERATIONAL_EXPENSE = "operational_expense"
    RESERVE = "reserve"
    INVESTMENT = "investment"

class TransactionType(Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionCategory(Enum):
    REVENUE = "revenue"
    OPERATIONAL_EXPENSE = "operational_expense"
    AGENT_COST = "agent_cost"
    INFRASTRUCTURE = "infrastructure"
    MARKETING = "marketing"
    DEVELOPMENT = "development"
    TRANSFER = "transfer"
    INVESTMENT = "investment"
    DISTRIBUTION = "distribution"

class ValidationStatus(Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"

@dataclass
class Account:
    account_id: str
    account_name: str
    account_type: AccountType
    current_balance: Decimal
    currency: str = "USD"
    account_number: Optional[str] = None
    institution_name: Optional[str] = None
    status: str = "active"
    creation_date: datetime = field(default_factory=datetime.now)
    last_transaction_date: Optional[datetime] = None

@dataclass
class FinancialTransaction:
    transaction_id: str
    account_id: str
    transaction_type: TransactionType
    amount: Decimal
    category: TransactionCategory
    subcategory: Optional[str]
    description: str
    reference_number: Optional[str]
    transaction_date: datetime
    processed_date: Optional[datetime]
    validation_status: ValidationStatus = ValidationStatus.PENDING
    related_task_id: Optional[str] = None
    related_project_id: Optional[str] = None
    related_agent_id: Optional[str] = None
    external_reference: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())

@dataclass
class FinancialReport:
    report_id: str
    report_type: str
    report_period_start: date
    report_period_end: date
    generated_date: datetime
    report_data: Dict[str, Any]
    summary_metrics: Dict[str, Any]
    generated_by_agent_id: Optional[str] = None
    approval_status: str = "draft"
    stakeholder_reviewed: bool = False

class DatabaseManager:
    """Manages SQLite database operations for financial data"""
    
    def __init__(self, db_path: str = "jah_financial.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize database with required tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Accounts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id TEXT PRIMARY KEY,
                    account_name TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    current_balance REAL NOT NULL DEFAULT 0.0,
                    currency TEXT DEFAULT 'USD',
                    account_number TEXT,
                    institution_name TEXT,
                    status TEXT DEFAULT 'active',
                    creation_date TEXT NOT NULL,
                    last_transaction_date TEXT
                )
            ''')
            
            # Financial transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_transactions (
                    transaction_id TEXT PRIMARY KEY,
                    account_id TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    description TEXT NOT NULL,
                    reference_number TEXT,
                    transaction_date TEXT NOT NULL,
                    processed_date TEXT,
                    validation_status TEXT DEFAULT 'pending',
                    related_task_id TEXT,
                    related_project_id TEXT,
                    related_agent_id TEXT,
                    external_reference TEXT,
                    metadata TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts (account_id)
                )
            ''')
            
            # Financial reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_reports (
                    report_id TEXT PRIMARY KEY,
                    report_type TEXT NOT NULL,
                    report_period_start TEXT NOT NULL,
                    report_period_end TEXT NOT NULL,
                    generated_date TEXT NOT NULL,
                    report_data TEXT NOT NULL,
                    summary_metrics TEXT,
                    generated_by_agent_id TEXT,
                    approval_status TEXT DEFAULT 'draft',
                    stakeholder_reviewed INTEGER DEFAULT 0
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_account ON financial_transactions(account_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON financial_transactions(transaction_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_category ON financial_transactions(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_type ON financial_reports(report_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_date ON financial_reports(generated_date)')
            
            conn.commit()
            conn.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute SELECT query and return results"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            return results
    
    def execute_update(self, query: str, params: Tuple = ()) -> bool:
        """Execute INSERT/UPDATE/DELETE query"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logging.error(f"Database update error: {str(e)}")
            return False

class TransactionProcessor:
    """Processes and validates financial transactions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.fraud_detection_rules = {
            'max_single_transaction': Decimal('10000.00'),
            'max_daily_total': Decimal('25000.00'),
            'suspicious_patterns': ['rapid_succession', 'round_amounts', 'unusual_times']
        }
        self.validation_rules = {
            'min_amount': Decimal('0.01'),
            'max_amount': Decimal('100000.00'),
            'required_fields': ['description', 'category', 'amount']
        }
        
    def process_transaction(self, transaction: FinancialTransaction) -> Dict[str, Any]:
        """Process a financial transaction with full validation"""
        try:
            # Validate transaction
            validation_result = self._validate_transaction(transaction)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': validation_result['errors'],
                    'transaction_id': transaction.transaction_id
                }
            
            # Fraud detection
            fraud_check = self._perform_fraud_detection(transaction)
            if fraud_check['risk_level'] == 'high':
                transaction.validation_status = ValidationStatus.REQUIRES_REVIEW
                return {
                    'success': False,
                    'error': 'Transaction flagged for fraud review',
                    'fraud_details': fraud_check,
                    'transaction_id': transaction.transaction_id
                }
            
            # Process the transaction
            processing_result = self._execute_transaction(transaction)
            
            if processing_result['success']:
                # Update account balance
                self._update_account_balance(transaction)
                transaction.processed_date = datetime.now()
                transaction.validation_status = ValidationStatus.VALIDATED
                
                # Store in database
                self._store_transaction(transaction)
                
                return {
                    'success': True,
                    'transaction_id': transaction.transaction_id,
                    'new_balance': processing_result['new_balance'],
                    'processed_date': transaction.processed_date
                }
            else:
                transaction.validation_status = ValidationStatus.REJECTED
                self._store_transaction(transaction)  # Store failed transaction for audit
                return {
                    'success': False,
                    'error': processing_result['error'],
                    'transaction_id': transaction.transaction_id
                }
                
        except Exception as e:
            logging.error(f"Transaction processing error: {str(e)}")
            return {
                'success': False,
                'error': f"Processing exception: {str(e)}",
                'transaction_id': transaction.transaction_id
            }
    
    def _validate_transaction(self, transaction: FinancialTransaction) -> Dict[str, Any]:
        """Validate transaction data and business rules"""
        errors = []
        
        # Check required fields
        for field in self.validation_rules['required_fields']:
            if not getattr(transaction, field, None):
                errors.append(f"Missing required field: {field}")
        
        # Validate amount
        if transaction.amount < self.validation_rules['min_amount']:
            errors.append(f"Amount below minimum: {self.validation_rules['min_amount']}")
        
        if transaction.amount > self.validation_rules['max_amount']:
            errors.append(f"Amount exceeds maximum: {self.validation_rules['max_amount']}")
        
        # Validate account exists
        account_exists = self._check_account_exists(transaction.account_id)
        if not account_exists:
            errors.append(f"Account not found: {transaction.account_id}")
        
        # Validate sufficient balance for debits
        if transaction.transaction_type == TransactionType.DEBIT:
            balance_check = self._check_sufficient_balance(transaction.account_id, transaction.amount)
            if not balance_check['sufficient']:
                errors.append(f"Insufficient balance. Available: {balance_check['available']}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _perform_fraud_detection(self, transaction: FinancialTransaction) -> Dict[str, Any]:
        """Perform fraud detection analysis"""
        risk_score = 0
        risk_factors = []
        
        # Check transaction amount
        if transaction.amount > self.fraud_detection_rules['max_single_transaction']:
            risk_score += 30
            risk_factors.append('large_amount')
        
        # Check daily total
        daily_total = self._get_daily_transaction_total(transaction.account_id, transaction.transaction_date.date())
        if daily_total + transaction.amount > self.fraud_detection_rules['max_daily_total']:
            risk_score += 25
            risk_factors.append('high_daily_total')
        
        # Check for suspicious patterns
        if self._detect_rapid_succession(transaction):
            risk_score += 20
            risk_factors.append('rapid_succession')
        
        if self._is_round_amount(transaction.amount):
            risk_score += 5
            risk_factors.append('round_amount')
        
        if self._is_unusual_time(transaction.transaction_date):
            risk_score += 10
            risk_factors.append('unusual_time')
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 25:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors
        }
    
    def _execute_transaction(self, transaction: FinancialTransaction) -> Dict[str, Any]:
        """Execute the actual transaction"""
        try:
            # Get current account balance
            current_balance = self._get_account_balance(transaction.account_id)
            
            # Calculate new balance
            if transaction.transaction_type == TransactionType.CREDIT:
                new_balance = current_balance + transaction.amount
            else:  # DEBIT
                new_balance = current_balance - transaction.amount
            
            # Additional validation for negative balance
            if new_balance < 0 and not self._allow_negative_balance(transaction.account_id):
                return {
                    'success': False,
                    'error': 'Transaction would result in negative balance'
                }
            
            return {
                'success': True,
                'new_balance': new_balance,
                'previous_balance': current_balance
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Execution error: {str(e)}"
            }
    
    def _update_account_balance(self, transaction: FinancialTransaction) -> None:
        """Update account balance after successful transaction"""
        current_balance = self._get_account_balance(transaction.account_id)
        
        if transaction.transaction_type == TransactionType.CREDIT:
            new_balance = current_balance + transaction.amount
        else:
            new_balance = current_balance - transaction.amount
        
        update_query = '''
            UPDATE accounts 
            SET current_balance = ?, last_transaction_date = ? 
            WHERE account_id = ?
        '''
        self.db_manager.execute_update(
            update_query, 
            (float(new_balance), transaction.transaction_date.isoformat(), transaction.account_id)
        )
    
    def _store_transaction(self, transaction: FinancialTransaction) -> None:
        """Store transaction in database"""
        insert_query = '''
            INSERT INTO financial_transactions 
            (transaction_id, account_id, transaction_type, amount, category, subcategory,
             description, reference_number, transaction_date, processed_date, validation_status,
             related_task_id, related_project_id, related_agent_id, external_reference, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        self.db_manager.execute_update(insert_query, (
            transaction.transaction_id,
            transaction.account_id,
            transaction.transaction_type.value,
            float(transaction.amount),
            transaction.category.value,
            transaction.subcategory,
            transaction.description,
            transaction.reference_number,
            transaction.transaction_date.isoformat(),
            transaction.processed_date.isoformat() if transaction.processed_date else None,
            transaction.validation_status.value,
            transaction.related_task_id,
            transaction.related_project_id,
            transaction.related_agent_id,
            transaction.external_reference,
            json.dumps(transaction.metadata)
        ))
    
    def _check_account_exists(self, account_id: str) -> bool:
        """Check if account exists"""
        query = "SELECT COUNT(*) FROM accounts WHERE account_id = ?"
        result = self.db_manager.execute_query(query, (account_id,))
        return result[0][0] > 0 if result else False
    
    def _check_sufficient_balance(self, account_id: str, amount: Decimal) -> Dict[str, Any]:
        """Check if account has sufficient balance"""
        current_balance = self._get_account_balance(account_id)
        return {
            'sufficient': current_balance >= amount,
            'available': current_balance,
            'requested': amount
        }
    
    def _get_account_balance(self, account_id: str) -> Decimal:
        """Get current account balance"""
        query = "SELECT current_balance FROM accounts WHERE account_id = ?"
        result = self.db_manager.execute_query(query, (account_id,))
        return Decimal(str(result[0][0])) if result else Decimal('0')
    
    def _get_daily_transaction_total(self, account_id: str, transaction_date: date) -> Decimal:
        """Get total transaction amount for account on specific date"""
        query = '''
            SELECT COALESCE(SUM(amount), 0) FROM financial_transactions 
            WHERE account_id = ? AND DATE(transaction_date) = ? AND validation_status = 'validated'
        '''
        result = self.db_manager.execute_query(query, (account_id, transaction_date.isoformat()))
        return Decimal(str(result[0][0])) if result else Decimal('0')
    
    def _detect_rapid_succession(self, transaction: FinancialTransaction) -> bool:
        """Detect if transaction is part of rapid succession"""
        # Check for transactions in last 5 minutes
        five_minutes_ago = transaction.transaction_date - timedelta(minutes=5)
        query = '''
            SELECT COUNT(*) FROM financial_transactions 
            WHERE account_id = ? AND transaction_date >= ? AND transaction_date <= ?
        '''
        result = self.db_manager.execute_query(query, (
            transaction.account_id,
            five_minutes_ago.isoformat(),
            transaction.transaction_date.isoformat()
        ))
        return result[0][0] > 3 if result else False
    
    def _is_round_amount(self, amount: Decimal) -> bool:
        """Check if amount is suspiciously round"""
        return amount % 100 == 0 and amount >= 1000
    
    def _is_unusual_time(self, transaction_time: datetime) -> bool:
        """Check if transaction time is unusual (outside business hours)"""
        hour = transaction_time.hour
        day_of_week = transaction_time.weekday()
        
        # Weekends or outside 6 AM - 10 PM
        return day_of_week >= 5 or hour < 6 or hour > 22
    
    def _allow_negative_balance(self, account_id: str) -> bool:
        """Check if account allows negative balance"""
        # For now, only allow negative balance for operational accounts
        query = "SELECT account_type FROM accounts WHERE account_id = ?"
        result = self.db_manager.execute_query(query, (account_id,))
        if result:
            account_type = result[0][0]
            return account_type == AccountType.OPERATIONAL_EXPENSE.value
        return False

class AccountManager:
    """Manages financial accounts and account operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.accounts_cache = {}
        self.cache_lock = threading.Lock()
        self._load_accounts_cache()
    
    def create_account(self, account_name: str, account_type: AccountType, 
                      initial_balance: Decimal = Decimal('0'), **kwargs) -> str:
        """Create a new financial account"""
        try:
            account_id = str(uuid.uuid4())
            account = Account(
                account_id=account_id,
                account_name=account_name,
                account_type=account_type,
                current_balance=initial_balance,
                **kwargs
            )
            
            # Store in database
            insert_query = '''
                INSERT INTO accounts 
                (account_id, account_name, account_type, current_balance, currency,
                 account_number, institution_name, status, creation_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            success = self.db_manager.execute_update(insert_query, (
                account.account_id,
                account.account_name,
                account.account_type.value,
                float(account.current_balance),
                account.currency,
                account.account_number,
                account.institution_name,
                account.status,
                account.creation_date.isoformat()
            ))
            
            if success:
                # Update cache
                with self.cache_lock:
                    self.accounts_cache[account_id] = account
                logging.info(f"Account created: {account_name} ({account_id})")
                return account_id
            else:
                raise Exception("Failed to create account in database")
                
        except Exception as e:
            logging.error(f"Account creation error: {str(e)}")
            return ""
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        with self.cache_lock:
            if account_id in self.accounts_cache:
                return self.accounts_cache[account_id]
        
        # Load from database
        query = "SELECT * FROM accounts WHERE account_id = ?"
        result = self.db_manager.execute_query(query, (account_id,))
        
        if result:
            row = result[0]
            account = Account(
                account_id=row[0],
                account_name=row[1],
                account_type=AccountType(row[2]),
                current_balance=Decimal(str(row[3])),
                currency=row[4],
                account_number=row[5],
                institution_name=row[6],
                status=row[7],
                creation_date=datetime.fromisoformat(row[8]),
                last_transaction_date=datetime.fromisoformat(row[9]) if row[9] else None
            )
            
            # Update cache
            with self.cache_lock:
                self.accounts_cache[account_id] = account
            
            return account
        
        return None
    
    def get_accounts_by_type(self, account_type: AccountType) -> List[Account]:
        """Get all accounts of specific type"""
        query = "SELECT * FROM accounts WHERE account_type = ? AND status = 'active'"
        results = self.db_manager.execute_query(query, (account_type.value,))
        
        accounts = []
        for row in results:
            account = Account(
                account_id=row[0],
                account_name=row[1],
                account_type=AccountType(row[2]),
                current_balance=Decimal(str(row[3])),
                currency=row[4],
                account_number=row[5],
                institution_name=row[6],
                status=row[7],
                creation_date=datetime.fromisoformat(row[8]),
                last_transaction_date=datetime.fromisoformat(row[9]) if row[9] else None
            )
            accounts.append(account)
        
        return accounts
    
    def update_account_balance(self, account_id: str, new_balance: Decimal) -> bool:
        """Update account balance"""
        query = "UPDATE accounts SET current_balance = ? WHERE account_id = ?"
        success = self.db_manager.execute_update(query, (float(new_balance), account_id))
        
        if success:
            # Update cache
            with self.cache_lock:
                if account_id in self.accounts_cache:
                    self.accounts_cache[account_id].current_balance = new_balance
        
        return success
    
    def get_account_summary(self) -> Dict[str, Any]:
        """Get summary of all accounts"""
        summary = {
            'total_accounts': 0,
            'accounts_by_type': {},
            'total_balance_by_type': {},
            'account_details': []
        }
        
        query = "SELECT * FROM accounts WHERE status = 'active'"
        results = self.db_manager.execute_query(query)
        
        for row in results:
            account_type = row[2]
            balance = Decimal(str(row[3]))
            
            summary['total_accounts'] += 1
            
            if account_type not in summary['accounts_by_type']:
                summary['accounts_by_type'][account_type] = 0
                summary['total_balance_by_type'][account_type] = Decimal('0')
            
            summary['accounts_by_type'][account_type] += 1
            summary['total_balance_by_type'][account_type] += balance
            
            summary['account_details'].append({
                'account_id': row[0],
                'account_name': row[1],
                'account_type': account_type,
                'current_balance': float(balance),
                'currency': row[4],
                'creation_date': row[8]
            })
        
        # Convert Decimal to float for JSON serialization
        for account_type in summary['total_balance_by_type']:
            summary['total_balance_by_type'][account_type] = float(summary['total_balance_by_type'][account_type])
        
        return summary
    
    def _load_accounts_cache(self) -> None:
        """Load accounts into cache"""
        query = "SELECT * FROM accounts WHERE status = 'active'"
        results = self.db_manager.execute_query(query)
        
        with self.cache_lock:
            for row in results:
                account = Account(
                    account_id=row[0],
                    account_name=row[1],
                    account_type=AccountType(row[2]),
                    current_balance=Decimal(str(row[3])),
                    currency=row[4],
                    account_number=row[5],
                    institution_name=row[6],
                    status=row[7],
                    creation_date=datetime.fromisoformat(row[8]),
                    last_transaction_date=datetime.fromisoformat(row[9]) if row[9] else None
                )
                self.accounts_cache[account.account_id] = account

class FinancialReportingSystem:
    """Generates automated financial reports and analytics"""
    
    def __init__(self, db_manager: DatabaseManager, account_manager: AccountManager):
        self.db_manager = db_manager
        self.account_manager = account_manager
    
    def generate_weekly_financial_statement(self, end_date: date = None) -> FinancialReport:
        """Generate comprehensive weekly financial statement"""
        if end_date is None:
            end_date = date.today()
        
        start_date = end_date - timedelta(days=7)
        
        try:
            # Collect financial data for the period
            transactions = self._get_transactions_for_period(start_date, end_date)
            account_balances = self._get_account_balances_summary()
            
            # Generate profit & loss analysis
            profit_loss = self._generate_profit_loss_analysis(transactions)
            
            # Generate cash flow analysis
            cash_flow = self._generate_cash_flow_analysis(transactions)
            
            # Generate expense analysis
            expense_analysis = self._generate_expense_analysis(transactions)
            
            # Generate revenue analysis
            revenue_analysis = self._generate_revenue_analysis(transactions)
            
            # Calculate key metrics
            key_metrics = self._calculate_key_metrics(transactions, account_balances)
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                profit_loss, cash_flow, key_metrics
            )
            
            # Compile report data
            report_data = {
                'executive_summary': executive_summary,
                'profit_loss_statement': profit_loss,
                'cash_flow_statement': cash_flow,
                'expense_analysis': expense_analysis,
                'revenue_analysis': revenue_analysis,
                'account_balances': account_balances,
                'key_metrics': key_metrics,
                'transaction_count': len(transactions),
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
            
            # Create summary metrics
            summary_metrics = {
                'total_revenue': profit_loss.get('total_revenue', 0),
                'total_expenses': profit_loss.get('total_expenses', 0),
                'net_profit': profit_loss.get('net_profit', 0),
                'profit_margin': key_metrics.get('profit_margin', 0),
                'cash_flow_net': cash_flow.get('net_cash_flow', 0),
                'transaction_volume': len(transactions)
            }
            
            # Create report object
            report = FinancialReport(
                report_id=str(uuid.uuid4()),
                report_type="weekly_financial_statement",
                report_period_start=start_date,
                report_period_end=end_date,
                generated_date=datetime.now(),
                report_data=report_data,
                summary_metrics=summary_metrics,
                generated_by_agent_id="financial_reporting_system"
            )
            
            # Store report
            self._store_report(report)
            
            logging.info(f"Weekly financial statement generated for period {start_date} to {end_date}")
            return report
            
        except Exception as e:
            logging.error(f"Weekly report generation error: {str(e)}")
            # Return empty report with error info
            return FinancialReport(
                report_id=str(uuid.uuid4()),
                report_type="weekly_financial_statement",
                report_period_start=start_date,
                report_period_end=end_date,
                generated_date=datetime.now(),
                report_data={'error': str(e)},
                summary_metrics={}
            )
    
    def _get_transactions_for_period(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get all validated transactions for specified period"""
        query = '''
            SELECT * FROM financial_transactions 
            WHERE DATE(transaction_date) >= ? AND DATE(transaction_date) <= ?
            AND validation_status = 'validated'
            ORDER BY transaction_date
        '''
        
        results = self.db_manager.execute_query(query, (start_date.isoformat(), end_date.isoformat()))
        
        transactions = []
        for row in results:
            transaction = {
                'transaction_id': row[0],
                'account_id': row[1],
                'transaction_type': row[2],
                'amount': Decimal(str(row[3])),
                'category': row[4],
                'subcategory': row[5],
                'description': row[6],
                'reference_number': row[7],
                'transaction_date': datetime.fromisoformat(row[8]),
                'processed_date': datetime.fromisoformat(row[9]) if row[9] else None,
                'validation_status': row[10],
                'related_task_id': row[11],
                'related_project_id': row[12],
                'related_agent_id': row[13],
                'external_reference': row[14],
                'metadata': json.loads(row[15]) if row[15] else {}
            }
            transactions.append(transaction)
        
        return transactions
    
    def _get_account_balances_summary(self) -> Dict[str, Any]:
        """Get current account balances summary"""
        return self.account_manager.get_account_summary()
    
    def _generate_profit_loss_analysis(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate profit and loss analysis"""
        revenue_categories = [TransactionCategory.REVENUE.value]
        expense_categories = [
            TransactionCategory.OPERATIONAL_EXPENSE.value,
            TransactionCategory.AGENT_COST.value,
            TransactionCategory.INFRASTRUCTURE.value,
            TransactionCategory.MARKETING.value,
            TransactionCategory.DEVELOPMENT.value
        ]
        
        total_revenue = Decimal('0')
        total_expenses = Decimal('0')
        revenue_breakdown = defaultdict(Decimal)
        expense_breakdown = defaultdict(Decimal)
        
        for transaction in transactions:
            amount = transaction['amount']
            category = transaction['category']
            subcategory = transaction['subcategory'] or 'Other'
            
            if category in revenue_categories:
                if transaction['transaction_type'] == 'credit':
                    total_revenue += amount
                    revenue_breakdown[subcategory] += amount
                else:
                    total_revenue -= amount
                    revenue_breakdown[subcategory] -= amount
            
            elif category in expense_categories:
                if transaction['transaction_type'] == 'debit':
                    total_expenses += amount
                    expense_breakdown[f"{category}_{subcategory}"] += amount
                else:
                    total_expenses -= amount
                    expense_breakdown[f"{category}_{subcategory}"] -= amount
        
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0')
        
        return {
            'total_revenue': float(total_revenue),
            'total_expenses': float(total_expenses),
            'net_profit': float(net_profit),
            'profit_margin': float(profit_margin),
            'revenue_breakdown': {k: float(v) for k, v in revenue_breakdown.items()},
            'expense_breakdown': {k: float(v) for k, v in expense_breakdown.items()}
        }
    
    def _generate_cash_flow_analysis(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate cash flow analysis"""
        cash_inflows = Decimal('0')
        cash_outflows = Decimal('0')
        daily_cash_flow = defaultdict(Decimal)
        
        for transaction in transactions:
            amount = transaction['amount']
            transaction_date = transaction['transaction_date'].date()
            
            if transaction['transaction_type'] == 'credit':
                cash_inflows += amount
                daily_cash_flow[transaction_date.isoformat()] += amount
            else:
                cash_outflows += amount
                daily_cash_flow[transaction_date.isoformat()] -= amount
        
        net_cash_flow = cash_inflows - cash_outflows
        
        return {
            'cash_inflows': float(cash_inflows),
            'cash_outflows': float(cash_outflows),
            'net_cash_flow': float(net_cash_flow),
            'daily_cash_flow': {k: float(v) for k, v in daily_cash_flow.items()}
        }
    
    def _generate_expense_analysis(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed expense analysis"""
        expense_by_category = defaultdict(Decimal)
        expense_by_agent = defaultdict(Decimal)
        expense_by_project = defaultdict(Decimal)
        
        expense_categories = [
            TransactionCategory.OPERATIONAL_EXPENSE.value,
            TransactionCategory.AGENT_COST.value,
            TransactionCategory.INFRASTRUCTURE.value,
            TransactionCategory.MARKETING.value,
            TransactionCategory.DEVELOPMENT.value
        ]
        
        for transaction in transactions:
            if (transaction['category'] in expense_categories and 
                transaction['transaction_type'] == 'debit'):
                
                amount = transaction['amount']
                category = transaction['category']
                agent_id = transaction['related_agent_id']
                project_id = transaction['related_project_id']
                
                expense_by_category[category] += amount
                
                if agent_id:
                    expense_by_agent[agent_id] += amount
                
                if project_id:
                    expense_by_project[project_id] += amount
        
        return {
            'expense_by_category': {k: float(v) for k, v in expense_by_category.items()},
            'expense_by_agent': {k: float(v) for k, v in expense_by_agent.items()},
            'expense_by_project': {k: float(v) for k, v in expense_by_project.items()},
            'total_expenses': float(sum(expense_by_category.values()))
        }
    
    def _generate_revenue_analysis(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed revenue analysis"""
        revenue_by_source = defaultdict(Decimal)
        revenue_by_agent = defaultdict(Decimal)
        revenue_by_project = defaultdict(Decimal)
        
        for transaction in transactions:
            if (transaction['category'] == TransactionCategory.REVENUE.value and
                transaction['transaction_type'] == 'credit'):
                
                amount = transaction['amount']
                subcategory = transaction['subcategory'] or 'Direct'
                agent_id = transaction['related_agent_id']
                project_id = transaction['related_project_id']
                
                revenue_by_source[subcategory] += amount
                
                if agent_id:
                    revenue_by_agent[agent_id] += amount
                
                if project_id:
                    revenue_by_project[project_id] += amount
        
        return {
            'revenue_by_source': {k: float(v) for k, v in revenue_by_source.items()},
            'revenue_by_agent': {k: float(v) for k, v in revenue_by_agent.items()},
            'revenue_by_project': {k: float(v) for k, v in revenue_by_project.items()},
            'total_revenue': float(sum(revenue_by_source.values()))
        }
    
    def _calculate_key_metrics(self, transactions: List[Dict[str, Any]], 
                             account_balances: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key financial metrics"""
        total_revenue = sum(
            float(t['amount']) for t in transactions 
            if t['category'] == TransactionCategory.REVENUE.value and t['transaction_type'] == 'credit'
        )
        
        total_expenses = sum(
            float(t['amount']) for t in transactions 
            if t['category'] in [
                TransactionCategory.OPERATIONAL_EXPENSE.value,
                TransactionCategory.AGENT_COST.value,
                TransactionCategory.INFRASTRUCTURE.value,
                TransactionCategory.MARKETING.value,
                TransactionCategory.DEVELOPMENT.value
            ] and t['transaction_type'] == 'debit'
        )
        
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Calculate total assets (account balances)
        total_assets = sum(
            account['current_balance'] for account in account_balances.get('account_details', [])
        )
        
        # ROA (Return on Assets)
        roa = (net_profit / total_assets * 100) if total_assets > 0 else 0
        
        return {
            'profit_margin': round(profit_margin, 2),
            'return_on_assets': round(roa, 2),
            'total_assets': round(total_assets, 2),
            'revenue_growth': 0,  # Would calculate from historical data
            'expense_ratio': round((total_expenses / total_revenue * 100) if total_revenue > 0 else 0, 2),
            'transaction_volume': len(transactions)
        }
    
    def _generate_executive_summary(self, profit_loss: Dict[str, Any], 
                                  cash_flow: Dict[str, Any], 
                                  key_metrics: Dict[str, Any]) -> str:
        """Generate executive summary text"""
        net_profit = profit_loss.get('net_profit', 0)
        profit_margin = key_metrics.get('profit_margin', 0)
        net_cash_flow = cash_flow.get('net_cash_flow', 0)
        
        performance_status = "profitable" if net_profit > 0 else "loss-making"
        cash_status = "positive" if net_cash_flow > 0 else "negative"
        
        summary = f"""
        Financial Performance Summary:
        
        • Business is currently {performance_status} with a net profit of ${net_profit:,.2f}
        • Profit margin stands at {profit_margin:.1f}%
        • Cash flow is {cash_status} at ${net_cash_flow:,.2f}
        • Total revenue: ${profit_loss.get('total_revenue', 0):,.2f}
        • Total expenses: ${profit_loss.get('total_expenses', 0):,.2f}
        • Return on assets: {key_metrics.get('return_on_assets', 0):.1f}%
        
        Key Insights:
        • Expense ratio: {key_metrics.get('expense_ratio', 0):.1f}%
        • Transaction volume: {key_metrics.get('transaction_volume', 0)} transactions
        """
        
        return summary.strip()
    
    def _store_report(self, report: FinancialReport) -> None:
        """Store financial report in database"""
        insert_query = '''
            INSERT INTO financial_reports 
            (report_id, report_type, report_period_start, report_period_end, 
             generated_date, report_data, summary_metrics, generated_by_agent_id,
             approval_status, stakeholder_reviewed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        self.db_manager.execute_update(insert_query, (
            report.report_id,
            report.report_type,
            report.report_period_start.isoformat(),
            report.report_period_end.isoformat(),
            report.generated_date.isoformat(),
            json.dumps(report.report_data, default=str),
            json.dumps(report.summary_metrics, default=str),
            report.generated_by_agent_id,
            report.approval_status,
            1 if report.stakeholder_reviewed else 0
        ))

class FinancialInfrastructureSystem:
    """Main financial infrastructure system coordinating all components"""
    
    def __init__(self, db_path: str = "jah_financial.db"):
        # Initialize core components
        self.db_manager = DatabaseManager(db_path)
        self.account_manager = AccountManager(self.db_manager)
        self.transaction_processor = TransactionProcessor(self.db_manager)
        self.reporting_system = FinancialReportingSystem(self.db_manager, self.account_manager)
        
        # System state
        self.system_initialized = False
        self.primary_revenue_account_id = None
        self.operational_expense_account_id = None
        
        # Performance metrics
        self.metrics = {
            'total_transactions_processed': 0,
            'successful_transactions': 0,
            'failed_transactions': 0,
            'total_revenue_generated': Decimal('0'),
            'total_expenses_processed': Decimal('0'),
            'reports_generated': 0
        }
        
        self.logger = logging.getLogger("FinancialInfrastructure")
        
        # Initialize default accounts
        self._initialize_default_accounts()
    
    def _initialize_default_accounts(self) -> None:
        """Initialize default account structure"""
        try:
            # Check if accounts already exist
            primary_accounts = self.account_manager.get_accounts_by_type(AccountType.PRIMARY_REVENUE)
            operational_accounts = self.account_manager.get_accounts_by_type(AccountType.OPERATIONAL_EXPENSE)
            
            # Create primary revenue account if not exists
            if not primary_accounts:
                self.primary_revenue_account_id = self.account_manager.create_account(
                    account_name="JAH Agency Primary Revenue Account",
                    account_type=AccountType.PRIMARY_REVENUE,
                    initial_balance=Decimal('0'),
                    currency="USD"
                )
                self.logger.info(f"Created primary revenue account: {self.primary_revenue_account_id}")
            else:
                self.primary_revenue_account_id = primary_accounts[0].account_id
            
            # Create operational expense account if not exists
            if not operational_accounts:
                self.operational_expense_account_id = self.account_manager.create_account(
                    account_name="JAH Agency Operational Expense Account",
                    account_type=AccountType.OPERATIONAL_EXPENSE,
                    initial_balance=Decimal('1000'),  # Initial operational funds
                    currency="USD"
                )
                self.logger.info(f"Created operational expense account: {self.operational_expense_account_id}")
            else:
                self.operational_expense_account_id = operational_accounts[0].account_id
            
            # Create reserve account
            reserve_accounts = self.account_manager.get_accounts_by_type(AccountType.RESERVE)
            if not reserve_accounts:
                reserve_account_id = self.account_manager.create_account(
                    account_name="JAH Agency Reserve Fund",
                    account_type=AccountType.RESERVE,
                    initial_balance=Decimal('0'),
                    currency="USD"
                )
                self.logger.info(f"Created reserve account: {reserve_account_id}")
            
            self.system_initialized = True
            self.logger.info("Financial infrastructure system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing default accounts: {str(e)}")
    
    def process_revenue_transaction(self, amount: Decimal, description: str, 
                                  source: str = "Direct", **kwargs) -> Dict[str, Any]:
        """Process incoming revenue transaction"""
        try:
            transaction = FinancialTransaction(
                transaction_id=str(uuid.uuid4()),
                account_id=self.primary_revenue_account_id,
                transaction_type=TransactionType.CREDIT,
                amount=amount,
                category=TransactionCategory.REVENUE,
                subcategory=source,
                description=description,
                transaction_date=datetime.now(),
                **kwargs
            )
            
            result = self.transaction_processor.process_transaction(transaction)
            
            if result['success']:
                self.metrics['successful_transactions'] += 1
                self.metrics['total_revenue_generated'] += amount
            else:
                self.metrics['failed_transactions'] += 1
            
            self.metrics['total_transactions_processed'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Revenue transaction processing error: {str(e)}")
            return {
                'success': False,
                'error': f"Processing exception: {str(e)}"
            }
    
    def process_expense_transaction(self, amount: Decimal, description: str, 
                                  expense_type: str = "Operational", **kwargs) -> Dict[str, Any]:
        """Process outgoing expense transaction"""
        try:
            # Determine appropriate expense category
            category_mapping = {
                'operational': TransactionCategory.OPERATIONAL_EXPENSE,
                'agent': TransactionCategory.AGENT_COST,
                'infrastructure': TransactionCategory.INFRASTRUCTURE,
                'marketing': TransactionCategory.MARKETING,
                'development': TransactionCategory.DEVELOPMENT
            }
            
            category = category_mapping.get(expense_type.lower(), TransactionCategory.OPERATIONAL_EXPENSE)
            
            transaction = FinancialTransaction(
                transaction_id=str(uuid.uuid4()),
                account_id=self.operational_expense_account_id,
                transaction_type=TransactionType.DEBIT,
                amount=amount,
                category=category,
                subcategory=expense_type,
                description=description,
                transaction_date=datetime.now(),
                **kwargs
            )
            
            result = self.transaction_processor.process_transaction(transaction)
            
            if result['success']:
                self.metrics['successful_transactions'] += 1
                self.metrics['total_expenses_processed'] += amount
            else:
                self.metrics['failed_transactions'] += 1
            
            self.metrics['total_transactions_processed'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Expense transaction processing error: {str(e)}")
            return {
                'success': False,
                'error': f"Processing exception: {str(e)}"
            }
    
    def transfer_between_accounts(self, from_account_id: str, to_account_id: str, 
                                amount: Decimal, description: str) -> Dict[str, Any]:
        """Transfer funds between accounts"""
        try:
            # Create debit transaction
            debit_transaction = FinancialTransaction(
                transaction_id=str(uuid.uuid4()),
                account_id=from_account_id,
                transaction_type=TransactionType.DEBIT,
                amount=amount,
                category=TransactionCategory.TRANSFER,
                subcategory="Internal Transfer",
                description=f"Transfer to {to_account_id}: {description}",
                transaction_date=datetime.now()
            )
            
            debit_result = self.transaction_processor.process_transaction(debit_transaction)
            
            if not debit_result['success']:
                return debit_result
            
            # Create credit transaction
            credit_transaction = FinancialTransaction(
                transaction_id=str(uuid.uuid4()),
                account_id=to_account_id,
                transaction_type=TransactionType.CREDIT,
                amount=amount,
                category=TransactionCategory.TRANSFER,
                subcategory="Internal Transfer",
                description=f"Transfer from {from_account_id}: {description}",
                transaction_date=datetime.now(),
                reference_number=debit_transaction.transaction_id
            )
            
            credit_result = self.transaction_processor.process_transaction(credit_transaction)
            
            if credit_result['success']:
                self.metrics['successful_transactions'] += 2
            else:
                self.metrics['failed_transactions'] += 1
                # TODO: Implement reversal of debit transaction
                
            self.metrics['total_transactions_processed'] += 2
            
            return {
                'success': credit_result['success'],
                'debit_transaction_id': debit_transaction.transaction_id,
                'credit_transaction_id': credit_transaction.transaction_id,
                'amount_transferred': float(amount)
            }
            
        except Exception as e:
            self.logger.error(f"Transfer processing error: {str(e)}")
            return {
                'success': False,
                'error': f"Transfer exception: {str(e)}"
            }
    
    def generate_weekly_report(self) -> FinancialReport:
        """Generate and return weekly financial report"""
        try:
            report = self.reporting_system.generate_weekly_financial_statement()
            self.metrics['reports_generated'] += 1
            return report
        except Exception as e:
            self.logger.error(f"Weekly report generation error: {str(e)}")
            raise
    
    def get_account_balances(self) -> Dict[str, Any]:
        """Get current account balances"""
        return self.account_manager.get_account_summary()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive financial system status"""
        account_summary = self.account_manager.get_account_summary()
        
        return {
            'system_initialized': self.system_initialized,
            'primary_revenue_account_id': self.primary_revenue_account_id,
            'operational_expense_account_id': self.operational_expense_account_id,
            'account_summary': account_summary,
            'performance_metrics': {
                'total_transactions_processed': self.metrics['total_transactions_processed'],
                'successful_transactions': self.metrics['successful_transactions'],
                'failed_transactions': self.metrics['failed_transactions'],
                'success_rate': (
                    self.metrics['successful_transactions'] / 
                    max(self.metrics['total_transactions_processed'], 1) * 100
                ),
                'total_revenue_generated': float(self.metrics['total_revenue_generated']),
                'total_expenses_processed': float(self.metrics['total_expenses_processed']),
                'net_position': float(
                    self.metrics['total_revenue_generated'] - 
                    self.metrics['total_expenses_processed']
                ),
                'reports_generated': self.metrics['reports_generated']
            },
            'timestamp': datetime.now().isoformat()
        }

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Initialize financial infrastructure
    print("Initializing JAH Agency Financial Infrastructure...")
    financial_system = FinancialInfrastructureSystem()
    
    # Process some sample transactions
    print("\nProcessing sample revenue transactions...")
    
    # Revenue from client work
    revenue_result1 = financial_system.process_revenue_transaction(
        amount=Decimal('2500.00'),
        description="Website development project completion",
        source="Client Services",
        related_project_id="project_001"
    )
    print(f"Revenue transaction 1: {'Success' if revenue_result1['success'] else 'Failed'}")
    
    # Revenue from marketplace
    revenue_result2 = financial_system.process_revenue_transaction(
        amount=Decimal('750.00'),
        description="Data analysis service",
        source="Marketplace",
        related_agent_id="data_agent_001"
    )
    print(f"Revenue transaction 2: {'Success' if revenue_result2['success'] else 'Failed'}")
    
    # Process some expenses
    print("\nProcessing sample expense transactions...")
    
    # Agent operational cost
    expense_result1 = financial_system.process_expense_transaction(
        amount=Decimal('150.00'),
        description="API usage costs for agent operations",
        expense_type="infrastructure",
        related_agent_id="technical_agent_001"
    )
    print(f"Expense transaction 1: {'Success' if expense_result1['success'] else 'Failed'}")
    
    # Marketing expense
    expense_result2 = financial_system.process_expense_transaction(
        amount=Decimal('300.00'),
        description="Social media advertising campaign",
        expense_type="marketing",
        related_agent_id="marketing_agent_001"
    )
    print(f"Expense transaction 2: {'Success' if expense_result2['success'] else 'Failed'}")
    
    # Get system status
    print("\nFinancial System Status:")
    status = financial_system.get_system_status()
    print(f"Total Transactions: {status['performance_metrics']['total_transactions_processed']}")
    print(f"Success Rate: {status['performance_metrics']['success_rate']:.1f}%")
    print(f"Total Revenue: ${status['performance_metrics']['total_revenue_generated']:,.2f}")
    print(f"Total Expenses: ${status['performance_metrics']['total_expenses_processed']:,.2f}")
    print(f"Net Position: ${status['performance_metrics']['net_position']:,.2f}")
    
    # Generate weekly report
    print("\nGenerating weekly financial report...")
    try:
        weekly_report = financial_system.generate_weekly_report()
        print("Weekly Report Generated Successfully!")
        print(f"Report ID: {weekly_report.report_id}")
        print(f"Net Profit: ${weekly_report.summary_metrics.get('net_profit', 0):,.2f}")
        print(f"Profit Margin: {weekly_report.summary_metrics.get('profit_margin', 0):.1f}%")
        
        # Print executive summary
        if 'executive_summary' in weekly_report.report_data:
            print("\nExecutive Summary:")
            print(weekly_report.report_data['executive_summary'])
            
    except Exception as e:
        print(f"Report generation failed: {str(e)}")
    
    # Display account balances
    print("\nCurrent Account Balances:")
    balances = financial_system.get_account_balances()
    for account_detail in balances.get('account_details', []):
        print(f"  {account_detail['account_name']}: ${account_detail['current_balance']:,.2f}")
