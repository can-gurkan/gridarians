"""
Main graph implementation for NetLogo code generation.
"""

from typing import List
from langgraph.graph import StateGraph, END, START

from src.generators.base import BaseCodeGenerator
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.logging import get_logger
from src.graph_providers.base import GraphProviderBase
from src.netlogo_code_generator.state import GenerationState
from src.netlogo_code_generator.nodes import (
    evolve_pseudocode,
    generate_code,
    verify_code,
    should_retry)

class NetLogoCodeGenerator(BaseCodeGenerator):
    """
    NetLogo code generator using LangGraph for structured generation flow.
    """
    
    def __init__(self, provider: GraphProviderBase, verifier: NetLogoVerifier):
        """
        Initialize with graph provider and verifier.
        
        Args:
            provider: GraphProviderBase implementation
            verifier: NetLogoVerifier instance for code validation
        """
        super().__init__(verifier)
        self.provider = provider
        self.logger = get_logger()
        
    def _build_graph(self) -> StateGraph:
        """
        Build and return the LangGraph for code generation.
        
        Returns:
            Compiled StateGraph for code generation
        """
        # Create the graph
        workflow = StateGraph(GenerationState)
        
        # Add nodes with bound parameters
        workflow.add_node(
            "evolve_pseudocode", 
            lambda state: evolve_pseudocode(state, self.provider)
        )
        workflow.add_node(
            "generate_code", 
            lambda state: generate_code(state, self.provider)
        )
        workflow.add_node(
            "verify_code", 
            lambda state: verify_code(state, self.verifier)
        )
        
        # Define edges
        # workflow.add_edge(START, "evolve_pseudocode")
        workflow.add_edge("evolve_pseudocode", "generate_code")
        workflow.add_edge("generate_code", "verify_code")
        
        workflow.add_conditional_edges("verify_code", should_retry, {"retry": "generate_code", "end": END})
                
        workflow.set_entry_point("evolve_pseudocode")
        
        self.logger.info("Compiling the graph...")
        return workflow.compile()
        
    def generate_code(self, agent_info: List, initial_pseudocode: str, use_text_evolution: bool = False) -> tuple:
        """
        Generate code using LangGraph with the same interface as existing generators.

        Args:
            agent_info: List containing agent state and environment information
            initial_pseudocode: Initial pseudocode or text to guide the code generation
            use_text_evolution: Whether to use text-based evolution approach

        Returns:
            Tuple of (generated_code, text) where generated_code is the NetLogo code
            and text is the descriptive text or pseudocode
        """
        self.logger.info(f"Starting code generation with model type: {self.provider.__class__.__name__}, use_text_evolution: {use_text_evolution}")
        
        # Validate input format
        self.logger.info(f"Validating input format: {agent_info}")
        is_valid, error_msg = self.validate_input(agent_info)
        
        if not is_valid:
            self.logger.error(f"Invalid input: {error_msg}")
            return (agent_info[0], initial_pseudocode)

        self.logger.info(f"Input validation successful")
        self.logger.info(f"Original code: {agent_info[0]}")
        self.logger.info(f"Initial text: {initial_pseudocode}")

        # Initial state
        self.logger.info("Creating initial state")
        initial_state = {
            "original_code": agent_info[0],
            "current_code": agent_info[0],
            "agent_info": agent_info,
            "error_message": None,
            "retry_count": 0,
            "use_text_evolution": use_text_evolution,
            "modified_pseudocode": None,
            "initial_pseudocode": initial_pseudocode
        }

        # Build and compile the graph
        self.logger.info("Building and compiling the graph")
        app = self._build_graph()

        # Run the graph
        self.logger.info("Invoking the graph with initial state")
        final_state = app.invoke(initial_state)
        self.logger.info(f"Graph execution complete, error_message: {final_state['error_message']}, retry_count: {final_state['retry_count']}")

        # Return the result or original code if failed
        if final_state["error_message"] is None:
            self.logger.info("Code generation successful, returning new code and text")
            # Get the final text - either the modified pseudocode or the initial one if no modification was done
            final_text = final_state.get("modified_pseudocode", initial_pseudocode) or initial_pseudocode
            return (final_state["current_code"], final_text)
        else:
            self.logger.error(f"Code generation failed with error: {final_state['error_message']}, returning original code and text")
            return (agent_info[0], initial_pseudocode)
