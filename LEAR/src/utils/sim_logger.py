import os
import datetime
import logging
import json
from collections import ChainMap

_logger_instance = None  # Global variable to hold the logger instance

def initialize_logger(experiment_name):
    """Reinitialize the logger (called every time NetLogo setup runs)."""

    global _logger_instance

    _logger_instance = NetLogoLogger(experiment_name)  # Create a new logger instance
    
    return _logger_instance

def get_logger():
    """Retrieve the current logger instance."""


    if _logger_instance is None:
        raise ValueError("Logger has not been initialized. Call initialize_logger() first.")

    return _logger_instance

class NetLogoLogger:
    def __init__(self, experiment_name, base_log_directory="../../Logs"):
        """Initialize a new logger instance."""
        self.base_log_directory = base_log_directory

        # Create a new folder with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
        self.log_directory = os.path.join(self.base_log_directory, experiment_name, timestamp)

        try:
            os.makedirs(self.log_directory, exist_ok=True)
            print(f"Log directory created at: {self.log_directory}")  # Debugging statement
        except Exception as e:
            print(f"Failed to create log directory: {e}")  # Prints error if directory creation fails

        # Define log file path
        self.log_file = os.path.join(self.log_directory, "simulation.log")
        self.json_file = os.path.join(self.log_directory, "generation_output.json")

        # Setup logger
        self.logger = logging.getLogger(f"NetLogoLogger_{timestamp}")
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        # json output list
        self.generation_data = []

    def log_initial_parameters(self, params):
        """Log simulation parameters at the start."""

        params_dict = dict(params)
        self.logger.info(f"Simulation Parameters: {params_dict}")

    def log_base_prompt(self, prompt):
        """Log the LLM base prompt."""
        self.logger.info(f"Base Prompt: {prompt}")

    def log_generation(self, data):
        """Log per-generation evolution stats."""

        master_dict = {}

        for table in data:
            if isinstance(table, str):  # Check if table is a string (in JSON format)
                table = json.loads(table)  # Convert JSON string to dictionary

            master_dict |= table  # merge dictionaries

        self.generation_data.append(master_dict)

        # Save to json file
        with open(self.json_file, "w") as f:
            json.dump(self.generation_data, f, indent=4)
