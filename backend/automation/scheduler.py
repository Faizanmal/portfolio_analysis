"""
Task Scheduler for Automation

Implements scheduled execution of automated tasks including:
- Data pipeline runs
- Report generation
- Model retraining
- Notifications

Features:
- Cron-like scheduling
- Background task execution
- Error handling and retries
- Logging and monitoring
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Callable, Dict
from loguru import logger
import sys


# Import automation modules
sys.path.append(str(Path(__file__).parent.parent))
from automation.data_pipeline import DataPipeline, create_pipeline_config
from automation.report_generator import ReportGenerator, generate_sample_report_data


class AutomationScheduler:
    """
    Centralized task scheduler for all automation workflows.
    
    Manages scheduled execution of:
    - Data extraction and processing
    - Report generation and distribution
    - Model training and deployment
    - System maintenance tasks
    """
    
    def __init__(self, config_path: str = "config/scheduler_config.json"):
        """
        Initialize automation scheduler.
        
        Args:
            config_path: Path to scheduler configuration file
        """
        self.scheduler = BackgroundScheduler()
        self.config_path = Path(config_path)
        self.jobs = {}
        self.execution_history = []
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        logger.info("Automation Scheduler initialized")
    
    def load_config(self) -> Dict:
        """
        Load scheduler configuration.
        
        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        else:
            # Create default configuration
            default_config = {
                'timezone': 'America/New_York',
                'max_instances': 3,
                'jobs': []
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Dict):
        """
        Save scheduler configuration.
        
        Args:
            config: Configuration dictionary
        """
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {self.config_path}")
    
    def log_execution(self, job_id: str, status: str, details: Dict = None):
        """
        Log job execution.
        
        Args:
            job_id: Job identifier
            status: Execution status
            details: Additional details
        """
        execution_record = {
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'details': details or {}
        }
        
        self.execution_history.append(execution_record)
        
        # Save to file
        history_path = Path("logs/execution_history.json")
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(history_path, 'a') as f:
            f.write(json.dumps(execution_record) + '\n')
    
    def run_data_pipeline(self):
        """Execute the data pipeline."""
        job_id = "data_pipeline"
        logger.info(f"[{job_id}] Starting scheduled data pipeline execution...")
        
        try:
            pipeline = DataPipeline(data_dir="data")
            config = create_pipeline_config()
            results = pipeline.run_full_pipeline(config)
            
            self.log_execution(job_id, 'SUCCESS', results)
            logger.info(f"[{job_id}] Pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"[{job_id}] Pipeline failed: {str(e)}")
            self.log_execution(job_id, 'FAILED', {'error': str(e)})
    
    def run_report_generation(self):
        """Execute report generation."""
        job_id = "report_generation"
        logger.info(f"[{job_id}] Starting scheduled report generation...")
        
        try:
            generator = ReportGenerator(output_dir="reports")
            data = generate_sample_report_data()
            report_path = generator.generate_complete_report(data)
            
            self.log_execution(job_id, 'SUCCESS', {'report_path': str(report_path)})
            logger.info(f"[{job_id}] Report generated successfully: {report_path}")
            
        except Exception as e:
            logger.error(f"[{job_id}] Report generation failed: {str(e)}")
            self.log_execution(job_id, 'FAILED', {'error': str(e)})
    
    def run_model_retraining(self):
        """Execute model retraining."""
        job_id = "model_retraining"
        logger.info(f"[{job_id}] Starting scheduled model retraining...")
        
        try:
            # Import model modules
            from models.risk_predictor import RiskPredictor, generate_sample_data
            
            # Generate or load training data
            df = generate_sample_data(n_samples=2000)
            
            # Train model
            predictor = RiskPredictor()
            metrics = predictor.train(df, optimize=False)
            predictor.save_model()
            
            self.log_execution(job_id, 'SUCCESS', metrics)
            logger.info(f"[{job_id}] Model retrained successfully")
            
        except Exception as e:
            logger.error(f"[{job_id}] Model retraining failed: {str(e)}")
            self.log_execution(job_id, 'FAILED', {'error': str(e)})
    
    def run_data_quality_check(self):
        """Execute data quality checks."""
        job_id = "data_quality_check"
        logger.info(f"[{job_id}] Starting data quality checks...")
        
        try:
            # Check for recent data files
            data_dir = Path("data/processed")
            recent_files = []
            
            if data_dir.exists():
                for file in data_dir.glob("*.csv"):
                    mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if datetime.now() - mtime < timedelta(days=7):
                        recent_files.append({
                            'file': file.name,
                            'modified': mtime.isoformat(),
                            'size_mb': file.stat().st_size / (1024 * 1024)
                        })
            
            results = {
                'files_checked': len(list(data_dir.glob("*.csv"))) if data_dir.exists() else 0,
                'recent_files': len(recent_files),
                'details': recent_files
            }
            
            self.log_execution(job_id, 'SUCCESS', results)
            logger.info(f"[{job_id}] Quality check completed. Recent files: {len(recent_files)}")
            
        except Exception as e:
            logger.error(f"[{job_id}] Quality check failed: {str(e)}")
            self.log_execution(job_id, 'FAILED', {'error': str(e)})
    
    def run_system_cleanup(self):
        """Execute system cleanup tasks."""
        job_id = "system_cleanup"
        logger.info(f"[{job_id}] Starting system cleanup...")
        
        try:
            # Clean up old files
            archive_dir = Path("data/archive")
            if archive_dir.exists():
                cutoff_date = datetime.now() - timedelta(days=90)
                deleted_count = 0
                
                for file in archive_dir.rglob("*"):
                    if file.is_file():
                        mtime = datetime.fromtimestamp(file.stat().st_mtime)
                        if mtime < cutoff_date:
                            file.unlink()
                            deleted_count += 1
                
                results = {'files_deleted': deleted_count}
            else:
                results = {'files_deleted': 0}
            
            self.log_execution(job_id, 'SUCCESS', results)
            logger.info(f"[{job_id}] Cleanup completed. Files deleted: {results['files_deleted']}")
            
        except Exception as e:
            logger.error(f"[{job_id}] Cleanup failed: {str(e)}")
            self.log_execution(job_id, 'FAILED', {'error': str(e)})
    
    def schedule_job(self, 
                    job_id: str,
                    func: Callable,
                    trigger_type: str = 'cron',
                    **trigger_kwargs):
        """
        Schedule a job.
        
        Args:
            job_id: Unique job identifier
            func: Function to execute
            trigger_type: Type of trigger ('cron' or 'interval')
            **trigger_kwargs: Trigger-specific arguments
        """
        if trigger_type == 'cron':
            trigger = CronTrigger(**trigger_kwargs)
        elif trigger_type == 'interval':
            trigger = IntervalTrigger(**trigger_kwargs)
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
        
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            max_instances=self.config.get('max_instances', 3),
            replace_existing=True
        )
        
        self.jobs[job_id] = job
        logger.info(f"Scheduled job: {job_id}")
        
        return job
    
    def setup_default_schedule(self):
        """Set up default job schedule."""
        logger.info("Setting up default job schedule...")
        
        # Daily data pipeline at 6 AM
        self.schedule_job(
            job_id='daily_data_pipeline',
            func=self.run_data_pipeline,
            trigger_type='cron',
            hour=6,
            minute=0
        )
        
        # Weekly report generation on Monday at 8 AM
        self.schedule_job(
            job_id='weekly_report',
            func=self.run_report_generation,
            trigger_type='cron',
            day_of_week='mon',
            hour=8,
            minute=0
        )
        
        # Monthly model retraining on 1st of month at 2 AM
        self.schedule_job(
            job_id='monthly_model_retraining',
            func=self.run_model_retraining,
            trigger_type='cron',
            day=1,
            hour=2,
            minute=0
        )
        
        # Daily data quality check at 7 AM
        self.schedule_job(
            job_id='daily_quality_check',
            func=self.run_data_quality_check,
            trigger_type='cron',
            hour=7,
            minute=0
        )
        
        # Weekly cleanup on Sunday at midnight
        self.schedule_job(
            job_id='weekly_cleanup',
            func=self.run_system_cleanup,
            trigger_type='cron',
            day_of_week='sun',
            hour=0,
            minute=0
        )
        
        logger.info("Default schedule configured")
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Scheduler started")
        logger.info(f"Active jobs: {len(self.jobs)}")
        
        # Print job schedule
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.id}: Next run at {job.next_run_time}")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def get_status(self) -> Dict:
        """
        Get scheduler status.
        
        Returns:
            Status dictionary
        """
        jobs_status = []
        for job in self.scheduler.get_jobs():
            jobs_status.append({
                'id': job.id,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'running': self.scheduler.running,
            'jobs_count': len(self.jobs),
            'jobs': jobs_status,
            'recent_executions': self.execution_history[-10:]  # Last 10 executions
        }
    
    def run_job_now(self, job_id: str):
        """
        Run a specific job immediately.
        
        Args:
            job_id: Job identifier
        """
        job = self.jobs.get(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"Job {job_id} scheduled to run immediately")
        else:
            logger.error(f"Job {job_id} not found")


def main():
    """Main function to run scheduler."""
    # Configure logging
    logger.add("logs/scheduler.log", rotation="10 MB", level="INFO")
    
    # Create scheduler
    scheduler = AutomationScheduler()
    
    # Setup default schedule
    scheduler.setup_default_schedule()
    
    # Start scheduler
    scheduler.start()
    
    # Print status
    logger.info("\n" + "="*50)
    logger.info("AUTOMATION SCHEDULER STATUS")
    logger.info("="*50)
    status = scheduler.get_status()
    logger.info(f"Running: {status['running']}")
    logger.info(f"Scheduled Jobs: {status['jobs_count']}")
    logger.info("\nJob Schedule:")
    for job in status['jobs']:
        logger.info(f"  {job['id']}: {job['next_run_time']}")
    logger.info("="*50)
    
    # Keep running
    try:
        import time
        logger.info("\nScheduler is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("\nShutting down scheduler...")
        scheduler.stop()


if __name__ == "__main__":
    main()
