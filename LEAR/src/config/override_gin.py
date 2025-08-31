import gin
import os

def write_prompt_config(prompt_type: str, prompt_name: str):
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "default.gin")
    gin.clear_config()  # clear previous binding
    gin.parse_config_file(os.path.abspath(config_path))

    gin.bind_parameter("create_graph_provider.prompt_type", prompt_type)
    gin.bind_parameter("create_graph_provider.prompt_name", prompt_name)