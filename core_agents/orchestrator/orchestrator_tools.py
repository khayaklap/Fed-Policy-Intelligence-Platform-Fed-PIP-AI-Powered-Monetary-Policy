"""
Orchestrator Tools

Five ADK tools for coordinating the Fed Policy Intelligence Platform.
"""

import logging
from typing import Dict, List, Optional

# Handle relative imports for package usage and absolute for direct execution
try:
    from .query_router import QueryRouter
    from .agent_coordinator import AgentCoordinator
    from .state_manager import StateManager
    from .orchestrator_config import (
        AGENT_REGISTRY,
        WORKFLOW_TEMPLATES,
        QUERY_TYPES
    )
except ImportError:
    from query_router import QueryRouter
    from agent_coordinator import AgentCoordinator
    from state_manager import StateManager
    from orchestrator_config import (
        AGENT_REGISTRY,
        WORKFLOW_TEMPLATES,
        QUERY_TYPES
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
_router = QueryRouter()
_coordinator = AgentCoordinator()
_state_manager = StateManager()


# ============================================================================
# TOOL 1: ANALYZE QUERY
# ============================================================================

def analyze_query_tool(query: str, context: Optional[Dict] = None) -> Dict:
    """
    Analyze user query and determine which agents to use.
    
    This tool is the first step in the orchestration process. It analyzes
    the query, classifies it, and determines which agents are needed.
    
    Args:
        query: User query string
        context: Optional conversation context
    
    Returns:
        Dictionary containing:
        - query_type: Classification (meeting_analysis, current_stance, etc.)
        - required_agents: List of required agents
        - optional_agents: List of optional agents
        - confidence: Routing confidence (0-1)
        - reasoning: Why these agents were selected
        - parameters: Extracted parameters (dates, episodes, formats)
        - suggested_workflow: Recommended workflow template
    
    Query Types:
        - meeting_analysis: Analyze specific FOMC meeting
        - current_stance: What's current Fed policy
        - trend_analysis: Policy evolution over time
        - historical_comparison: Compare to past episodes
        - comprehensive_analysis: Complete analysis
        - economic_context: Current economic conditions
        - prediction: Predict next Fed action
        - report_generation: Generate formatted report
    
    Example:
        >>> result = analyze_query_tool(
        ...     "How has Fed policy evolved over the past 5 years?"
        ... )
        >>> print(result['query_type'])
        'trend_analysis'
        >>> print(result['required_agents'])
        ['policy_analyzer', 'trend_tracker']
    """
    logger.info(f"Tool called: analyze_query")
    
    try:
        # Route query
        routing = _router.route_query(query, context)
        
        # Extract parameters
        parameters = _router.extract_parameters(query)
        
        # Suggest workflow template if applicable
        suggested_workflow = None
        query_type = routing['query_type']
        
        if query_type == 'comprehensive_analysis':
            suggested_workflow = 'full_analysis'
        elif query_type == 'report_generation':
            suggested_workflow = 'quick_brief'
        elif query_type == 'historical_comparison':
            suggested_workflow = 'episode_deep_dive'
        
        # Check if clarification needed
        clarification = _router.suggest_clarification(query, routing)
        
        logger.info(f"Query analyzed: type={query_type}, confidence={routing['confidence']}")
        
        return {
            **routing,
            'parameters': parameters,
            'suggested_workflow': suggested_workflow,
            'clarification_needed': clarification,
            'available_agents': list(AGENT_REGISTRY.keys())
        }
        
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        return {
            'error': str(e),
            'message': 'Failed to analyze query'
        }


# ============================================================================
# TOOL 2: EXECUTE WORKFLOW
# ============================================================================

def execute_workflow_tool(
    agents: List[str],
    mode: str = 'sequential',
    parameters: Optional[Dict] = None
) -> Dict:
    """
    Execute multi-agent workflow.
    
    This tool coordinates execution of multiple agents to answer complex
    queries that require data from multiple sources.
    
    Args:
        agents: List of agent names to execute
        mode: Coordination mode:
            - 'sequential': Execute one after another (default)
            - 'parallel': Execute simultaneously (faster)
            - 'adaptive': Adjust based on results
        parameters: Parameters for agents
    
    Returns:
        Dictionary containing:
        - results: Results from each agent
        - execution_time: Total time taken (seconds)
        - status: 'success', 'partial', or 'failed'
        - errors: Any errors encountered
        - agents_executed: List of agents that ran
        - mode: Coordination mode used
    
    Available Agents:
        Core:
        - document_processor: Parse FOMC documents
        - policy_analyzer: Analyze recent trends
        - trend_tracker: Long-term patterns
        - comparative_analyzer: Historical comparisons
        - report_generator: Generate reports
        
        External:
        - fred: Economic data
        - bls: Inflation/employment
        - treasury: Market expectations
    
    Example:
        >>> # Analyze current Fed stance
        >>> result = execute_workflow_tool(
        ...     agents=['document_processor', 'policy_analyzer', 'fred'],
        ...     mode='sequential',
        ...     parameters={
        ...         'document_processor': {'num_meetings': 3},
        ...         'fred': {'indicators': ['inflation', 'unemployment']}
        ...     }
        ... )
        >>> print(result['status'])
        'success'
        >>> print(f"Executed in {result['execution_time']} seconds")
        Executed in 3.2 seconds
    """
    logger.info(f"Tool called: execute_workflow with {len(agents)} agents")
    
    try:
        result = _coordinator.execute_workflow(agents, mode, parameters)
        
        logger.info(f"Workflow executed: status={result['status']}, time={result['execution_time']}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return {
            'error': str(e),
            'message': 'Failed to execute workflow',
            'status': 'failed'
        }


# ============================================================================
# TOOL 3: EXECUTE TEMPLATE WORKFLOW
# ============================================================================

def execute_template_workflow_tool(
    template_name: str,
    parameters: Optional[Dict] = None
) -> Dict:
    """
    Execute a predefined workflow template.
    
    This tool runs preconfigured multi-agent workflows for common use cases.
    Templates define which agents to use and in what order.
    
    Args:
        template_name: Name of workflow template:
            - 'full_analysis': Complete Fed policy analysis (all agents)
            - 'quick_brief': Fast summary (minimal agents)
            - 'episode_deep_dive': Historical episode analysis
        parameters: Optional parameters for agents
    
    Returns:
        Dictionary containing:
        - results: Results from all agents in workflow
        - execution_time: Total time taken
        - status: Success/failure
        - template: Template name
        - template_description: What this template does
        - agents_executed: Which agents ran
    
    Templates:
        **full_analysis** (30-60 seconds):
        1. Document Processor → Recent meetings
        2. Policy Analyzer → Sentiment trends
        3. Trend Tracker → Cycles
        4. Comparative Analyzer → Similar episodes
        5. FRED → Economic data
        6. Report Generator → Comprehensive report
        
        **quick_brief** (5-10 seconds):
        1. Document Processor → Latest meeting
        2. Policy Analyzer → Current stance
        3. Report Generator → Quick summary
        
        **episode_deep_dive** (10-15 seconds):
        1. Comparative Analyzer → Compare episodes
        2. Comparative Analyzer → Extract lessons
        3. Report Generator → Comparison report
    
    Example:
        >>> # Generate complete analysis
        >>> result = execute_template_workflow_tool(
        ...     template_name='full_analysis',
        ...     parameters={'export_format': 'pdf'}
        ... )
        >>> print(result['template_description'])
        'Comprehensive analysis using all agents'
        >>> print(f"Report: {result['results']['report_generator']['data']['report_path']}")
        Report: fed_policy_report.pdf
    """
    logger.info(f"Tool called: execute_template_workflow ({template_name})")
    
    try:
        result = _coordinator.execute_template_workflow(template_name, parameters)
        
        logger.info(f"Template workflow executed: {template_name}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing template workflow: {e}")
        return {
            'error': str(e),
            'message': 'Failed to execute template workflow'
        }


# ============================================================================
# TOOL 4: GET AGENT INFO
# ============================================================================

def get_agent_info_tool(agent_name: Optional[str] = None) -> Dict:
    """
    Get information about available agents.
    
    This tool provides details about agent capabilities, what data they
    provide, and when to use them.
    
    Args:
        agent_name: Optional specific agent name. If None, returns all agents.
    
    Returns:
        If agent_name provided:
        - type: 'core' or 'external'
        - description: What the agent does
        - capabilities: List of capabilities
        - required_for: When this agent is needed
        - data_provided: What data it returns
        - typical_response_time: How fast it runs
        
        If agent_name is None:
        - num_agents: Total number of agents
        - core_agents: List of core agents
        - external_agents: List of external agents
        - all_agents: Dictionary of all agent info
    
    Example:
        >>> # Get info on specific agent
        >>> info = get_agent_info_tool('policy_analyzer')
        >>> print(info['description'])
        'Analyze short-term policy trends (1.5-6 years)'
        >>> print(info['capabilities'])
        ['sentiment_trend_analysis', 'regime_change_detection', ...]
        
        >>> # Get all agents
        >>> all_info = get_agent_info_tool()
        >>> print(f"{all_info['num_agents']} agents available")
        8 agents available
        >>> print(all_info['core_agents'])
        ['document_processor', 'policy_analyzer', 'trend_tracker', ...]
    """
    logger.info(f"Tool called: get_agent_info ({agent_name or 'all'})")
    
    try:
        if agent_name:
            # Return specific agent info
            if agent_name in AGENT_REGISTRY:
                return AGENT_REGISTRY[agent_name]
            else:
                return {
                    'error': f'Agent not found: {agent_name}',
                    'available_agents': list(AGENT_REGISTRY.keys())
                }
        else:
            # Return all agents
            core_agents = [name for name, info in AGENT_REGISTRY.items() if info['type'] == 'core']
            external_agents = [name for name, info in AGENT_REGISTRY.items() if info['type'] == 'external']
            
            return {
                'num_agents': len(AGENT_REGISTRY),
                'core_agents': core_agents,
                'external_agents': external_agents,
                'all_agents': AGENT_REGISTRY
            }
        
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        return {
            'error': str(e),
            'message': 'Failed to get agent info'
        }


# ============================================================================
# TOOL 5: GET PLATFORM STATUS
# ============================================================================

def get_platform_status_tool() -> Dict:
    """
    Get status and statistics of the Fed Policy Intelligence Platform.
    
    This tool provides an overview of the platform including available
    agents, recent executions, and system health.
    
    Returns:
        Dictionary containing:
        - platform_name: "Fed Policy Intelligence Platform"
        - version: Platform version
        - status: 'operational' or 'degraded'
        - agents: Agent availability and status
        - recent_executions: Statistics on recent workflows
        - capabilities: Summary of what platform can do
        - available_workflows: List of workflow templates
        - query_types: Supported query types
    
    Example:
        >>> status = get_platform_status_tool()
        >>> print(status['status'])
        'operational'
        >>> print(f"{len(status['agents']['available'])} agents available")
        8 agents available
        >>> print(status['recent_executions']['total_executions'])
        15
    """
    logger.info("Tool called: get_platform_status")
    
    try:
        # Get coordinator stats
        exec_stats = _coordinator.get_execution_stats()
        
        # Count agents
        total_agents = len(AGENT_REGISTRY)
        core_agents = [name for name, info in AGENT_REGISTRY.items() if info['type'] == 'core']
        external_agents = [name for name, info in AGENT_REGISTRY.items() if info['type'] == 'external']
        
        return {
            'platform_name': 'Fed Policy Intelligence Platform',
            'version': '1.0.0',
            'status': 'operational',
            'agents': {
                'total': total_agents,
                'core': len(core_agents),
                'external': len(external_agents),
                'available': list(AGENT_REGISTRY.keys()),
                'core_agents': core_agents,
                'external_agents': external_agents
            },
            'recent_executions': exec_stats,
            'capabilities': {
                'document_parsing': True,
                'sentiment_analysis': True,
                'trend_detection': True,
                'historical_comparison': True,
                'report_generation': True,
                'economic_data_access': True,
                'multi_agent_coordination': True
            },
            'available_workflows': list(WORKFLOW_TEMPLATES.keys()),
            'query_types': list(QUERY_TYPES.keys()),
            'num_workflow_templates': len(WORKFLOW_TEMPLATES),
            'num_query_types': len(QUERY_TYPES)
        }
        
    except Exception as e:
        logger.error(f"Error getting platform status: {e}")
        return {
            'error': str(e),
            'message': 'Failed to get platform status',
            'status': 'degraded'
        }


# ============================================================================
# HELPER: LIST WORKFLOWS
# ============================================================================

def list_workflows() -> Dict:
    """
    List all available workflow templates.
    
    Returns:
        Dictionary with workflow information
    """
    return {
        'num_workflows': len(WORKFLOW_TEMPLATES),
        'workflows': {
            key: {
                'name': config['name'],
                'description': config['description'],
                'num_steps': len(config['steps']),
                'estimated_time': config['estimated_time']
            }
            for key, config in WORKFLOW_TEMPLATES.items()
        }
    }


# ============================================================================
# HELPER: LIST QUERY TYPES
# ============================================================================

def list_query_types() -> Dict:
    """
    List all supported query types.
    
    Returns:
        Dictionary with query type information
    """
    return {
        'num_types': len(QUERY_TYPES),
        'types': {
            key: {
                'description': config['description'],
                'required_agents': config['required_agents'],
                'example': config.get('example', '')
            }
            for key, config in QUERY_TYPES.items()
        }
    }
