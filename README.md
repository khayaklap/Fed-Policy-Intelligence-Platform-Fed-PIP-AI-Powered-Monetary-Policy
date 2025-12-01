# BLS Inflation Analysis Agent

**Detailed inflation component analysis via Bureau of Labor Statistics data**

This agent complements the FRED agent by providing granular inflation breakdowns, leading indicators, and wage pressure analysis critical for understanding Fed monetary policy.

---

## 📊 Overview

The BLS Agent provides:
- **CPI Component Breakdown**: Food, energy, shelter, transportation, medical, services, goods
- **Producer Price Index (PPI)**: Leading indicator for CPI (3-6 month lead time)
- **Employment Cost Index (ECI)**: Fed's preferred wage pressure measure
- **Goods vs Services**: Critical for understanding inflation persistence
- **Import/Export Prices**: Global inflation transmission
- **Productivity & Unit Labor Costs**: Wage-price spiral indicators

**Why This Matters for Fed Analysis:**
- **Shelter** = 32% of CPI, most persistent component, Fed watches closely
- **Core Services** = Wage-driven, sticky inflation signal
- **PPI** = Early warning system for CPI movements
- **ECI** = Wage-price spiral detector

**Usage Modes:**
- **🌐 A2A Server Mode**: Run as standalone server (production)
- **📦 Package Mode**: Import directly into your application (development)
- **🧪 Direct Execution**: Run scripts directly for testing

---

## 🚀 Quick Start

### 1. Get BLS API Key (Optional but Recommended)

```bash
# Visit: https://data.bls.gov/registrationEngine/
# Fill out the registration form
# Receive API key via email

# Benefits of API key:
# - Without key: 25 queries/day, 10 years per query
# - With key: 500 queries/day, 20 years per query
```

### 2. Installation

```bash
cd external_agents/bls_agent/

# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "BLS_API_KEY=your_key_here" >> .env  # Optional
echo "GOOGLE_API_KEY=your_google_key" >> .env
echo "BLS_AGENT_HOST=0.0.0.0" >> .env
echo "BLS_AGENT_PORT=8002" >> .env
```

### 3. Run A2A Server

```bash
python bls_agent.py
```

### 4. Consume in Your Platform

```python
from google.adk.a2a import RemoteA2aAgent

bls_agent = RemoteA2aAgent(
    agent_card_url="http://localhost:8002/agent_card.json"
)

# Use in orchestrator alongside FRED agent
orchestrator = LlmAgent(
    sub_agents=[
        AgentTool(fred_agent),  # Port 8001
        AgentTool(bls_agent),   # Port 8002
        # ...
    ]
)
```

---

## 📦 Package Usage

### Direct Import (Package Mode)

```python
# Import the BLS package
from external_agents.bls import (
    create_bls_agent,
    get_cpi_components,
    get_ppi_data,
    BLS_SERIES_MAP
)

# Use tools directly
result = get_cpi_components(start_year=2022, components=["food", "energy"])

# Create agent programmatically
agent = create_bls_agent()
```

### Module Import (Individual Components)

```python
# Import specific modules
from external_agents.bls.bls_tools import get_cpi_components, analyze_inflation_drivers
from external_agents.bls.bls_agent import create_bls_agent
from external_agents.bls.bls_config import BLS_SERIES_MAP, CPI_COMPONENTS

# Use components as needed
cpi_data = get_cpi_components(start_year=2020)
analysis = analyze_inflation_drivers()
```

---

## 📚 Available Tools

### 1. `get_cpi_components`

Get detailed CPI component breakdown - identifies inflation drivers.

**Parameters:**
- `start_year` (int): Start year (default: 2020)
- `end_year` (int, optional): End year
- `components` (list, optional): ["food", "energy", "housing", "transportation", "services", "goods"]

**Example:**
```python
result = get_cpi_components(
    start_year=2022,
    end_year=2023,
    components=["food", "energy", "housing"]
)

# Returns:
# {
#     'period': '2022-2023',
#     'components': {
#         'food': {
#             'cpi_food': {
#                 'latest': {'date': '2023-12', 'yoy': 2.7},
#                 'peak': {'date': '2022-08', 'yoy': 11.4}
#             }
#         },
#         'energy': {
#             'cpi_energy': {
#                 'latest': {'date': '2023-12', 'yoy': -2.0},
#                 'peak': {'date': '2022-06', 'yoy': 41.6}
#             }
#         },
#         'housing': {
#             'cpi_shelter': {
#                 'latest': {'date': '2023-12', 'yoy': 6.2},
#                 'peak': {'date': '2023-03', 'yoy': 8.2}
#             }
#         }
#     },
#     'summary': 'Energy peaked in mid-2022, now negative. Shelter remains elevated at 6.2% YoY.'
# }
```

**Use Cases:**
- "What drove 2022 inflation surge?" → Shows energy +41% was primary driver
- "Is inflation broadening or narrowing?" → Compare # of components above 3%
- "What's the stickiest inflation component?" → Shelter has highest persistence

---

### 2. `get_ppi_data`

Producer Price Index - leading indicator for CPI.

**Parameters:**
- `start_year` (int): Start year
- `end_year` (int, optional): End year
- `stage` (str): "final_demand", "intermediate", "crude"

**Example:**
```python
result = get_ppi_data(
    start_year=2021,
    end_year=2023,
    stage="final_demand"
)

# Returns:
# {
#     'stage': 'final_demand',
#     'latest': {'date': '2023-12', 'yoy': 1.0},
#     'peak': {'date': '2022-06', 'yoy': 11.3},
#     'recent_trend': 'falling',
#     'interpretation': 'PPI final demand at 1.0% YoY and falling. 
#                       Peaked at 11.3% in 2022-06. This suggests 
#                       disinflationary pressures ahead for CPI.'
# }
```

**Why PPI Matters:**
- Measures wholesale prices before they reach consumers
- Typically leads CPI by 3-6 months
- Rising PPI → future CPI pressure
- Falling PPI → disinflation ahead

---

### 3. `get_employment_cost_index`

Employment Cost Index - comprehensive labor cost measure.

**Parameters:**
- `start_year` (int): Start year
- `end_year` (int, optional): End year
- `component` (str): "total_comp", "wages_salaries", "benefits"

**Example:**
```python
result = get_employment_cost_index(
    start_year=2020,
    component="total_comp"
)

# Returns:
# {
#     'component': 'total_comp',
#     'frequency': 'Quarterly',
#     'latest': {'date': '2024-Q3', 'yoy': 3.9},
#     'peak': {'date': '2022-Q4', 'yoy': 5.1},
#     'wage_pressure': 'elevated',
#     'trend': 'moderating',
#     'interpretation': 'ECI total_comp at 3.9% YoY indicates elevated wage pressure.
#                       Trend is moderating from peak of 5.1% in 2022-Q4.
#                       Wage pressures moderating.'
# }
```

**Why ECI Matters:**
- Fed's preferred wage measure (more comprehensive than average hourly earnings)
- Includes benefits, not just wages
- Quarterly data, less volatile
- Rising ECI + low productivity = wage-price spiral risk

**Thresholds:**
- < 2.5%: Low wage pressure
- 2.5-3.5%: Moderate (consistent with 2% inflation)
- 3.5-4.5%: Elevated
- > 4.5%: High (wage-price spiral risk)

---

### 4. `compare_inflation_measures`

Compare CPI, Core CPI, PPI, and import prices side-by-side.

**Parameters:**
- `start_year` (int): Start year
- `end_year` (int, optional): End year

**Example:**
```python
result = compare_inflation_measures(start_year=2021)

# Returns:
# {
#     'period': '2021-2024',
#     'comparison': {
#         'cpi_all': {'latest_yoy': 3.2, 'peak_yoy': 9.1, 'peak_date': '2022-06'},
#         'cpi_core': {'latest_yoy': 4.0, 'peak_yoy': 6.6, 'peak_date': '2022-09'},
#         'ppi': {'latest_yoy': 1.8, 'peak_yoy': 11.3, 'peak_date': '2022-06'},
#         'import_prices': {'latest_yoy': 0.5, 'peak_yoy': 12.1, 'peak_date': '2022-03'}
#     },
#     'insights': [
#         'Core CPI exceeds headline - services/shelter driving inflation',
#         'PPI peaked before CPI - producer costs led consumer prices'
#     ]
# }
```

**Key Insights:**
- Core > Headline → Persistent, broad-based inflation (bad for Fed)
- Headline > Core → Energy/food volatility (transitory)
- PPI peaking before CPI → Leading indicator working
- Import prices rising → Global inflation transmission

---

### 5. `analyze_inflation_drivers`

**THE KILLER APP** - Comprehensive "what's driving inflation" analysis.

**Parameters:**
- `as_of_date` (str, optional): Date for analysis (default: latest)

**Example:**
```python
result = analyze_inflation_drivers(as_of_date="2022-12-01")

# Returns:
# {
#     'analysis_date': '2022-12-01',
#     'headline_inflation': 7.1,
#     'core_inflation': 6.0,
#     'spread': 1.1,
#     'primary_drivers': [
#         {'component': 'Shelter', 'yoy': 7.1, 'category': 'housing'},
#         {'component': 'Food at Home', 'yoy': 10.2, 'category': 'food'},
#         {'component': 'Energy', 'yoy': 13.1, 'category': 'energy'},
#         {'component': 'Medical Care', 'yoy': 4.1, 'category': 'medical'},
#         {'component': 'Transportation', 'yoy': 14.3, 'category': 'transportation'}
#     ],
#     'assessment': 'High inflation above Fed target',
#     'component_summary': 'Broad-based inflation with shelter, food, and energy all elevated'
# }
```

**This Tool Answers:**
- "What's driving inflation RIGHT NOW?"
- "Is inflation broad-based or concentrated?"
- "What should the Fed focus on?"
- "Is this transitory or persistent?"

---

## 💡 Real-World Use Cases

### Use Case 1: Fed Forecast Validation

**Query:** "The Fed projected 2.4% PCE inflation for 2022. Was their forecast accurate based on CPI components?"

**Flow:**
1. BLS agent: Get 2022 CPI component breakdown
2. Analysis: Energy +32% (peak), Shelter +8%, Services +6%
3. Conclusion: "Fed underestimated. Energy shock + persistent services inflation"

### Use Case 2: Inflation Transition Analysis

**Query:** "Analyze the transition from 2022 goods-driven to 2023 services-driven inflation"

**Flow:**
1. `get_cpi_components(2022, 2023, ["goods", "services"])`
2. 2022: Goods inflation peaked at +15% (supply chains)
3. 2023: Goods moderating, Services elevated at +6% (wages)
4. Insight: "Inflation shifted from transitory (goods) to persistent (services)"

### Use Case 3: Wage-Price Spiral Detection

**Query:** "Is there wage-price spiral risk?"

**Flow:**
1. `get_employment_cost_index()` → ECI at 4.5% YoY
2. Get productivity growth (separate tool) → 1.0% YoY
3. Unit labor costs = ECI - Productivity = 3.5%
4. Compare to inflation: 3.5% < 6% → "Wage increases lagging, but catching up"
5. Assessment: "Moderate wage-price spiral risk - watch closely"

### Use Case 4: Leading Indicator Signal

**Query:** "What do leading indicators suggest for future inflation?"

**Flow:**
1. `get_ppi_data()` → PPI falling to 1.8% YoY, trend: falling
2. Import prices → Also moderating
3. Signal: "Leading indicators point to continued disinflation"
4. Fed implication: "Can maintain restrictive policy without further hikes"

---

## 🎓 Inflation Analysis Framework

### CPI Component Taxonomy

```
CPI (100%)
├── Food & Beverages (13.4%)
│   ├── Food at Home (volatile, supply-sensitive)
│   └── Food Away from Home (sticky, wage-driven)
│
├── Housing (32.9%) ← LARGEST COMPONENT
│   ├── Shelter (sticky, 12-18 month lag)
│   │   ├── Rent of Primary Residence
│   │   └── Owners' Equivalent Rent
│   └── Utilities (energy-sensitive)
│
├── Transportation (16.8%)
│   ├── New Vehicles (supply chain)
│   ├── Used Vehicles (very volatile)
│   └── Gasoline (extremely volatile)
│
├── Medical Care (8.5%)
│
├── Recreation (5.6%)
│
├── Education (3.0%)
│
└── Other (20.0%)
```

### Persistence Classification

**Transitory (typically <6 months):**
- Energy (gasoline, natural gas)
- Food (weather, seasonal)
- Used cars (demand surges)

**Sticky (6-18+ months):**
- Shelter (rental contracts, slow adjustment)
- Medical care (insurance, regulations)
- Education (annual adjustments)

**Most Persistent:**
- **Core Services** excluding shelter
  - Wage-driven
  - Hardest to reverse
  - Fed's biggest concern

---

## 🔍 Data Quality & Interpretation

### BLS Data Characteristics

| Series | Frequency | Lag | Revisions | Volatility |
|--------|-----------|-----|-----------|------------|
| CPI | Monthly | ~14 days | Rare | Low-Medium |
| PPI | Monthly | ~14 days | Minor | Medium |
| ECI | Quarterly | ~30 days | Rare | Low |
| Import Prices | Monthly | ~14 days | Minor | High |

### Seasonal Adjustment

All BLS series are seasonally adjusted (SA):
- "CUUR0000SA0" ← "SA" indicates seasonal adjustment
- Removes predictable seasonal patterns
- Use SA data for trend analysis

### Historical Context

**Normal Inflation (pre-2020):**
- CPI All: 1.5-2.5% YoY
- Core CPI: 1.8-2.3% YoY
- Shelter: 2.5-3.5% YoY
- Energy: -10% to +10% YoY (highly volatile)

**2021-2022 Inflation Surge:**
- Peak CPI: 9.1% (June 2022) - highest since 1981
- Peak Core: 6.6% (Sept 2022)
- Drivers: Energy (+41%), Food (+11%), Shelter (+8%)

---

## 🧪 Testing

### Run Tests

```bash
# From the bls directory
cd external_agents/bls

# Run all tests
pytest test_bls_agent.py -v

# Test specific tools
pytest test_bls_agent.py::test_get_cpi_components_tool -v
pytest test_bls_agent.py::test_analyze_inflation_drivers_tool -v

# Interactive demo
python test_bls_agent.py
```

### From Project Root

```bash
# Run tests from project root
python -m pytest external_agents/bls/test_bls_agent.py -v

# Import and test tools directly
python -c "from external_agents.bls import get_cpi_components; print(get_cpi_components(2023))"
```

---

## 🤝 Integration with Fed-PIP

### Combined FRED + BLS Analysis

**Option 1: A2A Remote Agents (Recommended for Production)**
```python
from google.adk.a2a import RemoteA2aAgent
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

# Connect to remote agents
fred_agent = RemoteA2aAgent(agent_card_url="http://localhost:8001/agent_card.json")
bls_agent = RemoteA2aAgent(agent_card_url="http://localhost:8002/agent_card.json")

orchestrator = LlmAgent(
    name="inflation_analyst",
    sub_agents=[
        AgentTool(fred_agent),   # PCE, actual outcomes
        AgentTool(bls_agent),    # CPI components, drivers
    ]
)
```

**Option 2: Direct Package Import (Development/Testing)**
```python
from external_agents.bls import create_bls_agent, get_cpi_components, analyze_inflation_drivers
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

# Create agent directly
bls_agent = create_bls_agent()

# Or use tools directly in your orchestrator
orchestrator = LlmAgent(
    name="inflation_analyst",
    tools=[
        FunctionTool(get_cpi_components),
        FunctionTool(analyze_inflation_drivers),
        # ... other tools
    ]
)
```

**Example Multi-Agent Query:**
```
"Compare the Fed's 2022 inflation forecast with actual outcomes. 
What components drove the forecast error?"

Flow:
1. FRED: Get actual 2022 PCE inflation → 6.5%
2. Document Processor: Get Fed's 2021 SEP forecast → 2.1%
3. BLS: Get 2022 CPI component breakdown → Energy +32%, Shelter +8%
4. Analysis: "Fed underestimated by 4.4pp. Primary miss was energy shock 
   (Russia-Ukraine) and persistent shelter inflation."
```

---

## 📖 BLS Resources

- **API Documentation**: https://www.bls.gov/developers/api_signature_v2.htm
- **Series Finder**: https://data.bls.gov/cgi-bin/surveymost
- **CPI Methodology**: https://www.bls.gov/opub/hom/cpi/
- **Economic Calendar**: https://www.bls.gov/schedule/

---

## ✅ BLS Agent Summary

**Purpose**: Detailed inflation component analysis

**Key Strength**: Identifies WHAT is driving inflation (energy? shelter? services?)

**Complements FRED**: FRED has overall PCE/CPI, BLS has granular breakdowns

**Critical for Fed Analysis**:
- Shelter = largest component, Fed watches closely
- Core Services = most persistent, hardest to fix
- PPI = early warning system
- ECI = wage-price spiral detector

**Production Ready**: ✅ A2A server, caching, comprehensive tests

---

**Next:** Build Treasury Agent for yield curves and market-based inflation expectations! 🚀
