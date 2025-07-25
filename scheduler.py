import os
import json
import time
import subprocess
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
import signal
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ArbitrageScheduler:
    def __init__(self, config_path="config/scheduler_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.running = False
        self.processes = {}
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def load_config(self):
        """Load scheduler configuration from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            raise
            
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
        
    def run_scraper(self, scraper_config):
        """Run a single scraper."""
        name = scraper_config["name"]
        script_path = scraper_config["script_path"]
        args = scraper_config.get("args", [])
        timeout = scraper_config.get("timeout_minutes", 10) * 60
        
        logger.info(f"Starting scraper: {name}")
        
        try:
            # Build the command
            cmd = [sys.executable, script_path] + args
            
            # Run the scraper
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            self.processes[name] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                
                if process.returncode == 0:
                    logger.info(f"Scraper {name} completed successfully")
                    if stdout:
                        logger.debug(f"Scraper {name} output: {stdout}")
                else:
                    logger.error(f"Scraper {name} failed with return code {process.returncode}")
                    if stderr:
                        logger.error(f"Scraper {name} error: {stderr}")
                        
            except subprocess.TimeoutExpired:
                logger.warning(f"Scraper {name} timed out after {timeout} seconds")
                process.kill()
                process.communicate()
                
        except Exception as e:
            logger.error(f"Failed to run scraper {name}: {e}")
        finally:
            if name in self.processes:
                del self.processes[name]
                
    def run_arbitrage_checker(self):
        """Run the arbitrage checker."""
        checker_config = self.config["arbitrage_checker"]
        script_path = checker_config["script_path"]
        args = checker_config.get("args", [])
        delay = checker_config.get("delay_after_scrapers_seconds", 30)
        
        logger.info(f"Waiting {delay} seconds before running arbitrage checker...")
        time.sleep(delay)
        
        logger.info("Starting arbitrage checker")
        
        try:
            cmd = [sys.executable, script_path] + args
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            self.processes["arbitrage_checker"] = process
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("Arbitrage checker completed successfully")
                if stdout:
                    logger.debug(f"Arbitrage checker output: {stdout}")
            else:
                logger.error(f"Arbitrage checker failed with return code {process.returncode}")
                if stderr:
                    logger.error(f"Arbitrage checker error: {stderr}")
                    
        except Exception as e:
            logger.error(f"Failed to run arbitrage checker: {e}")
        finally:
            if "arbitrage_checker" in self.processes:
                del self.processes["arbitrage_checker"]
                
    def run_cycle(self):
        """Run one complete cycle of scrapers followed by arbitrage checker."""
        logger.info("Starting new scraping cycle")
        
        # Run all scrapers in parallel
        scraper_threads = []
        
        for scraper_config in self.config["scrapers"]:
            thread = threading.Thread(
                target=self.run_scraper,
                args=(scraper_config,),
                name=f"scraper_{scraper_config['name']}"
            )
            thread.start()
            scraper_threads.append(thread)
            
        # Wait for all scrapers to complete
        for thread in scraper_threads:
            thread.join()
            
        logger.info("All scrapers completed, running arbitrage checker")
        
        # Run arbitrage checker
        self.run_arbitrage_checker()
        
        logger.info("Cycle completed")
        
    def start(self):
        """Start the scheduler."""
        self.running = True
        frequency_minutes = self.config["scraping_frequency_minutes"]
        
        logger.info(f"Starting scheduler with {frequency_minutes} minute intervals")
        
        while self.running:
            cycle_start = datetime.now()
            
            try:
                self.run_cycle()
            except Exception as e:
                logger.error(f"Error during cycle: {e}")
                
            # Calculate sleep time
            cycle_duration = datetime.now() - cycle_start
            sleep_time = max(0, (frequency_minutes * 60) - cycle_duration.total_seconds())
            
            if self.running and sleep_time > 0:
                logger.info(f"Cycle completed in {cycle_duration.total_seconds():.1f}s, sleeping for {sleep_time:.1f}s")
                time.sleep(sleep_time)
                
    def stop(self):
        """Stop the scheduler and kill any running processes."""
        logger.info("Stopping scheduler...")
        self.running = False
        
        # Kill any running processes
        for name, process in self.processes.items():
            if process.poll() is None:  # Process is still running
                logger.info(f"Terminating process: {name}")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing process: {name}")
                    process.kill()
                    
        logger.info("Scheduler stopped")

def main():
    """Main entry point."""
    # Ensure required directories exist
    os.makedirs("config", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Create scheduler and start
    scheduler = ArbitrageScheduler()
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        scheduler.stop()

if __name__ == "__main__":
    main()
