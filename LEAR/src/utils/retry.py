from typing import Callable
import logging
import gin
from src.verification.verify_netlogo import NetLogoVerifier

@gin.configurable
class CodeRetryHandler:
    def __init__(self, verifier: NetLogoVerifier, max_attempts: int = 5):
        """Initialize the retry handler.
        
        Args:
            verifier: NetLogoVerifier instance for code validation
            max_attempts: Maximum number of retry attempts before reverting
        """
        self.verifier = verifier
        self.max_attempts = max_attempts
        self.error_prompt = """
            The generated NetLogo code has an error:
            Code: {original_code}
            Error: {error_message}
            
            Please fix the code following these rules:
            1. Use only fd, rt, or lt commands with numbers or 'random N'
            2. Keep expressions simple - avoid complex arithmetic
            3. Use positive numbers only
            4. Each command must be followed by either:
               - A single number (e.g., "fd 1")
               - random N (e.g., "rt random 30")
               - random-float N (e.g., "lt random-float 45")
            
            Return ONLY the fixed NetLogo code with no explanations.
            """

    def execute_with_retry(
        self,
        original_code: str,
        generate_fn: Callable,
        agent_info: list = None,
        use_text_evolution: bool = False
    ) -> str:
        """Execute code generation with retry logic.
        
        Args:
            original_code: Original NetLogo code to fall back to
            generate_fn: Function that generates new code
            agent_info: Agent information for code generation
            
        Returns:
            str: Valid NetLogo code or original code if retries exhausted
        """
        attempts = 0
        current_code = None

        while attempts < self.max_attempts:
            try:
                # Generate new code if first attempt or retry with error context
                if current_code is None:
                    current_code = generate_fn(agent_info=agent_info, use_text_evolution=use_text_evolution)
                else:
                    # Retry with error context
                    error_prompt = self.error_prompt.format(
                        code=current_code,
                        error=error_message
                    )
                    current_code = generate_fn(agent_info=agent_info, use_text_evolution=use_text_evolution, error_prompt=error_prompt)

                # Verify the generated/fixed code
                is_safe, error_message = self.verifier.is_safe(current_code)
                
                if is_safe:
                    logging.info(f"Successfully generated valid code after {attempts + 1} attempts")
                    return current_code
                
                logging.warning(f"Attempt {attempts + 1} failed: {error_message}")
                attempts += 1
                
            except Exception as e:
                logging.error(f"Error during retry attempt {attempts + 1}: {str(e)}")
                attempts += 1

        logging.warning(f"Failed to generate valid code after {self.max_attempts} attempts. Reverting to original code.")
        return original_code
