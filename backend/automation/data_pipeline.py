"""
Automated Data Pipeline

Implements ETL (Extract, Transform, Load) processes for financial data.
Automates data collection, cleaning, validation, and storage.

Features:
- Multi-source data extraction (APIs, files, databases)
- Data validation and quality checks
- Automated scheduling
- Error handling and logging
- Data versioning
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import yfinance as yf
from typing import List, Dict
import json
import sqlite3
from loguru import logger
import time
from dotenv import load_dotenv


load_dotenv()


class DataPipeline:
    """
    Automated ETL pipeline for financial data.
    
    Handles data extraction from multiple sources, transformation,
    validation, and loading into storage.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data pipeline.
        
        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.archive_dir = self.data_dir / "archive"
        
        # Create directories
        for dir_path in [self.raw_dir, self.processed_dir, self.archive_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / "portfolio_analysis.db"
        self.validation_results = []
        
    def extract_stock_data(self, 
                          tickers: List[str], 
                          period: str = "1y",
                          interval: str = "1d") -> pd.DataFrame:
        """
        Extract stock data from Yahoo Finance.
        
        Args:
            tickers: List of stock ticker symbols
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with stock data
        """
        logger.info(f"Extracting stock data for {len(tickers)} tickers...")
        
        all_data = []
        
        for ticker in tickers:
            try:
                logger.info(f"Fetching data for {ticker}")
                stock = yf.Ticker(ticker)
                df = stock.history(period=period, interval=interval)
                
                if not df.empty:
                    df['ticker'] = ticker
                    df['extracted_at'] = datetime.now()
                    all_data.append(df)
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error fetching {ticker}: {str(e)}")
                continue
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=False)
            logger.info(f"Extracted {len(combined_df)} records")
            return combined_df
        else:
            logger.warning("No data extracted")
            return pd.DataFrame()
    
    def extract_financial_news(self, 
                              keywords: List[str], 
                              max_articles: int = 100) -> pd.DataFrame:
        """
        Extract financial news articles.
        (This is a placeholder - in production, use News API or similar)
        
        Args:
            keywords: Search keywords
            max_articles: Maximum number of articles
            
        Returns:
            DataFrame with news articles
        """
        logger.info(f"Extracting news for keywords: {keywords}")
        
        # Placeholder: Generate sample news data
        # In production, integrate with News API, Alpha Vantage News, etc.
        
        news_data = {
            'date': pd.date_range(end=datetime.now(), periods=max_articles, freq='H'),
            'headline': [f"Financial news headline {i}" for i in range(max_articles)],
            'source': np.random.choice(['Reuters', 'Bloomberg', 'WSJ', 'FT'], max_articles),
            'keyword': np.random.choice(keywords, max_articles),
            'url': [f"https://example.com/article/{i}" for i in range(max_articles)],
            'extracted_at': datetime.now()
        }
        
        df = pd.DataFrame(news_data)
        logger.info(f"Extracted {len(df)} news articles")
        
        return df
    
    def extract_economic_indicators(self) -> pd.DataFrame:
        """
        Extract economic indicators.
        (Placeholder - integrate with FRED, World Bank, etc.)
        
        Returns:
            DataFrame with economic indicators
        """
        logger.info("Extracting economic indicators...")
        
        # Placeholder data
        dates = pd.date_range(end=datetime.now(), periods=60, freq='ME')
        
        indicators = {
            'date': dates,
            'gdp_growth': np.random.uniform(1, 4, len(dates)),
            'inflation_rate': np.random.uniform(1, 6, len(dates)),
            'unemployment_rate': np.random.uniform(3, 8, len(dates)),
            'interest_rate': np.random.uniform(0, 5, len(dates)),
            'consumer_confidence': np.random.uniform(80, 120, len(dates)),
            'extracted_at': datetime.now()
        }
        
        df = pd.DataFrame(indicators)
        logger.info(f"Extracted {len(df)} indicator records")
        
        return df
    
    def validate_data(self, df: pd.DataFrame, validation_rules: Dict) -> Dict:
        """
        Validate data quality.
        
        Args:
            df: DataFrame to validate
            validation_rules: Dictionary of validation rules
            
        Returns:
            Validation results
        """
        logger.info("Validating data...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(df),
            'checks': []
        }
        
        # Check for missing values
        missing_check = {
            'check': 'missing_values',
            'passed': True,
            'details': {}
        }
        
        for col in df.columns:
            missing_pct = df[col].isna().sum() / len(df) * 100
            missing_check['details'][col] = f"{missing_pct:.2f}%"
            
            if missing_pct > validation_rules.get('max_missing_pct', 10):
                missing_check['passed'] = False
        
        results['checks'].append(missing_check)
        
        # Check for duplicates
        duplicate_check = {
            'check': 'duplicates',
            'passed': True,
            'duplicates_found': df.duplicated().sum()
        }
        
        if duplicate_check['duplicates_found'] > 0:
            duplicate_check['passed'] = False
        
        results['checks'].append(duplicate_check)
        
        # Check data types
        dtype_check = {
            'check': 'data_types',
            'passed': True,
            'details': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        results['checks'].append(dtype_check)
        
        # Check value ranges (if specified)
        if 'value_ranges' in validation_rules:
            range_check = {
                'check': 'value_ranges',
                'passed': True,
                'violations': []
            }
            
            for col, (min_val, max_val) in validation_rules['value_ranges'].items():
                if col in df.columns:
                    violations = ((df[col] < min_val) | (df[col] > max_val)).sum()
                    if violations > 0:
                        range_check['passed'] = False
                        range_check['violations'].append({
                            'column': col,
                            'violations': int(violations)
                        })
            
            results['checks'].append(range_check)
        
        # Overall status
        results['all_passed'] = all(check.get('passed', True) for check in results['checks'])
        
        self.validation_results.append(results)
        
        logger.info(f"Validation complete. Status: {'PASSED' if results['all_passed'] else 'FAILED'}")
        
        return results
    
    def transform_stock_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw stock data.
        
        Args:
            df: Raw stock DataFrame
            
        Returns:
            Transformed DataFrame
        """
        logger.info("Transforming stock data...")
        
        df_transformed = df.copy()
        
        # Calculate returns
        df_transformed['daily_return'] = df_transformed.groupby('ticker')['Close'].pct_change()
        
        # Calculate moving averages
        df_transformed['ma_7'] = df_transformed.groupby('ticker')['Close'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        df_transformed['ma_30'] = df_transformed.groupby('ticker')['Close'].transform(
            lambda x: x.rolling(window=30, min_periods=1).mean()
        )
        
        # Calculate volatility
        df_transformed['volatility_30'] = df_transformed.groupby('ticker')['daily_return'].transform(
            lambda x: x.rolling(window=30, min_periods=1).std()
        )
        
        # Add technical indicators
        df_transformed['high_low_spread'] = df_transformed['High'] - df_transformed['Low']
        df_transformed['close_open_diff'] = df_transformed['Close'] - df_transformed['Open']
        
        logger.info("Transformation complete")
        
        return df_transformed
    
    def load_to_database(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
        """
        Load data into SQLite database.
        
        Args:
            df: DataFrame to load
            table_name: Name of the table
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
        """
        logger.info(f"Loading {len(df)} records to {table_name}...")
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            logger.info(f"Successfully loaded data to {table_name}")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
        finally:
            conn.close()
    
    def load_to_csv(self, df: pd.DataFrame, filename: str, archive: bool = True):
        """
        Load data to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Output filename
            archive: Whether to archive existing file
        """
        output_path = self.processed_dir / filename
        
        # Archive existing file if it exists
        if output_path.exists() and archive:
            archive_path = self.archive_dir / f"{output_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output_path.rename(archive_path)
            logger.info(f"Archived existing file to {archive_path}")
        
        # Save new file
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to {output_path}")
    
    def run_full_pipeline(self, config: Dict) -> Dict:
        """
        Run the complete ETL pipeline.
        
        Args:
            config: Pipeline configuration
            
        Returns:
            Pipeline execution results
        """
        logger.info("="*50)
        logger.info("STARTING AUTOMATED DATA PIPELINE")
        logger.info("="*50)
        
        start_time = datetime.now()
        results = {
            'start_time': start_time.isoformat(),
            'config': config,
            'stages': {}
        }
        
        try:
            # Stage 1: Extract
            logger.info("\nSTAGE 1: EXTRACTION")
            
            stock_data = None
            if config.get('extract_stocks', False):
                stock_data = self.extract_stock_data(
                    tickers=config.get('tickers', ['AAPL', 'GOOGL', 'MSFT']),
                    period=config.get('period', '1y')
                )
                self.load_to_csv(stock_data, 'raw_stock_data.csv')
                results['stages']['stock_extraction'] = {'records': len(stock_data)}
            
            news_data = None
            if config.get('extract_news', False):
                news_data = self.extract_financial_news(
                    keywords=config.get('news_keywords', ['stocks', 'market']),
                    max_articles=config.get('max_news', 100)
                )
                self.load_to_csv(news_data, 'raw_news_data.csv')
                results['stages']['news_extraction'] = {'records': len(news_data)}
            
            indicators_data = None
            if config.get('extract_indicators', False):
                indicators_data = self.extract_economic_indicators()
                self.load_to_csv(indicators_data, 'raw_economic_indicators.csv')
                results['stages']['indicators_extraction'] = {'records': len(indicators_data)}
            
            # Stage 2: Validate
            logger.info("\nSTAGE 2: VALIDATION")
            
            validation_rules = config.get('validation_rules', {'max_missing_pct': 10})
            
            if stock_data is not None and not stock_data.empty:
                stock_validation = self.validate_data(stock_data, validation_rules)
                results['stages']['stock_validation'] = stock_validation
            
            # Stage 3: Transform
            logger.info("\nSTAGE 3: TRANSFORMATION")
            
            if stock_data is not None and not stock_data.empty:
                transformed_stock = self.transform_stock_data(stock_data)
                self.load_to_csv(transformed_stock, 'transformed_stock_data.csv')
                results['stages']['stock_transformation'] = {'records': len(transformed_stock)}
            
            # Stage 4: Load
            logger.info("\nSTAGE 4: LOADING TO DATABASE")
            
            if stock_data is not None and not stock_data.empty:
                self.load_to_database(transformed_stock, 'stock_data', if_exists='replace')
            
            if news_data is not None and not news_data.empty:
                self.load_to_database(news_data, 'news_data', if_exists='replace')
            
            if indicators_data is not None and not indicators_data.empty:
                self.load_to_database(indicators_data, 'economic_indicators', if_exists='replace')
            
            results['status'] = 'SUCCESS'
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            results['status'] = 'FAILED'
            results['error'] = str(e)
        
        end_time = datetime.now()
        results['end_time'] = end_time.isoformat()
        results['duration_seconds'] = (end_time - start_time).total_seconds()
        
        # Save pipeline results
        results_path = self.processed_dir / f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("\n" + "="*50)
        logger.info(f"PIPELINE COMPLETED: {results['status']}")
        logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
        logger.info("="*50)
        
        return results


def create_pipeline_config() -> Dict:
    """Create default pipeline configuration."""
    
    config = {
        'extract_stocks': True,
        'extract_news': True,
        'extract_indicators': True,
        'tickers': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'],
        'period': '6mo',
        'news_keywords': ['stocks', 'market', 'earnings', 'investment'],
        'max_news': 50,
        'validation_rules': {
            'max_missing_pct': 10,
            'value_ranges': {
                'Close': (0, 10000),
                'Volume': (0, 1e12)
            }
        }
    }
    
    return config


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/data_pipeline.log", rotation="10 MB")
    
    # Create pipeline
    pipeline = DataPipeline(data_dir="data")
    
    # Create configuration
    config = create_pipeline_config()
    
    # Run pipeline
    results = pipeline.run_full_pipeline(config)
    
    # Print summary
    logger.info("\nPipeline Summary:")
    for stage, details in results.get('stages', {}).items():
        logger.info(f"  {stage}: {details}")
