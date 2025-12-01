# REPORT GENERATOR - QUICK REFERENCE

## 🚀 Installation
```bash
pip install -r report_generator_requirements.txt
```

## 🛠️ Five Tools

### 1. Comprehensive Report
```python
generate_comprehensive_report_tool(agent_data, export_format='pdf')
# Returns: 15-25 page full analysis
```

### 2. Episode Comparison
```python
generate_episode_comparison_report_tool(episode1, episode2, export_format='pdf')
# Returns: 8-12 page comparison
```

### 3. Quick Summary
```python
generate_quick_summary_tool(recent_meetings, export_format='markdown')
# Returns: 2-3 page briefing
```

### 4. Custom Report
```python
generate_custom_report_tool(sections, agent_data, title, export_format='docx')
# Returns: Custom sections
```

### 5. Export Report
```python
export_report_tool(report, filename, formats=['pdf', 'docx', 'html'])
# Returns: Multiple format exports
```

## 📊 Report Types

| Type | Pages | Sections | Use |
|------|-------|----------|-----|
| Comprehensive | 15-25 | 8 | Full analysis |
| Episode Comparison | 8-12 | 6 | Historical context |
| Quick Summary | 2-3 | 4 | Executive briefing |
| Trend Analysis | 10-15 | 7 | Pattern analysis |
| Custom | Variable | User-selected | Specific needs |

## 💾 Export Formats

| Format | Extension | Features |
|--------|-----------|----------|
| PDF | .pdf | Professional, pagination |
| DOCX | .docx | Editable, styles |
| HTML | .html | Responsive, interactive |
| Markdown | .md | Plain text, GitHub |
| JSON | .json | Structured data |

## 📈 Comprehensive Report Sections

1. **Executive Summary** - Key findings (500 words)
2. **Current Stance** - Fed funds, sentiment, classification
3. **Recent Trends** - 1.5-6 year evolution
4. **Long-Term Patterns** - 6-20 year cycles
5. **Historical Comparisons** - Similar episodes
6. **Economic Context** - Inflation, unemployment, GDP
7. **Predictive Indicators** - Leading signals
8. **Recommendations** - Key takeaways

## 🔗 Required Agent Data

```python
agent_data = {
    'document_processor': {...},   # Meeting analyses
    'policy_analyzer': {...},      # Sentiment trends
    'trend_tracker': {...},        # Long-term patterns
    'comparative_analyzer': {...}, # Comparisons
    'fred': {...},                 # Economic data
    'bls': {...},                  # Inflation data
    'treasury': {...}              # Market data
}
```

## 🎨 Visualizations

- **Time Series** - Policy evolution charts
- **Gauge** - Stance meter (-20 to +20)
- **Tables** - Comparison matrices
- **Bar Charts** - Action counts
- **Dashboards** - Economic indicators

## ⚡ Quick Examples

### Generate Quarterly Report
```python
report = generate_comprehensive_report_tool(
    all_agent_data,
    time_period=('2024-07-01', '2024-09-30'),
    export_format='pdf'
)
```

### Compare Two Episodes
```python
comparison = generate_episode_comparison_report_tool(
    'gfc_response_2007_2008',
    'covid_response_2020',
    export_format='docx'
)
```

### Pre-Meeting Briefing
```python
summary = generate_quick_summary_tool(
    last_3_meetings,
    export_format='markdown'
)
```

### Multi-Format Export
```python
exports = export_report_tool(
    report,
    'fed_policy_q3_2024',
    formats=['pdf', 'docx', 'html', 'markdown']
)
```

## 🧪 Testing
```bash
pytest test_report_generator.py -v
```

## 📁 Files

- report_generator_config.py (500 lines) - Templates, styles
- report_builder.py (650 lines) - Report construction
- format_exporters.py (650 lines) - PDF, DOCX, HTML, MD
- visualization_generator.py (300 lines) - Charts
- report_generator_tools.py (650 lines) - 5 ADK tools
- report_generator_agent.py (150 lines) - Agent

**Total: ~3,200 lines | 5 tools | 5 formats | 5 report types**
