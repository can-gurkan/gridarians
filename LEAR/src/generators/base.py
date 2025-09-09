from abc import ABC, abstractmethod
from typing import Tuple, Optional
from pydantic import BaseModel

import logging
import gin

from src.utils.storeprompts import prompts
from src.utils.retry import CodeRetryHandler
from src.verification.verify_netlogo import NetLogoVerifier


class NLogoCode(BaseModel):
    new_code: str

@gin.register
class BaseCodeGenerator(ABC):
    def __init__(self, verifier: NetLogoVerifier):
        """Initialize with verifier instance."""
        self.verifier = verifier
        
    def validate_input(self, agent_info: list) -> Tuple[bool, Optional[str]]:
        """Validate the input format and content."""
        if not isinstance(agent_info, list) or len(agent_info) < 2:
            return False, "agent_info must be a list with atleast 2 elements"
        
        if not isinstance(agent_info[0], str):
            return False, "First element must be a string containing NetLogo code"
            
        #if not isinstance(agent_info[1], list) or len(agent_info[1]) != 3:
         #   return False, "Second element must be a list with exactly 3 food distances"
        #if not isinstance(agent_info[1], list) or len(agent_info[1]) != 3:
        #    return False, "Second element must be a list with exactly 3 food distances"
            
        # if not all(isinstance(x, (int, float)) for x in agent_info[1]):
        #     return False, "All food distances must be numbers"
            
        return True, None

    # Removed unused get_base_prompt method
    
    # @abstractmethod - Removed decorator as this method is no longer required by all subclasses
    def generate_code(self, agent_info: list) -> str:
        """Generate new NetLogo code based on agent info."""
        # Default implementation (optional, could also just be 'pass')
        self.logger.warning("Base generate_code method called. Subclass should implement if needed.")
        if agent_info and isinstance(agent_info, list) and len(agent_info) > 0 and isinstance(agent_info[0], str):
            return agent_info[0] # Return original code as fallback
        return ""

    # @abstractmethod # Removed decorator to avoid forcing implementation in subclasses like NetLogoCodeGenerator
    def generate_code_from_state(self, state: dict) -> str:
        """Generate new NetLogo code based on the full generation state."""
        self.logger.warning("Base generate_code_from_state method called. Subclass should implement if needed.")
        original_code = state.get("original_code", "")
        return original_code # Return original code as fallback
