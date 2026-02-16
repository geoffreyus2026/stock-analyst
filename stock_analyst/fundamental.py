import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FundamentalAnalyzer:
    """Fundamental analysis using company financials and metrics"""
    
    def __init__(self):
        self.sector_benchmarks = {
            'Technology': {'pe_ratio': 25, 'peg_ratio': 2.0, 'pb_ratio': 4.0},
            'Healthcare': {'pe_ratio': 20, 'peg_ratio': 1.8, 'pb_ratio': 3.5},
            'Financial': {'pe_ratio': 15, 'peg_ratio': 1.5, 'pb_ratio': 1.2},
            'Consumer Discretionary': {'pe_ratio': 18, 'peg_ratio': 1.6, 'pb_ratio': 2.5},
            'Industrial': {'pe_ratio': 18, 'peg_ratio': 1.6, 'pb_ratio': 2.0},
            'Energy': {'pe_ratio': 12, 'peg_ratio': 1.2, 'pb_ratio': 1.5},
            'Utilities': {'pe_ratio': 16, 'peg_ratio': 1.4, 'pb_ratio': 1.8},
            'Materials': {'pe_ratio': 16, 'peg_ratio': 1.4, 'pb_ratio': 2.0},
            'Real Estate': {'pe_ratio': 20, 'peg_ratio': 2.0, 'pb_ratio': 2.0},
            'Communication Services': {'pe_ratio': 18, 'peg_ratio': 1.6, 'pb_ratio': 2.5}
        }
    
    def get_fundamental_data(self, symbol: str) -> Dict:
        """Fetch comprehensive fundamental data"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            
            # Get financial statements
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            # Get earnings data
            earnings = ticker.earnings
            quarterly_earnings = ticker.quarterly_earnings
            
            return {
                'info': info,
                'financials': financials,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'earnings': earnings,
                'quarterly_earnings': quarterly_earnings
            }
        except Exception as e:
            logger.error(f"Error fetching fundamental data for {symbol}: {e}")
            return {'error': str(e), 'symbol': symbol}
    
    def analyze_valuation_metrics(self, data: Dict) -> Dict:
        """Analyze key valuation metrics"""
        info = data['info']
        
        # Basic valuation ratios
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        peg_ratio = info.get('pegRatio', None)
        price_to_book = info.get('priceToBook', None)
        price_to_sales = info.get('priceToSalesTrailing12Months', None)
        
        # Enterprise value metrics
        ev = info.get('enterpriseValue', None)
        ebitda = info.get('ebitda', None)
        ev_to_ebitda = info.get('enterpriseToEbitda', None)
        ev_to_revenue = info.get('enterpriseToRevenue', None)
        
        return {
            'pe_ratio': pe_ratio,
            'forward_pe': forward_pe,
            'peg_ratio': peg_ratio,
            'price_to_book': price_to_book,
            'price_to_sales': price_to_sales,
            'enterprise_value': ev,
            'ebitda': ebitda,
            'ev_to_ebitda': ev_to_ebitda,
            'ev_to_revenue': ev_to_revenue
        }
    
    def analyze_profitability_metrics(self, data: Dict) -> Dict:
        """Analyze profitability and margins"""
        info = data['info']
        financials = data['financials']
        
        # Profitability ratios
        gross_margin = info.get('grossMargins', None)
        operating_margin = info.get('operatingMargins', None)
        profit_margin = info.get('profitMargins', None)
        
        # Return metrics
        roe = info.get('returnOnEquity', None)
        roa = info.get('returnOnAssets', None)
        roic = info.get('returnOnCapital', None)
        
        # Revenue and earnings growth
        revenue_growth = info.get('revenueGrowth', None)
        earnings_growth = info.get('earningsGrowth', None)
        
        return {
            'gross_margin': gross_margin,
            'operating_margin': operating_margin,
            'profit_margin': profit_margin,
            'return_on_equity': roe,
            'return_on_assets': roa,
            'return_on_invested_capital': roic,
            'revenue_growth': revenue_growth,
            'earnings_growth': earnings_growth
        }
    
    def analyze_financial_health(self, data: Dict) -> Dict:
        """Analyze financial health and debt metrics"""
        info = data['info']
        balance_sheet = data['balance_sheet']
        
        # Debt metrics
        total_debt = info.get('totalDebt', None)
        total_cash = info.get('totalCash', None)
        net_debt = info.get('netDebt', None)
        
        # Leverage ratios
        debt_to_equity = info.get('debtToEquity', None)
        current_ratio = info.get('currentRatio', None)
        quick_ratio = info.get('quickRatio', None)
        
        # Cash flow metrics
        free_cash_flow = info.get('freeCashflow', None)
        operating_cash_flow = info.get('operatingCashflow', None)
        
        return {
            'total_debt': total_debt,
            'total_cash': total_cash,
            'net_debt': net_debt,
            'debt_to_equity': debt_to_equity,
            'current_ratio': current_ratio,
            'quick_ratio': quick_ratio,
            'free_cash_flow': free_cash_flow,
            'operating_cash_flow': operating_cash_flow
        }
    
    def analyze_efficiency_metrics(self, data: Dict) -> Dict:
        """Analyze operational efficiency"""
        info = data['info']
        
        # Asset efficiency
        asset_turnover = info.get('assetTurnover', None)
        inventory_turnover = info.get('inventoryTurnover', None)
        
        # Working capital
        working_capital = info.get('workingCapital', None)
        days_sales_outstanding = info.get('daysSalesOutstanding', None)
        days_inventory_outstanding = info.get('daysInventoryOutstanding', None)
        days_payables_outstanding = info.get('daysPayablesOutstanding', None)
        cash_conversion_cycle = info.get('cashConversionCycle', None)
        
        return {
            'asset_turnover': asset_turnover,
            'inventory_turnover': inventory_turnover,
            'working_capital': working_capital,
            'days_sales_outstanding': days_sales_outstanding,
            'days_inventory_outstanding': days_inventory_outstanding,
            'days_payables_outstanding': days_payables_outstanding,
            'cash_conversion_cycle': cash_conversion_cycle
        }
    
    def analyze_growth_metrics(self, data: Dict) -> Dict:
        """Analyze growth trends"""
        info = data['info']
        quarterly_earnings = data['quarterly_earnings']
        
        # Historical growth rates
        revenue_growth_3y = info.get('revenueGrowth3Y', None)
        earnings_growth_3y = info.get('earningsGrowth3Y', None)
        
        # Forward growth estimates
        revenue_growth_est = info.get('revenueGrowthEstimate', None)
        earnings_growth_est = info.get('earningsGrowthEstimate', None)
        
        # Quarterly trends
        if not quarterly_earnings.empty:
            recent_quarters = quarterly_earnings.tail(4)
            quarterly_revenue_growth = recent_quarters['Revenue'].pct_change().mean() if len(recent_quarters) > 1 else None
            quarterly_earnings_growth = recent_quarters['Earnings'].pct_change().mean() if len(recent_quarters) > 1 else None
        else:
            quarterly_revenue_growth = None
            quarterly_earnings_growth = None
        
        return {
            'revenue_growth_3y': revenue_growth_3y,
            'earnings_growth_3y': earnings_growth_3y,
            'revenue_growth_estimate': revenue_growth_est,
            'earnings_growth_estimate': earnings_growth_est,
            'quarterly_revenue_growth': quarterly_revenue_growth,
            'quarterly_earnings_growth': quarterly_earnings_growth
        }
    
    def get_sector_comparison(self, symbol: str, data: Dict) -> Dict:
        """Compare metrics to sector averages"""
        info = data['info']
        sector = info.get('sector', 'Unknown')
        
        sector_benchmarks = self.sector_benchmarks.get(sector, self.sector_benchmarks['Technology'])
        
        # Get actual metrics
        pe_ratio = info.get('trailingPE', None)
        peg_ratio = info.get('pegRatio', None)
        pb_ratio = info.get('priceToBook', None)
        
        # Compare to sector
        pe_comparison = self._compare_to_benchmark(pe_ratio, sector_benchmarks['pe_ratio'])
        peg_comparison = self._compare_to_benchmark(peg_ratio, sector_benchmarks['peg_ratio'])
        pb_comparison = self._compare_to_benchmark(pb_ratio, sector_benchmarks['pb_ratio'])
        
        return {
            'sector': sector,
            'pe_vs_sector': pe_comparison,
            'peg_vs_sector': peg_comparison,
            'pb_vs_sector': pb_comparison,
            'sector_benchmarks': sector_benchmarks
        }
    
    def _compare_to_benchmark(self, actual: float, benchmark: float) -> str:
        """Compare actual value to benchmark"""
        if actual is None or benchmark is None:
            return "N/A"
        
        ratio = actual / benchmark
        if ratio < 0.8:
            return "UNDERVALUED"
        elif ratio > 1.2:
            return "OVERVALUED"
        else:
            return "FAIRLY_VALUED"
    
    def calculate_fundamental_score(self, data: Dict) -> Dict:
        """Calculate overall fundamental score"""
        valuation = self.analyze_valuation_metrics(data)
        profitability = self.analyze_profitability_metrics(data)
        health = self.analyze_financial_health(data)
        efficiency = self.analyze_efficiency_metrics(data)
        growth = self.analyze_growth_metrics(data)
        sector_comp = self.get_sector_comparison(data['info'].get('symbol', ''), data)
        
        # Scoring logic (0-100)
        score = 0
        factors = []
        
        # Valuation score (25 points)
        if valuation['pe_ratio'] and valuation['pe_ratio'] < 25:
            score += 12.5
            factors.append("Reasonable P/E ratio")
        if valuation['peg_ratio'] and valuation['peg_ratio'] < 2:
            score += 12.5
            factors.append("Good PEG ratio")
        
        # Profitability score (25 points)
        if profitability['profit_margin'] and profitability['profit_margin'] > 0.15:
            score += 12.5
            factors.append("Strong profit margins")
        if profitability['return_on_equity'] and profitability['return_on_equity'] > 0.15:
            score += 12.5
            factors.append("High ROE")
        
        # Financial health score (25 points)
        if health['debt_to_equity'] and health['debt_to_equity'] < 1:
            score += 12.5
            factors.append("Low debt levels")
        if health['free_cash_flow'] and health['free_cash_flow'] > 0:
            score += 12.5
            factors.append("Positive free cash flow")
        
        # Growth score (25 points)
        revenue_growth = growth.get('revenue_growth_3y') or growth.get('revenue_growth_estimate')
        earnings_growth = growth.get('earnings_growth_3y') or growth.get('earnings_growth_estimate')

        if revenue_growth and revenue_growth > 0.1:
            score += 12.5
            factors.append("Strong revenue growth")
        if earnings_growth and earnings_growth > 0.1:
            score += 12.5
            factors.append("Strong earnings growth")
        
        # Rating based on score
        if score >= 80:
            rating = "EXCELLENT"
        elif score >= 65:
            rating = "GOOD"
        elif score >= 50:
            rating = "FAIR"
        elif score >= 35:
            rating = "POOR"
        else:
            rating = "VERY_POOR"
        
        return {
            'total_score': score,
            'rating': rating,
            'positive_factors': factors,
            'valuation_score': self._get_metric_score(valuation),
            'profitability_score': self._get_metric_score(profitability),
            'health_score': self._get_metric_score(health),
            'growth_score': self._get_metric_score(growth)
        }
    
    def _get_metric_score(self, metrics: Dict) -> float:
        """Calculate score for individual metric category"""
        valid_metrics = [v for v in metrics.values() if v is not None and not pd.isna(v)]
        return len(valid_metrics) / len(metrics) * 100 if metrics else 0
    
    def get_fundamental_summary(self, symbol: str) -> Dict:
        """Get comprehensive fundamental analysis summary"""
        try:
            data = self.get_fundamental_data(symbol)
            
            if 'error' in data:
                return data
            
            # Analyze all metrics
            valuation = self.analyze_valuation_metrics(data)
            profitability = self.analyze_profitability_metrics(data)
            health = self.analyze_financial_health(data)
            efficiency = self.analyze_efficiency_metrics(data)
            growth = self.analyze_growth_metrics(data)
            sector_comparison = self.get_sector_comparison(symbol, data)
            
            # Calculate overall score
            fundamental_score = self.calculate_fundamental_score(data)
            
            return {
                'symbol': symbol,
                'valuation_metrics': valuation,
                'profitability_metrics': profitability,
                'financial_health': health,
                'efficiency_metrics': efficiency,
                'growth_metrics': growth,
                'sector_comparison': sector_comparison,
                'fundamental_score': fundamental_score,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in fundamental analysis for {symbol}: {e}")
            return {'error': str(e), 'symbol': symbol}