"""
Momentum Trading System
A comprehensive Python-based momentum trading application for Indian stock markets
"""

__version__ = "1.0.0"
__author__ = "Bob - AI Software Engineer"

# Import only what exists
try:
    from .data import DataFetcher
except ImportError:
    DataFetcher = None

try:
    from .indicators import MomentumIndicators, TrendIndicators
except ImportError:
    MomentumIndicators = None
    TrendIndicators = None

__all__ = [
    'DataFetcher',
    'MomentumIndicators',
    'TrendIndicators',
]

# Made with Bob
