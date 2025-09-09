"""
Node implementations for the NetLogo code generation graph.
"""

import logging
from typing import Dict, Any

from src.netlogo_code_generator.state import GenerationState
from src.mutation.text_based_evolution import TextBasedEvolution
from src.graph_providers.base import GraphProviderBase
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.logging import get_logger

# Get the global logger instance
logger = get_logger()


def evolve_pseudocode(
    state: GenerationState,
    provider: GraphProviderBase,
) -> GenerationState:
    """
    Generate modified pseudocode if text-based evolution is enabled.

    Args:
        state: Current generation state
        provider: Model provider for text generation
        use_text_evolution: Whether to use text-based evolution

    Returns:
        Updated generation state with modified pseudocode
    """
    logger.info(f"NODE: evolve_pseudocode")
    use_text_evolution = state.get("use_text_evolution", False)
    logger.info(f"Evolving pseudocode, use_text_evolution: {use_text_evolution}")

    # Log truncated versions of potentially large strings
    original_code_sample = state.get('original_code', '')
    initial_pseudocode_sample = state.get('initial_pseudocode', '')
    logger.info(f"Original code (sample): {original_code_sample}")
    logger.info(f"Initial pseudocode (sample): {initial_pseudocode_sample}")
    
    if not state["use_text_evolution"]:
        logger.info("Text evolution disabled, skipping pseudocode generation")
        return state

    logger.info("Text evolution enabled, generating pseudocode")
    text_evolution = TextBasedEvolution(provider)
    modified_pseudocode = text_evolution.generate_pseudocode( 
        state["agent_info"], 
        state["initial_pseudocode"], 
        state["original_code"]
    )
    
    # Log truncated version of modified pseudocode
    modified_pseudocode_sample = modified_pseudocode
    logger.info(f"Generated modified pseudocode (sample): \n{modified_pseudocode_sample}")
    
    state["modified_pseudocode"] = modified_pseudocode
    return state

def generate_code(
    state: GenerationState,
    provider: GraphProviderBase
) -> GenerationState:
    """
    Generate code using the provider.

    Args:
        state: Current generation state
        provider: Model provider for code generation

    Returns:
        Updated generation state with new code
    """
    retry_count = state.get('retry_count', 0)
    error_msg = state.get('error_message', None)
    logger.info(f"NODE: generate_code - retry_count: {retry_count}, error_message: {error_msg}")
    
    try:
        # Check if we have both modified_pseudocode and error_message for retry scenario
        if state.get("modified_pseudocode") and state.get("error_message"):
            logger.info("Using both modified_pseudocode and error_message for code generation")
        elif state.get("modified_pseudocode"):
             logger.info("Using modified_pseudocode for code generation")
        elif state.get("error_message"):
             logger.info("Using error_message for code generation retry")
        else:
             logger.info("Generating code based on initial state (no pseudocode modification or error)")

        # Call the provider using the new state-based interface
        new_code = provider.generate_code_from_state(state)

    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        new_code = state["current_code"]
    
    code_sample = new_code
    logger.info(f"Generated new code (sample): {code_sample}")
    return {**state, "current_code": new_code}

def verify_code(
    state: GenerationState, 
    verifier: NetLogoVerifier
) -> GenerationState:
    """
    Verify the generated code.
    
    Args:
        state: Current generation state
        verifier: NetLogo verifier for code validation
        
    Returns:
        Updated generation state with verification results
    """
    logger.info(f"NODE: verify_code - current retry count: {state.get('retry_count', 0)}")
    
    is_safe, error_message = verifier.is_safe(state["current_code"])
    error_msg_sample = error_message if error_message else None
    logger.info(f"Verification result: is_safe={is_safe}, error_message={error_msg_sample}")
    
    result = {
        **state, 
        "error_message": None if is_safe else error_message
    }
    
    # If verification failed, increment retry count and update initial_pseudocode
    if result["error_message"]:
        logger.info(f"Verification failed with error: {error_msg_sample}, incrementing retry count")
        result["retry_count"] = state["retry_count"] + 1
        
        # Update initial_pseudocode with modified_pseudocode if available
        if state.get("modified_pseudocode"):
            logger.info("Updating initial_pseudocode with modified_pseudocode")
            result["initial_pseudocode"] = state["modified_pseudocode"]
        else:
            logger.info("Updating code with Error")
    else:
        logger.info("Verification successful")
    
    return result

def should_retry(state: GenerationState, max_attempts: int = 5) -> str:
    logger.info(f"Checking if should retry, retry_count: {state['retry_count']}, max_attempts: {max_attempts}, error_message: {state['error_message']}")
    """
    Determine if code generation should be retried.
    
    Args:
        state: Current generation state
        max_attempts: Maximum number of retry attempts
        
    Returns:
        "retry" if should retry, "end" otherwise
    """
    should_retry_value = "retry" if state["error_message"] and state["retry_count"] < max_attempts else "end"
    logger.info(f"Should retry decision: {should_retry_value}")
    return should_retry_value

