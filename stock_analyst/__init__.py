# Stock Analysis package

from .fundamental import FundamentalAnalyzer
from .technical import TechnicalAnalyzer
from .web_analyzer import generate_full_analysis

__version__ = "1.0.0"
__all__ = [
    "TechnicalAnalyzer",
    "FundamentalAnalyzer",
    "generate_full_analysis",
]
