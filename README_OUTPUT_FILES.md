# Portfolio Analysis with Date-Stamped Output Files

## Overview

This system generates **CSV** and **HTML** output files with date stamps, ensuring only **one file per day** is created. This prevents duplicate analysis runs and maintains a historical record of daily portfolio analysis.

## Features

✅ **Date-Stamped Files**: Files are named with the format `portfolio_analysis_YYYY-MM-DD.csv/html`  
✅ **Once Per Day**: Automatically skips regeneration if files already exist for today  
✅ **Force Regenerate**: Option to override and regenerate files if needed  
✅ **Interactive HTML Dashboard**: Beautiful visualization with charts and tables  
✅ **Historical Tracking**: Keep daily snapshots of portfolio performance  
✅ **Automatic Cleanup**: Built-in function to remove old files (optional)

## Files Created

### 1. `file_manager.py`
Utility module that handles all file operations:
- Date-stamped filename generation
- Check if files exist for today
- Save CSV and HTML files
- List historical files
- Cleanup old files

### 2. `analyze_portfolio_with_output.py`
Enhanced portfolio analyzer that:
- Analyzes stocks based on Relative Strength, Volume Expansion, and Sector Strength
- Generates CSV file with all analysis data
- Creates interactive HTML dashboard with charts
- Only runs once per day (unless forced)

## Usage

### Basic Usage (Default)

```bash
python3 analyze_portfolio_with_output.py
```

**First run of the day:**
- Fetches stock data
- Performs analysis
- Generates CSV and HTML files
- Files saved in `output/` directory

**Subsequent runs on the same day:**
- Detects existing files
- Skips analysis
- Shows file locations

### Force Regenerate

To regenerate files even if they exist for today, modify the script:

```python
# In analyze_portfolio_with_output.py, change the last line:
csv_file, html_file = analyze_portfolio(force_regenerate=True)
```

Or use it programmatically:

```python
from analyze_portfolio_with_output import analyze_portfolio

# Force regenerate
csv_file, html_file = analyze_portfolio(force_regenerate=True)
```

## Output Files

### CSV File Structure

Location: `output/portfolio_analysis_YYYY-MM-DD.csv`

Columns:
- **Symbol**: Stock ticker symbol
- **Sector**: Industry sector
- **Close**: Latest closing price
- **RSI**: Relative Strength Index
- **Momentum**: Momentum score (0-100)
- **RS_Score**: Relative strength score vs NIFTY
- **RS_Value**: Relative strength percentage
- **Vol_Ratio**: Volume expansion ratio
- **Vol_Score**: Volume score
- **Mom_Score**: Momentum score
- **Total_Score**: Combined total score
- **Signal**: BUY/SELL/HOLD signal
- **Emoji**: Visual indicator (🟢/🟡/🔴)
- **Trend**: Bullish/Bearish
- **Date**: Analysis date (YYYY-MM-DD)

### HTML Dashboard

Location: `output/portfolio_analysis_YYYY-MM-DD.html`

Features:
- 📊 **Summary Statistics**: Quick overview of signals
- 📈 **Interactive Charts**:
  - Stock Total Scores (Bar Chart)
  - Sector Strength Analysis (Horizontal Bar)
  - Relative Strength vs NIFTY (Bar Chart)
  - Volume Expansion Ratios (Bar Chart)
- 📋 **Detailed Table**: Complete stock analysis data
- 🎨 **Beautiful Design**: Modern, responsive interface
- 🌐 **Standalone**: No internet required, works offline

## File Manager API

### Initialize

```python
from file_manager import DateStampedFileManager

# Create file manager (default output directory: 'output')
fm = DateStampedFileManager(output_dir='output')

# Custom output directory
fm = DateStampedFileManager(output_dir='my_reports')
```

### Get Filenames

```python
# Get today's CSV filename
csv_file = fm.get_csv_filename('portfolio_analysis')
# Returns: output/portfolio_analysis_2026-05-15.csv

# Get today's HTML filename
html_file = fm.get_html_filename('portfolio_analysis')
# Returns: output/portfolio_analysis_2026-05-15.html
```

### Check if Files Exist

```python
# Check if CSV exists for today
if fm.csv_exists_for_today('portfolio_analysis'):
    print("Already analyzed today!")
```

### Save Files

```python
import pandas as pd

# Save DataFrame to CSV (skips if exists)
df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
csv_file = fm.save_to_csv(df, 'portfolio_analysis')

# Force overwrite
csv_file = fm.save_to_csv(df, 'portfolio_analysis', force=True)

# Save HTML content
html_content = "<html>...</html>"
html_file = fm.save_html(html_content, 'portfolio_analysis')
```

### List Historical Files

```python
# List all CSV files
csv_files = fm.list_files('portfolio_analysis', 'csv')
# Returns: ['output/portfolio_analysis_2026-05-15.csv', 
#           'output/portfolio_analysis_2026-05-14.csv', ...]

# List all HTML files
html_files = fm.list_files('portfolio_analysis', 'html')

# Get latest file
latest_csv = fm.get_latest_file('portfolio_analysis', 'csv')
```

### Cleanup Old Files

```python
# Remove files older than 30 days (default)
deleted = fm.cleanup_old_files('portfolio_analysis', keep_days=30)
print(f"Deleted {deleted} old files")

# Keep only last 7 days
deleted = fm.cleanup_old_files('portfolio_analysis', keep_days=7)
```

## Directory Structure

```
StockAnalysis/
├── analyze_portfolio_with_output.py  # Main analysis script
├── file_manager.py                   # File management utility
├── output/                           # Output directory (auto-created)
│   ├── portfolio_analysis_2026-05-15.csv
│   ├── portfolio_analysis_2026-05-15.html
│   ├── portfolio_analysis_2026-05-14.csv
│   ├── portfolio_analysis_2026-05-14.html
│   └── ...
└── README_OUTPUT_FILES.md            # This file
```

## Examples

### Example 1: Daily Automated Run

```python
#!/usr/bin/env python3
"""
Daily portfolio analysis script
Run this via cron job or task scheduler
"""
from analyze_portfolio_with_output import analyze_portfolio

# Run analysis (will skip if already done today)
csv_file, html_file = analyze_portfolio(force_regenerate=False)

if csv_file:
    print(f"Analysis complete: {csv_file}")
```

### Example 2: Custom Analysis with Different Prefix

```python
from file_manager import DateStampedFileManager
import pandas as pd

# Create file manager
fm = DateStampedFileManager(output_dir='custom_reports')

# Your analysis code here
df = pd.DataFrame({
    'Stock': ['AAPL', 'GOOGL'],
    'Price': [150.0, 2800.0]
})

# Save with custom prefix
csv_file = fm.save_to_csv(df, prefix='tech_stocks')
# Saves as: custom_reports/tech_stocks_2026-05-15.csv
```

### Example 3: Weekly Cleanup

```python
from file_manager import DateStampedFileManager

fm = DateStampedFileManager()

# Keep only last 30 days of reports
deleted = fm.cleanup_old_files('portfolio_analysis', keep_days=30)
print(f"Cleaned up {deleted} old files")
```

## Scheduling (Optional)

### Linux/Mac (cron)

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 6 PM
0 18 * * * cd /path/to/StockAnalysis && /usr/bin/python3 analyze_portfolio_with_output.py
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 6:00 PM
4. Action: Start a program
5. Program: `python3`
6. Arguments: `analyze_portfolio_with_output.py`
7. Start in: `C:\path\to\StockAnalysis`

## Benefits

1. **No Duplicate Analysis**: Prevents running the same analysis multiple times per day
2. **Historical Record**: Keep daily snapshots for trend analysis
3. **Easy Comparison**: Compare today's analysis with previous days
4. **Automated Workflow**: Set up once, runs automatically
5. **Clean Organization**: All files in one directory with clear naming
6. **Visual Reports**: Beautiful HTML dashboards for easy interpretation

## Troubleshooting

### Files Not Being Created

Check if the `output` directory exists and has write permissions:
```bash
ls -la output/
```

### Force Regenerate Not Working

Make sure you're passing `force_regenerate=True`:
```python
analyze_portfolio(force_regenerate=True)
```

### Old Files Not Cleaning Up

Verify the file naming pattern matches:
```python
fm = DateStampedFileManager()
files = fm.list_files('portfolio_analysis', 'csv')
print(files)  # Check if files are being detected
```

## Advanced Usage

### Custom Date Format

Modify `file_manager.py` to use a different date format:

```python
# In DateStampedFileManager.__init__
self.today = datetime.now().strftime('%Y%m%d')  # 20260515
# or
self.today = datetime.now().strftime('%d-%b-%Y')  # 15-May-2026
```

### Multiple Portfolios

```python
# Analyze different portfolios with different prefixes
csv1, html1 = analyze_portfolio(prefix='tech_portfolio')
csv2, html2 = analyze_portfolio(prefix='energy_portfolio')
```

## Support

For issues or questions:
1. Check this documentation
2. Review the code comments in `file_manager.py`
3. Examine example usage in `analyze_portfolio_with_output.py`

---

**Made with Bob** 🤖