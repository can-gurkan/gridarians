"""
State definitions for the NetLogo code generation graph.
"""

from typing import Optional, List, TypedDict

class GenerationState(TypedDict):
    """
    State for the NetLogo code generation graph.
    
    Attributes:
        original_code: The original NetLogo code
        current_code: The current generated NetLogo code
        agent_info: List containing agent state and environment information
        error_message: Optional error message from verification
        retry_count: Number of retry attempts
        use_text_evolution: Whether to use text-based evolution
        modified_pseudocode: Optional modified pseudocode for code generation
        initial_pseudocode: Initial pseudocode provided as input
    """
    original_code: str
    current_code: str
    agent_info: List
    error_message: Optional[str]
    retry_count: int
    use_text_evolution: bool
    initial_pseudocode: str
    modified_pseudocode: Optional[str]
    
