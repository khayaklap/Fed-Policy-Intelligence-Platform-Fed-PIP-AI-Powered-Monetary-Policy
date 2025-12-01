"""
Visualization Generator

Generate charts and visualizations for Fed policy reports.
"""

import logging
from typing import Dict, List, Optional
import io
import base64

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib/seaborn not available - visualizations disabled")

try:
    # Try relative imports first (when used as module)
    from .report_generator_config import CHART_STYLE
except ImportError:
    # Fall back to absolute imports (when run directly)
    from report_generator_config import CHART_STYLE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisualizationGenerator:
    """
    Generate visualizations for Fed policy reports.
    """
    
    def __init__(self):
        """Initialize visualization generator."""
        logger.info("Initialized Visualization Generator")
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('seaborn-v0_8-darkgrid')
    
    def generate_time_series_chart(
        self,
        data: List[Dict],
        title: str = "Fed Policy Sentiment Over Time",
        xlabel: str = "Date",
        ylabel: str = "Sentiment Score"
    ) -> Optional[str]:
        """
        Generate time series chart.
        
        Args:
            data: List of {'date': str, 'value': float}
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
        
        Returns:
            Base64-encoded image or None
        """
        if not MATPLOTLIB_AVAILABLE or not data:
            return None
        
        logger.info("Generating time series chart")
        
        dates = [d['date'] for d in data]
        values = [d['value'] for d in data]
        
        fig, ax = plt.subplots(figsize=CHART_STYLE['figure_size'])
        ax.plot(dates, values, linewidth=2, color='#1f77b4')
        ax.set_title(title, fontsize=CHART_STYLE['title_size'])
        ax.set_xlabel(xlabel, fontsize=CHART_STYLE['label_size'])
        ax.set_ylabel(ylabel, fontsize=CHART_STYLE['label_size'])
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=CHART_STYLE['dpi'])
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    
    def generate_gauge_chart(
        self,
        score: float,
        title: str = "Current Policy Stance"
    ) -> Optional[str]:
        """
        Generate gauge chart for policy stance.
        
        Args:
            score: Sentiment score (-20 to +20)
            title: Chart title
        
        Returns:
            Base64-encoded image or None
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        logger.info("Generating gauge chart")
        
        fig, ax = plt.subplots(figsize=(8, 4), subplot_kw={'projection': 'polar'})
        
        # Normalize score to 0-1
        normalized = (score + 20) / 40
        
        # Color based on score
        if score < -10:
            color = '#2ca02c'  # Green (dovish)
        elif score > 10:
            color = '#d62728'  # Red (hawkish)
        else:
            color = '#ff9800'  # Amber (neutral)
        
        # Draw gauge
        theta = np.linspace(0, np.pi, 100)
        r = np.ones(100)
        ax.plot(theta, r, color='lightgray', linewidth=20)
        
        # Fill to score position
        theta_fill = np.linspace(0, np.pi * normalized, 100)
        ax.plot(theta_fill, np.ones(100), color=color, linewidth=20)
        
        # Pointer
        ax.arrow(0, 0, np.pi * normalized, 0.95, head_width=0.15, head_length=0.05, fc='black', ec='black')
        
        ax.set_ylim(0, 1.2)
        ax.set_yticks([])
        ax.set_xticks([0, np.pi/2, np.pi])
        ax.set_xticklabels(['Hawkish\n(+20)', 'Neutral\n(0)', 'Dovish\n(-20)'])
        ax.set_title(title, fontsize=14, pad=20)
        
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=CHART_STYLE['dpi'], bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    
    def generate_comparison_table(
        self,
        data: List[Dict],
        columns: List[str]
    ) -> str:
        """
        Generate HTML comparison table.
        
        Args:
            data: List of dictionaries
            columns: Column names
        
        Returns:
            HTML table string
        """
        logger.info("Generating comparison table")
        
        html = '<table style="border-collapse: collapse; width: 100%;">\n'
        
        # Header
        html += '  <tr style="background-color: #1f77b4; color: white;">\n'
        for col in columns:
            html += f'    <th style="padding: 8px; border: 1px solid #ddd;">{col}</th>\n'
        html += '  </tr>\n'
        
        # Rows
        for i, row in enumerate(data):
            bg_color = '#f9f9f9' if i % 2 == 0 else 'white'
            html += f'  <tr style="background-color: {bg_color};">\n'
            for col in columns:
                value = row.get(col.lower().replace(' ', '_'), 'N/A')
                html += f'    <td style="padding: 8px; border: 1px solid #ddd;">{value}</td>\n'
            html += '  </tr>\n'
        
        html += '</table>'
        
        return html
    
    def generate_bar_chart(
        self,
        data: Dict[str, float],
        title: str = "Comparison",
        xlabel: str = "Category",
        ylabel: str = "Value"
    ) -> Optional[str]:
        """
        Generate bar chart.
        
        Args:
            data: Dictionary of {label: value}
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
        
        Returns:
            Base64-encoded image or None
        """
        if not MATPLOTLIB_AVAILABLE or not data:
            return None
        
        logger.info("Generating bar chart")
        
        fig, ax = plt.subplots(figsize=CHART_STYLE['figure_size'])
        
        categories = list(data.keys())
        values = list(data.values())
        
        bars = ax.bar(categories, values, color='#1f77b4', alpha=0.7)
        ax.set_title(title, fontsize=CHART_STYLE['title_size'])
        ax.set_xlabel(xlabel, fontsize=CHART_STYLE['label_size'])
        ax.set_ylabel(ylabel, fontsize=CHART_STYLE['label_size'])
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=CHART_STYLE['dpi'])
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64


def generate_visualization(viz_type: str, data: any, **kwargs) -> Optional[str]:
    """
    Convenience function to generate visualization.
    
    Args:
        viz_type: Type of visualization
        data: Data for visualization
        **kwargs: Additional parameters
    
    Returns:
        Base64-encoded image or HTML string
    """
    generator = VisualizationGenerator()
    
    if viz_type == 'time_series':
        return generator.generate_time_series_chart(data, **kwargs)
    elif viz_type == 'gauge':
        return generator.generate_gauge_chart(data, **kwargs)
    elif viz_type == 'comparison_table':
        return generator.generate_comparison_table(data, **kwargs)
    elif viz_type == 'bar_chart':
        return generator.generate_bar_chart(data, **kwargs)
    else:
        logger.warning(f"Unknown visualization type: {viz_type}")
        return None
