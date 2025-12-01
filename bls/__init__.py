"""BLS Agent

Bureau of Labor Statistics integration agent.
"""

__version__ = "1.0.0"

# Handle relative imports for package usage and absolute for direct execution
try:
    # Import main components for easier external access
    from .bls_agent import create_bls_agent, run_a2a_server
    from .bls_api_wrapper import BLSAPIWrapper, get_bls_wrapper
    from .bls_config import BLS_SERIES_MAP, CPI_COMPONENTS, A2A_HOST, A2A_PORT

    # Import all tool functions
    from .bls_tools import (
        get_cpi_components,
        get_ppi_data,
        get_employment_cost_index,
        compare_inflation_measures,
        analyze_inflation_drivers
    )
except ImportError:
    # Fallback for direct execution or when used as standalone module
    try:
        from bls_agent import create_bls_agent, run_a2a_server
        from bls_api_wrapper import BLSAPIWrapper, get_bls_wrapper
        from bls_config import BLS_SERIES_MAP, CPI_COMPONENTS, A2A_HOST, A2A_PORT
        from bls_tools import (
            get_cpi_components,
            get_ppi_data,
            get_employment_cost_index,
            compare_inflation_measures,
            analyze_inflation_drivers
        )
    except ImportError as e:
        # If we can't import anything, at least provide version info
        import warnings
        warnings.warn(f"Could not import BLS agent components: {e}")

# Define exports - these will be available if imports succeed
__all__ = [
    # Main agent components
    "create_bls_agent",
    "run_a2a_server",
    
    # API wrapper
    "BLSAPIWrapper", 
    "get_bls_wrapper",
    
    # Configuration
    "BLS_SERIES_MAP",
    "CPI_COMPONENTS", 
    "A2A_HOST",
    "A2A_PORT",
    
    # Tool functions
    "get_cpi_components",
    "get_ppi_data", 
    "get_employment_cost_index",
    "compare_inflation_measures",
    "analyze_inflation_drivers"
]

# Helper function to check if all components are available
def is_fully_loaded():
    """Check if all BLS agent components were successfully imported."""
    required_components = [
        'create_bls_agent', 'get_cpi_components', 'BLS_SERIES_MAP'
    ]
    return all(name in globals() for name in required_components)
