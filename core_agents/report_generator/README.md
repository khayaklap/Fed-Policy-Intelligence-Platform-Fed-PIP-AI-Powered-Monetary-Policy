# Report Generator - Professional Fed Policy Reports

**Generate publication-quality Fed policy reports in multiple formats.**

The Report Generator is the fifth core agent in the Fed Policy Intelligence Platform. It synthesizes analysis from all other agents into comprehensive, professional documents exportable to PDF, DOCX, HTML, Markdown, and JSON.

---

## 🎯 Quick Start

```python
from report_generator_tools import generate_comprehensive_report_tool

# Gather data from all agents
agent_data = {
    'document_processor': doc_analysis,
    'policy_analyzer': policy_analysis,
    'trend_tracker': trend_analysis,
    'comparative_analyzer': historical_analysis,
    'fred': economic_data,
    'bls': inflation_data,
    'treasury': market_data
}

# Generate comprehensive report
report = generate_comprehensive_report_tool(
    agent_data,
    export_format='pdf'
)

print(f"Report generated: {report['export_path']}")
# Output: fed_policy_comprehensive_report_2024-11-29.pdf
```

---

## 📦 Installation

```bash
pip install -r report_generator_requirements.txt
```

---

## 🛠️ Five Tools

### 1. **generate_comprehensive_report_tool**
Full 15-25 page analysis using all agents
- 8 sections: Executive Summary, Current Stance, Recent Trends, Long-Term Patterns, Historical Comparisons, Economic Context, Predictive Indicators, Recommendations
- Exports to: PDF, DOCX, HTML, Markdown, JSON

### 2. **generate_episode_comparison_report_tool**
8-12 page comparison of two Fed episodes
- Detailed similarity analysis
- Lessons learned
- Implications for current policy

### 3. **generate_quick_summary_tool**
2-3 page executive briefing
- Current stance
- Recent actions
- Key metrics
- Outlook

### 4. **generate_custom_report_tool**
Flexible reports with chosen sections
- Select specific sections
- Custom title
- Tailored analysis

### 5. **export_report_tool**
Export to multiple formats
- One report → many formats
- PDF, DOCX, HTML, Markdown, JSON

---

## 📊 Report Types

| Type | Length | Sections | Use Case |
|------|--------|----------|----------|
| Comprehensive | 15-25 pages | 8 | Full analysis for decision-makers |
| Episode Comparison | 8-12 pages | 6 | Historical context |
| Quick Summary | 2-3 pages | 4 | Executive briefing |
| Custom | Variable | User-selected | Specific needs |

---

## 💾 Export Formats

| Format | Extension | Features | Best For |
|--------|-----------|----------|----------|
| PDF | .pdf | Professional, pagination | Final reports |
| DOCX | .docx | Editable, styles | Collaboration |
| HTML | .html | Responsive, interactive | Web publishing |
| Markdown | .md | Plain text, GitHub | Quick sharing |
| JSON | .json | Structured data | APIs, automation |

---

## 📈 Example Use Cases

### Use Case 1: Quarterly Fed Policy Report
```python
# Comprehensive quarterly analysis
report = generate_comprehensive_report_tool(
    agent_data=all_agent_data,
    time_period=('2024-07-01', '2024-09-30'),
    export_format='pdf'
)
```

### Use Case 2: Compare GFC vs COVID
```python
# Episode comparison for historical context
comparison = generate_episode_comparison_report_tool(
    episode1='gfc_response_2007_2008',
    episode2='covid_response_2020',
    export_format='docx'
)
```

### Use Case 3: Pre-Meeting Briefing
```python
# Quick summary before FOMC meeting
summary = generate_quick_summary_tool(
    recent_meetings=last_3_meetings,
    export_format='markdown'
)
```

---

## 🧪 Testing

```bash
pytest test_report_generator.py -v
```

---

## 🔗 Integration

Aggregates data from all agents:
- **Document Processor** → Meeting analyses
- **Policy Analyzer** → Sentiment trends
- **Trend Tracker** → Long-term patterns
- **Comparative Analyzer** → Historical comparisons
- **FRED** → Economic data
- **BLS** → Inflation/employment
- **Treasury** → Market expectations

---

## 📁 Files

- report_generator_config.py (500 lines) - Templates, styles
- report_builder.py (650 lines) - Core report construction
- format_exporters.py (650 lines) - PDF, DOCX, HTML, Markdown exporters
- visualization_generator.py (300 lines) - Charts and graphs
- report_generator_tools.py (650 lines) - 5 ADK tools
- report_generator_agent.py (150 lines) - Agent
- test_report_generator.py (300 lines) - Tests

**Total: ~3,200 lines | 5 tools | 5 formats | 4 report types**

---

**Report Generator: Professional Fed policy reports at your fingertips.**
