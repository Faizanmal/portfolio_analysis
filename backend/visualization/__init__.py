"""
Advanced Visualization & Reporting Module
==========================================

Provides next-level visualization capabilities including:
- AR/3D portfolio visualization
- Dynamic heatmaps for correlation analysis
- Real-time performance benchmarking
- Automated insight generation
- Customizable report builder
"""

from .ar_visualization import ARPortfolioVisualizer, PortfolioScene3D
from .dynamic_heatmaps import DynamicHeatmapEngine, CorrelationAnalyzer
from .performance_benchmarking import PerformanceBenchmark, PeerComparisonEngine
from .insight_generator import InsightGenerator, AutomatedInsights
from .report_builder import ReportBuilder, ReportTemplate, DragDropBuilder

__all__ = [
    'ARPortfolioVisualizer',
    'PortfolioScene3D',
    'DynamicHeatmapEngine',
    'CorrelationAnalyzer',
    'PerformanceBenchmark',
    'PeerComparisonEngine',
    'InsightGenerator',
    'AutomatedInsights',
    'ReportBuilder',
    'ReportTemplate',
    'DragDropBuilder'
]
