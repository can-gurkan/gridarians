from typing import Union
import os
from pathlib import Path
# Ensure the script is run from the correct directory

# Add parent directory to path
import sys
import os
import sys
from pathlib import Path

# Add project root directory to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

print("Current working directory:", os.getcwd())

from src.utils.config import load_config
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils import logging
from src.netlogo_code_generator.graph import NetLogoCodeGenerator
from src.graph_providers.unified_provider import create_graph_provider

config = load_config()
logger = logging.get_logger()
logger.info("Loading NetLogoVerifier...")
verifier = NetLogoVerifier()
logger.info("NetLogoVerifier loaded.")

def get_graph_provider(model_type: str):
    """Get the appropriate Graph provider based on model type."""
    return create_graph_provider(model_type, verifier)

def mutate_code(agent_info: list, model_type: str = "groq", use_text_evolution: bool = False) -> tuple:
    """
    Generate evolved NetLogo code using graph-based evolution.
    
    Returns:
        tuple: (new_rule, text) containing the new rule and the descriptive text (pseudocode)
    """
    logger.info(f"Starting code generation with model type: {model_type}, use_text_evolution: {use_text_evolution}")

    
    # Extract current text from agent_info if available (at index 5)
    current_text = ""
    if len(agent_info) > 5:
        current_text = agent_info[5]
    
    provider = get_graph_provider(model_type)
    graph_generator = NetLogoCodeGenerator(provider, verifier)
    result = graph_generator.generate_code(agent_info, current_text, use_text_evolution)
    
    # Check if result is a tuple (new_rule, modified_pseudocode)
    if isinstance(result, tuple) and len(result) == 2:
        new_rule, text = result
    else:
        new_rule = result
        text = current_text
    
    logger.info(f"Graph-based code generation complete. Result code: {new_rule}")
    logger.info(f"Text: {text}")
    
    return (new_rule, text)



if __name__ == "__main__":
    # Example usage
    agent_info = [
        "original_code",
        "current_code",
        "agent_info",
        None,
        0,
        "initial_pseudocode"
    ]
    
    model_type = "groq"  # or any other model type
    use_text_evolution = True
    
    new_rule, text = mutate_code(agent_info, model_type, use_text_evolution)
    print(f"New Rule: {new_rule}")
    print(f"Text: {text}")