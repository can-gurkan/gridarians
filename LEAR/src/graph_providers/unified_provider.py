import os
from src.utils import logging
import gin, re
from typing import Optional, List, Any
from enum import Enum

from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.graph_providers.base import GraphProviderBase
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.storeprompts import prompts

# Define supported models
class SupportedModels(Enum):
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    OPENAI = "openai"

@gin.configurable
class GraphUnifiedProvider(GraphProviderBase):
    """
    Unified graph-based provider that supports multiple models.
    """
    
    # Model name parameters defined at init level to make them configurable
    def __init__(self, model_name: str, verifier: NetLogoVerifier,
                 prompt_type: str = 'default_type', # Added prompt_type
                 prompt_name: str = 'default_name', # Added prompt_name
                 temperature: float = 0.7, max_tokens: int = 1000,
                 claude_model_name: str = "claude-3-5-sonnet-20240229",
                 deepseek_model_name: str = "deepseek-chat",
                 groq_model_name: str = "llama-3.3-70b-versatile",
                 openai_model_name: str = "gpt-4o"):
        """
        Initialize with model name and verifier instance.
        
        Args:
            model_name: Type of model to use
            verifier: NetLogoVerifier instance
            prompt_type: Type of prompt to use for code generation (from Gin)
            prompt_name: Name of prompt to use for code generation (from Gin)
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            claude_model_name: Model name for Claude
            deepseek_model_name: Model name for DeepSeek
            groq_model_name: Model name for Groq
            openai_model_name: Model name for OpenAI
        """
        super().__init__(verifier)
        self.model_name = model_name
        self.model = None
        self.api_key = None
        self.logger = logging.get_logger()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.claude_model_name = claude_model_name
        self.deepseek_model_name = deepseek_model_name
        self.groq_model_name = groq_model_name
        self.openai_model_name = openai_model_name
        # Store prompt config explicitly
        self.prompt_type = prompt_type
        self.prompt_name = prompt_name

        # Set API key based on model name
        if self.model_name == SupportedModels.CLAUDE.value:
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        elif self.model_name == SupportedModels.DEEPSEEK.value:
            self.api_key = os.getenv('DEEPSEEK_API_KEY')
            if not self.api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        elif self.model_name == SupportedModels.GROQ.value:
            self.api_key = os.getenv('GROQ_API_KEY')
            if not self.api_key:
                raise ValueError("GROQ_API_KEY environment variable is required")
        elif self.model_name == SupportedModels.OPENAI.value:
            self.api_key = os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
        else:
            raise ValueError(f"Unsupported model name: {self.model_name}")
            
    def initialize_model(self):
        """Initialize and return provider-specific model based on model name."""
        try:
            if self.model_name == SupportedModels.CLAUDE.value:
                model = ChatAnthropic(
                    model=self.claude_model_name,
                    anthropic_api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            elif self.model_name == SupportedModels.DEEPSEEK.value:
                model = ChatDeepSeek(
                    model_name=self.deepseek_model_name,
                    api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            elif self.model_name == SupportedModels.GROQ.value:
                model = ChatGroq(
                    model_name=self.groq_model_name,
                    groq_api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            elif self.model_name == SupportedModels.OPENAI.value:
                model = ChatOpenAI(
                    model=self.openai_model_name,
                    openai_api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            else:
                raise ValueError(f"Unsupported model name: {self.model_name}")
            return model

        except Exception as e:
            self.logger.error(f"Failed to initialize model for {self.model_name}: {str(e)}")
            raise

    def generate_code_from_state(self, state: dict) -> str:
        """
        Generate new NetLogo code based on the full generation state provided by the graph.
        Uses the initialized model for the specific provider (Groq, Claude, etc.).

        Args:
            state: The current generation state dictionary. Expected keys include:
                   'original_code', 'error_message' (optional),
                   'modified_pseudocode' (optional), 'initial_pseudocode'.

        Returns:
            The generated NetLogo code as a string.
        """
        self.logger.info(f"Generating code from state using {self.model_name} provider")
        try:
            # Ensure model is initialized
            if not self.model:
                self.model = self.initialize_model()

            # Extract relevant info from state
            original_code = state.get("original_code", "")
            error_message = state.get("error_message", None)
            modified_pseudocode = state.get("modified_pseudocode", None)
            initial_pseudocode = state.get("initial_pseudocode", "") # Fallback if no modified

            # --- Determine Prompt and Input ---
            user_content = ""

            system_message = prompts.get("langchain", {}).get("cot_system", "You are a NetLogo programming assistant.")
            invoke_input = {} # Initialize empty invoke input

            if error_message and modified_pseudocode:
                self.logger.info(f"Using retry prompt '{self.retry_prompt}' with pseudocode due to error: {error_message[:100]}...")
                
                prompt_template = prompts.get("retry_prompts", {}).get(self.retry_prompt, "")
                if not prompt_template:
                    prompt_template = prompts.get("retry_prompts", {}).get("generate_code_with_pseudocode_and_error")
                
                # Format the prompt with all required fields
                user_content = prompt_template.format(
                    original_code=original_code, # Match prompt variable name
                    error_message=error_message, # Match prompt variable name
                    pseudocode=modified_pseudocode
                )
                # Update invoke_input for the chain
                invoke_input["original_code"] = original_code
                invoke_input["error"] = error_message
                invoke_input["pseudocode"] = modified_pseudocode

            elif error_message:
                # Case 2: Only Error is present - Use error-only retry prompt
                self.logger.info(f"Using retry prompt '{self.retry_prompt}' without pseudocode due to error: {error_message[:100]}...")
                
                prompt_template = prompts.get("retry_prompts", {}).get(self.retry_prompt, "")
                if not prompt_template:
                    prompt_template = prompts.get("retry_prompts", {}).get("generate_code_with_error")
                
                user_content = prompt_template.format(original_code=original_code, error_message=error_message)
                
                # Update invoke_input
                #invoke_input["original_code"] = original_code
                invoke_input["error_message"] = error_message

            elif modified_pseudocode:
                # Use code generation prompt with modified pseudocode
                self.logger.info(f"Using {self.evolution_strategy} for Code Generation with modified pseudocode.")
                prompt_template = prompts.get("evolution_strategies", {}).get(self.evolution_strategy, "Generate NetLogo code based on this pseudocode:\n{pseudocode}\n\nOriginal code for context:\n```netlogo\n{original_code}\n```").get("code_prompt") # Default template
                user_content = prompt_template.format(pseudocode=modified_pseudocode)
                
                # Add necessary inputs for the prompt template
                invoke_input["initial_pseudocode"] = modified_pseudocode

            else:
                self.logger.info(f"Using code generation/evolution prompt '{self.prompt_type}/{self.prompt_name}' with original code only.")
                default_code_only_template = "Evolve or generate code based on the following NetLogo code:\n```netlogo\n{original_code}\n```"
                prompt_template = prompts.get(self.prompt_type, {}).get(self.prompt_name, default_code_only_template) 
                user_content = prompt_template.format(original_code=original_code)
                
                invoke_input = {"original_code": original_code}

            # --- Construct Prompt & Chain ---
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                ("user", user_content)
            ])
            self.logger.info(f"Final prompt created. User content: {user_content}")

            chain = prompt | self.model | StrOutputParser()

            # --- Invoke LLM ---
            self.logger.info(f"Invoking LLM chain with input keys: {list(invoke_input.keys())}")
            response = chain.invoke(invoke_input) # Pass the dictionary matching prompt variables
            self.logger.info("LLM chain invocation complete.")

            # --- Extract Code ---
            match = re.search(r"```(?:netlogo)?\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                if code:
                    self.logger.info(f"Code extracted successfully. Code: {code}")
                    return code
                else:
                    self.logger.warning("Extracted code block was empty. Falling back.")
                    return original_code
            else:
                 self.logger.warning(f"Could not extract NetLogo code block from response: {response[:500]}... Falling back.")
                 return original_code # Fallback

        except Exception as e:
            self.logger.error(f"Error during code generation from state: {str(e)}", exc_info=True)
            return state.get("original_code", "") # Fallback


@gin.configurable
def create_graph_provider(model_name: str = "groq", verifier: NetLogoVerifier = None,
                          prompt_type: str = 'default_type', # Added prompt_type
                          prompt_name: str = 'default_name'): # Added prompt_name
    """
    Factory method to create a graph provider based on model name.

    Args:
        model_name: Type of model to use ("groq", "claude", "openai", or "deepseek")
        verifier: NetLogoVerifier instance for code validation
        prompt_type: Type of prompt to use for code generation (configured by Gin)
        prompt_name: Name of prompt to use for code generation (configured by Gin)

    Returns:
        Initialized GraphUnifiedProvider instance

    Raises:
        ValueError: If unsupported model type provided
    """
    # Pass prompt_type and prompt_name to the constructor
    return GraphUnifiedProvider(
        model_name=model_name,
        verifier=verifier,
        prompt_type=prompt_type,
        prompt_name=prompt_name
    )
