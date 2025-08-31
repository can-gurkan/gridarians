from typing import List, Dict, Optional
from dataclasses import dataclass
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import logging
import re
import gin

from src.utils.storeprompts import prompts
from src.graph_providers.base import GraphProviderBase


# Removed unused EnvironmentContext dataclass

@gin.configurable
class TextBasedEvolution:
    """Handles text-based description generation for NetLogo code evolution"""
    
    def __init__(
        self,
        provider: Optional[GraphProviderBase] = None, 
        evolution_strategy: str = "simple"  # Default to simple evolution strategy simple
    ):
        """
        Initialize TextBasedEvolution.
        
        Args:
            provider: LangChain provider for text generation
            evolution_strategy: The evolution strategy to use (e.g., "simple", "complex")
                                Controls which prompts will be used for code generation
        """
        self.logger = logging.getLogger(__name__)
        self.provider = provider
        self.evolution_strategy = evolution_strategy
        print(self.evolution_strategy)
        self.logger.info(f"Initialized TextBasedEvolution with strategy: {evolution_strategy}")

    def generate_pseudocode(self, agent_info: list, current_text: str, original_code: str) -> str:
        """
        Generate modified pseudocode for NetLogo code evolution using prompts from the prompt dictionary.
        
        Args:
            agent_info: List containing agent state and environment information
            current_text: The current text description or pseudocode
            original_code: The original NetLogo code
            
        Returns:
            Modified pseudocode
        """
        if not self.provider:
            self.logger.warning("No LLM provider available, using current text")
            return current_text
            
        try:            
            # Check if the evolution strategy exists
            if "evolution_strategies" not in prompts or self.evolution_strategy not in prompts["evolution_strategies"]:
                self.logger.warning(f"Evolution strategy '{self.evolution_strategy}' not found, falling back to simple strategy")
                # Fall back to text_evolution for backward compatibility
                if "text_evolution" in prompts:
                    user_prompt = prompts["text_evolution"]["pseudocode_prompt"].format(current_text)
                    self.logger.info("Using legacy text_evolution.pseudo_gen_prompt")
                else:
                    self.logger.error("No valid prompt found for pseudocode generation")
                    return current_text
            else:
                # Use the configured evolution strategy
                self.logger.info(f"Using evolution strategy: {self.evolution_strategy} for pseudocode generation")
                user_prompt = prompts["evolution_strategies"][self.evolution_strategy]["pseudocode_prompt"].format(pseudocode=current_text)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", ""),
                ("user", user_prompt)
            ])
                        
            chain = prompt | self.provider.initialize_model() | StrOutputParser()
            pseudocode_response = chain.invoke({"input": ""})
            
            if pseudocode_response:
                # Parse the response to extract the pseudocode
                match = re.search(r'```(.*?)```', pseudocode_response, re.DOTALL)
                if match:
                    pseudocode_response = match.group(1).strip()
                else:
                    self.logger.warning("No pseudocode found in response, using current text.")
                    return current_text
            
            return pseudocode_response
            
        except Exception as e:
            self.logger.error(f"Error generating pseudocode: {str(e)}")
            return current_text
