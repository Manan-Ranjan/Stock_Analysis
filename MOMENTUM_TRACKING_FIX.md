# Momentum Tracking Fix

## Problem
All stocks were showing as "NEW" (🆕) entries with no momentum trends (Rising 📈, Falling 📉, or Stable ➡️).

## Root Cause
The code was trying to compare today's scores with "previous day's" scores, but:
1. The CSV file appends multiple runs per day with timestamps
2. The filter `previous_df['Date'] < today_date` excluded ALL data when running multiple times on the same day
3. This resulted in no previous scores to compare against, marking everything as "NEW"

## Solution
Changed the logic to compare with the **previous run's data** instead of previous day's data:

### Before:
```python
# Filter out today's entries and get the most recent for each symbol
prev_data = previous_df[previous_df['Date'] < today_date]
```

### After:
```python
# Get the second-to-last complete set of data using timestamps
if 'Timestamp' in previous_df.columns:
    unique_timestamps = previous_df['Timestamp'].unique()
    if len(unique_timestamps) >= 2:
        # Use second most recent timestamp
        prev_timestamp = sorted(unique_timestamps)[-2]
        prev_data = previous_df[previous_df['Timestamp'] == prev_timestamp]
```

## How It Works Now
1. **First Run**: All stocks marked as "NEW" (expected behavior)
2. **Second Run**: Compares with first run's scores
3. **Third+ Runs**: Compares with previous run's scores
4. **Trend Detection**:
   - 📈 **RISING**: Score increased by more than 5 points
   - 📉 **FALLING**: Score decreased by more than 5 points
   - ➡️ **STABLE**: Score changed by 5 points or less
   - 🆕 **NEW**: First time being tracked

## Benefits
- Track momentum changes **within the same day**
- See which stocks are gaining or losing strength in real-time
- Better decision-making with trend information
- Works with multiple runs per day

## Example Output
After the fix, you'll see:
```
📈 Rising Momentum: 5 stocks gaining strength
📉 Falling Momentum: 3 stocks losing strength
➡️ Stable: 7 stocks maintaining position
🆕 New Entries: 5 first time tracked
```

Instead of:
```
📈 Rising Momentum: 0
📉 Falling Momentum: 0
➡️ Stable: 0
🆕 New Entries: 20  ← All stocks marked as new!
```

## Testing
Run the analysis multiple times to see the trends:
```bash
python3 analyze_portfolio_with_output.py
# Wait a few minutes, then run again
python3 analyze_portfolio_with_output.py
```

The second run will show momentum changes compared to the first run.