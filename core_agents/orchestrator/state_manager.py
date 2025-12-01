"""
State Manager

Manages conversation state and context across multiple queries.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StateManager:
    """
    Manage conversation state and context.
    """
    
    def __init__(self):
        """Initialize state manager."""
        logger.info("Initialized State Manager")
        self.conversations = {}
        self.current_conversation_id = None
    
    def create_conversation(self, conversation_id: Optional[str] = None) -> str:
        """Create new conversation."""
        
        if conversation_id is None:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.conversations[conversation_id] = {
            'id': conversation_id,
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'context': {},
            'agent_results': {}
        }
        
        self.current_conversation_id = conversation_id
        logger.info(f"Created conversation: {conversation_id}")
        
        return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Add message to conversation."""
        
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        
        message = {
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.conversations[conversation_id]['messages'].append(message)
    
    def update_context(self, conversation_id: str, key: str, value: any):
        """Update conversation context."""
        
        if conversation_id in self.conversations:
            self.conversations[conversation_id]['context'][key] = value
    
    def get_context(self, conversation_id: str) -> Dict:
        """Get conversation context."""
        
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]['context']
        return {}
    
    def store_agent_result(self, conversation_id: str, agent: str, result: Dict):
        """Store agent execution result."""
        
        if conversation_id in self.conversations:
            if 'agent_results' not in self.conversations[conversation_id]:
                self.conversations[conversation_id]['agent_results'] = {}
            
            self.conversations[conversation_id]['agent_results'][agent] = {
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get full conversation."""
        return self.conversations.get(conversation_id)
    
    def clear_conversation(self, conversation_id: str):
        """Clear conversation state."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation: {conversation_id}")
