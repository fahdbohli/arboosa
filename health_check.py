import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

def check_health():
    """Simple health check for the application."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Check if scheduler is running (look for recent log entries)
    try:
        if os.path.exists("scheduler.log"):
            stat = os.stat("scheduler.log")
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            if datetime.now() - last_modified < timedelta(minutes=10):
                health_status["checks"]["scheduler_log"] = "recent"
            else:
                health_status["checks"]["scheduler_log"] = "stale"
                health_status["status"] = "warning"
        else:
            health_status["checks"]["scheduler_log"] = "missing"
            health_status["status"] = "warning"
    except Exception as e:
        health_status["checks"]["scheduler_log"] = f"error: {str(e)}"
        health_status["status"] = "error"
    
    # Check if output directories exist
    output_dirs = [
        "output/arb_opportunities",
        "output/ev_output",
        "scrapers/TounesBet Scraper/scraped_prematch_matches",
        "scrapers/Clubx2 scraper/scraped_prematch_matches"
    ]
    
    for dir_path in output_dirs:
        if os.path.exists(dir_path):
            health_status["checks"][f"dir_{dir_path.replace('/', '_')}"] = "exists"
        else:
            health_status["checks"][f"dir_{dir_path.replace('/', '_')}"] = "missing"
            health_status["status"] = "warning"
    
    return health_status

if __name__ == "__main__":
    health = check_health()
    print(json.dumps(health, indent=2))
