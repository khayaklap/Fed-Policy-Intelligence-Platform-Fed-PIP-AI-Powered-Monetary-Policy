"""Configuration for BLS Agent

Handles API keys, BLS series IDs, and configuration settings.
Bureau of Labor Statistics data for detailed inflation analysis.
"""

import os
import warnings
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables - handle missing .env gracefully
try:
    load_dotenv()
except Exception as e:
    warnings.warn(f"Could not load .env file: {e}")

# API Configuration with validation
BLS_API_KEY = os.getenv("BLS_API_KEY", "")  # Optional - higher rate limits with key
# Get free API key at: https://data.bls.gov/registrationEngine/

# Validate API key format if provided
if BLS_API_KEY and len(BLS_API_KEY) < 30:
    warnings.warn("BLS_API_KEY appears to be invalid (too short). Check your API key.")

# A2A Server Configuration with validation
A2A_HOST = os.getenv("BLS_AGENT_HOST", "0.0.0.0")
try:
    A2A_PORT = int(os.getenv("BLS_AGENT_PORT", "8002"))
    if not (1024 <= A2A_PORT <= 65535):
        warnings.warn(f"BLS_AGENT_PORT {A2A_PORT} may not be valid. Using default 8002.")
        A2A_PORT = 8002
except (ValueError, TypeError):
    warnings.warn("Invalid BLS_AGENT_PORT in environment. Using default 8002.")
    A2A_PORT = 8002

# BLS API Configuration
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
BLS_API_V1_URL = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

# Cache Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour cache
MAX_CACHE_SIZE = 1000

# API Rate Limits
# Without API key: 25 queries per day, 10 years per query
# With API key: 500 queries per day, 20 years per query
RATE_LIMIT_NO_KEY = 25
RATE_LIMIT_WITH_KEY = 500

# BLS Series IDs
# Format: CUUR0000SA0 = CPI-U (Urban) for US City Average, All Items
# CUUR = CPI Urban consumers
# 0000 = US City Average
# SA0 = All items

BLS_SERIES_MAP: Dict[str, Dict[str, str]] = {
    # ========================================================================
    # CONSUMER PRICE INDEX (CPI) - Overall Measures
    # ========================================================================
    "cpi_all": {
        "series_id": "CUUR0000SA0",
        "name": "CPI-U: All Items",
        "category": "inflation",
        "base_period": "1982-84=100",
        "frequency": "Monthly"
    },
    "cpi_core": {
        "series_id": "CUUR0000SA0L1E",
        "name": "CPI-U: All Items Less Food and Energy",
        "category": "inflation",
        "base_period": "1982-84=100",
        "frequency": "Monthly"
    },
    
    # ========================================================================
    # CPI COMPONENTS - Food
    # ========================================================================
    "cpi_food": {
        "series_id": "CUUR0000SAF",
        "name": "CPI-U: Food and Beverages",
        "category": "inflation",
        "component": "food",
        "frequency": "Monthly"
    },
    "cpi_food_home": {
        "series_id": "CUUR0000SAF11",
        "name": "CPI-U: Food at Home",
        "category": "inflation",
        "component": "food",
        "frequency": "Monthly"
    },
    "cpi_food_away": {
        "series_id": "CUUR0000SEFV",
        "name": "CPI-U: Food Away from Home",
        "category": "inflation",
        "component": "food",
        "frequency": "Monthly"
    },
    
    # ========================================================================
    # CPI COMPONENTS - Energy
    # ========================================================================
    "cpi_energy": {
        "series_id": "CUUR0000SA0E",
        "name": "CPI-U: Energy",
        "category": "inflation",
        "component": "energy",
        "frequency": "Monthly"
    },
    "cpi_gasoline": {
        "series_id": "CUUR0000SETB01",
        "name": "CPI-U: Gasoline (All Types)",
        "category": "inflation",
        "component": "energy",
        "frequency": "Monthly"
    },
    "cpi_electricity": {
        "series_id": "CUUR0000SEHF01",
        "name": "CPI-U: Electricity",
        "category": "inflation",
        "component": "energy",
        "frequency": "Monthly"
    },
    "cpi_natural_gas": {
        "series_id": "CUUR0000SEHF02",
        "name": "CPI-U: Utility (Piped) Gas Service",
        "category": "inflation",
        "component": "energy",
        "frequency": "Monthly"
    },
    
    # ========================================================================
    # CPI COMPONENTS - Housing/Shelter
    # ========================================================================
    "cpi_housing": {
        "series_id": "CUUR0000SAH",
        "name": "CPI-U: Housing",
        "category": "inflation",
        "component": "housing",
        "frequency": "Monthly"
    },
    "cpi_shelter": {
        "series_id": "CUUR0000SAH1",
        "name": "CPI-U: Shelter",
        "category": "inflation",
        "component": "housing",
        "frequency": "Monthly",
        "note": "Largest CPI component, ~32% of total"
    },
    "cpi_rent_primary": {
        "series_id": "CUUR0000SEHA",
        "name": "CPI-U: Rent of Primary Residence",
        "category": "inflation",
        "component": "housing",
        "frequency": "Monthly"
    },
    "cpi_owners_equiv_rent": {
        "series_id": "CUUR0000SEHC",
        "name": "CPI-U: Owners' Equivalent Rent",
        "category": "inflation",
        "component": "housing",
        "frequency": "Monthly",
        "note": "What homeowners would pay to rent their home"
    },
    
    # ========================================================================
    # CPI COMPONENTS - Transportation
    # ========================================================================
    "cpi_transportation": {
        "series_id": "CUUR0000SAT",
        "name": "CPI-U: Transportation",
        "category": "inflation",
        "component": "transportation",
        "frequency": "Monthly"
    },
    "cpi_new_vehicles": {
        "series_id": "CUUR0000SETA01",
        "name": "CPI-U: New Vehicles",
        "category": "inflation",
        "component": "transportation",
        "frequency": "Monthly"
    },
    "cpi_used_vehicles": {
        "series_id": "CUUR0000SETA02",
        "name": "CPI-U: Used Cars and Trucks",
        "category": "inflation",
        "component": "transportation",
        "frequency": "Monthly"
    },
    
    # ========================================================================
    # CPI COMPONENTS - Medical Care
    # ========================================================================
    "cpi_medical": {
        "series_id": "CUUR0000SAM",
        "name": "CPI-U: Medical Care",
        "category": "inflation",
        "component": "medical",
        "frequency": "Monthly"
    },
    
    # ========================================================================
    # CPI COMPONENTS - Services vs Goods
    # ========================================================================
    "cpi_services": {
        "series_id": "CUUR0000SAS",
        "name": "CPI-U: Services",
        "category": "inflation",
        "component": "services",
        "frequency": "Monthly",
        "note": "All services excluding energy"
    },
    "cpi_commodities": {
        "series_id": "CUUR0000SAC",
        "name": "CPI-U: Commodities",
        "category": "inflation",
        "component": "goods",
        "frequency": "Monthly"
    },
    "cpi_core_services": {
        "series_id": "CUUR0000SASLE",
        "name": "CPI-U: Services Less Energy Services",
        "category": "inflation",
        "component": "services",
        "frequency": "Monthly",
        "note": "Core services - key for Fed analysis"
    },
    "cpi_core_goods": {
        "series_id": "CUUR0000SACL1E",
        "name": "CPI-U: Commodities Less Food and Energy",
        "category": "inflation",
        "component": "goods",
        "frequency": "Monthly"
    },
    
    # ========================================================================
    # PRODUCER PRICE INDEX (PPI) - Leading Indicators
    # ========================================================================
    "ppi_final_demand": {
        "series_id": "WPUFD49207",
        "name": "PPI: Final Demand",
        "category": "producer_prices",
        "frequency": "Monthly",
        "note": "Leading indicator for CPI"
    },
    "ppi_final_goods": {
        "series_id": "PPIFGS",
        "name": "PPI: Finished Goods",
        "category": "producer_prices",
        "frequency": "Monthly"
    },
    "ppi_intermediate": {
        "series_id": "WPSID61",
        "name": "PPI: Intermediate Materials",
        "category": "producer_prices",
        "frequency": "Monthly"
    },
    "ppi_crude": {
        "series_id": "WPSSOP3000",
        "name": "PPI: Crude Materials",
        "category": "producer_prices",
        "frequency": "Monthly"
    },
    
    # ========================================================================
    # EMPLOYMENT COST INDEX (ECI) - Wage Pressures
    # ========================================================================
    "eci_total_comp": {
        "series_id": "CIU1010000000000A",
        "name": "ECI: Total Compensation - All Workers",
        "category": "wages",
        "frequency": "Quarterly",
        "note": "Comprehensive measure of labor costs"
    },
    "eci_wages_salaries": {
        "series_id": "CIU1010000000000I",
        "name": "ECI: Wages and Salaries - All Workers",
        "category": "wages",
        "frequency": "Quarterly",
        "note": "Excludes benefits"
    },
    "eci_benefits": {
        "series_id": "CIU1020000000000A",
        "name": "ECI: Benefits - All Workers",
        "category": "wages",
        "frequency": "Quarterly"
    },
    
    # ========================================================================
    # IMPORT/EXPORT PRICE INDICES
    # ========================================================================
    "import_prices": {
        "series_id": "EIUIR",
        "name": "Import Price Index: All Imports",
        "category": "trade",
        "frequency": "Monthly",
        "note": "Impact of global prices on US inflation"
    },
    "export_prices": {
        "series_id": "EIUIQ",
        "name": "Export Price Index: All Exports",
        "category": "trade",
        "frequency": "Monthly"
    },
    
    # ========================================================================
    # PRODUCTIVITY
    # ========================================================================
    "productivity_nonfarm": {
        "series_id": "PRS85006092",
        "name": "Productivity: Nonfarm Business Sector",
        "category": "productivity",
        "frequency": "Quarterly",
        "note": "Output per hour - key for wage-price dynamics"
    },
    "unit_labor_costs": {
        "series_id": "PRS85006112",
        "name": "Unit Labor Costs: Nonfarm Business",
        "category": "productivity",
        "frequency": "Quarterly",
        "note": "Labor costs per unit output - inflation pressure"
    }
}

# Component Categories for Analysis
CPI_COMPONENTS: Dict[str, List[str]] = {
    "food": ["cpi_food", "cpi_food_home", "cpi_food_away"],
    "energy": ["cpi_energy", "cpi_gasoline", "cpi_electricity", "cpi_natural_gas"],
    "housing": ["cpi_housing", "cpi_shelter", "cpi_rent_primary", "cpi_owners_equiv_rent"],
    "transportation": ["cpi_transportation", "cpi_new_vehicles", "cpi_used_vehicles"],
    "services": ["cpi_services", "cpi_core_services"],
    "goods": ["cpi_commodities", "cpi_core_goods"],
    "core": ["cpi_core", "cpi_core_services", "cpi_core_goods"]
}

# CPI Weights (approximate, for 2024)
# These change over time based on consumer spending patterns
CPI_WEIGHTS = {
    "housing": 32.9,
    "transportation": 16.8,
    "food": 13.4,
    "medical": 8.5,
    "recreation": 5.6,
    "education": 3.0,
    "apparel": 2.6,
    "other": 17.2
}

# Inflation Thresholds for Interpretation
INFLATION_THRESHOLDS = {
    "very_low": 0.0,      # Below 0% = deflation
    "low": 1.0,           # Below 1% = low inflation
    "moderate": 2.0,      # Fed's target
    "elevated": 3.0,      # Above target
    "high": 5.0,          # High inflation
    "very_high": 10.0     # Very high inflation
}

# Default parameters
DEFAULT_START_YEAR = 2005
DEFAULT_CALCULATION_BASE = 12  # Months for YoY calculation

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configuration utility functions
def get_api_info() -> Dict[str, any]:
    """Get current API configuration information."""
    return {
        "has_api_key": bool(BLS_API_KEY),
        "api_key_length": len(BLS_API_KEY) if BLS_API_KEY else 0,
        "api_version": "v2" if BLS_API_KEY else "v1",
        "rate_limit": RATE_LIMIT_WITH_KEY if BLS_API_KEY else RATE_LIMIT_NO_KEY,
        "host": A2A_HOST,
        "port": A2A_PORT
    }

def validate_config() -> List[str]:
    """Validate configuration and return list of issues."""
    issues = []
    
    if not BLS_API_KEY:
        issues.append("No BLS API key provided - using v1 API with lower rate limits")
    
    if BLS_API_KEY and len(BLS_API_KEY) < 30:
        issues.append("BLS API key appears invalid (too short)")
    
    if not (1024 <= A2A_PORT <= 65535):
        issues.append(f"A2A port {A2A_PORT} may not be valid")
    
    return issues

def get_series_info(series_key: str) -> Optional[Dict[str, str]]:
    """Get information about a specific BLS series."""
    return BLS_SERIES_MAP.get(series_key)

def list_available_series() -> Dict[str, List[str]]:
    """List all available series organized by category."""
    categories = {}
    for key, info in BLS_SERIES_MAP.items():
        category = info.get("category", "other")
        if category not in categories:
            categories[category] = []
        categories[category].append(key)
    return categories

# Export list for controlled imports
__all__ = [
    # Core configuration
    "BLS_API_KEY",
    "BLS_API_URL",
    "BLS_API_V1_URL", 
    "A2A_HOST",
    "A2A_PORT",
    
    # Data configuration
    "BLS_SERIES_MAP",
    "CPI_COMPONENTS",
    "CPI_WEIGHTS",
    "INFLATION_THRESHOLDS",
    
    # Cache and limits
    "CACHE_TTL_SECONDS",
    "MAX_CACHE_SIZE",
    "RATE_LIMIT_NO_KEY",
    "RATE_LIMIT_WITH_KEY",
    
    # Defaults
    "DEFAULT_START_YEAR",
    "DEFAULT_CALCULATION_BASE",
    
    # Utility functions
    "get_api_info",
    "validate_config", 
    "get_series_info",
    "list_available_series"
]
