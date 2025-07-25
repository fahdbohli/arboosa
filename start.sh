#!/bin/bash

# Create necessary directories
mkdir -p logs
mkdir -p output/arb_opportunities
mkdir -p output/ev_output
mkdir -p "scrapers/TounesBet Scraper/scraped_prematch_matches/football"
mkdir -p "scrapers/TounesBet Scraper/scraped_prematch_matches/tennis"
mkdir -p "scrapers/Clubx2 scraper/scraped_prematch_matches/football"
mkdir -p "scrapers/Clubx2 scraper/scraped_prematch_matches/tennis"
mkdir -p "scrapers/Clubx2 scraper/scraped_live_matches/football"
mkdir -p "scrapers/Clubx2 scraper/scraped_live_matches/tennis"

# Set permissions
chmod +x start.sh

# Start the scheduler
python scheduler.py
