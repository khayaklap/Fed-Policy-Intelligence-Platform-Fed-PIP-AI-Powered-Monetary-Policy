# Document Processor Agent

**Parse and analyze FOMC documents to extract Fed forecasts, policy decisions, and sentiment**

This is the **first core agent** for Fed-PIP that connects your FOMC document dataset with the external data agents (FRED, BLS, Treasury).

---

## 📊 Overview

The Document Processor parses three types of FOMC documents:

- **SEP** (4/year): Economic projections
- **Minutes** (8/year): Policy decisions & sentiment
- **MPR** (2/year): Comprehensive reports

**Extracts:**
- ✅ Fed forecasts (GDP, inflation, unemployment, Fed Funds)
- ✅ Policy decisions (rate changes)
- ✅ Hawkish/dovish sentiment
- ✅ Forward guidance
- ✅ Voting records

---

## 🚀 Quick Start

```bash
# Install
pip install -r doc_processor_requirements.txt
python -m spacy download en_core_web_sm

# Use
from doc_processor_agent import create_document_processor_agent

agent = create_document_processor_agent()
```

---

## 📚 5 Tools

### 1. `extract_sep_forecasts` - Get Fed forecasts

```python
result = extract_sep_forecasts("/path/to/sep.pdf")
# → All economic projections by year
```

### 2. `analyze_fomc_minutes_tool` - Full Minutes analysis

```python
result = analyze_fomc_minutes_tool("/path/to/minutes.pdf")
# → Policy decision, sentiment, voting, key phrases
```

### 3. `extract_policy_decision` - Quick policy action

```python
decision = extract_policy_decision("/path/to/minutes.pdf")
# → Rate change only (faster)
```

### 4. `compare_sep_with_actual` - **KILLER TOOL**

```python
result = compare_sep_with_actual(
    "/path/to/sep_20210616.pdf",
    "pce_inflation",
    "2022",
    6.5  # Actual from FRED
)
# → Forecast error analysis
```

### 5. `get_document_metadata` - Quick info

```python
info = get_document_metadata("/path/to/any_doc.pdf")
# → File info without full parse
```

---

## 💡 Complete Example

**Validate Fed's 2021 inflation forecast:**

```python
# 1. Extract Fed forecast
sep = extract_sep_forecasts("/path/to/sep_20210616.pdf")
fed_forecast = sep['projections']['pce_inflation']['projections']['2022']
# → 2.1%

# 2. Compare with actual (FRED agent)
comparison = compare_sep_with_actual(
    "/path/to/sep_20210616.pdf",
    "pce_inflation",
    "2022",
    6.5  # From FRED
)

print(comparison['interpretation'])
# → "Fed significantly underestimated inflation by 4.4pp"
```

---

## 🔄 Integration with External Agents

```python
# All agents working together
orchestrator = LlmAgent(
    sub_agents=[
        AgentTool(doc_processor),  # Fed forecasts
        AgentTool(fred_agent),     # Actual data
        AgentTool(bls_agent),      # Components
        AgentTool(treasury_agent)  # Market expectations
    ]
)

# Comprehensive query
response = await runner.run_debug("""
    Analyze Fed's June 2021 inflation forecast:
    1. Extract forecast from SEP
    2. Get actual 2022 inflation (FRED)
    3. Identify drivers (BLS)
    4. Check market expectations (Treasury)
""")
```

---

## 📖 What It Parses

### SEP Structure

```
Variable          | 2023 | 2024 | 2025 | Longer Run
------------------|------|------|------|------------
Real GDP          | 1.0  | 1.1  | 1.8  | 1.8
Unemployment      | 4.1  | 4.1  | 4.1  | 4.0
PCE inflation     | 3.2  | 2.5  | 2.1  | 2.0
Fed funds rate    | 5.1  | 4.6  | 3.4  | 2.5
```

### Minutes Structure

1. Market developments
2. Staff economic review
3. **Participants' views** ← Sentiment here
4. **Policy action** ← Decision here
5. **Voting** ← Split/dissents

---

## 🎓 Understanding Forecasts

**"Longer Run" projections = Fed's view of normal:**
- GDP: ~1.8% (potential growth)
- Unemployment: ~4.0% (NAIRU)
- Inflation: 2.0% (target)
- Fed Funds: ~2.5% (R-star)

**Forecast Accuracy:**
- Inflation: Often underestimated
- GDP: Good near-term, uncertain long-term
- Unemployment: Relatively accurate
- Fed Funds: Self-fulfilling (Fed controls it)

---

## 📦 Files Created

All in `/mnt/user-data/outputs/`:

1. ✅ doc_processor_requirements.txt
2. ✅ doc_processor_config.py
3. ✅ pdf_parser.py
4. ✅ sep_extractor.py
5. ✅ text_analyzer.py
6. ✅ doc_processor_tools.py
7. ✅ doc_processor_agent.py
8. ✅ test_doc_processor.py
9. ✅ README_DOC_PROCESSOR.md

**Total: ~3,000 lines of code**

---

## ✅ Summary

**You can now:**
- ✅ Parse FOMC documents
- ✅ Extract Fed forecasts
- ✅ Analyze policy decisions
- ✅ Compare forecasts vs actuals
- ✅ Integrate with external data agents

**This connects your dataset to your analysis framework!** 🎉

Download FOMC docs: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
