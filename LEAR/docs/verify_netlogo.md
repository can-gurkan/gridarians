# NetLogo Verification System

## Overview

The NetLogo Verification System is a critical component of the LEAR (LLM-based Evolution of Agent Rules) framework that ensures generated NetLogo code is safe, syntactically correct, and follows best practices. This document provides an overview of how the verifier works, how to use it, and its integration with the code generation process.

## Core Components

### `NetLogoVerifier` Class

The main verification class that provides comprehensive validation for NetLogo code.

**Location**: `src/verification/verify_netlogo.py`

**Key Methods**:
- `is_safe(code: str) -> Tuple[bool, str]`: Main validation method that returns whether code is safe and an error message if not
- `validate(code: str) -> ValidationResult`: Detailed validation with multiple errors
- `measure_complexity(code: str) -> CodeComplexity`: Measures code complexity on a scale from SIMPLE to EXPERT

### `ValidationResult` Class

Contains the results of a validation check, including:
- `is_valid`: Boolean indicating if code passed validation
- `errors`: List of `ValidationError` objects

### `ValidationError` Class

Represents specific validation errors with:
- `message`: Error description
- `line_number`: Line where error occurred
- `code_snippet`: Context around error
- `severity`: WARNING or ERROR

### `CodeComplexity` Enum

Defines complexity levels for NetLogo code:
- SIMPLE (1): Basic movement without conditions
- BASIC (2): Simple conditionals
- MODERATE (3): Multiple conditions, basic sensing
- ADVANCED (4): Complex conditions, environment awareness
- COMPLEX (5): Advanced sensing, memory usage
- SOPHISTICATED (6): Multiple strategies, adaptation
- EXPERT (7): Optimal pathfinding, complex decision making

## Validation Checks

The verifier performs several types of checks:

1. **Dangerous Primitives**: Prevents use of primitives that could harm the simulation or create security risks (`die`, `ask`, `python`, etc.)

2. **Bracket Balance**: Ensures all brackets are properly balanced and nested

3. **Movement Commands**: Verifies code contains at least one movement command (`fd`, `rt`, `lt`, `bk`)

4. **Command Syntax**: Validates syntax of NetLogo commands and control structures

5. **Value Ranges**: Ensures numeric values are within acceptable ranges (default -1000 to 1000)

## Integration with Code Generation

The verifier is integrated into the code generation process through the following components:

### In `netlogo_code_generator/nodes.py`:

- **`verify_code` node**: Verifies generated code using the `NetLogoVerifier.is_safe()` method
- If verification fails, increments retry count and includes error message for the next generation attempt
- Updates initial pseudocode with modified pseudocode if available

### In `graph_providers/base.py`:

- **`GraphProviderBase` class**: Takes a `NetLogoVerifier` instance in its constructor
- Uses verifier for code validation in the generation process
- Handles error messages to guide retry attempts when verification fails

## Allowed vs. Restricted Features

### Allowed NetLogo Primitives

**Commands**:
- Movement: `fd`, `forward`, `rt`, `right`, `lt`, `left`, `bk`, `back`
- Control: `if`, `ifelse`, `ifelse-value`
- Variables: `set`, `let`

**Reporters**:
- Random: `random`, `random-float`
- Math: `sin`, `cos`, `tan`
- Lists: `item`, `count`, `length`, `position`
- Agent properties: `xcor`, `ycor`, `heading`
- Agent sensing: `any?`, `in-radius`, `distance`, `towards`
- Logic: `and`, `or`, `not`

### Dangerous/Restricted Primitives

- Agent lifecycle: `die`, `kill`, `create`, `hatch`, `sprout`
- Agent control: `ask`, `of`, `with`
- Code execution: `run`, `runresult`
- File operations: `file`, `import`, `export`
- External code: `python`, `js`
- Simulation control: `clear`, `reset`, `setup`, `go`
- Loops: `while`, `loop`, `repeat`, `forever`
- Breeds: `breed`, `create-ordered`
- Network/extension: `hubnet`, `gis`, `sql`
- System operations: `wait`, `beep`, `system`
- Global state: `clear-all`, `reset-ticks`

## Usage Example

```python
from src.verification.verify_netlogo import NetLogoVerifier

# Create verifier with default configuration
verifier = NetLogoVerifier()

# Simple verification (returns boolean and error message)
is_safe, error_message = verifier.is_safe("fd random 10 rt 90")
if not is_safe:
    print(f"Code is not safe: {error_message}")

# Detailed validation (returns ValidationResult with list of errors)
result = verifier.validate("ifelse random 10 > 5 [fd 1] [rt 90 fd 2]")
if not result.is_valid:
    for error in result.errors:
        print(error)

# Measure code complexity
complexity = verifier.measure_complexity("ifelse random 10 > 5 [fd 1] [rt 90 fd 2]")
print(f"Code complexity: {complexity.name} ({complexity.value})")
```

## Configuration Options

The `NetLogoVerifier` can be configured with the following options:

```python
config = {
    "max_code_length": 10000,  # Maximum allowed length of code
    "max_value": 1000,         # Maximum allowed numeric value
    "min_value": -1000         # Minimum allowed numeric value
}

verifier = NetLogoVerifier(config)
```

## Best Practices

1. **Always Validate Before Execution**: Never run NetLogo code generated by LLMs without verification

2. **Handle Errors Appropriately**: Use error messages to guide the code generation process in a feedback loop

3. **Check Complexity**: Use the complexity measure to ensure generated code meets desired sophistication level

4. **Test Verification**: Regularly test the verifier with new patterns to ensure it remains effective

## Common Error Messages

- "Dangerous primitive found: <primitive>"
- "Unmatched closing bracket"
- "Unclosed bracket: <bracket>"
- "No movement commands found"
- "Invalid value for <command>: <value>"
- "Value too large: <value>"
- "Invalid or unsupported condition: <condition>"

## Integration with Text-Based Evolution

When using text-based evolution, the verification process becomes particularly important as it ensures that evolved code remains safe and syntactically correct.

The typical workflow is:
1. Generate initial pseudocode
2. Evolve pseudocode
3. Convert pseudocode to NetLogo code
4. Verify the generated code
5. If verification fails, retry with error feedback