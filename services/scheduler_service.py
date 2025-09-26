import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from threading import Thread, Event
from dataclasses import dataclass
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class ScheduledJob:
    """Represents a scheduled job"""
    job_id: str
    name: str
    function: Callable
    interval_minutes: int
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True
    max_retries: int = 3
    retry_count: int = 0
    last_error: Optional[str] = None
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0


class SchedulerService:
    """Service for managing scheduled tasks like automated scraping"""
    
    def __init__(self, config_file: str = 'config/scheduler_config.json'):
        self.jobs: Dict[str, ScheduledJob] = {}
        self.running = False
        self.scheduler_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.config_file = config_file
        self.check_interval = 60  # Check every minute
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load scheduler configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.check_interval = config.get('check_interval', 60)
                    logger.info(f"Loaded scheduler config from {self.config_file}")
            else:
                logger.info("No scheduler config file found, using defaults")
        except Exception as e:
            logger.error(f"Failed to load scheduler config: {e}")
    
    def _save_config(self):
        """Save scheduler configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            config = {
                'check_interval': self.check_interval,
                'jobs': {
                    job_id: {
                        'name': job.name,
                        'interval_minutes': job.interval_minutes,
                        'enabled': job.enabled,
                        'max_retries': job.max_retries,
                        'last_run': job.last_run.isoformat() if job.last_run else None,
                        'next_run': job.next_run.isoformat() if job.next_run else None,
                        'total_runs': job.total_runs,
                        'successful_runs': job.successful_runs,
                        'failed_runs': job.failed_runs,
                        'last_error': job.last_error
                    }
                    for job_id, job in self.jobs.items()
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save scheduler config: {e}")
    
    def add_job(self, job_id: str, name: str, function: Callable, 
                interval_minutes: int, enabled: bool = True, max_retries: int = 3) -> bool:
        """Add a new scheduled job"""
        try:
            if job_id in self.jobs:
                logger.warning(f"Job {job_id} already exists, updating...")
            
            next_run = datetime.now() + timedelta(minutes=interval_minutes)
            
            job = ScheduledJob(
                job_id=job_id,
                name=name,
                function=function,
                interval_minutes=interval_minutes,
                next_run=next_run,
                enabled=enabled,
                max_retries=max_retries
            )
            
            self.jobs[job_id] = job
            self._save_config()
            
            logger.info(f"Added job '{name}' (ID: {job_id}) with {interval_minutes}min interval")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job"""
        try:
            if job_id in self.jobs:
                job_name = self.jobs[job_id].name
                del self.jobs[job_id]
                self._save_config()
                logger.info(f"Removed job '{job_name}' (ID: {job_id})")
                return True
            else:
                logger.warning(f"Job {job_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False
    
    def enable_job(self, job_id: str) -> bool:
        """Enable a scheduled job"""
        try:
            if job_id in self.jobs:
                self.jobs[job_id].enabled = True
                # Reset next run time
                self.jobs[job_id].next_run = datetime.now() + timedelta(
                    minutes=self.jobs[job_id].interval_minutes
                )
                self._save_config()
                logger.info(f"Enabled job {job_id}")
                return True
            else:
                logger.warning(f"Job {job_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to enable job {job_id}: {e}")
            return False
    
    def disable_job(self, job_id: str) -> bool:
        """Disable a scheduled job"""
        try:
            if job_id in self.jobs:
                self.jobs[job_id].enabled = False
                self._save_config()
                logger.info(f"Disabled job {job_id}")
                return True
            else:
                logger.warning(f"Job {job_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to disable job {job_id}: {e}")
            return False
    
    def update_job_interval(self, job_id: str, interval_minutes: int) -> bool:
        """Update job interval"""
        try:
            if job_id in self.jobs:
                self.jobs[job_id].interval_minutes = interval_minutes
                # Update next run time
                self.jobs[job_id].next_run = datetime.now() + timedelta(minutes=interval_minutes)
                self._save_config()
                logger.info(f"Updated job {job_id} interval to {interval_minutes} minutes")
                return True
            else:
                logger.warning(f"Job {job_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update job {job_id} interval: {e}")
            return False
    
    def _execute_job(self, job: ScheduledJob):
        """Execute a single job"""
        try:
            logger.info(f"Executing job '{job.name}' (ID: {job.job_id})")
            
            # Update job status
            job.last_run = datetime.now()
            job.total_runs += 1
            
            # Execute the job function
            job.function()
            
            # Job succeeded
            job.successful_runs += 1
            job.retry_count = 0
            job.last_error = None
            
            # Schedule next run
            job.next_run = datetime.now() + timedelta(minutes=job.interval_minutes)
            
            logger.info(f"Job '{job.name}' completed successfully")
            
        except Exception as e:
            # Job failed
            job.failed_runs += 1
            job.retry_count += 1
            job.last_error = str(e)
            
            logger.error(f"Job '{job.name}' failed: {e}")
            
            if job.retry_count < job.max_retries:
                # Schedule retry in 5 minutes
                job.next_run = datetime.now() + timedelta(minutes=5)
                logger.info(f"Scheduling retry {job.retry_count}/{job.max_retries} for job '{job.name}'")
            else:
                # Max retries reached, schedule next regular run
                job.next_run = datetime.now() + timedelta(minutes=job.interval_minutes)
                job.retry_count = 0
                logger.error(f"Max retries reached for job '{job.name}', scheduling next regular run")
        
        finally:
            self._save_config()
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        while not self.stop_event.is_set():
            try:
                current_time = datetime.now()
                
                # Check each job
                for job in self.jobs.values():
                    if not job.enabled:
                        continue
                    
                    if job.next_run and current_time >= job.next_run:
                        # Execute job in a separate thread to avoid blocking
                        job_thread = Thread(target=self._execute_job, args=(job,))
                        job_thread.daemon = True
                        job_thread.start()
                
                # Wait for next check
                self.stop_event.wait(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        logger.info("Scheduler loop stopped")
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            self.running = True
            self.stop_event.clear()
            
            self.scheduler_thread = Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
            logger.info("Scheduler started")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            self.running = False
    
    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            logger.info("Stopping scheduler...")
            
            self.stop_event.set()
            self.running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=10)
            
            logger.info("Scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a specific job"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        return {
            'job_id': job.job_id,
            'name': job.name,
            'enabled': job.enabled,
            'interval_minutes': job.interval_minutes,
            'last_run': job.last_run.isoformat() if job.last_run else None,
            'next_run': job.next_run.isoformat() if job.next_run else None,
            'total_runs': job.total_runs,
            'successful_runs': job.successful_runs,
            'failed_runs': job.failed_runs,
            'retry_count': job.retry_count,
            'max_retries': job.max_retries,
            'last_error': job.last_error,
            'success_rate': (job.successful_runs / job.total_runs * 100) if job.total_runs > 0 else 0
        }
    
    def get_all_jobs_status(self) -> List[Dict]:
        """Get status of all jobs"""
        return [self.get_job_status(job_id) for job_id in self.jobs.keys()]
    
    def get_scheduler_status(self) -> Dict:
        """Get overall scheduler status"""
        total_jobs = len(self.jobs)
        enabled_jobs = sum(1 for job in self.jobs.values() if job.enabled)
        
        return {
            'running': self.running,
            'total_jobs': total_jobs,
            'enabled_jobs': enabled_jobs,
            'disabled_jobs': total_jobs - enabled_jobs,
            'check_interval': self.check_interval,
            'config_file': self.config_file
        }