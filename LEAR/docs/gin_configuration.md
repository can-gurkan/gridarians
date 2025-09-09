# GIN Configuration for LangGraph-Based Providers

This document explains how to use the GIN configuration system to control parameters for LangGraph-based providers in the LEAR project.

## Overview

The LEAR project uses Google's GIN configuration system to make it easy to control parameters without modifying code. The configuration is defined in `src/config/default.gin` and is loaded when the application starts.

## Key Configuration Parameters

### Model Selection

```gin
# Default model selection
create_graph_provider.model_name = "groq"  # Options: "groq", "claude", "openai", "deepseek"
```

### Temperature and Token Limits

```gin
# Model-specific configurations
GraphUnifiedProvider.temperature = 0.65  # Controls randomness (0.0 to 1.0)
GraphUnifiedProvider.max_tokens = 1000   # Maximum tokens to generate
```

### Model Names

```gin
# Model-specific name configurations
GraphUnifiedProvider.groq_model_name = "llama-3.3-70b-versatile"
GraphUnifiedProvider.claude_model_name = "claude-3-5-sonnet-20241022"
GraphUnifiedProvider.openai_model_name = "gpt-4o"
GraphUnifiedProvider.deepseek_model_name = "deepseek-chat"
```

### Retry Configuration

```gin
# Retry configuration
GraphProviderBase.retry_max_attempts = 5  # Maximum number of retry attempts
should_retry.max_attempts = 5             # Should match the above value
```

### Text Evolution

```gin
# LangGraph node configurations
evolve_pseudocode.use_text_evolution = False  # Set to True to enable text-based evolution
TextBasedEvolution.evolution_strategy = 'simple'  # Options: 'simple', 'complex'
```

The `evolution_strategy` parameter controls which prompt strategy is used for text-based evolution:
- 'simple': Basic incremental evolution with minimal changes (default)
- 'complex': Advanced evolution with sophisticated patterns including trigonometric functions and multi-stage movements

### Prompt Selection

```gin
# Prompt configuration
get_base_prompt.model_prompt = 'groq_prompt2'  # Prompt template to use
```

## Examples

### Switching to Claude

To switch from Groq to Claude:

```gin
# Default model selection
create_graph_provider.model_name = "claude"
```

### Adjusting Temperature

To make the generation more deterministic:

```gin
# Model-specific configurations
GraphUnifiedProvider.temperature = 0.2  # Lower values are more deterministic
```

### Changing Model Versions

To use a different model version:

```gin
# Model-specific name configurations
GraphUnifiedProvider.groq_model_name = "llama-3.3-8b-versatile"
```

### Enabling Text Evolution

To enable text-based evolution:

```gin
# LangGraph node configurations
evolve_pseudocode.use_text_evolution = True
```

## How to Modify Configuration

You can modify the configuration in two ways:

1. **Edit the GIN file directly**: Open `src/config/default.gin` and modify the parameters.

2. **Programmatically**: Use the GIN API to modify parameters at runtime:

```python
import gin

# Override a parameter
gin.bind_parameter('GraphUnifiedProvider.temperature', 0.8)
```

## Troubleshooting

If you encounter errors related to GIN configuration:

1. **Missing configurable**: Make sure the class or function is decorated with `@gin.configurable`.
2. **Import errors**: Ensure that the module containing the configurable class or function is imported before parsing the GIN configuration.
3. **Parameter type mismatch**: Check that the parameter value in the GIN configuration matches the expected type.
