# Policy Analyzer Agent

**Analyze Fed policy stance evolution, regime changes, and sentiment trends over time.**

The Policy Analyzer is a core agent in the Fed Policy Intelligence Platform that tracks how Fed policy evolves across multiple FOMC meetings. It identifies:
- **Sentiment trends** (hawkish/dovish evolution)
- **Regime changes** (accommodative ↔ tightening ↔ neutral)
- **Policy turning points** (when Fed pivots)
- **Historical comparisons** (current vs past episodes)
- **Stance appropriateness** (policy vs economic conditions)

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Tools Reference](#tools-reference)
4. [Real-World Use Cases](#real-world-use-cases)
5. [Integration Patterns](#integration-patterns)
6. [Understanding Policy Regimes](#understanding-policy-regimes)
7. [Testing](#testing)
8. [Examples](#examples)

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r policy_analyzer_requirements.txt

# Install Document Processor (required)
# Policy Analyzer needs meeting-level data from Document Processor
```

### Basic Usage

```python
from policy_analyzer_agent import create_policy_analyzer_agent
from google.adk.in_memory_runner import InMemoryRunner

# Create agent
agent = create_policy_analyzer_agent()
runner = InMemoryRunner(agent=agent)

# Analyze sentiment trend
meeting_data = [
    {'date': '2021-06-16', 'sentiment': 'dovish', 'score': -8},
    {'date': '2021-11-03', 'sentiment': 'neutral', 'score': 2},
    {'date': '2022-03-16', 'sentiment': 'hawkish', 'score': 12},
    {'date': '2022-06-15', 'sentiment': 'hawkish', 'score': 18}
]

response = await runner.run_debug(
    "Analyze the sentiment trend in this data",
    context={'meeting_data': meeting_data}
)
```

---

## 🏗️ Architecture

### Component Overview

```
Policy Analyzer
├── sentiment_tracker.py      # Time-series sentiment analysis
├── regime_detector.py         # Policy regime classification
├── stance_classifier.py       # Overall stance assessment
├── policy_analyzer_tools.py   # 5 ADK tools
└── policy_analyzer_agent.py   # ADK agent orchestrator
```

### Data Flow

```
Document Processor (per meeting)
    ↓
    Extract: sentiment, score, action, guidance
    ↓
Policy Analyzer (across meetings)
    ↓
    Analyze: trends, regimes, shifts, turning points
    ↓
Results: Evolution analysis, historical context
```

---

## 🛠️ Tools Reference

### Tool 1: `analyze_sentiment_trend`

**Track hawkish/dovish sentiment evolution over time.**

```python
analyze_sentiment_trend(
    meeting_data: List[Dict],
    recent_meetings: int = 12
) -> Dict
```

**Input:**
```python
[
    {'date': '2021-06-16', 'sentiment': 'dovish', 'score': -8},
    {'date': '2022-03-16', 'sentiment': 'hawkish', 'score': 12},
    # ... more meetings
]
```

**Output:**
```python
{
    'current_stance': {
        'classification': 'hawkish',
        'score': 12,
        'confidence': 'high'
    },
    'trend': {
        'direction': 'strong_hawkish_trend',
        'slope': 2.5,  # Score increase per meeting
        'strength': 'strong',
        'interpretation': 'Sentiment strongly becoming more hawkish'
    },
    'significant_shifts': [
        {
            'date': '2022-01-26',
            'change': 8,  # From 2 to 10
            'previous_stance': 'neutral',
            'new_stance': 'hawkish',
            'magnitude': 'moderate'
        }
    ],
    'volatility': {
        'volatility': 4.2,
        'level': 'stable',
        'interpretation': 'Sentiment fairly consistent'
    }
}
```

**Use Cases:**
- Track 2021-2022 inflation surge evolution
- Identify when Fed abandoned "transitory" view
- Measure consistency of Fed messaging

---

### Tool 2: `detect_regime_changes`

**Identify policy regime changes and compare to history.**

```python
detect_regime_changes(
    meeting_data: List[Dict]
) -> Dict
```

**Policy Regimes:**
- **Accommodative**: Rate cuts, dovish, supporting growth
- **Tightening**: Rate hikes, hawkish, fighting inflation
- **Neutral**: Rates stable, data-dependent, balanced
- **Pivot to Tightening**: Transitioning from ease to tightening
- **Pivot to Easing**: Transitioning from tightening to ease

**Input:**
```python
[
    {'date': '2020-03-15', 'action': 'decrease', 'sentiment': 'dovish'},
    {'date': '2022-03-16', 'action': 'increase', 'sentiment': 'hawkish'},
    # ... more meetings
]
```

**Output:**
```python
{
    'current_regime': {
        'regime': 'tightening',
        'description': 'Raising rates to combat inflation',
        'duration': 7,  # meetings in regime
        'stability': 'established'
    },
    'regime_changes': [
        {
            'date': '2022-03-16',
            'previous_regime': 'accommodative',
            'new_regime': 'tightening',
            'duration': 8,
            'type': 'shift_to_tightening'
        }
    ],
    'historical_comparison': {
        'most_similar': {
            'episode': '2022_inflation_fight',
            'description': 'Fastest tightening since 1980s',
            'period': ('2022-03-01', '2023-07-31'),
            'similarity': 0.9
        }
    }
}
```

**Use Cases:**
- Identify when Fed shifted from COVID support to inflation fighting
- Compare current cycle to historical episodes
- Predict regime duration

---

### Tool 3: `classify_policy_stance_tool`

**Classify overall policy stance combining multiple signals.**

```python
classify_policy_stance_tool(
    meeting_data: List[Dict],
    economic_data: Optional[Dict] = None
) -> Dict
```

**Signals Combined:**
1. Policy actions (rate changes) - 40% weight
2. Sentiment (language) - 30% weight
3. Rate levels (real rates) - 30% weight

**Stance Categories:**
- **Highly Accommodative**: Very loose, maximum support
- **Accommodative**: Supportive, encouraging growth
- **Neutral**: Balanced, data-dependent
- **Restrictive**: Tight, slowing economy
- **Highly Restrictive**: Very tight, aggressive inflation fight

**Input:**
```python
meeting_data = [...]  # Recent meetings
economic_data = {
    'fed_funds': 5.25,
    'real_rate': 2.0,  # nominal - inflation
    'inflation': 3.2,
    'unemployment': 3.7,
    'gdp_growth': 2.1
}
```

**Output:**
```python
{
    'overall_stance': {
        'stance': 'restrictive',
        'overall_score': 8.5,
        'description': 'Tight policy - slowing economy to control inflation',
        'confidence': 'high',
        'component_scores': {
            'action_score': 10,      # Rate increases
            'sentiment_score': 12,   # Hawkish language
            'rate_score': 10         # High real rates
        }
    },
    'conditions_comparison': {
        'appropriate_stance': 'restrictive',
        'alignment': 'well_aligned',
        'interpretation': 'Policy stance is appropriate for current conditions',
        'rationale': 'High inflation + low unemployment = economy overheating, needs tightening'
    },
    'trajectory': {
        'trajectory': 'tightening',
        'start_stance': 'accommodative',
        'end_stance': 'restrictive',
        'change': 2,
        'description': 'Policy has shifted toward restriction'
    }
}
```

**Use Cases:**
- Assess if Fed policy matches economic conditions
- Identify policy too tight/loose for environment
- Track stance evolution over time

---

### Tool 4: `compare_policy_periods`

**Compare Fed policy between two time periods.**

```python
compare_policy_periods(
    period1_data: List[Dict],
    period2_data: List[Dict],
    period1_label: str = "Period 1",
    period2_label: str = "Period 2"
) -> Dict
```

**Input:**
```python
covid_response = [...]  # 2020-2021 meetings
inflation_fight = [...]  # 2022-2023 meetings

result = compare_policy_periods(
    covid_response,
    inflation_fight,
    "COVID Response",
    "Inflation Fight"
)
```

**Output:**
```python
{
    'period1': {
        'label': 'COVID Response',
        'regime': 'accommodative',
        'avg_sentiment_score': -12,
        'num_meetings': 8,
        'actions': ['decrease', 'unchanged', 'unchanged', ...]
    },
    'period2': {
        'label': 'Inflation Fight',
        'regime': 'tightening',
        'avg_sentiment_score': 16,
        'num_meetings': 7,
        'actions': ['increase', 'increase', 'increase', ...]
    },
    'comparison': {
        'sentiment_shift': 28,  # From -12 to +16
        'regime_change': 'accommodative → tightening',
        'interpretation': 'Complete policy reversal toward more hawkish stance'
    }
}
```

**Use Cases:**
- Compare 2008 GFC vs 2020 COVID responses
- Contrast tightening cycles (2004-2006 vs 2022-2023)
- Evaluate different Fed chairs' approaches

---

### Tool 5: `get_current_policy_assessment`

**Get comprehensive current policy assessment.**

```python
get_current_policy_assessment(
    recent_meetings: List[Dict],
    economic_data: Optional[Dict] = None
) -> Dict
```

**Output:**
```python
{
    'summary': 'Fed in tightening regime, restrictive stance well-aligned with conditions',
    'current_stance': {...},  # From classify_policy_stance_tool
    'current_regime': {...},  # From detect_regime_changes
    'sentiment_trend': {...}, # From analyze_sentiment_trend
    'appropriateness': {...}, # Conditions assessment
    'recent_shifts': [...],   # Significant changes
    'num_meetings_analyzed': 12
}
```

**Use Cases:**
- Quick snapshot of current Fed policy
- Comprehensive briefing
- Integration with other agents for full analysis

---

## 💡 Real-World Use Cases

### Use Case 1: Track 2021-2022 Inflation Surge Evolution

**Question:** "How did Fed sentiment evolve during the 2021-2022 inflation surge?"

```python
# Step 1: Get meeting data from Document Processor
meetings_2021_2022 = [
    # Document Processor extracts sentiment from each meeting
    {'date': '2021-01-27', 'sentiment': 'dovish', 'score': -10},
    {'date': '2021-06-16', 'sentiment': 'dovish', 'score': -8},  # "Transitory"
    {'date': '2021-11-03', 'sentiment': 'neutral', 'score': 2},  # Starting to worry
    {'date': '2022-01-26', 'sentiment': 'hawkish', 'score': 10}, # Inflation "entrenched"
    {'date': '2022-03-16', 'sentiment': 'hawkish', 'score': 12},
    {'date': '2022-06-15', 'sentiment': 'highly_hawkish', 'score': 18}
]

# Step 2: Analyze with Policy Analyzer
result = analyze_sentiment_trend(meetings_2021_2022)

# Result:
# - Trend: Strong hawkish trend (slope: +2.8 per meeting)
# - Shifts: Major shift Jan 2022 (neutral → hawkish, +8 points)
# - Current: Highly hawkish (score: 18)
# - Interpretation: "Fed abandoned 'transitory' view, shifted to aggressive tightening"
```

**Key Insights:**
- Fed stayed dovish too long (June 2021: still -8 despite rising inflation)
- Pivot came late (Nov 2021, 6 months after inflation surge began)
- Once pivoted, became very hawkish very fast (+26 points in 6 months)

---

### Use Case 2: Identify Regime Changes

**Question:** "When did Fed switch from COVID support to inflation fighting?"

```python
result = detect_regime_changes(meetings_2020_2023)

# Result:
{
    'regime_changes': [
        {
            'date': '2022-03-16',
            'previous_regime': 'accommodative',
            'new_regime': 'tightening',
            'duration': 24,  # Accommodative lasted 24 meetings (3 years)
            'type': 'shift_to_tightening'
        }
    ],
    'historical_comparison': {
        'most_similar': '2022_inflation_fight',
        'description': 'Fastest tightening since 1980s'
    }
}
```

**Analysis:**
- Regime change: March 16, 2022 (first rate hike)
- Accommodative lasted: March 2020 - March 2022 (2 years)
- Tightening phase: March 2022 - present
- Historical parallel: Similar to 1980s Volcker, but slower

---

### Use Case 3: Assess Policy Appropriateness

**Question:** "Is current Fed policy appropriate for economic conditions?"

```python
current_data = {
    'fed_funds': 5.25,
    'real_rate': 2.0,
    'inflation': 3.2,
    'unemployment': 3.7,
    'gdp_growth': 2.1
}

result = classify_policy_stance_tool(recent_meetings, current_data)

# Result:
{
    'overall_stance': {
        'stance': 'restrictive',
        'overall_score': 8.5
    },
    'conditions_comparison': {
        'appropriate_stance': 'restrictive',
        'alignment': 'well_aligned',
        'interpretation': 'Policy stance is appropriate for current conditions',
        'rationale': 'Inflation above target + tight labor market = tightening needed'
    }
}
```

**Interpretation:**
- Current stance: Restrictive (real rates at 2.0%)
- Conditions: Inflation 3.2% (above 2% target), unemployment 3.7% (low)
- Assessment: ✅ Well-aligned (policy appropriately tight)
- Recommendation: Maintain restrictive stance until inflation sustainably at target

---

### Use Case 4: Compare Historical Episodes

**Question:** "How does current tightening compare to 2004-2006 cycle?"

```python
result = compare_policy_periods(
    meetings_2004_2006,
    meetings_2022_2023,
    "2004-2006 Tightening",
    "2022-2023 Tightening"
)

# Result:
{
    'period1': {
        'regime': 'tightening',
        'avg_sentiment_score': 8,  # Moderately hawkish
        'actions': 17 rate hikes of 25bp each
    },
    'period2': {
        'regime': 'tightening',
        'avg_sentiment_score': 16,  # Very hawkish
        'actions': 11 hikes including 4 × 75bp
    },
    'comparison': {
        'interpretation': '2022-2023 much more aggressive (larger hikes, more hawkish)'
    }
}
```

**Key Differences:**
- **2004-2006**: Gradual (17 × 25bp), measured, "measured pace"
- **2022-2023**: Aggressive (4 × 75bp), fastest since 1980s, "front-loaded"
- **Why different**: 2022 inflation much higher (9% vs 3%)

---

## 🔗 Integration Patterns

### Integration 1: Document Processor → Policy Analyzer

**Complete workflow for multi-meeting analysis:**

```python
from document_processor_tools import analyze_fomc_minutes_tool
from policy_analyzer_tools import analyze_sentiment_trend

# Step 1: Extract data from each meeting (Document Processor)
meetings = []
for minutes_file in minutes_files_2021_2022:
    analysis = analyze_fomc_minutes_tool(minutes_file)
    meetings.append({
        'date': analysis['metadata']['meeting_date'],
        'sentiment': analysis['sentiment']['sentiment'],
        'score': analysis['sentiment']['score'],
        'action': analysis['policy_decision']['action']
    })

# Step 2: Analyze evolution (Policy Analyzer)
evolution = analyze_sentiment_trend(meetings)

# Result: Complete picture of sentiment evolution
```

---

### Integration 2: Policy Analyzer + FRED + Treasury

**Assess stance appropriateness with external data:**

```python
# Step 1: Get Fed policy data (Policy Analyzer)
policy_assessment = get_current_policy_assessment(recent_meetings)

# Step 2: Get economic data (FRED)
inflation = fred_agent.get_inflation_data(measure='pce')
unemployment = fred_agent.get_unemployment_rate()
gdp = fred_agent.get_gdp_growth()

# Step 3: Get real rates (Treasury)
real_rate = treasury_agent.get_real_yield(maturity='10y')

# Step 4: Comprehensive assessment (Policy Analyzer)
stance = classify_policy_stance_tool(
    recent_meetings,
    {
        'inflation': inflation['latest']['yoy'],
        'unemployment': unemployment['latest'],
        'gdp_growth': gdp['latest']['yoy'],
        'real_rate': real_rate['yield']
    }
)

# Result: Policy stance + conditions + appropriateness
```

---

### Integration 3: Multi-Agent Complete Analysis

**Full Fed policy analysis combining all agents:**

```python
# 1. Document Processor: Parse meetings
meetings = [analyze_fomc_minutes_tool(f) for f in files]

# 2. Policy Analyzer: Track evolution
evolution = analyze_sentiment_trend(meetings)
regime = detect_regime_changes(meetings)

# 3. FRED: Get actual outcomes
actual_inflation = fred_agent.get_inflation_data()
actual_gdp = fred_agent.get_gdp_growth()

# 4. Document Processor: Get forecasts
forecasts = extract_sep_forecasts(sep_file)

# 5. Document Processor: Compare forecast vs actual
validation = compare_sep_with_actual(
    sep_file,
    'pce_inflation',
    '2022',
    actual_inflation['latest']['yoy']
)

# Result: Complete analysis
# - Fed forecasts (Document Processor)
# - Actual outcomes (FRED)
# - Forecast accuracy (Document Processor)
# - Policy evolution (Policy Analyzer)
# - Regime changes (Policy Analyzer)
```

---

## 📊 Understanding Policy Regimes

### Regime Characteristics

| Regime | Actions | Sentiment | Economic Context | Example Period |
|--------|---------|-----------|------------------|----------------|
| **Accommodative** | Rate cuts, QE | Dovish | Recession, weak growth | 2008-2015, 2020-2021 |
| **Tightening** | Rate hikes, QT | Hawkish | Strong economy, high inflation | 2004-2006, 2022-2023 |
| **Neutral** | Rates stable | Balanced | Data-dependent | 2019, 2024 |
| **Pivot to Tightening** | Ending ease | Hawkish shift | Inflation rising | Late 2021 |
| **Pivot to Easing** | Ending tightening | Dovish shift | Growth slowing | 2007, 2019 |

### Regime Duration Patterns

- **Accommodative**: Typically long (2-5 years) - Fed patient with support
- **Tightening**: Typically medium (1-3 years) - Fed normalizes then stops
- **Neutral**: Variable (months to years) - "data-dependent" pause
- **Pivots**: Short (1-3 meetings) - transitional states

### Historical Regime Sequences

**2000-2024 Regimes:**
```
2001-2004: Accommodative (dot-com bust recovery)
2004-2006: Tightening (normalization)
2007-2008: Pivot to Easing (financial crisis building)
2008-2015: Accommodative (GFC, zero rates, QE)
2015-2018: Tightening (normalization)
2019: Pivot to Easing (growth concerns)
2020-2021: Accommodative (COVID response)
2022-2023: Tightening (inflation fight)
2024: Neutral (higher for longer)
```

---

## 🧪 Testing

### Run Full Test Suite

```bash
pytest test_policy_analyzer.py -v
```

### Run Specific Test Categories

```bash
# Sentiment tracker tests
pytest test_policy_analyzer.py::TestSentimentTracker -v

# Regime detector tests
pytest test_policy_analyzer.py::TestRegimeDetector -v

# Stance classifier tests
pytest test_policy_analyzer.py::TestStanceClassifier -v

# Tool tests
pytest test_policy_analyzer.py::TestPolicyAnalyzerTools -v

# Integration tests
pytest test_policy_analyzer.py::TestIntegration -v
```

### Run Example Demonstrations

```bash
python test_policy_analyzer.py
```

---

## 📝 Examples

### Example 1: Quick Sentiment Check

```python
from policy_analyzer_tools import analyze_sentiment_trend

meetings = [
    {'date': '2022-01-26', 'sentiment': 'neutral', 'score': 2},
    {'date': '2022-03-16', 'sentiment': 'hawkish', 'score': 12},
    {'date': '2022-05-04', 'sentiment': 'hawkish', 'score': 15}
]

result = analyze_sentiment_trend(meetings)
print(f"Current stance: {result['current_stance']['classification']}")
print(f"Trend: {result['trend']['interpretation']}")
```

### Example 2: Detect Turning Points

```python
from policy_analyzer_tools import detect_regime_changes

meetings = load_meetings('2021-01-01', '2023-12-31')
result = detect_regime_changes(meetings)

for change in result['regime_changes']:
    print(f"{change['date']}: {change['previous_regime']} → {change['new_regime']}")
```

### Example 3: Full Current Assessment

```python
from policy_analyzer_tools import get_current_policy_assessment

recent_meetings = load_recent_meetings(num=12)
economic_data = get_current_economic_data()

assessment = get_current_policy_assessment(recent_meetings, economic_data)
print(assessment['summary'])
```

---

## 🎯 Key Insights

### Sentiment Leads Actions

- Hawkish language typically precedes rate hikes by 1-2 meetings
- Dovish pivot often signals cuts coming in 3-6 months
- Watch for language shifts - they're the early warning

### Regime Changes Are Inflection Points

- Markets often react strongly to regime changes
- Fed rarely reverses once committed to new regime
- Typical sequence: Language shift → Action follows → Regime established

### Historical Comparisons Reveal Patterns

- Fed tends to repeat playbooks (gradual hikes, front-loaded cuts)
- But each cycle has unique features (GFC: QE, COVID: speed)
- Current cycle most similar to...? → Use compare_to_historical

### Policy Often Lags Conditions

- Fed "behind the curve" on both inflation and growth
- 2021: Stayed dovish too long as inflation rose
- 2023: Stayed hawkish as inflation fell
- Monitor alignment for policy mistakes

---

## 📚 Additional Resources

- **Document Processor**: Parse individual FOMC documents
- **FRED Agent**: Get actual economic outcomes
- **Treasury Agent**: Track market expectations
- **FOMC Calendar**: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

---

## 🆘 Troubleshooting

**Issue: "No regime changes detected"**
- Need minimum 6 meetings for robust detection
- Check data has 'action' and 'sentiment' fields

**Issue: "Insufficient data for trend analysis"**
- Need minimum 3 meetings
- Recommend 12+ meetings for reliable trends

**Issue: "Stance alignment unknown"**
- Economic data missing or incomplete
- Provide all required fields: inflation, unemployment, gdp_growth

---

## 📄 License

Part of the Fed Policy Intelligence Platform.

---

**Built with Google ADK** | **Integrates with Document Processor** | **Uses FRED, BLS, Treasury data**
