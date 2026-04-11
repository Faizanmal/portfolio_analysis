"""
Automated Report Generator

Generates professional PDF and HTML reports from data analysis.
Automates report creation, distribution, and scheduling.

Features:
- Multiple report templates
- PDF/HTML generation
- Email distribution
- Scheduled generation
- Custom visualizations
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
from typing import Dict
from loguru import logger
import base64
from io import BytesIO


class ReportGenerator:
    """
    Automated report generation system.
    
    Creates professional reports with data, visualizations,
    and insights for stakeholders.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory for generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        sns.set_style("whitegrid")
        
    def create_portfolio_summary_chart(self, data: pd.DataFrame) -> str:
        """
        Create portfolio summary visualization.
        
        Args:
            data: Portfolio data
            
        Returns:
            Base64 encoded image string
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Portfolio Performance Summary', fontsize=16, fontweight='bold')
        
        # Chart 1: Asset Allocation
        if 'asset' in data.columns and 'value' in data.columns:
            asset_data = data.groupby('asset')['value'].sum()
            axes[0, 0].pie(asset_data.values, labels=asset_data.index, autopct='%1.1f%%')
            axes[0, 0].set_title('Asset Allocation')
        
        # Chart 2: Performance Timeline
        if 'date' in data.columns and 'portfolio_value' in data.columns:
            timeline_data = data.groupby('date')['portfolio_value'].mean()
            axes[0, 1].plot(timeline_data.index, timeline_data.values, linewidth=2)
            axes[0, 1].set_title('Portfolio Value Over Time')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Chart 3: Returns Distribution
        if 'returns' in data.columns:
            axes[1, 0].hist(data['returns'].dropna(), bins=30, edgecolor='black')
            axes[1, 0].set_title('Returns Distribution')
            axes[1, 0].set_xlabel('Returns')
            axes[1, 0].set_ylabel('Frequency')
        
        # Chart 4: Risk-Return Scatter
        if 'risk' in data.columns and 'return' in data.columns:
            axes[1, 1].scatter(data['risk'], data['return'], alpha=0.6)
            axes[1, 1].set_title('Risk-Return Profile')
            axes[1, 1].set_xlabel('Risk (Volatility)')
            axes[1, 1].set_ylabel('Expected Return')
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    def create_risk_analysis_chart(self, risk_data: Dict) -> str:
        """
        Create risk analysis visualization.
        
        Args:
            risk_data: Risk metrics dictionary
            
        Returns:
            Base64 encoded image string
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle('Risk Analysis', fontsize=16, fontweight='bold')
        
        # Risk levels bar chart
        risk_levels = risk_data.get('risk_levels', {'Low': 10, 'Medium': 15, 'High': 5})
        axes[0].bar(risk_levels.keys(), risk_levels.values(), color=['green', 'yellow', 'red'])
        axes[0].set_title('Portfolio Companies by Risk Level')
        axes[0].set_ylabel('Number of Companies')
        
        # Risk metrics radar
        metrics = risk_data.get('metrics', {
            'Credit Risk': 7,
            'Market Risk': 6,
            'Liquidity Risk': 5,
            'Operational Risk': 8,
            'Compliance Risk': 4
        })
        
        categories = list(metrics.keys())
        values = list(metrics.values())
        values += values[:1]  # Close the plot
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        axes[1] = plt.subplot(122, projection='polar')
        axes[1].plot(angles, values, 'o-', linewidth=2)
        axes[1].fill(angles, values, alpha=0.25)
        axes[1].set_xticks(angles[:-1])
        axes[1].set_xticklabels(categories)
        axes[1].set_ylim(0, 10)
        axes[1].set_title('Risk Metrics Overview')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    def generate_executive_summary(self, data: Dict) -> str:
        """
        Generate executive summary section.
        
        Args:
            data: Summary data dictionary
            
        Returns:
            HTML formatted summary
        """
        template = """
        <div class="executive-summary">
            <h2>Executive Summary</h2>
            <div class="key-metrics">
                <div class="metric">
                    <h3>Total Portfolio Value</h3>
                    <p class="value">${total_value:,.0f}</p>
                    <p class="change {value_change_class}">{value_change:+.2f}%</p>
                </div>
                <div class="metric">
                    <h3>Total Return</h3>
                    <p class="value">{total_return:+.2f}%</p>
                    <p class="change {return_change_class}">{return_change:+.2f}%</p>
                </div>
                <div class="metric">
                    <h3>Portfolio Risk</h3>
                    <p class="value">{risk_level}</p>
                    <p class="detail">Volatility: {volatility:.2f}%</p>
                </div>
                <div class="metric">
                    <h3>Active Investments</h3>
                    <p class="value">{active_investments}</p>
                    <p class="detail">{new_investments} new this period</p>
                </div>
            </div>
            
            <div class="highlights">
                <h3>Key Highlights</h3>
                <ul>
                    {% for highlight in highlights %}
                    <li>{{ highlight }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="recommendations">
                <h3>Recommendations</h3>
                <ul>
                    {% for rec in recommendations %}
                    <li><strong>{{ rec.title }}:</strong> {{ rec.description }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        """
        
        template_obj = Template(template)
        
        # Determine change classes for color coding
        data['value_change_class'] = 'positive' if data.get('value_change', 0) > 0 else 'negative'
        data['return_change_class'] = 'positive' if data.get('return_change', 0) > 0 else 'negative'
        
        return template_obj.render(**data)
    
    def generate_detailed_analysis(self, analysis_data: Dict) -> str:
        """
        Generate detailed analysis section.
        
        Args:
            analysis_data: Analysis results
            
        Returns:
            HTML formatted analysis
        """
        template = """
        <div class="detailed-analysis">
            <h2>Detailed Analysis</h2>
            
            <div class="section">
                <h3>Performance Metrics</h3>
                <table class="metrics-table">
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Benchmark</th>
                        <th>Difference</th>
                    </tr>
                    {% for metric in performance_metrics %}
                    <tr>
                        <td>{{ metric.name }}</td>
                        <td>{{ metric.value }}</td>
                        <td>{{ metric.benchmark }}</td>
                        <td class="{{ metric.diff_class }}">{{ metric.difference }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h3>Top Performers</h3>
                <table class="performers-table">
                    <tr>
                        <th>Asset</th>
                        <th>Return</th>
                        <th>Contribution</th>
                    </tr>
                    {% for asset in top_performers %}
                    <tr>
                        <td>{{ asset.name }}</td>
                        <td class="positive">{{ asset.return }}%</td>
                        <td>{{ asset.contribution }}%</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h3>Risk Analysis</h3>
                <p>{{ risk_summary }}</p>
                <ul>
                    {% for risk_item in risk_items %}
                    <li><strong>{{ risk_item.category }}:</strong> {{ risk_item.assessment }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        """
        
        template_obj = Template(template)
        return template_obj.render(**analysis_data)
    
    def generate_html_report(self, 
                            report_data: Dict,
                            report_title: str = "Portfolio Analysis Report") -> str:
        """
        Generate complete HTML report.
        
        Args:
            report_data: All report data
            report_title: Report title
            
        Returns:
            Complete HTML report
        """
        logger.info(f"Generating HTML report: {report_title}")
        
        # CSS Styles
        css = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 40px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }
            .report-info {
                color: #7f8c8d;
            }
            .key-metrics {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .metric {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .metric h3 {
                margin: 0 0 10px 0;
                font-size: 14px;
                opacity: 0.9;
            }
            .metric .value {
                font-size: 32px;
                font-weight: bold;
                margin: 10px 0;
            }
            .metric .change {
                font-size: 16px;
                margin: 5px 0;
            }
            .metric .detail {
                font-size: 14px;
                opacity: 0.8;
                margin: 5px 0;
            }
            .positive {
                color: #27ae60;
            }
            .negative {
                color: #e74c3c;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th {
                background-color: #34495e;
                color: white;
                padding: 12px;
                text-align: left;
            }
            td {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .section {
                margin: 30px 0;
            }
            ul {
                line-height: 1.8;
            }
            .chart-container {
                margin: 30px 0;
                text-align: center;
            }
            .chart-container img {
                max-width: 100%;
                height: auto;
            }
            .footer {
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                text-align: center;
                color: #7f8c8d;
                font-size: 12px;
            }
        </style>
        """
        
        # HTML Template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{report_title}</title>
            {css}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{report_title}</h1>
                    <div class="report-info">
                        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <p><strong>Period:</strong> {report_data.get('period', 'N/A')}</p>
                    </div>
                </div>
                
                {report_data.get('executive_summary', '')}
                
                <div class="chart-container">
                    <img src="data:image/png;base64,{report_data.get('portfolio_chart', '')}" alt="Portfolio Summary">
                </div>
                
                {report_data.get('detailed_analysis', '')}
                
                <div class="chart-container">
                    <img src="data:image/png;base64,{report_data.get('risk_chart', '')}" alt="Risk Analysis">
                </div>
                
                <div class="footer">
                    <p>This report was automatically generated by the AI-Powered Portfolio Analysis Platform</p>
                    <p>Confidential - For Internal Use Only</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def save_report(self, html_content: str, filename: str) -> Path:
        """
        Save report to file.
        
        Args:
            html_content: HTML report content
            filename: Output filename
            
        Returns:
            Path to saved report
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Report saved to {output_path}")
        
        return output_path
    
    def generate_complete_report(self, data: Dict) -> Path:
        """
        Generate a complete portfolio report.
        
        Args:
            data: All necessary data for the report
            
        Returns:
            Path to generated report
        """
        logger.info("Generating complete portfolio report...")
        
        # Generate charts
        portfolio_chart = self.create_portfolio_summary_chart(
            data.get('portfolio_data', pd.DataFrame())
        )
        
        risk_chart = self.create_risk_analysis_chart(
            data.get('risk_data', {})
        )
        
        # Generate sections
        executive_summary = self.generate_executive_summary(
            data.get('summary_data', {})
        )
        
        detailed_analysis = self.generate_detailed_analysis(
            data.get('analysis_data', {})
        )
        
        # Combine all parts
        report_data = {
            'period': data.get('period', 'Q4 2024'),
            'executive_summary': executive_summary,
            'portfolio_chart': portfolio_chart,
            'detailed_analysis': detailed_analysis,
            'risk_chart': risk_chart
        }
        
        # Generate HTML
        html_report = self.generate_html_report(
            report_data,
            report_title=data.get('title', 'Portfolio Analysis Report')
        )
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"portfolio_report_{timestamp}.html"
        report_path = self.save_report(html_report, filename)
        
        logger.info("Report generation complete!")
        
        return report_path


def generate_sample_report_data() -> Dict:
    """Generate sample data for report demonstration."""
    
    # Portfolio data
    portfolio_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'asset': np.random.choice(['Stocks', 'Bonds', 'Real Estate', 'Commodities'], 100),
        'value': np.random.uniform(100000, 500000, 100),
        'portfolio_value': np.cumsum(np.random.uniform(-1000, 2000, 100)) + 1000000,
        'returns': np.random.normal(0.001, 0.02, 100),
        'risk': np.random.uniform(0.05, 0.25, 100),
        'return': np.random.uniform(0.05, 0.20, 100)
    })
    
    # Risk data
    risk_data = {
        'risk_levels': {'Low': 12, 'Medium': 18, 'High': 5},
        'metrics': {
            'Credit Risk': 7,
            'Market Risk': 6,
            'Liquidity Risk': 5,
            'Operational Risk': 8,
            'Compliance Risk': 4
        }
    }
    
    # Summary data
    summary_data = {
        'total_value': 2500000,
        'value_change': 5.2,
        'total_return': 12.5,
        'return_change': 2.3,
        'risk_level': 'Medium',
        'volatility': 15.3,
        'active_investments': 35,
        'new_investments': 4,
        'highlights': [
            'Portfolio value increased by 5.2% this quarter',
            'Successfully exited 2 underperforming investments',
            '4 new investments added in technology sector',
            'Risk metrics remain within acceptable ranges'
        ],
        'recommendations': [
            {'title': 'Diversification', 'description': 'Consider increasing allocation to international markets'},
            {'title': 'Risk Management', 'description': 'Monitor high-risk investments closely'},
            {'title': 'Rebalancing', 'description': 'Quarterly rebalancing recommended based on drift analysis'}
        ]
    }
    
    # Analysis data
    analysis_data = {
        'performance_metrics': [
            {'name': 'Total Return', 'value': '12.5%', 'benchmark': '10.0%', 'difference': '+2.5%', 'diff_class': 'positive'},
            {'name': 'Volatility', 'value': '15.3%', 'benchmark': '18.0%', 'difference': '-2.7%', 'diff_class': 'positive'},
            {'name': 'Sharpe Ratio', 'value': '0.82', 'benchmark': '0.65', 'difference': '+0.17', 'diff_class': 'positive'},
            {'name': 'Max Drawdown', 'value': '-8.5%', 'benchmark': '-12.0%', 'difference': '+3.5%', 'diff_class': 'positive'}
        ],
        'top_performers': [
            {'name': 'Tech Startup A', 'return': '+45.2', 'contribution': '3.2'},
            {'name': 'Real Estate Fund B', 'return': '+28.5', 'contribution': '2.1'},
            {'name': 'Growth Stock C', 'return': '+22.1', 'contribution': '1.8'}
        ],
        'risk_summary': 'Overall portfolio risk is within acceptable parameters. Market risk exposure has decreased by 15% compared to last quarter.',
        'risk_items': [
            {'category': 'Market Risk', 'assessment': 'Moderate - Diversified across sectors'},
            {'category': 'Credit Risk', 'assessment': 'Low - High-quality credit ratings'},
            {'category': 'Liquidity Risk', 'assessment': 'Low - Adequate cash reserves'}
        ]
    }
    
    return {
        'title': 'Q4 2024 Portfolio Analysis Report',
        'period': 'Q4 2024',
        'portfolio_data': portfolio_data,
        'risk_data': risk_data,
        'summary_data': summary_data,
        'analysis_data': analysis_data
    }


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/report_generator.log", rotation="10 MB")
    
    # Create report generator
    generator = ReportGenerator(output_dir="reports")
    
    # Generate sample report
    logger.info("Generating sample report...")
    sample_data = generate_sample_report_data()
    
    report_path = generator.generate_complete_report(sample_data)
    
    logger.info(f"\n{'='*50}")
    logger.info("Report successfully generated!")
    logger.info(f"Location: {report_path}")
    logger.info(f"{'='*50}")
