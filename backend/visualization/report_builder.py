"""
Report Builder - Customizable Report Templates
==============================================

Drag-and-drop report builder with:
- Pre-built report templates
- Customizable widgets and layouts
- Multiple export formats (PDF, HTML, Excel)
- Scheduled report generation
- White-label branding support
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from io import BytesIO


class WidgetType(Enum):
    """Types of report widgets"""
    CHART_LINE = "chart_line"
    CHART_BAR = "chart_bar"
    CHART_PIE = "chart_pie"
    CHART_AREA = "chart_area"
    CHART_SCATTER = "chart_scatter"
    HEATMAP = "heatmap"
    TABLE = "table"
    METRIC_CARD = "metric_card"
    TEXT = "text"
    HEADER = "header"
    DIVIDER = "divider"
    IMAGE = "image"
    INSIGHT_LIST = "insight_list"
    PORTFOLIO_SUMMARY = "portfolio_summary"
    PERFORMANCE_TABLE = "performance_table"
    ALLOCATION_PIE = "allocation_pie"
    RETURNS_CHART = "returns_chart"
    RISK_METRICS = "risk_metrics"
    BENCHMARK_COMPARISON = "benchmark_comparison"


class ExportFormat(Enum):
    """Export formats"""
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"
    JSON = "json"
    MARKDOWN = "markdown"
    POWERPOINT = "pptx"


class LayoutType(Enum):
    """Report layout types"""
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "two_column"
    THREE_COLUMN = "three_column"
    GRID = "grid"
    FREEFORM = "freeform"


@dataclass
class Widget:
    """Report widget component"""
    widget_id: str
    widget_type: WidgetType
    title: str
    
    # Position and size (grid-based)
    row: int = 0
    col: int = 0
    width: int = 1  # Grid units
    height: int = 1  # Grid units
    
    # Data binding
    data_source: str = ""  # Key to fetch data
    data_config: Dict[str, Any] = field(default_factory=dict)
    
    # Styling
    style: Dict[str, Any] = field(default_factory=dict)
    show_title: bool = True
    show_border: bool = True
    
    # Interaction
    drilldown_enabled: bool = False
    drilldown_target: str = ""
    
    # Content (for static widgets)
    content: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.widget_id,
            'type': self.widget_type.value,
            'title': self.title,
            'position': {'row': self.row, 'col': self.col},
            'size': {'width': self.width, 'height': self.height},
            'data': {
                'source': self.data_source,
                'config': self.data_config
            },
            'style': self.style,
            'show_title': self.show_title,
            'content': self.content
        }


@dataclass
class ReportSection:
    """Section within a report"""
    section_id: str
    title: str
    widgets: List[Widget] = field(default_factory=list)
    layout: LayoutType = LayoutType.SINGLE_COLUMN
    columns: int = 1
    show_title: bool = True
    page_break_before: bool = False
    
    def add_widget(self, widget: Widget):
        self.widgets.append(widget)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.section_id,
            'title': self.title,
            'layout': self.layout.value,
            'columns': self.columns,
            'widgets': [w.to_dict() for w in self.widgets],
            'show_title': self.show_title,
            'page_break_before': self.page_break_before
        }


@dataclass
class ReportTemplate:
    """Complete report template"""
    template_id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    
    # Report structure
    sections: List[ReportSection] = field(default_factory=list)
    
    # Branding
    logo_url: str = ""
    primary_color: str = "#1a73e8"
    secondary_color: str = "#5f6368"
    font_family: str = "Arial"
    
    # Page settings
    page_size: str = "A4"
    orientation: str = "portrait"
    margin_top: float = 1.0
    margin_bottom: float = 1.0
    margin_left: float = 0.75
    margin_right: float = 0.75
    
    # Header/Footer
    header_text: str = ""
    footer_text: str = "Page {page_number} of {total_pages}"
    show_date: bool = True
    show_logo: bool = True
    
    # Category
    category: str = "custom"
    tags: List[str] = field(default_factory=list)
    
    # Permissions
    is_public: bool = False
    owner_id: str = ""
    
    def add_section(self, section: ReportSection):
        self.sections.append(section)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'sections': [s.to_dict() for s in self.sections],
            'branding': {
                'logo_url': self.logo_url,
                'primary_color': self.primary_color,
                'secondary_color': self.secondary_color,
                'font_family': self.font_family
            },
            'page': {
                'size': self.page_size,
                'orientation': self.orientation,
                'margins': {
                    'top': self.margin_top,
                    'bottom': self.margin_bottom,
                    'left': self.margin_left,
                    'right': self.margin_right
                }
            },
            'header_footer': {
                'header': self.header_text,
                'footer': self.footer_text,
                'show_date': self.show_date,
                'show_logo': self.show_logo
            },
            'metadata': {
                'category': self.category,
                'tags': self.tags,
                'is_public': self.is_public
            }
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass 
class GeneratedReport:
    """Instance of a generated report"""
    report_id: str
    template_id: str
    portfolio_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    
    # Content
    data: Dict[str, Any] = field(default_factory=dict)
    rendered_content: str = ""
    
    # Export files
    pdf_path: str = ""
    html_path: str = ""
    excel_path: str = ""


class ReportBuilder:
    """
    Drag-and-drop report builder with template management.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("report_builder")
        self.templates: Dict[str, ReportTemplate] = {}
        self.generated_reports: Dict[str, GeneratedReport] = {}
        
        # Register default templates
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create standard report templates"""
        
        # Monthly Performance Report
        monthly = self._create_monthly_performance_template()
        self.templates[monthly.template_id] = monthly
        
        # Risk Analysis Report
        risk = self._create_risk_analysis_template()
        self.templates[risk.template_id] = risk
        
        # Executive Summary
        executive = self._create_executive_summary_template()
        self.templates[executive.template_id] = executive
        
        # Client Report
        client = self._create_client_report_template()
        self.templates[client.template_id] = client
    
    def _create_monthly_performance_template(self) -> ReportTemplate:
        """Create monthly performance report template"""
        template = ReportTemplate(
            template_id="monthly_performance",
            name="Monthly Performance Report",
            description="Comprehensive monthly portfolio performance analysis",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            category="performance"
        )
        
        # Header section
        header_section = ReportSection(
            section_id="header",
            title="",
            layout=LayoutType.SINGLE_COLUMN,
            show_title=False
        )
        header_section.add_widget(Widget(
            widget_id="title",
            widget_type=WidgetType.HEADER,
            title="Monthly Performance Report",
            content="Monthly Performance Report",
            style={'font_size': 24, 'font_weight': 'bold'}
        ))
        template.add_section(header_section)
        
        # Summary section
        summary_section = ReportSection(
            section_id="summary",
            title="Portfolio Summary",
            layout=LayoutType.THREE_COLUMN,
            columns=3
        )
        summary_section.add_widget(Widget(
            widget_id="return_card",
            widget_type=WidgetType.METRIC_CARD,
            title="Total Return",
            data_source="performance.total_return",
            col=0, width=1
        ))
        summary_section.add_widget(Widget(
            widget_id="sharpe_card",
            widget_type=WidgetType.METRIC_CARD,
            title="Sharpe Ratio",
            data_source="performance.sharpe_ratio",
            col=1, width=1
        ))
        summary_section.add_widget(Widget(
            widget_id="volatility_card",
            widget_type=WidgetType.METRIC_CARD,
            title="Volatility",
            data_source="performance.volatility",
            col=2, width=1
        ))
        template.add_section(summary_section)
        
        # Performance chart section
        chart_section = ReportSection(
            section_id="performance_chart",
            title="Performance Over Time",
            layout=LayoutType.SINGLE_COLUMN
        )
        chart_section.add_widget(Widget(
            widget_id="cumulative_returns",
            widget_type=WidgetType.RETURNS_CHART,
            title="Cumulative Returns",
            data_source="timeseries.cumulative_returns",
            height=2,
            data_config={'include_benchmark': True}
        ))
        template.add_section(chart_section)
        
        # Allocation section
        allocation_section = ReportSection(
            section_id="allocation",
            title="Asset Allocation",
            layout=LayoutType.TWO_COLUMN,
            columns=2
        )
        allocation_section.add_widget(Widget(
            widget_id="allocation_pie",
            widget_type=WidgetType.ALLOCATION_PIE,
            title="Current Allocation",
            data_source="allocation.current",
            col=0, width=1
        ))
        allocation_section.add_widget(Widget(
            widget_id="allocation_table",
            widget_type=WidgetType.TABLE,
            title="Holdings",
            data_source="holdings.summary",
            col=1, width=1
        ))
        template.add_section(allocation_section)
        
        # Performance table
        perf_table_section = ReportSection(
            section_id="performance_table",
            title="Performance Attribution",
            layout=LayoutType.SINGLE_COLUMN,
            page_break_before=True
        )
        perf_table_section.add_widget(Widget(
            widget_id="attribution_table",
            widget_type=WidgetType.PERFORMANCE_TABLE,
            title="Sector Attribution",
            data_source="attribution.sector",
            height=2
        ))
        template.add_section(perf_table_section)
        
        return template
    
    def _create_risk_analysis_template(self) -> ReportTemplate:
        """Create risk analysis report template"""
        template = ReportTemplate(
            template_id="risk_analysis",
            name="Risk Analysis Report",
            description="Comprehensive risk metrics and analysis",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            category="risk"
        )
        
        # Risk metrics section
        metrics_section = ReportSection(
            section_id="risk_metrics",
            title="Risk Metrics",
            layout=LayoutType.GRID,
            columns=4
        )
        
        for i, metric in enumerate(['VaR (95%)', 'CVaR (95%)', 'Max Drawdown', 'Beta']):
            metrics_section.add_widget(Widget(
                widget_id=f"metric_{i}",
                widget_type=WidgetType.METRIC_CARD,
                title=metric,
                data_source=f"risk.{metric.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('%', '')}",
                col=i, width=1
            ))
        template.add_section(metrics_section)
        
        # Correlation heatmap
        corr_section = ReportSection(
            section_id="correlation",
            title="Correlation Analysis",
            layout=LayoutType.SINGLE_COLUMN
        )
        corr_section.add_widget(Widget(
            widget_id="correlation_heatmap",
            widget_type=WidgetType.HEATMAP,
            title="Asset Correlations",
            data_source="risk.correlation_matrix",
            height=3
        ))
        template.add_section(corr_section)
        
        # Drawdown analysis
        dd_section = ReportSection(
            section_id="drawdown",
            title="Drawdown Analysis",
            layout=LayoutType.SINGLE_COLUMN
        )
        dd_section.add_widget(Widget(
            widget_id="drawdown_chart",
            widget_type=WidgetType.CHART_AREA,
            title="Historical Drawdowns",
            data_source="risk.drawdown_series",
            height=2,
            style={'fill_color': 'rgba(255, 0, 0, 0.3)'}
        ))
        template.add_section(dd_section)
        
        return template
    
    def _create_executive_summary_template(self) -> ReportTemplate:
        """Create executive summary template"""
        template = ReportTemplate(
            template_id="executive_summary",
            name="Executive Summary",
            description="One-page executive summary for stakeholders",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            category="summary"
        )
        
        # Key metrics
        metrics_section = ReportSection(
            section_id="key_metrics",
            title="Key Performance Indicators",
            layout=LayoutType.GRID,
            columns=4
        )
        
        kpis = ['Total Return', 'Benchmark Comparison', 'Risk-Adjusted Return', 'Portfolio Value']
        for i, kpi in enumerate(kpis):
            metrics_section.add_widget(Widget(
                widget_id=f"kpi_{i}",
                widget_type=WidgetType.METRIC_CARD,
                title=kpi,
                data_source=f"kpi.{kpi.lower().replace(' ', '_').replace('-', '_')}",
                col=i, width=1
            ))
        template.add_section(metrics_section)
        
        # Mini chart and insights
        main_section = ReportSection(
            section_id="main",
            title="",
            layout=LayoutType.TWO_COLUMN,
            columns=2,
            show_title=False
        )
        main_section.add_widget(Widget(
            widget_id="performance_mini",
            widget_type=WidgetType.CHART_LINE,
            title="Performance Trend",
            data_source="timeseries.cumulative_returns",
            col=0, width=1, height=2
        ))
        main_section.add_widget(Widget(
            widget_id="insights",
            widget_type=WidgetType.INSIGHT_LIST,
            title="Key Insights",
            data_source="insights.top_5",
            col=1, width=1, height=2
        ))
        template.add_section(main_section)
        
        return template
    
    def _create_client_report_template(self) -> ReportTemplate:
        """Create client-facing report template"""
        template = ReportTemplate(
            template_id="client_report",
            name="Client Portfolio Report",
            description="Professional client-facing portfolio report",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            category="client",
            show_logo=True
        )
        
        # Welcome section
        welcome = ReportSection(
            section_id="welcome",
            title="",
            layout=LayoutType.SINGLE_COLUMN,
            show_title=False
        )
        welcome.add_widget(Widget(
            widget_id="greeting",
            widget_type=WidgetType.TEXT,
            title="",
            content="Dear Valued Client,\n\nPlease find enclosed your portfolio performance report for the reporting period.",
            style={'font_size': 12}
        ))
        template.add_section(welcome)
        
        # Summary metrics
        summary = ReportSection(
            section_id="portfolio_summary",
            title="Portfolio Summary",
            layout=LayoutType.SINGLE_COLUMN
        )
        summary.add_widget(Widget(
            widget_id="summary_widget",
            widget_type=WidgetType.PORTFOLIO_SUMMARY,
            title="Your Portfolio at a Glance",
            data_source="summary.overview"
        ))
        template.add_section(summary)
        
        # Performance vs benchmark
        benchmark = ReportSection(
            section_id="benchmark",
            title="Performance vs Benchmark",
            layout=LayoutType.SINGLE_COLUMN
        )
        benchmark.add_widget(Widget(
            widget_id="benchmark_chart",
            widget_type=WidgetType.BENCHMARK_COMPARISON,
            title="",
            data_source="benchmark.comparison",
            height=2
        ))
        template.add_section(benchmark)
        
        return template
    
    def create_template(
        self,
        name: str,
        description: str = "",
        category: str = "custom"
    ) -> ReportTemplate:
        """Create a new empty template"""
        template = ReportTemplate(
            template_id=str(uuid.uuid4()),
            name=name,
            description=description,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            category=category
        )
        
        self.templates[template.template_id] = template
        return template
    
    def clone_template(
        self,
        template_id: str,
        new_name: str
    ) -> Optional[ReportTemplate]:
        """Clone an existing template"""
        if template_id not in self.templates:
            return None
        
        original = self.templates[template_id]
        
        # Deep clone
        clone = ReportTemplate(
            template_id=str(uuid.uuid4()),
            name=new_name,
            description=f"Clone of {original.name}",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            category=original.category,
            logo_url=original.logo_url,
            primary_color=original.primary_color,
            secondary_color=original.secondary_color,
            font_family=original.font_family
        )
        
        # Clone sections
        for section in original.sections:
            new_section = ReportSection(
                section_id=str(uuid.uuid4()),
                title=section.title,
                layout=section.layout,
                columns=section.columns,
                show_title=section.show_title
            )
            
            # Clone widgets
            for widget in section.widgets:
                new_widget = Widget(
                    widget_id=str(uuid.uuid4()),
                    widget_type=widget.widget_type,
                    title=widget.title,
                    row=widget.row,
                    col=widget.col,
                    width=widget.width,
                    height=widget.height,
                    data_source=widget.data_source,
                    data_config=widget.data_config.copy(),
                    style=widget.style.copy(),
                    content=widget.content
                )
                new_section.add_widget(new_widget)
            
            clone.add_section(new_section)
        
        self.templates[clone.template_id] = clone
        return clone
    
    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available templates"""
        templates = []
        
        for template in self.templates.values():
            if category is None or template.category == category:
                templates.append({
                    'id': template.template_id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'sections': len(template.sections),
                    'updated_at': template.updated_at.isoformat()
                })
        
        return templates
    
    def add_widget_to_section(
        self,
        template_id: str,
        section_id: str,
        widget: Widget
    ) -> bool:
        """Add widget to a section (drag-and-drop)"""
        template = self.templates.get(template_id)
        if not template:
            return False
        
        for section in template.sections:
            if section.section_id == section_id:
                section.add_widget(widget)
                template.updated_at = datetime.now()
                return True
        
        return False
    
    def move_widget(
        self,
        template_id: str,
        widget_id: str,
        new_row: int,
        new_col: int
    ) -> bool:
        """Move widget to new position"""
        template = self.templates.get(template_id)
        if not template:
            return False
        
        for section in template.sections:
            for widget in section.widgets:
                if widget.widget_id == widget_id:
                    widget.row = new_row
                    widget.col = new_col
                    template.updated_at = datetime.now()
                    return True
        
        return False
    
    def resize_widget(
        self,
        template_id: str,
        widget_id: str,
        new_width: int,
        new_height: int
    ) -> bool:
        """Resize widget"""
        template = self.templates.get(template_id)
        if not template:
            return False
        
        for section in template.sections:
            for widget in section.widgets:
                if widget.widget_id == widget_id:
                    widget.width = new_width
                    widget.height = new_height
                    template.updated_at = datetime.now()
                    return True
        
        return False
    
    def update_branding(
        self,
        template_id: str,
        logo_url: Optional[str] = None,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        font_family: Optional[str] = None
    ) -> bool:
        """Update template branding (white-label support)"""
        template = self.templates.get(template_id)
        if not template:
            return False
        
        if logo_url is not None:
            template.logo_url = logo_url
        if primary_color is not None:
            template.primary_color = primary_color
        if secondary_color is not None:
            template.secondary_color = secondary_color
        if font_family is not None:
            template.font_family = font_family
        
        template.updated_at = datetime.now()
        return True


class DragDropBuilder:
    """
    Interactive drag-and-drop interface for report building.
    Generates frontend-compatible configuration.
    """
    
    def __init__(self, report_builder: ReportBuilder):
        self.builder = report_builder
        self.logger = logging.getLogger("drag_drop_builder")
        
        # Widget palette
        self.widget_palette = [
            {'type': 'chart_line', 'name': 'Line Chart', 'icon': '📈'},
            {'type': 'chart_bar', 'name': 'Bar Chart', 'icon': '📊'},
            {'type': 'chart_pie', 'name': 'Pie Chart', 'icon': '🥧'},
            {'type': 'chart_area', 'name': 'Area Chart', 'icon': '📉'},
            {'type': 'heatmap', 'name': 'Heatmap', 'icon': '🗺️'},
            {'type': 'table', 'name': 'Data Table', 'icon': '📋'},
            {'type': 'metric_card', 'name': 'Metric Card', 'icon': '🔢'},
            {'type': 'text', 'name': 'Text Block', 'icon': '📝'},
            {'type': 'insight_list', 'name': 'Insights', 'icon': '💡'},
            {'type': 'portfolio_summary', 'name': 'Portfolio Summary', 'icon': '💼'},
            {'type': 'allocation_pie', 'name': 'Allocation Chart', 'icon': '🎯'},
            {'type': 'benchmark_comparison', 'name': 'Benchmark Comparison', 'icon': '🏆'},
        ]
    
    def get_builder_config(self, template_id: str) -> Dict[str, Any]:
        """Get configuration for frontend drag-drop builder"""
        template = self.builder.get_template(template_id)
        
        if not template:
            return {'error': 'Template not found'}
        
        return {
            'template': template.to_dict(),
            'palette': self.widget_palette,
            'data_sources': self._get_available_data_sources(),
            'style_options': self._get_style_options(),
            'layout_options': [l.value for l in LayoutType],
            'page_sizes': ['A4', 'Letter', 'Legal', 'A3'],
            'font_options': ['Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Roboto']
        }
    
    def _get_available_data_sources(self) -> List[Dict[str, str]]:
        """Get list of available data sources for binding"""
        return [
            {'key': 'performance.total_return', 'name': 'Total Return', 'type': 'metric'},
            {'key': 'performance.sharpe_ratio', 'name': 'Sharpe Ratio', 'type': 'metric'},
            {'key': 'performance.volatility', 'name': 'Volatility', 'type': 'metric'},
            {'key': 'performance.max_drawdown', 'name': 'Max Drawdown', 'type': 'metric'},
            {'key': 'performance.alpha', 'name': 'Alpha', 'type': 'metric'},
            {'key': 'performance.beta', 'name': 'Beta', 'type': 'metric'},
            {'key': 'timeseries.cumulative_returns', 'name': 'Cumulative Returns', 'type': 'chart'},
            {'key': 'timeseries.daily_returns', 'name': 'Daily Returns', 'type': 'chart'},
            {'key': 'allocation.current', 'name': 'Current Allocation', 'type': 'pie'},
            {'key': 'allocation.target', 'name': 'Target Allocation', 'type': 'pie'},
            {'key': 'holdings.summary', 'name': 'Holdings Summary', 'type': 'table'},
            {'key': 'risk.correlation_matrix', 'name': 'Correlation Matrix', 'type': 'heatmap'},
            {'key': 'risk.drawdown_series', 'name': 'Drawdown History', 'type': 'chart'},
            {'key': 'attribution.sector', 'name': 'Sector Attribution', 'type': 'table'},
            {'key': 'benchmark.comparison', 'name': 'Benchmark Comparison', 'type': 'chart'},
            {'key': 'insights.top_5', 'name': 'Top Insights', 'type': 'list'},
        ]
    
    def _get_style_options(self) -> Dict[str, Any]:
        """Get available styling options"""
        return {
            'colors': {
                'primary': ['#1a73e8', '#34a853', '#fbbc04', '#ea4335', '#673ab7'],
                'chart': ['#4285f4', '#34a853', '#fbbc04', '#ea4335', '#46bdc6', '#7baaf7'],
                'background': ['#ffffff', '#f8f9fa', '#e8eaed', '#202124']
            },
            'fonts': {
                'sizes': [10, 12, 14, 16, 18, 20, 24, 28, 32],
                'weights': ['normal', 'bold', 'light']
            },
            'borders': {
                'widths': [0, 1, 2, 3],
                'styles': ['solid', 'dashed', 'dotted', 'none'],
                'radius': [0, 4, 8, 12, 16]
            }
        }
    
    def handle_drop(
        self,
        template_id: str,
        widget_type: str,
        section_id: str,
        position: Dict[str, int]
    ) -> Dict[str, Any]:
        """Handle widget drop from palette"""
        widget = Widget(
            widget_id=str(uuid.uuid4()),
            widget_type=WidgetType(widget_type),
            title=f"New {widget_type.replace('_', ' ').title()}",
            row=position.get('row', 0),
            col=position.get('col', 0)
        )
        
        success = self.builder.add_widget_to_section(template_id, section_id, widget)
        
        return {
            'success': success,
            'widget': widget.to_dict() if success else None
        }
    
    def handle_move(
        self,
        template_id: str,
        widget_id: str,
        new_position: Dict[str, int]
    ) -> Dict[str, Any]:
        """Handle widget move"""
        success = self.builder.move_widget(
            template_id,
            widget_id,
            new_position.get('row', 0),
            new_position.get('col', 0)
        )
        
        return {'success': success}
    
    def handle_resize(
        self,
        template_id: str,
        widget_id: str,
        new_size: Dict[str, int]
    ) -> Dict[str, Any]:
        """Handle widget resize"""
        success = self.builder.resize_widget(
            template_id,
            widget_id,
            new_size.get('width', 1),
            new_size.get('height', 1)
        )
        
        return {'success': success}
    
    def export_for_frontend(self, template_id: str) -> str:
        """Export template as JSON for frontend rendering"""
        template = self.builder.get_template(template_id)
        if template:
            return template.to_json()
        return json.dumps({'error': 'Template not found'})


class ReportRenderer:
    """
    Renders reports to various formats.
    """
    
    def __init__(self, builder: ReportBuilder):
        self.builder = builder
        self.logger = logging.getLogger("report_renderer")
    
    def render_html(
        self,
        template_id: str,
        data: Dict[str, Any]
    ) -> str:
        """Render report as HTML"""
        template = self.builder.get_template(template_id)
        if not template:
            return "<html><body>Template not found</body></html>"
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{template.name}</title>",
            "<style>",
            self._generate_css(template),
            "</style>",
            "</head>",
            "<body>",
            f'<div class="report-container">',
        ]
        
        # Header
        if template.show_logo and template.logo_url:
            html_parts.append(f'<img src="{template.logo_url}" class="logo" />')
        
        if template.show_date:
            html_parts.append(f'<div class="report-date">{datetime.now().strftime("%B %d, %Y")}</div>')
        
        # Sections
        for section in template.sections:
            html_parts.append(self._render_section_html(section, data))
        
        # Footer
        html_parts.append(f'<div class="footer">{template.footer_text}</div>')
        
        html_parts.extend([
            "</div>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _generate_css(self, template: ReportTemplate) -> str:
        """Generate CSS for report"""
        return f"""
        body {{
            font-family: {template.font_family}, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .logo {{
            max-height: 60px;
            margin-bottom: 20px;
        }}
        .report-date {{
            color: #666;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            color: {template.primary_color};
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            border-bottom: 2px solid {template.primary_color};
            padding-bottom: 5px;
        }}
        .widget {{
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .widget-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: {template.secondary_color};
        }}
        .metric-card {{
            text-align: center;
            padding: 20px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: {template.primary_color};
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .grid-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
            font-size: 12px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #f5f5f5;
            font-weight: bold;
        }}
        """
    
    def _render_section_html(
        self,
        section: ReportSection,
        data: Dict[str, Any]
    ) -> str:
        """Render a section as HTML"""
        html = [f'<div class="section">']
        
        if section.show_title:
            html.append(f'<div class="section-title">{section.title}</div>')
        
        html.append('<div class="grid-container">')
        
        for widget in section.widgets:
            html.append(self._render_widget_html(widget, data))
        
        html.append('</div></div>')
        
        return "\n".join(html)
    
    def _render_widget_html(
        self,
        widget: Widget,
        data: Dict[str, Any]
    ) -> str:
        """Render a widget as HTML"""
        value = self._get_data_value(widget.data_source, data)
        
        html = [f'<div class="widget">']
        
        if widget.show_title:
            html.append(f'<div class="widget-title">{widget.title}</div>')
        
        if widget.widget_type == WidgetType.METRIC_CARD:
            formatted_value = self._format_metric_value(value)
            html.append(f'''
                <div class="metric-card">
                    <div class="metric-value">{formatted_value}</div>
                </div>
            ''')
        
        elif widget.widget_type == WidgetType.TEXT:
            html.append(f'<div class="text-content">{widget.content}</div>')
        
        elif widget.widget_type == WidgetType.TABLE:
            html.append(self._render_table_html(value))
        
        else:
            # Placeholder for charts (would use Plotly/Chart.js in real implementation)
            html.append(f'<div class="chart-placeholder">[{widget.widget_type.value} visualization]</div>')
        
        html.append('</div>')
        
        return "\n".join(html)
    
    def _get_data_value(
        self,
        data_source: str,
        data: Dict[str, Any]
    ) -> Any:
        """Extract value from data using dot notation path"""
        if not data_source:
            return None
        
        parts = data_source.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def _format_metric_value(self, value: Any) -> str:
        """Format metric value for display"""
        if value is None:
            return "N/A"
        
        if isinstance(value, float):
            if abs(value) < 1:
                return f"{value:.2%}"
            else:
                return f"{value:.2f}"
        
        return str(value)
    
    def _render_table_html(self, data: Any) -> str:
        """Render data as HTML table"""
        if not data:
            return "<p>No data available</p>"
        
        if isinstance(data, list) and len(data) > 0:
            headers = list(data[0].keys()) if isinstance(data[0], dict) else []
            
            html = ['<table>']
            
            if headers:
                html.append('<thead><tr>')
                for h in headers:
                    html.append(f'<th>{h}</th>')
                html.append('</tr></thead>')
            
            html.append('<tbody>')
            for row in data:
                html.append('<tr>')
                if isinstance(row, dict):
                    for h in headers:
                        val = row.get(h, '')
                        html.append(f'<td>{self._format_metric_value(val)}</td>')
                html.append('</tr>')
            html.append('</tbody></table>')
            
            return "\n".join(html)
        
        return "<p>Invalid data format</p>"
