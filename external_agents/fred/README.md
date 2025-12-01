# FRED Economic Data Agent

**A production-ready A2A agent providing access to Federal Reserve Economic Data (FRED)**

This agent is part of the Fed Policy Intelligence Platform and provides real-time US economic data for comparing with FOMC forecasts and analyzing monetary policy effectiveness.

---

## 📊 Overview

The FRED Agent provides:
- **GDP & Growth Data**: Real GDP, nominal GDP, growth rates
- **Inflation Metrics**: PCE, Core PCE (Fed's preferred measure), CPI, Core CPI
- **Employment Data**: Unemployment rate, nonfarm payrolls, labor force participation
- **Interest Rates**: Federal Funds rate, Treasury yields, yield curve analysis
- **Monetary Aggregates**: M2 money supply, bank reserves
- **Housing Indicators**: Home sales, housing starts, Case-Shiller index
- **Consumer Sentiment**: University of Michigan, Conference Board indices

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.11+
python --version

# Get FRED API key (free)
# Visit: https://fred.stlouisfed.org/docs/api/api_key.html
```

### 2. Installation

```bash
# Clone or copy the FRED agent files
cd external_agents/fred_agent/

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "FRED_API_KEY=your_api_key_here" > .env
echo "FRED_AGENT_HOST=0.0.0.0" >> .env
echo "FRED_AGENT_PORT=8001" >> .env
```

### 3. Run as A2A Server

```bash
# Start the FRED agent A2A server
python fred_agent.py
```

Output:
```
============================================================
FRED Economic Data Agent - A2A Server
============================================================

This agent provides access to US economic data from FRED
for integration with the Fed Policy Intelligence Platform

Server will start on: 0.0.0.0:8001
Agent card: http://0.0.0.0:8001/agent_card.json

Press Ctrl+C to stop the server
============================================================
```

### 4. Consume from Your Platform

```python
from google.adk.a2a import RemoteA2aAgent
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

# Connect to FRED agent
fred_agent = RemoteA2aAgent(
    agent_card_url="http://localhost:8001/agent_card.json"
)

# Use in your orchestrator
orchestrator = LlmAgent(
    name="fed_policy_analyst",
    sub_agents=[
        AgentTool(fred_agent),  # Remote FRED agent
        # ... your other agents
    ]
)
```

---

## 📚 Available Tools

### 1. `get_gdp_data`

Get GDP data with optional transformations.

**Parameters:**
- `start_date` (str): Start date in 'YYYY-MM-DD' format
- `end_date` (str, optional): End date (default: latest)
- `metric` (str): "real", "nominal", or "growth"

**Example:**
```python
from fred_tools import get_gdp_data

result = get_gdp_data(
    start_date="2020-01-01",
    end_date="2023-12-31",
    metric="growth"
)

# Returns:
# {
#     'metric': 'growth',
#     'series_id': 'A191RL1Q225SBEA',
#     'name': 'Real GDP Growth Rate',
#     'units': 'Percent Change from Preceding Period',
#     'dates': ['2020-01-01', '2020-04-01', ...],
#     'values': [2.3, -31.2, 33.8, ...],
#     'statistics': {...}
# }
```

### 2. `get_inflation_data`

Get inflation measures (Fed's preferred: Core PCE).

**Parameters:**
- `start_date` (str): Start date
- `end_date` (str, optional): End date
- `measure` (str): "pce", "pce_core", "cpi", "cpi_core"
- `yoy` (bool): Return year-over-year % change (default: True)

**Example:**
```python
from fred_tools import get_inflation_data

result = get_inflation_data(
    start_date="2021-01-01",
    end_date="2023-12-31",
    measure="pce_core",
    yoy=True
)

# Returns YoY % change in Core PCE inflation
```

### 3. `get_employment_data`

Get comprehensive employment metrics.

**Parameters:**
- `start_date` (str): Start date
- `end_date` (str, optional): End date
- `indicators` (list, optional): Specific indicators or all employment data

**Example:**
```python
from fred_tools import get_employment_data

result = get_employment_data(
    start_date="2020-01-01",
    indicators=["unemployment", "nonfarm_payrolls"]
)

# Returns unemployment rate and NFP data
```

### 4. `get_interest_rates`

Get interest rates and yield curve data.

**Parameters:**
- `start_date` (str): Start date
- `end_date` (str, optional): End date
- `rates` (list, optional): Specific rates to fetch

**Example:**
```python
from fred_tools import get_interest_rates

result = get_interest_rates(
    start_date="2022-01-01",
    rates=["fed_funds", "treasury_10y", "treasury_2y"]
)

# Returns rates and calculates yield curve spread
# Includes inversion detection: result['yield_curve']['inverted']
```

### 5. `get_economic_snapshot`

Get comprehensive snapshot of all major indicators at a point in time.

**Parameters:**
- `as_of_date` (str, optional): Date for snapshot (default: latest)

**Example:**
```python
from fred_tools import get_economic_snapshot

result = get_economic_snapshot(as_of_date="2008-09-15")

# Returns snapshot of:
# - Inflation (PCE Core, CPI)
# - Growth (GDP)
# - Employment (unemployment, NFP)
# - Interest rates (Fed Funds, 10Y)
```

### 6. `compare_to_fed_projection`

Compare Fed SEP projection with actual FRED data.

**Parameters:**
- `indicator` (str): "inflation", "gdp_growth", or "unemployment"
- `projection_value` (float): Fed's projected value
- `projection_date` (str): When Fed made projection
- `actual_date` (str): Date to check actual outcome

**Example:**
```python
from fred_tools import compare_to_fed_projection

result = compare_to_fed_projection(
    indicator="inflation",
    projection_value=2.0,
    projection_date="2021-06-01",
    actual_date="2021-12-31"
)

# Returns:
# {
#     'fed_projection': 2.0,
#     'actual_outcome': 5.8,
#     'forecast_error': -3.8,
#     'error_percentage': -190.0,
#     'interpretation': 'Fed significantly underestimated inflation'
# }
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# Required: FRED API Key
FRED_API_KEY=your_fred_api_key_here

# Optional: A2A Server Configuration
FRED_AGENT_HOST=0.0.0.0
FRED_AGENT_PORT=8001

# Optional: Logging
LOG_LEVEL=INFO
```

### FRED Series Mapping

The agent uses official FRED series IDs defined in `config.py`:

```python
FRED_SERIES_MAP = {
    "pce_core": "PCEPILFE",      # Fed's preferred inflation measure
    "gdp_real": "GDPC1",          # Real GDP
    "unemployment": "UNRATE",     # Unemployment Rate
    "fed_funds": "FEDFUNDS",      # Federal Funds Rate
    # ... many more
}
```

---

## 💡 Usage Examples

### Example 1: Direct Tool Usage

```python
from fred_tools import get_inflation_data, get_employment_data

# Get 2022 inflation data
inflation = get_inflation_data(
    start_date="2022-01-01",
    end_date="2022-12-31",
    measure="pce_core"
)

print(f"2022 Core PCE: {inflation['statistics']['mean']:.2f}% average")
print(f"Peak: {inflation['statistics']['max']:.2f}%")

# Get employment snapshot
employment = get_employment_data(
    start_date="2022-12-01",
    end_date="2022-12-31"
)

print(f"Unemployment: {employment['indicators']['unemployment']['statistics']['latest']['value']}%")
```

### Example 2: Agent Query (Local)

```python
from fred_agent import create_fred_agent
from google.adk.runners import InMemoryRunner

# Create agent and runner
agent = create_fred_agent()
runner = InMemoryRunner(agent=agent)

# Query the agent
response = await runner.run_debug(
    "What was Core PCE inflation in December 2022?"
)
print(response)
```

### Example 3: A2A Integration

```python
from google.adk.a2a import RemoteA2aAgent
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from google.adk.runners import InMemoryRunner

# Connect to remote FRED agent
fred_remote = RemoteA2aAgent(
    agent_card_url="http://localhost:8001/agent_card.json"
)

# Create orchestrator that uses FRED agent
orchestrator = LlmAgent(
    name="policy_analyst",
    sub_agents=[AgentTool(fred_remote)],
    instruction="Use FRED data to answer economic questions"
)

# Query
runner = InMemoryRunner(agent=orchestrator)
response = await runner.run_debug(
    "Compare 2022 inflation with 2008 crisis period"
)
```

### Example 4: Fed Forecast Validation

```python
from fred_agent import create_fred_agent
from google.adk.runners import InMemoryRunner

agent = create_fred_agent()
runner = InMemoryRunner(agent=agent)

# Analyze forecast accuracy
response = await runner.run_debug("""
The Fed's June 2021 SEP projected:
- 2021 PCE inflation: 2.1%
- 2022 PCE inflation: 2.1%
- 2023 PCE inflation: 2.1%

What were the actual inflation outcomes for each year?
Calculate the forecast errors.
""")

print(response)
# Shows Fed significantly underestimated 2021-2022 inflation
```

---

## 🧪 Testing

### Run All Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest test_fred_agent.py -v
```

### Run Specific Tests

```bash
# Test tool functions directly
pytest test_fred_agent.py::test_get_inflation_data_tool -v

# Test agent queries
pytest test_fred_agent.py::test_fred_agent_inflation_query -v

# Test forecast comparison
pytest test_fred_agent.py::test_compare_to_fed_projection_tool -v
```

### Interactive Demo

```bash
# Run interactive demo
python test_fred_agent.py
```

---

## 📊 Data Quality & Sources

### Official Data Sources

All data comes from the Federal Reserve Economic Data (FRED) database:
- **Maintained by**: Federal Reserve Bank of St. Louis
- **Update Frequency**: Varies by series (daily, monthly, quarterly)
- **Data Providers**: Bureau of Economic Analysis (BEA), Bureau of Labor Statistics (BLS), Federal Reserve, Treasury, etc.

### Data Reliability

- ✅ **GDP Data**: Official BEA data, subject to revisions
- ✅ **Inflation**: Official CPI (BLS) and PCE (BEA) data
- ✅ **Employment**: Official BLS establishment and household surveys
- ✅ **Interest Rates**: Official Fed and Treasury rates

### Historical Revisions

Note: Economic data (especially GDP) is subject to revisions:
- **Advance**: First estimate (~1 month after quarter end)
- **Preliminary**: Revised estimate (~2 months after)
- **Final**: Third estimate (~3 months after)
- **Annual Revisions**: July of each year

The FRED agent returns the latest available (revised) data.

---

## 🔐 Security & Rate Limits

### API Key Security

- **Never commit** your FRED API key to version control
- Use `.env` file (already in `.gitignore`)
- In production, use secure secret management (e.g., Google Secret Manager)

### Rate Limits

- **FRED API**: 120 requests per minute (registered users)
- The agent implements caching (1-hour TTL) to reduce API calls
- Cached responses are served instantly

### Caching Strategy

```python
# Automatic caching in fred_api_wrapper.py
cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour cache

# Same query within 1 hour = instant response from cache
# Different queries = new API call
```

---

## 🐛 Troubleshooting

### Issue: API Key Error

```
ValueError: FRED API key is required
```

**Solution**: 
1. Get API key from https://fred.stlouisfed.org/docs/api/api_key.html
2. Add to `.env` file: `FRED_API_KEY=your_key_here`

### Issue: Series Not Found

```
Error fetching GDPC1: Series does not exist
```

**Solution**: Check the series ID in `config.py` or FRED website

### Issue: A2A Server Won't Start

```
Address already in use
```

**Solution**: Change port in `.env` or kill process on port 8001:
```bash
lsof -ti:8001 | xargs kill -9
```

### Issue: No Data Returned

```
No data available for indicator on date
```

**Solution**: 
- Check date format: 'YYYY-MM-DD'
- Verify data exists for that date (weekends/holidays may have no data for daily series)
- Some series start later than 2005

---

## 📖 Additional Resources

### FRED API Documentation
- **API Docs**: https://fred.stlouisfed.org/docs/api/fred/
- **Series Search**: https://fred.stlouisfed.org/
- **Python fredapi**: https://github.com/mortada/fredapi

### Economic Data Background
- **PCE vs CPI**: Why the Fed prefers Core PCE inflation
- **GDP Revisions**: Understanding BEA's revision process
- **Employment Data**: Establishment vs Household surveys

### ADK Documentation
- **A2A Protocol**: https://google.github.io/adk-docs/a2a/
- **Tools Guide**: https://google.github.io/adk-docs/tools/

---

## 🤝 Integration with Fed-PIP

This FRED agent is designed to integrate seamlessly with the Fed Policy Intelligence Platform:

```python
# In your Fed-PIP orchestrator.py
from google.adk.a2a import RemoteA2aAgent

fred_agent = RemoteA2aAgent(
    agent_card_url="http://localhost:8001/agent_card.json"
)

orchestrator = LlmAgent(
    name="fed_pip_orchestrator",
    sub_agents=[
        AgentTool(document_processor),     # Local
        AgentTool(policy_analyzer),        # Local  
        AgentTool(fred_agent),             # External via A2A
        AgentTool(bls_agent),              # External via A2A
        AgentTool(treasury_agent),         # External via A2A
    ]
)
```

**Use Cases in Fed-PIP:**
1. **Forecast Validation**: Compare SEP projections with actual FRED data
2. **Economic Context**: Understand conditions during FOMC decisions
3. **Policy Effectiveness**: Analyze outcomes after rate changes
4. **Historical Analysis**: Compare different economic episodes

---

## 📝 License

Apache License 2.0

---

## 👥 Contributing

This is part of the Kaggle 5-Day GenAI Capstone Project.

For issues or improvements:
1. Test your changes: `pytest test_fred_agent.py`
2. Update documentation
3. Verify A2A integration works

---

## ✅ Next Steps

1. ✅ **FRED Agent is complete**
2. 🔄 **Next**: Build BLS agent for detailed inflation breakdown
3. 🔄 **Next**: Build Treasury agent for yield curves & TIPS
4. 🔄 **Next**: Integrate all agents into Fed-PIP orchestrator

---

**Questions?** Check the test file for more examples: `test_fred_agent.py`
