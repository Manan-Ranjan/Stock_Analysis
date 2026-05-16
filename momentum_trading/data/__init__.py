"""
Data module for fetching stock data from multiple sources
"""

# Import only what exists
try:
    from .fetcher import DataFetcher
except ImportError:
    DataFetcher = None

try:
    from .nse_fetcher import NSEDataFetcher
except ImportError:
    NSEDataFetcher = None

__all__ = [
    'DataFetcher',
    'NSEDataFetcher',
]

# Made with Bob
