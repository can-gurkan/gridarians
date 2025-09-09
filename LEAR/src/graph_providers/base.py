from abc import abstractmethod
import os
import gin
import re
from typing import Optional, List
from dotenv import load_dotenv

from src.generators.base import BaseCodeGenerator
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.storeprompts import prompts
from src.utils.logging import get_logger

# Load environment variables
load_dotenv()

@gin.configurable
class GraphProviderBase(BaseCodeGenerator):
    """Base class for graph-based code generators."""
    
    def __init__(self, verifier: NetLogoVerifier, retry_max_attempts: int = 5, evolution_strategy: str = "simple", prompt_type: str = "groq", prompt_name: str = "prompt2", retry_prompt: str = None):
        """Initialize with verifier instance."""
        super().__init__(verifier)
        self.model = None  # To be set by child classes
        self.logger = get_logger()
        self.evolution_strategy = evolution_strategy # Default evolution strategy
        
        # Code generation prompts
        self.prompt_type = prompt_type
        self.prompt_name = prompt_name
        
        # Retry Prompts
        self.retry_prompt = retry_prompt
        
    @abstractmethod
    def initialize_model(self):
        """Initialize and return provider-specific model."""
        pass

    