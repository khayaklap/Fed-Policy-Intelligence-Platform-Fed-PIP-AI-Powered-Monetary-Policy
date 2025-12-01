# Trend Tracker Agent

**Analyze long-term Fed policy trends, cycles, and predictive patterns across multiple years.**

The Trend Tracker is a core agent in the Fed Policy Intelligence Platform that analyzes Fed policy over 6-20 year horizons. It identifies:
- **Long-term trends** (structural breaks, persistence)
- **Policy cycles** (expansion → slowdown → recession)
- **Reaction functions** (how Fed responds to data)
- **Forecast biases** (systematic errors)
- **Predictive indicators** (leading signals for policy changes)

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Tools Reference](#tools-reference)
4. [Real-World Use Cases](#real-world-use-cases)
5. [Integration Patterns](#integration-patterns)
6. [Understanding Fed Cycles](#understanding-fed-cycles)
7. [Testing](#testing)
8. [Examples](#examples)

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Note: Requires policy_analyzer and document_processor
```

### Basic Usage

```python
from trend_tracker_agent import create_trend_tracker_agent
from google.adk.in_memory_runner import InMemoryRunner

# Create agent
agent = create_trend_tracker_agent()
runner = InMemoryRunner(agent=agent)

# Analyze 10-year trends
response = await runner.run_debug(
    "What are the long-term trends in Fed policy over the past 10 years?",
    context={'meeting_data': meetings_2015_2025}
)
```

---

## 🗂️ Architecture

### Component Overview

```
Trend Tracker
├── long_term_analyzer.py       # Multi-year trend analysis
├── cycle_detector.py            # Policy cycle identification
├── reaction_forecast_analysis.py  # Taylor Rule & forecast bias
├── trend_tracker_tools.py       # 5 ADK tools
└── trend_tracker_agent.py       # ADK agent orchestrator
```

### Data Flow

```
Document Processor (per meeting)
    ↓
    Extract: sentiment, score, action
    ↓
Policy Analyzer (6-24 meetings)
    ↓
    Analyze: short-term trends, regimes
    ↓
Trend Tracker (24-80 meetings)
    ↓
    Analyze: long-term patterns, cycles, predictions
```

### Time Horizons

| Agent | Time Span | Focus |
|-------|-----------|-------|
| **Document Processor** | Single meeting | Extract data |
| **Policy Analyzer** | 6-24 meetings (1.5-6 years) | Recent trends, regimes |
| **Trend Tracker** | 24-80 meetings (6-20 years) | Long-term patterns, cycles |

---

## 🛠️ Tools Reference

### Tool 1: `analyze_long_term_trends_tool`

**Analyze multi-year Fed policy trends with change point detection.**

```python
analyze_long_term_trends_tool(
    meeting_data: List[Dict],
    variable: str = 'score',
    min_meetings: int = 24
) -> Dict
```

**Input:**
```python
meetings_2005_2025 = [
    {'date': '2005-01-01', 'score': -5, 'fed_funds': 2.25},
    {'date': '2005-03-22', 'score': -3, 'fed_funds': 2.75},
    # ... 80 meetings over 20 years
]
```

**Output:**
```python
{
    'trend_analysis': {
        'direction': 'cyclical',  # hawkish_trend, dovish_trend, cyclical
        'slope': 0.12,
        'r_squared': 0.45,
        'strength': 'moderate',
        'changepoints': [
            {
                'index': 15,
                'date': '2008-09-15',
                'value_before': 8,
                'value_after': -12,
                'change': -20  # GFC - massive dovish shift
            },
            {
                'index': 60,
                'date': '2020-03-15',
                'value_before': 0,
                'value_after': -15,
                'change': -15  # COVID - emergency response
            },
            {
                'index': 67,
                'date': '2022-03-16',
                'value_before': -8,
                'value_after': 12,
                'change': 20  # Inflation fight - hawkish shift
            }
        ],
        'persistence': {
            'max_streak': 18,
            'level': 'persistent',
            'consistency': 0.45
        }
    },
    'volatility': {
        'by_window': {
            'window_6': {'mean_volatility': 4.2, 'current_volatility': 6.5},
            'window_12': {'mean_volatility': 5.8, 'current_volatility': 7.2}
        },
        'overall_trend': 'increasing',
        'interpretation': 'Current volatility is high and increasing'
    }
}
```

**Use Cases:**
- Identify structural breaks in Fed policy (2008 GFC, 2020 COVID, 2022 inflation)
- Measure long-term policy persistence
- Track volatility trends over decades

**Key Method: Change Point Detection**
- Uses PELT algorithm (Pruned Exact Linear Time)
- Detects major shifts in policy stance
- Typical change points: crisis events, regime changes

---

### Tool 2: `detect_policy_cycles_tool`

**Detect Fed policy cycles and identify current phase.**

```python
detect_policy_cycles_tool(
    meeting_data: List[Dict]
) -> Dict
```

**Policy Cycle Phases:**
1. **Recession**: Emergency cuts, very dovish
2. **Expansion (Early)**: Accommodative, supporting recovery
3. **Expansion (Mid)**: Gradual normalization, neutral shift
4. **Expansion (Late)**: Tightening, hawkish, restrictive
5. **Slowdown**: Pause, preparing for next phase

**Output:**
```python
{
    'current_phase': {
        'phase': 'expansion_late',
        'duration': 12,  # 12 meetings in tightening
        'description': 'Economy hot, inflation risk rising',
        'expected_next_phase': 'slowdown',
        'confidence': 'high'
    },
    'peaks_and_troughs': {
        'peaks': [
            {'date': '2006-06-29', 'value': 5.25, 'type': 'peak'},
            {'date': '2019-07-31', 'value': 2.50, 'type': 'peak'},
            {'date': '2023-07-26', 'value': 5.50, 'type': 'peak'}
        ],
        'troughs': [
            {'date': '2003-06-25', 'value': 1.00, 'type': 'trough'},
            {'date': '2008-12-16', 'value': 0.00, 'type': 'trough'},
            {'date': '2020-03-15', 'value': 0.00, 'type': 'trough'}
        ],
        'interpretation': 'Most recent peak at 5.50% - rates may be declining'
    },
    'cycle_metrics': {
        'peak_to_peak_duration': 48,  # meetings between peaks
        'amplitude': 5.50,  # peak-to-trough change
        'comparison_to_average': {
            'duration': 'shorter_than_average',
            'amplitude': 'larger_than_average'
        }
    },
    'historical_comparison': {
        'most_similar': 'covid_inflation',
        'description': 'COVID crisis to inflation fight',
        'similarity': 0.75
    }
}
```

**Use Cases:**
- Identify where we are in the cycle
- Predict next phase (late expansion → slowdown → recession)
- Compare to historical cycles

**Average Cycle Characteristics:**
- **Peak-to-peak**: ~18 years (72 meetings)
- **Tightening phase**: ~3 years (12 meetings)
- **Easing phase**: ~2 years (8 meetings)
- **Accommodation**: ~5 years (20 meetings)

---

### Tool 3: `analyze_reaction_function_tool`

**Analyze how Fed responds to economic data (Taylor Rule).**

```python
analyze_reaction_function_tool(
    meeting_data: List[Dict],
    economic_data: Optional[List[Dict]] = None
) -> Dict
```

**Taylor Rule:**
```
Fed Funds = R* + 1.5 × (Inflation - 2%) + 0.5 × (Output Gap)
```

Where:
- R* = neutral rate (~2.5%)
- 1.5 = inflation coefficient (Taylor's original)
- 0.5 = output coefficient (Taylor's original)

**Input:**
```python
economic_data = [
    {
        'date': '2022-01',
        'fed_funds': 0.25,
        'inflation': 7.5,
        'unemployment': 4.0
    },
    # ... 12+ observations
]
```

**Output:**
```python
{
    'taylor_rule': {
        'estimated_coefficients': {
            'inflation': 1.8,  # Fed MORE aggressive than Taylor (1.5)
            'unemployment': -0.6,
            'intercept': 2.3
        },
        'taylor_original': {
            'inflation': 1.5,
            'output': 0.5
        },
        'r_squared': 0.65,
        'interpretation': 'Fed more aggressive on inflation than Taylor'
    },
    'asymmetry': {
        'asymmetry': 'cuts_faster',
        'num_increases': 11,
        'num_decreases': 7,
        'interpretation': 'Fed cuts faster than it hikes (typical pattern)'
    }
}
```

**Key Insights:**
- **Fed vs Taylor**: Actual vs theoretical response
- **Asymmetry**: Fed typically cuts 2x faster than it hikes
- **Recent changes**: Fed's reaction function evolved after GFC

**Historical Patterns:**
- **Pre-GFC**: Close to Taylor Rule (R² > 0.7)
- **Post-GFC**: Deviates from Taylor (zero bound, QE)
- **2022-2023**: More aggressive on inflation (coef > 1.5)

---

### Tool 4: `track_forecast_bias_tool`

**Track systematic errors in Fed forecasts.**

```python
track_forecast_bias_tool(
    forecasts: List[Dict],
    actuals: List[Dict],
    variable: str = 'pce_inflation'
) -> Dict
```

**Input:**
```python
forecasts = [
    {'date': '2021-06-16', 'value': 2.1, 'horizon': '2022'},
    {'date': '2021-09-22', 'value': 2.3, 'horizon': '2022'},
    {'date': '2021-12-15', 'value': 2.6, 'horizon': '2022'},
    {'date': '2022-03-16', 'value': 4.3, 'horizon': '2022'},
    {'date': '2022-06-15', 'value': 5.2, 'horizon': '2022'}
]

actuals = [
    {'date': '2022-12-31', 'value': 6.5}  # Actual outcome
]
```

**Output:**
```python
{
    'bias_analysis': {
        'variable': 'pce_inflation',
        'num_observations': 5,
        'mean_error': -2.2,  # Forecasts 2.2pp too low on average
        'std_error': 1.5,
        'mae': 2.2,  # Mean absolute error
        'rmse': 2.6,  # Root mean squared error
        'has_systematic_bias': True,
        'bias_type': 'underestimation_bias',
        'p_value': 0.003,  # Statistically significant
        'interpretation': 'Fed systematically underestimates inflation'
    },
    'pattern': {
        'pattern': 'deteriorating',
        'trend_slope': 0.45,  # Errors getting worse
        'r_squared': 0.72,
        'recent_vs_historical': 'shift_detected',
        'recent_mean_error': -3.0,
        'historical_mean_error': -1.5,
        'interpretation': 'Forecast accuracy deteriorating over time'
    }
}
```

**Common Fed Forecast Biases:**

1. **Optimism Bias** (GDP, Unemployment)
   - Over-predicts growth: +0.5pp on average
   - Under-predicts unemployment: -0.3pp

2. **Inflation Underestimation** (during shocks)
   - Underestimates by 1-2pp during supply shocks
   - 2021-2022: Massive underestimate (-4.4pp on June 2021 forecast)

3. **Mean Reversion Bias**
   - Assumes economy returns to normal faster than it does
   - Forecasts converge to "longer run" too quickly

4. **Recency Bias**
   - Over-weights recent data
   - Slow to recognize turning points

**Use Cases:**
- Validate Fed forecasts against actuals
- Identify systematic patterns in errors
- Adjust for known biases in future forecasts

---

### Tool 5: `generate_predictive_indicators_tool`

**Generate leading signals for future Fed policy changes.**

```python
generate_predictive_indicators_tool(
    recent_meetings: List[Dict],
    current_economic_data: Optional[Dict] = None
) -> Dict
```

**Leading Indicators:**

| Indicator | Lead Time | Reliability | What to Watch |
|-----------|-----------|-------------|---------------|
| **Sentiment Shift** | 2 meetings (~6 months) | 75% | 10+ point score change |
| **Forecast Revision** | 1 meeting (~3 months) | 65% | 0.5pp revision |
| **Inflation Persistence** | 3 meetings (~9 months) | 80% | Inflation > 2.5% for 3+ quarters |
| **Unemployment Gap** | 4 meetings (~12 months) | 70% | 0.5pp below NAIRU |
| **Yield Curve Inversion** | 6 meetings (~18 months) | 85% | 2y-10y < -25bp |

**Input:**
```python
recent_meetings = last_12_meetings  # With sentiment scores

current_economic_data = {
    'inflation': 3.5,
    'unemployment': 3.7,
    'gdp_growth': 2.1
}
```

**Output:**
```python
{
    'active_indicators': [
        {
            'indicator': 'inflation_persistence',
            'status': 'triggered',
            'signal': 'Inflation at 3.5% > 2.5%',
            'lead_time': 3,
            'reliability': 0.80,
            'implication': 'Tightening likely in 3 meetings'
        },
        {
            'indicator': 'sentiment_shift',
            'status': 'triggered',
            'signal': '12-point hawkish shift',
            'lead_time': 2,
            'reliability': 0.75,
            'implication': 'Rate hike likely in 2 meetings'
        },
        {
            'indicator': 'unemployment_gap',
            'status': 'triggered',
            'signal': 'Unemployment 0.3pp below NAIRU',
            'lead_time': 4,
            'reliability': 0.70,
            'implication': 'Tightening likely in 4 meetings'
        }
    ],
    'predicted_action': 'hike',
    'confidence': 0.85,
    'time_horizon': 2,  # Shortest lead time
    'interpretation': 'High confidence rate hike expected in ~2 meetings (6 months)'
}
```

**Strong Signal Combinations:**
- **Tightening**: Sentiment shift + Inflation persistence + Unemployment gap
- **Easing**: Sentiment shift + Yield inversion + Forecast revision

**Use Cases:**
- Predict Fed's next move
- Time market positioning
- Assess policy risk

---

## 💡 Real-World Use Cases

### Use Case 1: 20-Year Fed Policy Analysis

**Question:** "What are the major structural breaks in Fed policy since 2005?"

```python
# Step 1: Collect 20 years of data
meetings_2005_2025 = []  # 80 meetings

for file in fomc_minutes_2005_2025:
    analysis = analyze_fomc_minutes_tool(file)
    meetings_2005_2025.append({
        'date': analysis['metadata']['meeting_date'],
        'score': analysis['sentiment']['score'],
        'sentiment': analysis['sentiment']['sentiment'],
        'action': analysis['policy_decision']['action']
    })

# Step 2: Analyze long-term trends
result = analyze_long_term_trends_tool(meetings_2005_2025, variable='score')

# Result: 3 major structural breaks detected
# 1. 2008-09-15: GFC (dovish shift, score: 8 → -12)
# 2. 2020-03-15: COVID (emergency response, score: 0 → -15)
# 3. 2022-03-16: Inflation fight (hawkish shift, score: -8 → 12)
```

**Interpretation:**
- **Pre-GFC (2005-2008)**: Gradual normalization after dot-com
- **GFC Era (2008-2015)**: Zero bound + QE, highly accommodative
- **Normalization (2015-2019)**: Gradual hikes, balance sheet reduction
- **COVID (2020-2021)**: Emergency support, fastest cuts ever
- **Inflation Fight (2022-2023)**: Fastest hikes since 1980s

---

### Use Case 2: Current Cycle Positioning

**Question:** "Where are we in the current policy cycle?"

```python
result = detect_policy_cycles_tool(meetings_2020_2025)

# Result:
{
    'current_phase': 'expansion_late',  # Tightening phase
    'duration': 18,  # 18 meetings (4.5 years)
    'expected_next_phase': 'slowdown',  # Pause coming
    'historical_comparison': {
        'most_similar': 'post_gfc_normalization',
        'similarity': 0.68
    }
}
```

**Analysis:**
- **Current**: Late expansion, restrictive policy
- **Similar to**: 2018 (end of 2015-2018 tightening)
- **What happened then**: Fed paused, then pivoted to cuts
- **Implication**: Pause/pivot likely in next 6-12 months

---

### Use Case 3: Taylor Rule Analysis

**Question:** "Does the Fed follow the Taylor Rule?"

```python
# Step 1: Collect economic data
economic_data = []
for date in dates_2015_2025:
    economic_data.append({
        'date': date,
        'fed_funds': get_fed_funds_rate(date),
        'inflation': get_pce_inflation(date),
        'unemployment': get_unemployment_rate(date)
    })

# Step 2: Estimate Taylor Rule
result = analyze_reaction_function_tool(meetings, economic_data)

# Result:
{
    'taylor_rule': {
        'estimated_coefficients': {
            'inflation': 1.8,  # vs Taylor's 1.5
            'unemployment': -0.6,  # vs Taylor's 0.5
            'intercept': 2.3
        },
        'r_squared': 0.58,
        'interpretation': 'Fed more aggressive on inflation than Taylor'
    },
    'asymmetry': {
        'asymmetry': 'cuts_faster',
        'interpretation': 'Fed cuts ~2x faster than it hikes'
    }
}
```

**Interpretation:**
- **Inflation sensitivity**: Fed responds MORE aggressively (1.8 vs 1.5)
- **Fit quality**: Moderate (R² = 0.58) - Fed considers more than just inflation/unemployment
- **Asymmetry**: Typical pattern - Fed cuts faster in crises
- **Conclusion**: Fed roughly follows Taylor, but deviates during crises (2008, 2020)

---

### Use Case 4: Forecast Validation

**Question:** "How accurate are Fed's inflation forecasts?"

```python
# Step 1: Collect all SEP forecasts and actual outcomes
forecast_pairs = []

for sep_file in sep_files_2015_2023:
    # Get Fed forecast
    sep_data = extract_sep_forecasts(sep_file)
    forecast = sep_data['projections']['pce_inflation']['projections']['2023']
    
    # Get actual outcome
    actual = fred_agent.get_inflation_data(year=2023)['annual']
    
    forecast_pairs.append({
        'forecast': forecast,
        'actual': actual,
        'forecast_date': sep_data['meeting_date']
    })

# Step 2: Analyze bias
result = track_forecast_bias_tool(
    forecasts=[{'value': f['forecast']} for f in forecast_pairs],
    actuals=[{'value': f['actual']} for f in forecast_pairs],
    variable='pce_inflation'
)

# Result:
{
    'bias_analysis': {
        'mean_error': -0.8,  # Underestimates by 0.8pp on average
        'has_systematic_bias': True,
        'bias_type': 'underestimation_bias',
        'p_value': 0.02  # Statistically significant
    },
    'pattern': {
        'pattern': 'stable',
        'interpretation': 'Forecast bias stable over time'
    }
}
```

**Key Findings:**
- **2015-2019**: Accurate (errors < 0.5pp)
- **2020-2021**: Large underestimate (COVID supply shocks)
- **2022-2023**: Improved but still underestimating
- **Overall**: Systematic underestimation bias (-0.8pp)

---

### Use Case 5: Predict Next Fed Move

**Question:** "What do leading indicators say about Fed's next action?"

```python
# Recent meetings with sentiment data
recent_meetings = last_12_meetings

# Current economic conditions
current_data = {
    'inflation': 2.8,  # Above target
    'unemployment': 4.1,  # Near NAIRU
    'gdp_growth': 1.9  # Below trend
}

result = generate_predictive_indicators_tool(recent_meetings, current_data)

# Result:
{
    'active_indicators': [
        {
            'indicator': 'inflation_persistence',
            'status': 'triggered',
            'signal': 'Inflation at 2.8% for 3 quarters',
            'lead_time': 3,
            'implication': 'Could trigger tightening'
        }
    ],
    'predicted_action': 'unchanged',  # Mixed signals
    'confidence': 0.55,  # Moderate
    'time_horizon': None,
    'interpretation': 'No strong signals - likely unchanged'
}
```

**Analysis:**
- **Inflation**: Slightly elevated but moderating
- **Unemployment**: Near normal levels
- **Sentiment**: No major shifts
- **Conclusion**: Fed likely to remain patient, data-dependent

---

## 🔗 Integration Patterns

### Integration 1: Complete Multi-Agent Analysis

**Comprehensive 20-year Fed analysis:**

```python
# 1. Document Processor: Parse all meetings
all_meetings = []
for file in fomc_files_2005_2025:
    analysis = analyze_fomc_minutes_tool(file)
    all_meetings.append({
        'date': analysis['metadata']['meeting_date'],
        'score': analysis['sentiment']['score'],
        'sentiment': analysis['sentiment']['sentiment'],
        'action': analysis['policy_decision']['action']
    })

# 2. Policy Analyzer: Recent trends (last 3 years)
recent_analysis = analyze_sentiment_trend(all_meetings[-24:])
regime = detect_regime_changes(all_meetings[-24:])

# 3. Trend Tracker: Long-term patterns (all 20 years)
long_term = analyze_long_term_trends_tool(all_meetings)
cycles = detect_policy_cycles_tool(all_meetings)

# 4. FRED: Economic data
inflation = fred_agent.get_inflation_data()
unemployment = fred_agent.get_unemployment_rate()
gdp = fred_agent.get_gdp_growth()

# 5. Trend Tracker: Reaction function
reaction = analyze_reaction_function_tool(
    all_meetings,
    economic_data=[
        {
            'fed_funds': m.get('fed_funds'),
            'inflation': get_inflation_for_date(m['date']),
            'unemployment': get_unemployment_for_date(m['date'])
        }
        for m in all_meetings
    ]
)

# 6. Trend Tracker: Predictive indicators
prediction = generate_predictive_indicators_tool(
    all_meetings[-12:],
    {
        'inflation': inflation['latest']['yoy'],
        'unemployment': unemployment['latest'],
        'gdp_growth': gdp['latest']['yoy']
    }
)

# RESULT: Complete picture
{
    'recent_trend': recent_analysis,  # Last 3 years
    'current_regime': regime,  # Current policy stance
    'long_term_pattern': long_term,  # 20-year view
    'cycle_position': cycles,  # Where in cycle
    'reaction_function': reaction,  # How Fed responds
    'next_move_prediction': prediction  # What's likely next
}
```

---

### Integration 2: Forecast Validation Pipeline

**Validate all Fed forecasts:**

```python
# 1. Document Processor: Extract all SEP forecasts
sep_forecasts = []
for sep_file in sep_files_2015_2023:
    sep = extract_sep_forecasts(sep_file)
    sep_forecasts.append(sep)

# 2. FRED: Get actual outcomes
actuals = {}
for year in range(2015, 2024):
    actuals[year] = {
        'inflation': fred_agent.get_inflation_data(year=year),
        'gdp': fred_agent.get_gdp_growth(year=year),
        'unemployment': fred_agent.get_unemployment_rate(year=year)
    }

# 3. Document Processor: Compare forecast vs actual
comparisons = []
for sep in sep_forecasts:
    for variable in ['pce_inflation', 'gdp', 'unemployment']:
        for year in sep['projections'][variable]['projections'].keys():
            if year.isdigit() and int(year) in actuals:
                comparison = compare_sep_with_actual(
                    sep_file=sep['file_path'],
                    variable=variable,
                    year=year,
                    actual_value=actuals[int(year)][variable.split('_')[0]]
                )
                comparisons.append(comparison)

# 4. Trend Tracker: Analyze forecast bias
for variable in ['pce_inflation', 'gdp', 'unemployment']:
    var_forecasts = [c for c in comparisons if c['variable'] == variable]
    
    bias = track_forecast_bias_tool(
        forecasts=[{'value': c['forecast']} for c in var_forecasts],
        actuals=[{'value': c['actual']} for c in var_forecasts],
        variable=variable
    )
    
    print(f"{variable}: {bias['bias_analysis']['bias_type']}, "
          f"error = {bias['bias_analysis']['mean_error']:.2f}pp")

# Result: Comprehensive forecast accuracy analysis
```

---

## 📊 Understanding Fed Cycles

### Historical Cycles (1980-2025)

**1. Volcker Disinflation (1979-1987)**
- **Context**: Breaking double-digit inflation
- **Action**: Aggressive tightening (Fed Funds → 20%)
- **Outcome**: Severe recession, inflation crushed
- **Lesson**: Fed will tolerate recession to restore price stability

**2. Greenspan Era (1987-2006)**
- **Context**: "Great Moderation" - low, stable inflation
- **Style**: Gradual, data-dependent
- **Cycles**: Multiple mini-cycles
- **Lesson**: "Measured pace" - 25bp at a time

**3. GFC Response (2007-2015)**
- **Context**: Financial crisis, Great Recession
- **Action**: Emergency cuts to zero, QE
- **Duration**: 7 years at zero bound
- **Lesson**: Fed willing to use unconventional tools

**4. Post-GFC Normalization (2015-2019)**
- **Context**: Recovery well-established
- **Action**: Gradual normalization, balance sheet reduction
- **Duration**: 9 hikes over 3 years (25bp at a time)
- **Lesson**: "Patience" - data-driven, no preset path

**5. COVID Response (2020-2021)**
- **Context**: Pandemic shock
- **Action**: Emergency cuts to zero, massive QE
- **Speed**: Fastest easing in Fed history (150bp in 2 weeks)
- **Lesson**: Fed acts decisively in crises

**6. Inflation Fight (2022-2024)**
- **Context**: Highest inflation in 40 years
- **Action**: Fastest tightening since Volcker
- **Size**: 525bp in 16 months (including 4 × 75bp)
- **Lesson**: Fed will front-load when behind curve

---

### Cycle Phase Identification

**How to identify current phase:**

```python
def identify_phase_manually(recent_data):
    """
    Simple heuristic for phase identification.
    """
    actions = [m['action'] for m in recent_data]
    sentiments = [m['sentiment'] for m in recent_data]
    
    # Count recent actions
    increases = actions.count('increase')
    decreases = actions.count('decrease')
    
    # Count sentiment
    hawkish = sum(1 for s in sentiments if 'hawkish' in s)
    dovish = sum(1 for s in sentiments if 'dovish' in s)
    
    # Determine phase
    if decreases > increases and dovish > hawkish:
        if sentiments.count('highly_dovish') >= 2:
            return "recession"
        else:
            return "slowdown"
    
    elif increases > decreases and hawkish > dovish:
        if sentiments.count('highly_hawkish') >= 2:
            return "expansion_late"
        else:
            return "expansion_mid"
    
    else:
        if dovish > hawkish:
            return "expansion_early"
        else:
            return "expansion_mid"
```

---

### Typical Cycle Sequence

```
START: Recession
    ↓ (Emergency cuts, very dovish)
Expansion (Early) - 1-2 years
    ↓ (Accommodative, supporting recovery)
Expansion (Mid) - 2-3 years
    ↓ (Gradual normalization, neutral)
Expansion (Late) - 1-2 years
    ↓ (Tightening, hawkish, restrictive)
Slowdown - 1-2 years
    ↓ (Pause, data-dependent, preparing for next move)
EITHER: Recession OR back to Expansion (Mid)
```

**Current Cycle (2020-present):**
```
2020 Mar-Jun: Recession (emergency response)
2020 Jul-2021 Nov: Expansion (Early) (sustained accommodation)
2021 Nov-2022 Mar: Slowdown (pivot preparing)
2022 Mar-2023 Jul: Expansion (Late) (aggressive tightening)
2023 Sep-present: Slowdown (pause, "higher for longer")
Next: ? (Recession or continue slowdown)
```

---

## 🧪 Testing

### Run Full Test Suite

```bash
pytest test_trend_tracker.py -v
```

### Run Specific Tests

```bash
# Long-term analyzer tests
pytest test_trend_tracker.py::TestLongTermAnalyzer -v

# Cycle detector tests
pytest test_trend_tracker.py::TestCycleDetector -v

# Reaction function tests
pytest test_trend_tracker.py::TestReactionFunctionAnalyzer -v

# Forecast bias tests
pytest test_trend_tracker.py::TestForecastBiasTracker -v

# Tool tests
pytest test_trend_tracker.py::TestTrendTrackerTools -v
```

### Run Examples

```bash
python test_trend_tracker.py
```

---

## 📝 Examples

### Example 1: Detect Structural Breaks

```python
from trend_tracker_tools import analyze_long_term_trends_tool

# 20 years of Fed policy
meetings_2005_2025 = load_all_meetings()

result = analyze_long_term_trends_tool(meetings_2005_2025, variable='score')

print("Structural Breaks Detected:")
for cp in result['trend_analysis']['changepoints']:
    print(f"{cp['date']}: {cp['change']:+.0f} point shift")

# Output:
# 2008-09-15: -20 point shift (GFC)
# 2020-03-15: -15 point shift (COVID)
# 2022-03-16: +20 point shift (Inflation fight)
```

---

### Example 2: Cycle Phase Check

```python
from trend_tracker_tools import detect_policy_cycles_tool

meetings = load_meetings('2020-01-01', '2024-12-31')

result = detect_policy_cycles_tool(meetings)

print(f"Current Phase: {result['current_phase']['phase']}")
print(f"Duration: {result['current_phase']['duration']} meetings")
print(f"Next Expected: {result['current_phase']['expected_next_phase']}")
```

---

### Example 3: Taylor Rule Estimation

```python
from trend_tracker_tools import analyze_reaction_function_tool

meetings = load_meetings_with_data('2015-01-01', '2024-12-31')
economic = load_economic_data('2015-01-01', '2024-12-31')

result = analyze_reaction_function_tool(meetings, economic)

print("Taylor Rule Coefficients:")
print(f"  Inflation: {result['taylor_rule']['estimated_coefficients']['inflation']:.2f}")
print(f"  Unemployment: {result['taylor_rule']['estimated_coefficients']['unemployment']:.2f}")
print(f"  R²: {result['taylor_rule']['r_squared']:.3f}")
```

---

### Example 4: Forecast Accuracy

```python
from trend_tracker_tools import track_forecast_bias_tool

# Get all inflation forecasts
forecasts = get_sep_inflation_forecasts('2015-01-01', '2023-12-31')
actuals = get_actual_inflation('2015-01-01', '2023-12-31')

result = track_forecast_bias_tool(forecasts, actuals, 'pce_inflation')

print(f"Bias Type: {result['bias_analysis']['bias_type']}")
print(f"Mean Error: {result['bias_analysis']['mean_error']:.2f}pp")
print(f"Significant: {result['bias_analysis']['has_systematic_bias']}")
```

---

### Example 5: Predict Next Move

```python
from trend_tracker_tools import generate_predictive_indicators_tool

recent = load_meetings('2023-01-01', '2024-12-31')
current_econ = {
    'inflation': 2.8,
    'unemployment': 4.1,
    'gdp_growth': 1.9
}

result = generate_predictive_indicators_tool(recent, current_econ)

print(f"Predicted Action: {result['predicted_action']}")
print(f"Confidence: {result['confidence']:.0%}")
print(f"Active Indicators: {len(result['active_indicators'])}")
for ind in result['active_indicators']:
    print(f"  - {ind['indicator']}: {ind['signal']}")
```

---

## 🎯 Key Insights

### 1. Structural Breaks Align with Crises
- Fed policy has distinct eras separated by major events
- GFC (2008), COVID (2020), Inflation (2022) = biggest breaks
- Normal times show gradual evolution

### 2. Cycles Are Somewhat Predictable
- Average cycle: ~18 years peak-to-peak
- Late expansion typically leads to slowdown
- Recessions trigger aggressive easing
- But each cycle has unique features

### 3. Fed Follows Taylor... Roughly
- Pre-GFC: Close adherence (R² > 0.7)
- Post-GFC: More deviations (zero bound, QE)
- Generally: More aggressive on inflation than Taylor suggests
- Asymmetry: Cuts faster than hikes

### 4. Forecast Biases Are Systematic
- **GDP**: Optimism bias (+0.5pp)
- **Inflation**: Underestimation during shocks (-1 to -2pp)
- **Unemployment**: Assumes faster normalization
- **Overall**: Fed surprised by persistence of shocks

### 5. Leading Indicators Work
- Sentiment shifts reliably lead actions (2 meetings)
- Inflation persistence predicts tightening (3 meetings)
- Yield curve predicts recession (6-12 months)
- Combining indicators improves accuracy

---

## 📚 Additional Resources

- **Document Processor**: Parse individual meetings
- **Policy Analyzer**: Analyze recent trends (1-3 years)
- **Trend Tracker**: Analyze long-term patterns (6-20 years)
- **FRED Agent**: Economic data
- **Treasury Agent**: Market expectations
- **FOMC**: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

---

## 🆘 Troubleshooting

**Issue: "Insufficient data for cycle detection"**
- Need 24+ meetings (6 years)
- Provide longer dataset

**Issue: "Change point detection failed"**
- Install ruptures: `pip install ruptures`
- Or use simple method (automatic fallback)

**Issue: "Taylor Rule estimation error"**
- Need economic data with inflation & unemployment
- Minimum 12 observations

**Issue: "No predictive indicators triggered"**
- May indicate stable, data-dependent policy
- Or insufficient recent data

---

## 📄 Stats

- **Files**: 7 core files
- **Code**: ~2,710 lines
- **Tools**: 5 ADK tools
- **Tests**: 20+ tests
- **Documentation**: ~3,000 words

---

**Built with Google ADK** | **Integrates with Policy Analyzer & Document Processor** | **Uses FRED, Treasury data**
