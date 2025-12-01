# Treasury Market Data Agent

**Market-based inflation expectations and monetary policy stance analysis**

This agent completes the "inflation triangle" by providing market-based inflation expectations (TIPS breakevens) and yield curve analysis, complementing FRED (actual data) and BLS (component breakdowns).

---

## 📊 Overview

The Treasury Agent provides:
- **Yield Curves**: Complete Treasury curve (1M to 30Y)
- **TIPS Breakevens**: Market-implied inflation expectations
- **Real Yields**: Inflation-adjusted returns (policy stance indicator)
- **Inversion Detection**: Recession signal (2s10s, 3m10y spreads)
- **Policy Stance Assessment**: Is Fed restrictive or accommodative?
- **Fed Credibility**: Compare Fed forecasts with market expectations

**Why This Matters for Fed Analysis:**
- **TIPS Breakevens** = What market expects for inflation (credibility check)
- **Real Yields** = How tight/loose policy really is (vs R-star)
- **Yield Curve** = Recession signal (inversions precede recessions)
- **Fed vs Market** = Alignment check (credibility indicator)

---

## 🔺 The Inflation Triangle

```
         ACTUAL OUTCOMES
              (FRED)
                 ▲
                 │
                 │
                 │
    COMPONENTS   │   MARKET EXPECTATIONS
       (BLS) ────┼──── (TREASURY)
                 │
                 │
          Fed Forecasts
         (FOMC Documents)
```

**Complete Picture:**
1. **FRED**: What inflation actually was
2. **BLS**: What drove it (energy? shelter? services?)
3. **Treasury**: What market expected (vs Fed forecast)

---

## 🚀 Quick Start

### 1. Prerequisites

You already have the FRED API key from the FRED agent - that's all you need!

```bash
# Same FRED API key works for Treasury data
# Treasury yields are available via FRED
```

### 2. Installation

```bash
cd external_agents/treasury_agent/

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env_treasury.template .env
# Edit .env with your FRED_API_KEY and GOOGLE_API_KEY
```

### 3. Run A2A Server

```bash
python treasury_agent.py
# Running on port 8003
```

### 4. Consume in Platform

```python
from google.adk.a2a import RemoteA2aAgent

treasury_agent = RemoteA2aAgent(
    agent_card_url="http://localhost:8003/agent_card.json"
)

# Use with FRED + BLS for complete analysis
orchestrator = LlmAgent(
    sub_agents=[
        AgentTool(fred_agent),      # Port 8001 - actual data
        AgentTool(bls_agent),       # Port 8002 - components
        AgentTool(treasury_agent),  # Port 8003 - market expectations
    ]
)
```

---

## 📚 Available Tools

### 1. `get_yield_curve_data`

Get complete Treasury yield curve.

**Parameters:**
- `date` (str, optional): Date in 'YYYY-MM-DD' (default: latest)
- `maturities` (list, optional): Specific maturities (default: all)

**Example:**
```python
result = get_yield_curve_data(date="2022-12-31")

# Returns:
# {
#     'date': '2022-12-31',
#     'yields': {
#         '3m': {'yield': 4.42, 'maturity_years': 0.25},
#         '2y': {'yield': 4.43, 'maturity_years': 2.0},
#         '10y': {'yield': 3.88, 'maturity_years': 10.0},
#         '30y': {'yield': 3.97, 'maturity_years': 30.0}
#     },
#     'curve_characteristics': {
#         '2s10s_spread': -0.55,  # 55bp inverted
#         '2s10s_inverted': True,
#         'curve_status': 'inverted',
#         'recession_signal': True
#     },
#     'interpretation': 'Yield curve is inverted (2s10s: -55bp), 
#                       signaling recession concerns...'
# }
```

**Interpretation:**
- **Normal curve** (upward sloping): Healthy growth expectations
- **Flat curve**: Uncertainty
- **Inverted curve**: Recession signal

---

### 2. `get_market_inflation_expectations`

**THE MOST IMPORTANT TOOL** - Market's inflation expectations via TIPS.

**Parameters:**
- `maturity` (str): "5y", "10y", "20y", or "30y"
- `start_date` (str, optional): Start date
- `end_date` (str, optional): End date

**Example:**
```python
result = get_market_inflation_expectations(maturity="10y")

# Returns:
# {
#     'maturity': '10y',
#     'latest': {
#         'date': '2024-11-29',
#         'nominal_yield': 4.25,      # Regular 10Y Treasury
#         'tips_yield': 1.95,         # 10Y TIPS (real yield)
#         'breakeven': 2.30           # Implied inflation (4.25 - 1.95)
#     },
#     'statistics': {
#         'mean': 2.15,
#         'max': 3.05,
#         'min': 0.52
#     },
#     'expectation_status': 'moderately_anchored',
#     'interpretation': 'Inflation expectations somewhat elevated but contained',
#     'fed_implication': 'Inflation expectations moderately elevated - 
#                        Fed monitoring closely'
# }
```

**Key Thresholds:**
- **1.75-2.25%**: Well-anchored (strong Fed credibility)
- **2.25-2.75%**: Moderately anchored (some concern)
- **> 3.0%**: De-anchoring (credibility risk)
- **> 3.5%**: Unanchored (severe credibility problem)

**Fed Watches:**
- **10Y breakeven**: Most liquid, widely watched
- **5y5y forward**: Inflation 5-10 years ahead (long-term anchoring)

---

### 3. `analyze_monetary_policy_stance`

Assess if Fed policy is tight or loose using real yields.

**Parameters:**
- `date` (str, optional): Date for analysis (default: latest)

**Example:**
```python
result = analyze_monetary_policy_stance()

# Returns:
# {
#     'date': '2024-11-29',
#     'real_yields': {
#         '10y': {'real_yield': 2.15}  # 10Y TIPS yield
#     },
#     'policy_stance': 'restrictive',
#     'policy_interpretation': 'Elevated real rates - restrictive monetary policy',
#     'neutral_rate_reference': 0.5,   # R-star
#     'spread_to_neutral': 1.65,       # 165bp above neutral
#     'analysis': 'Real yields 165bp above neutral - policy is restrictive'
# }
```

**Framework:**
- **Neutral rate (R-star)**: ~0.5% (current FOMC estimate)
- **Real yield > R-star + 1%**: Restrictive (slowing economy)
- **Real yield ≈ R-star**: Neutral
- **Real yield < R-star**: Accommodative (stimulating)

---

### 4. `detect_yield_curve_inversion`

Detect inversions - the premier recession indicator.

**Parameters:**
- `spread_type` (str): "2s10s" or "3m10y"
- `start_date` (str, optional): Start date
- `end_date` (str, optional): End date

**Example:**
```python
result = detect_yield_curve_inversion(spread_type="2s10s")

# Returns:
# {
#     'spread_type': '2s10s',
#     'latest': {
#         'date': '2024-11-29',
#         'spread': 0.35  # 35bp positive = normal
#     },
#     'inversion_analysis': {
#         'currently_inverted': False,
#         'inversion_days': 245,
#         'inversion_percentage': 33.7
#     },
#     'recession_signal': False,
#     'recession_probability': 'moderate',
#     'interpretation': 'Curve has normalized after 245 days inverted. 
#                       Recession risk remains elevated for 6-12 months...'
# }
```

**Historical Record:**
- **Every recession** since 1970 preceded by 2s10s inversion
- **Lead time**: 6-18 months from inversion to recession
- **False positives**: Very few (highly reliable)

**2022-2023 Example:**
- Inverted July 2022 (Fed started hiking March 2022)
- Stayed inverted through mid-2024
- Un-inverted September 2024 (Fed started cutting)

---

### 5. `compare_fed_forecast_vs_market`

Compare Fed's forecast with market expectations - credibility check.

**Parameters:**
- `fed_inflation_forecast` (float): Fed's SEP projection
- `forecast_date` (str): When Fed made forecast
- `forecast_horizon` (str): "5y" or "10y"

**Example:**
```python
result = compare_fed_forecast_vs_market(
    fed_inflation_forecast=2.0,
    forecast_date="2021-06-15",
    forecast_horizon="10y"
)

# Returns:
# {
#     'fed_forecast': 2.0,
#     'market_expectation': 2.38,
#     'divergence': 0.38,  # Market 38bp higher
#     'interpretation': 'Market expects higher inflation than Fed - 
#                       credibility concerns or Fed behind curve',
#     'fed_credibility': 'moderate',
#     'market_data': {
#         'nominal_yield': 1.49,
#         'tips_yield': -0.89,  # Negative real yield!
#         'breakeven': 2.38
#     }
# }
```

**Interpretation:**
- **Market > Fed**: Market skeptical of Fed's inflation control
- **Fed > Market**: Fed may be over-tightening (recession risk)
- **Convergence**: Aligned expectations (strong credibility)

---

### 6. `get_yield_curve_evolution`

Track how yield curve changed during Fed policy cycles.

**Parameters:**
- `start_date` (str): Start date
- `end_date` (str): End date
- `key_dates` (list, optional): Specific FOMC meeting dates

**Example:**
```python
result = get_yield_curve_evolution(
    start_date="2022-01-01",
    end_date="2022-12-31",
    key_dates=["2022-03-16", "2022-06-15", "2022-09-21", "2022-12-14"]
)

# Shows yield curve at each FOMC meeting
# Tracks inversion progression
```

---

## 💡 Real-World Use Cases

### Use Case 1: Complete 2022 Inflation Analysis

**Query:** "Analyze the 2022 inflation episode comprehensively"

**Multi-Agent Flow:**

```python
# 1. FRED: Actual outcomes
fred_result = await fred_agent.get_inflation_data(
    start_date="2022-01-01",
    end_date="2022-12-31",
    measure="pce_core"
)
# → Actual: 4.7% Core PCE

# 2. BLS: What drove it
bls_result = await bls_agent.get_cpi_components(
    start_year=2022,
    components=["energy", "shelter", "services"]
)
# → Energy: +32%, Shelter: +8%, Services: +6%

# 3. Treasury: What market expected
treasury_result = await treasury_agent.get_market_inflation_expectations(
    maturity="10y",
    start_date="2022-01-01",
    end_date="2022-12-31"
)
# → Market breakeven peaked at 3.0% in April 2022

# 4. Fed forecast (from documents)
# → Fed forecast (Dec 2021): 2.6% for 2022

# Combined Analysis:
# - Fed forecast: 2.6%
# - Market expectation: 3.0% (peak)
# - Actual: 4.7%
# - Components: Energy shock + persistent shelter
# - Conclusion: Both Fed and market underestimated, 
#              but market was more realistic
```

---

### Use Case 2: Policy Stance Assessment

**Query:** "Is Fed policy currently restrictive enough to bring inflation down?"

```python
# 1. Treasury: Real yields
policy_stance = await treasury_agent.analyze_monetary_policy_stance()
# → 10Y real yield: 2.15%
# → Stance: Restrictive (165bp above R-star)

# 2. Treasury: Market inflation expectations
market_inflation = await treasury_agent.get_market_inflation_expectations("10y")
# → Breakeven: 2.30%

# 3. FRED: Actual inflation
actual_inflation = await fred_agent.get_inflation_data(measure="pce_core")
# → Current: 2.8% YoY

# Analysis:
# - Real rates (2.15%) > Neutral (0.5%) = Policy is restrictive
# - Market expects 2.30% inflation (near target)
# - Actual still at 2.8% (above target but falling)
# - Conclusion: Policy restrictive enough, market expects success,
#              but need to maintain stance until inflation hits 2%
```

---

### Use Case 3: Recession Risk Assessment

**Query:** "What's the recession risk based on yield curve?"

```python
# Treasury: Inversion analysis
inversion = await treasury_agent.detect_yield_curve_inversion("2s10s")

# If inverted:
# → Recession probability: ELEVATED
# → Lead time: 6-18 months
# → Historical accuracy: Very high

# If recently un-inverted:
# → Recession risk remains for 6-12 months
# → Monitor labor market, credit conditions

# If normal:
# → Recession risk: LOW
```

---

## 🎓 Treasury Data Framework

### TIPS Breakeven Formula

```
Breakeven Inflation = Nominal Yield - TIPS Yield

Example (10Y):
Nominal 10Y:  4.25%
TIPS 10Y:     1.95%
Breakeven:    2.30% ← Market expects 2.3% avg inflation over 10 years
```

### Real Yield = Policy Stance

```
Real Yield = TIPS Yield (or Nominal - Breakeven)

10Y TIPS:     2.15%
R-star:       0.50%
Difference:   +1.65% ← Policy is 165bp restrictive

If Real > R-star:  Restrictive (slowing economy)
If Real ≈ R-star:  Neutral
If Real < R-star:  Accommodative (stimulating)
```

### Yield Curve Spreads

```
2s10s = 10Y yield - 2Y yield

Positive (e.g., +150bp): Normal, healthy growth
Flat (e.g., +25bp):      Uncertainty
Inverted (e.g., -55bp):  Recession signal
```

---

## 📊 Key Relationships

### The Fed's Credibility Triangle

```
Fed Forecast
     │
     ├── Compare → Market Expectation (TIPS)
     │                     │
     └─────────────────────┴── Gap = Credibility Issue

Small gap  (<25bp): Strong credibility
Medium gap (25-50bp): Some concern
Large gap  (>50bp): Serious credibility problem
```

### Policy Transmission

```
Fed hikes rates
     ↓
Short-term yields rise
     ↓
If long-term yields don't rise as much → Curve flattens/inverts
     ↓
Inversion → Recession signal
     ↓
Real yields rise → Restrictive policy
     ↓
TIPS breakevens fall → Inflation expectations anchored
     ↓
Success: Inflation falls without recession (soft landing)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest test_treasury_agent.py -v

# Test specific tools
pytest test_treasury_agent.py::test_get_yield_curve_tool -v
pytest test_treasury_agent.py::test_get_tips_breakeven_tool -v

# Interactive demo
python test_treasury_agent.py
```

---

## 🤝 Integration with Fed-PIP

### The Complete Inflation Analysis Stack

```python
# All three agents running
fred_agent = RemoteA2aAgent("http://localhost:8001/agent_card.json")
bls_agent = RemoteA2aAgent("http://localhost:8002/agent_card.json")
treasury_agent = RemoteA2aAgent("http://localhost:8003/agent_card.json")

# Orchestrator combines all
inflation_analyst = LlmAgent(
    name="complete_inflation_analyst",
    sub_agents=[
        AgentTool(fred_agent),
        AgentTool(bls_agent),
        AgentTool(treasury_agent)
    ]
)

# Example query using all three
response = await runner.run_debug("""
    Analyze 2022 inflation comprehensively:
    1. What was actual inflation? (FRED)
    2. What components drove it? (BLS)
    3. What did markets expect? (Treasury)
    4. How did Fed's forecast compare?
""")
```

---

## 📖 Data Sources & Quality

**Source:** U.S. Department of Treasury via FRED St. Louis Fed

| Series | Frequency | Lag | Updates |
|--------|-----------|-----|---------|
| Treasury Yields | Daily | ~6pm ET | Business days |
| TIPS | Daily | ~6pm ET | Business days |
| Breakevens | Daily | Calculated | Business days |

**Notes:**
- No data on weekends/federal holidays
- TIPS yields can be negative (low inflation + high demand periods)
- Real-time data during market hours
- Historical data back to 1962 (nominal), 1997 (TIPS)

---

## ✅ Treasury Agent Summary

**Purpose:** Market-based inflation expectations and policy stance

**Key Strength:** Shows what MARKET thinks (vs what Fed thinks or actual data)

**Completes Triangle:**
- FRED: What happened
- BLS: Why it happened
- Treasury: What market expected/expects

**Critical Tools:**
1. **TIPS Breakevens**: Market inflation expectations (credibility check)
2. **Real Yields**: Policy stance (restrictive/accommodative)
3. **Yield Curve**: Recession indicator (inversions)

**Production Ready:** ✅ A2A server, caching, comprehensive tests

---

## 🎉 You Now Have the Complete Inflation Framework!

**3 Agents, Complete Picture:**

| Agent | Port | Provides | Key Insight |
|-------|------|----------|-------------|
| FRED | 8001 | Actual outcomes | "Inflation was 6.5%" |
| BLS | 8002 | Component drivers | "Because energy +32%, shelter +8%" |
| Treasury | 8003 | Market expectations | "Market expected 3.0%, Fed said 2.0%" |

**Next:** Build Fed-PIP core agents to analyze your FOMC documents! 🚀
