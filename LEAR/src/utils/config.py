# config.py
from dotenv import load_dotenv
import os
import gin

# Import configurable modules before parsing GIN config
import src.generators.base
import src.graph_providers.base
import src.graph_providers.unified_provider
import src.netlogo_code_generator.nodes

def load_config():
    """Load environment variables from .env file and GIN configuration"""
    load_dotenv()
    
    # Required environment variables
    required_vars = {
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
    }
    
    # Check for missing variables
    missing = [key for key, value in required_vars.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    # Load configurations from gin file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config", "default.gin")
    gin.parse_config_file(config_path)
        
    return required_vars

# Example usage
if __name__ == "__main__":
    try:
        config = load_config()
        print("Environment variables loaded successfully!")
    except ValueError as e:
        print(f"Error: {e}")
