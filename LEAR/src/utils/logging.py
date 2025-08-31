import logging
import os

_logger = None  # Initialize the global logger variable

def setup_logging(log_file_path='../../Logs/debug.log', level=logging.DEBUG):
    """Sets up logging configuration."""
    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    global _logger
    _logger = logging.getLogger('lear_app')
    _logger.setLevel(level)
    _logger.propagate = False  # Prevent propagation to avoid recursive logging

    # Remove any existing handlers to avoid duplicates on re-initialization
    if _logger.handlers:
        _logger.handlers.clear()

    # Create file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    return _logger

def get_logger():
    """Returns the global logger instance.
    
    If the logger hasn't been initialized yet, it will be initialized with default settings.
    
    Returns:
        The global logger instance
    """
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger
