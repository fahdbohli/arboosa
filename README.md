# Arbitrage Betting System

An automated system for scraping betting odds and finding arbitrage opportunities.

## Features

- **Multi-source scraping**: TounesBet and Clubx2 scrapers
- **Automated scheduling**: Configurable scraping intervals
- **Arbitrage detection**: Real-time opportunity identification
- **Cloud deployment**: Ready for Render deployment

## Deployment on Render

1. **Connect your repository** to Render
2. **Create a new Worker service**
3. **Use the following settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python scheduler.py`
   - Environment: Python 3.11

## Configuration

Edit `config/scheduler_config.json` to customize:

- **Scraping frequency**: Change `scraping_frequency_minutes`
- **Scraper arguments**: Modify `args` arrays for each scraper
- **Sports and modes**: Add/remove from `sports` and `modes` arrays

## Local Development

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run the scheduler
python scheduler.py

# Check health
python health_check.py
\`\`\`

## Directory Structure

\`\`\`
├── scheduler.py              # Main scheduler
├── main.py                  # Arbitrage checker
├── scrapers/                # Scraper modules
│   ├── TounesBet Scraper/
│   └── Clubx2 scraper/
├── settings/                # Configuration files
├── config/                  # Scheduler configuration
├── output/                  # Generated data
└── logs/                   # Log files
\`\`\`

## Environment Variables

- `PYTHONPATH`: Set to project root
- `PYTHONUNBUFFERED`: Set to "1" for real-time logging

## Monitoring

- Check `scheduler.log` for execution logs
- Use `health_check.py` for system status
- Monitor output directories for fresh data

## Customization

### Adding New Scrapers

1. Add scraper config to `scheduler_config.json`
2. Update source directories in `settings/*/settings.json`
3. Ensure scraper outputs to correct directory structure

### Changing Frequencies

Edit `scraping_frequency_minutes` in `config/scheduler_config.json`

### Adding Sports

1. Create settings directory: `settings/{sport}/`
2. Add sport to `scheduler_config.json`
3. Configure scraper arguments for the new sport
