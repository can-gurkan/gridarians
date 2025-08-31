# Evolution Strategies in LEAR

## Overview

This document explains the text-based evolution strategies implemented in the LEAR (LLM-based Evolution of Agent Rules) framework. Text-based evolution is a two-stage process where pseudocode is first generated and then converted to NetLogo code. This approach allows for more controlled and understandable evolution of agent behaviors compared to direct code manipulation.

## Evolution Strategy Types

The framework supports multiple evolution strategies, configurable via gin:

1. **Simple Evolution**: Basic mutation strategies for simple patterns
2. **Complex Evolution**: Advanced strategies for sophisticated movement patterns

## Implementation Details

### TextBasedEvolution Class

**Location**: `src/mutation/text_based_evolution.py`

The `TextBasedEvolution` class is responsible for implementing the text-based evolution process:

```python
@gin.configurable
class TextBasedEvolution:
    def __init__(self, provider, evolution_strategy="simple"):
        self.provider = provider
        self.evolution_strategy = evolution_strategy
        
    def generate_pseudocode(self, agent_info, initial_pseudocode, original_code):
        # Retrieve appropriate prompt based on strategy
        # Generate evolved pseudocode using provider
        
    def generate_code(self, pseudocode):
        # Convert pseudocode to NetLogo code
```

### Configuration in Gin

Text-based evolution is configurable through gin:

```python
# In default.gin
TextBasedEvolution.evolution_strategy = 'simple'  # Options: 'simple', 'complex'
```

### Prompt Structure

Prompts for text-based evolution are stored in `src/utils/storeprompts.py` under the `evolution_strategies` key:

```python
prompts = {
    "evolution_strategies": {
        "simple": {
            "pseudocode_prompt": "...",
            "code_prompt": "..."
        },
        "complex": {
            "pseudocode_prompt": "...",
            "code_prompt": "..."
        }
    }
}
```

## Complex Movement Patterns

The complex evolution strategy supports sophisticated patterns including:

1. **Adaptive Exploration**: Random movements with varying distances
   ```
   If no food nearby:
     Move forward random distance (1-5)
     Turn random angle (±30°)
   ```

2. **Sensor-Responsive Behavior**: Conditional movements based on environment
   ```
   If food detected on right:
     Turn right 15°
   Else if food detected on left:
     Turn left 15°
   Else:
     Move forward 1
   ```

3. **Trigonometric Navigation**: Using sine/cosine for complex movements
   ```
   Turn angle = sin(random 360) * 30
   Forward distance = 1 + random-float 0.5
   ```

4. **Multi-Stage Movement**: Sequences of movements with different parameters
   ```
   First move forward small distance
   Then turn sharp angle
   Then move forward larger distance
   ```

## Integration with Code Generation Graph

Text-based evolution integrates with the code generation graph through nodes defined in `src/netlogo_code_generator/nodes.py`:

1. **evolve_pseudocode Node**: 
   - Creates a `TextBasedEvolution` instance
   - Generates modified pseudocode from initial pseudocode
   - Stores the instance in the graph state

2. **generate_code Node**:
   - Uses the stored `TextBasedEvolution` instance
   - Converts pseudocode to NetLogo code
   - Falls back to provider.generate_code_with_model if needed

## Usage Example

```python
from src.mutation.text_based_evolution import TextBasedEvolution
from src.graph_providers.unified_provider import UnifiedGraphProvider

# Create provider and text evolution instance
provider = UnifiedGraphProvider()
evolution = TextBasedEvolution(provider, evolution_strategy="complex")

# Generate evolved pseudocode
pseudocode = evolution.generate_pseudocode(
    agent_info,
    initial_pseudocode,
    original_code
)

# Convert pseudocode to NetLogo code
netlogo_code = evolution.generate_code(pseudocode)

# Verify the code
from src.verification.verify_netlogo import NetLogoVerifier
verifier = NetLogoVerifier()
is_safe, error_message = verifier.is_safe(netlogo_code)
```

## Best Practices

1. **Start Simple**: Begin with the "simple" evolution strategy for basic agents

2. **Progress to Complex**: Use the "complex" strategy when agents need more sophisticated behaviors

3. **Verification**: Always verify evolved code using the NetLogoVerifier

4. **Feedback Loop**: Use verification errors to guide the evolution process

5. **Custom Strategies**: Create new evolution strategies for specific requirements:
   ```python
   # In storeprompts.py
   prompts["evolution_strategies"]["custom"] = {
       "pseudocode_prompt": "...",
       "code_prompt": "..."
   }
   
   # In gin config
   TextBasedEvolution.evolution_strategy = 'custom'
   ```

## Debugging and Troubleshooting

Common issues with text-based evolution include:

1. **Invalid Generated Code**: Ensure your prompts guide the model to produce valid NetLogo syntax

2. **Missing Evolution Strategy**: Verify the strategy exists in storeprompts.py

3. **Provider Compatibility**: Make sure your provider supports the text generation required

4. **Fallback Issues**: Check log messages when the system falls back to alternative code generation methods