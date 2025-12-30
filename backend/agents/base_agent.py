"""
Base Agent Class
All specialized agents inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json


class BaseAgent(ABC):
    """
    Base class for all agents
    Each agent must implement the execute() method
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.execution_count = 0
        self.last_execution = None
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's specific task
        
        Args:
            input_data: Input parameters for the agent
            
        Returns:
            Dictionary with:
                - success: bool
                - data: Any (agent-specific output)
                - metadata: Dict (execution info)
                - error: Optional[str]
        """
        pass
    
    def _create_response(
        self, 
        success: bool, 
        data: Any = None, 
        error: Optional[str] = None,
        sources: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create standardized response format
        """
        self.execution_count += 1
        self.last_execution = datetime.now()
        
        return {
            "success": success,
            "data": data,
            "error": error,
            "metadata": {
                "agent_name": self.name,
                "execution_time": self.last_execution.isoformat(),
                "execution_count": self.execution_count,
                "sources": sources or []
            }
        }
    
    def _log(self, message: str, level: str = "INFO"):
        """Simple logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] [{self.name}] {message}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.name,
            "description": self.description,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None
        }
