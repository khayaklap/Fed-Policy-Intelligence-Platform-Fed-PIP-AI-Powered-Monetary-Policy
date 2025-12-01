"""
Fed-PIP Orchestrator Agent

Multi-agent coordination system for Federal Reserve Policy Intelligence Platform.

This orchestrator coordinates 9 specialized agents:
- External Agents (A2A): FRED, BLS, Treasury (real-time data)
- Core Agents (Direct): Document Processor, Policy Analyzer, Trend Tracker,
                        Comparative Analyzer, Report Generator (historical analysis)

Key Capabilities:
- Intelligent query routing
- Parallel async execution  
- Comprehensive error handling
- Fed forecast validation (unique competitive advantage)

Quick Start:
    >>> from orchestrator import create_orchestrator
    >>> 
    >>> orchestrator = await create_orchestrator()
    >>> result = await orchestrator.validate_fed_forecast(
    ...     forecast_date="2021-06-16",
    ...     indicator="inflation",
    ...     projected_value=2.0,
    ...     actual_date="2021-12-31"
    ... )

For detailed documentation, see:
- README.md - Full documentation
- QUICKSTART_ORCHESTRATOR.md - Quick start guide
- ORCHESTRATOR_AGENT_SUMMARY.md - Technical summary
"""

__version__ = "1.0.0"
__author__ = "Fed-PIP Team"
__status__ = "Production"
__all__ = [
    # Core classes
    "OrchestratorAgent",
    "AgentCoordinator",
    "RealOrchestrator",
    
    # Factory functions
    "create_orchestrator",
    "create_real_coordinator",
    
    # Configuration
    "AGENT_REGISTRY",
    "ROUTING_KEYWORDS",
    "QUERY_TYPES",
    "COORDINATION_MODES",
    "PERFORMANCE_CONFIG",
    "ERROR_HANDLING",
    "OUTPUT_PREFERENCES",
    "EXTERNAL_AGENTS",
    
    # Tools
    "analyze_inflation_episode_tool",
    "validate_fed_forecast_tool",
    "compare_policy_periods_tool",
    "analyze_current_conditions_tool",
    "generate_comprehensive_report_tool",
    
    # Utility functions
    "get_version",
    "get_available_agents",
    "get_external_agents",
    "get_core_agents",
    "get_agent_capabilities",
    "print_info",
    
    # Metadata
    "__version__",
    "__author__",
    "__status__"
]

# ============================================================================
# IMPORTS
# ============================================================================

import sys
import warnings
from typing import List, Dict, Optional

# ============================================================================
# VERSION CHECK
# ============================================================================

if sys.version_info < (3, 8):
    raise RuntimeError(
        f"Python 3.8+ required. Current version: "
        f"{sys.version_info.major}.{sys.version_info.minor}"
    )

# ============================================================================
# CORE IMPORTS
# ============================================================================

try:
    # Try relative imports first (when used as module)
    from .orchestrator_agent import (
        OrchestratorAgent,
        create_orchestrator,
        RealOrchestrator
    )
    _orchestrator_available = True
except ImportError:
    try:
        # Fall back to absolute imports (when run directly)
        from orchestrator_agent import (
            OrchestratorAgent,
            create_orchestrator,
            RealOrchestrator
        )
        _orchestrator_available = True
    except ImportError as e:
        warnings.warn(f"Orchestrator agent not available: {e}", ImportWarning)
        _orchestrator_available = False

try:
    from .agent_coordinator import (
        AgentCoordinator,
        create_real_coordinator
    )
    _coordinator_available = True
except ImportError:
    try:
        from agent_coordinator import (
            AgentCoordinator,
            create_real_coordinator
        )
        _coordinator_available = True
    except ImportError as e:
        warnings.warn(f"Agent coordinator not available: {e}", ImportWarning)
        _coordinator_available = False

# ============================================================================
# CONFIGURATION IMPORTS
# ============================================================================

try:
    from .orchestrator_config import (
        AGENT_REGISTRY,
        ROUTING_KEYWORDS,
        QUERY_TYPES,
        COORDINATION_MODES,
        PERFORMANCE_CONFIG,
        ERROR_HANDLING,
        OUTPUT_PREFERENCES,
        EXTERNAL_AGENTS
    )
    _config_available = True
except ImportError:
    try:
        from orchestrator_config import (
            AGENT_REGISTRY,
            ROUTING_KEYWORDS,
            QUERY_TYPES,
            COORDINATION_MODES,
            PERFORMANCE_CONFIG,
            ERROR_HANDLING,
            OUTPUT_PREFERENCES,
            EXTERNAL_AGENTS
        )
        _config_available = True
    except ImportError as e:
        warnings.warn(f"Orchestrator config not available: {e}", ImportWarning)
        _config_available = False
        # Fallback empty configs
        AGENT_REGISTRY = {}
        ROUTING_KEYWORDS = {}
        QUERY_TYPES = {}
        COORDINATION_MODES = {}
        PERFORMANCE_CONFIG = {}
        ERROR_HANDLING = {}
        OUTPUT_PREFERENCES = {}
        EXTERNAL_AGENTS = {}

# ============================================================================
# TOOL IMPORTS
# ============================================================================

try:
    from .orchestrator_tools import (
try:
    from .orchestrator_tools import (
        analyze_inflation_episode_tool,
        validate_fed_forecast_tool,
        compare_policy_periods_tool,
        analyze_current_conditions_tool,
        generate_comprehensive_report_tool
    )
    _tools_available = True
except ImportError:
    try:
        from orchestrator_tools import (
            analyze_inflation_episode_tool,
            validate_fed_forecast_tool,
            compare_policy_periods_tool,
            analyze_current_conditions_tool,
            generate_comprehensive_report_tool
        )
        _tools_available = True
    except ImportError as e:
        warnings.warn(f"Orchestrator tools not available: {e}", ImportWarning)
        _tools_available = False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_version() -> str:
    """Return the current version of the orchestrator agent."""
    return __version__

def get_available_agents() -> List[str]:
    """
    Return list of all available agent names.
    
    Returns:
        List of agent names from registry
    """
    return list(AGENT_REGISTRY.keys()) if _config_available else []

def get_external_agents() -> List[str]:
    """
    Return list of external agent names (A2A protocol).
    
    External agents run as separate services and are accessed via HTTP.
    Currently: FRED, BLS, Treasury
    
    Returns:
        List of external agent names
    """
    if not _config_available:
        return []
    return [
        name for name, config in AGENT_REGISTRY.items()
        if config.get("type") == "external"
    ]

def get_core_agents() -> List[str]:
    """
    Return list of core agent names (direct Python import).
    
    Core agents are imported directly and called as Python functions.
    Currently: Document Processor, Policy Analyzer, Trend Tracker,
               Comparative Analyzer, Report Generator
    
    Returns:
        List of core agent names
    """
    if not _config_available:
        return []
    return [
        name for name, config in AGENT_REGISTRY.items()
        if config.get("type") == "core"
    ]

def get_agent_capabilities(agent_name: str) -> List[str]:
    """
    Get capabilities for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., "fred_agent")
        
    Returns:
        List of capability/tool names for that agent
        
    Example:
        >>> get_agent_capabilities("fred_agent")
        ['get_gdp_data', 'get_inflation_data', ...]
    """
    if not _config_available or agent_name not in AGENT_REGISTRY:
        return []
    return AGENT_REGISTRY[agent_name].get("capabilities", [])

def get_query_type_agents(query_type: str) -> Dict[str, List[str]]:
    """
    Get required and optional agents for a query type.
    
    Args:
        query_type: Type of query (e.g., "forecast_validation")
        
    Returns:
        Dict with "required_agents" and "optional_agents" lists
        
    Example:
        >>> get_query_type_agents("forecast_validation")
        {
            "required_agents": ["fred_agent", "treasury_agent"],
            "optional_agents": ["bls_agent", "comparative_analyzer"]
        }
    """
    if not _config_available or query_type not in QUERY_TYPES:
        return {"required_agents": [], "optional_agents": []}
    
    return {
        "required_agents": QUERY_TYPES[query_type].get("required_agents", []),
        "optional_agents": QUERY_TYPES[query_type].get("optional_agents", [])
    }

def print_info():
    """Print orchestrator package information."""
    external_count = len(get_external_agents())
    core_count = len(get_core_agents())
    
    status_emoji = "✅" if _orchestrator_available and _coordinator_available and _config_available and _tools_available else "⚠️"
    
    print(f"""
{status_emoji} Fed-PIP Orchestrator Agent v{__version__}
Status: {__status__}

Available Agents: {len(AGENT_REGISTRY)}
├─ External (A2A): {external_count} - {', '.join(get_external_agents()) if external_count else 'None'}
└─ Core (Direct): {core_count} - {', '.join(get_core_agents()) if core_count else 'None'}

Query Types: {len(QUERY_TYPES)}
Coordination Modes: {len(COORDINATION_MODES)}

Components:
├─ Orchestrator: {'✅ Available' if _orchestrator_available else '❌ Not Available'}
├─ Coordinator: {'✅ Available' if _coordinator_available else '❌ Not Available'}
├─ Configuration: {'✅ Available' if _config_available else '❌ Not Available'}
└─ Tools: {'✅ Available' if _tools_available else '❌ Not Available'}

Unique Capabilities:
✅ Fed Forecast Validation (compare SEP vs Market vs Actual)
✅ 78 Economic Series (FRED 22 + BLS 32 + Treasury 24)
✅ True Multi-Agent Coordination (A2A + Direct)
✅ Advanced Analytics (PELT + Taylor Rule + DTW)
✅ 68 FOMC Documents parsed

Documentation:
├─ README.md - Full documentation
├─ QUICKSTART_ORCHESTRATOR.md - Quick start guide
└─ ORCHESTRATOR_AGENT_SUMMARY.md - Technical summary

For help: print_info()
For version: get_version()
For agents: get_available_agents()
    """.strip())

def print_agent_info(agent_name: str):
    """
    Print detailed information about a specific agent.
    
    Args:
        agent_name: Name of the agent
    """
    if not _config_available or agent_name not in AGENT_REGISTRY:
        print(f"❌ Agent '{agent_name}' not found in registry")
        return
    
    agent = AGENT_REGISTRY[agent_name]
    agent_type = agent.get("type", "unknown")
    
    type_emoji = "🌐" if agent_type == "external" else "💻"
    
    print(f"""
{type_emoji} {agent_name}
Type: {agent_type.upper()}
Description: {agent.get('description', 'N/A')}

Capabilities ({len(agent.get('capabilities', []))}):
{chr(10).join(f"  ├─ {cap}" for cap in agent.get('capabilities', []))}

Data Provided:
{chr(10).join(f"  ├─ {data}" for data in agent.get('data_provided', []))}

Response Time: {agent.get('typical_response_time', 'N/A')}
Example Use: {agent.get('example_use', 'N/A')}
    """.strip())

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def quick_query(query: str, **kwargs):
    """
    Quick query using default orchestrator.
    
    Args:
        query: User query string
        **kwargs: Additional parameters
        
    Returns:
        Query result
        
    Example:
        >>> result = await quick_query("What was inflation in 2022?")
    """
    if not _orchestrator_available:
        raise ImportError("Orchestrator not available")
    
    orchestrator = await create_orchestrator()
    return await orchestrator.query(query, **kwargs)

# ============================================================================
# HEALTH CHECK
# ============================================================================

def check_external_agents() -> Dict[str, bool]:
    """
    Check if external agents are running (non-blocking).
    
    Returns:
        Dict mapping agent name to health status (True/False)
        
    Example:
        >>> check_external_agents()
        {'fred_agent': True, 'bls_agent': True, 'treasury_agent': False}
    """
    import aiohttp
    import asyncio
    
    if not _config_available:
        return {}
    
    async def check_agent(name: str, url: str) -> tuple:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    return name, resp.status == 200
        except Exception:
            return name, False
    
    async def check_all():
        tasks = [
            check_agent(name, url)
            for name, url in EXTERNAL_AGENTS.items()
        ]
        results = await asyncio.gather(*tasks)
        return dict(results)
    
    try:
        # Try to get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # Can't check synchronously if loop already running
            return {name: None for name in EXTERNAL_AGENTS.keys()}
        else:
            return loop.run_until_complete(check_all())
    except Exception:
        return {name: None for name in EXTERNAL_AGENTS.keys()}

# ============================================================================
# INITIALIZATION
# ============================================================================

# Print warning if critical components missing
if not _orchestrator_available or not _coordinator_available:
    warnings.warn(
        "Orchestrator components not fully available. "
        "Some functionality may be limited.",
        RuntimeWarning
    )

# Optional: Check external agents on import (uncomment to enable)
# _agent_status = check_external_agents()
# if _agent_status:
#     for agent, status in _agent_status.items():
#         if status is False:
#             warnings.warn(
#                 f"External agent '{agent}' not accessible. "
#                 f"Ensure it's running on {EXTERNAL_AGENTS.get(agent)}",
#                 RuntimeWarning
#             )

# ============================================================================
# MODULE INFO
# ============================================================================

def _get_module_info() -> Dict:
    """Get module metadata (for programmatic access)."""
    return {
        "name": "orchestrator",
        "version": __version__,
        "author": __author__,
        "status": __status__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "components": {
            "orchestrator": _orchestrator_available,
            "coordinator": _coordinator_available,
            "config": _config_available,
            "tools": _tools_available
        },
        "agents": {
            "total": len(AGENT_REGISTRY),
            "external": len(get_external_agents()),
            "core": len(get_core_agents())
        },
        "capabilities": {
            "query_types": len(QUERY_TYPES),
            "coordination_modes": len(COORDINATION_MODES),
            "forecast_validation": True,
            "multi_agent_coordination": True
        }
    }

# Export for introspection
MODULE_INFO = _get_module_info()
