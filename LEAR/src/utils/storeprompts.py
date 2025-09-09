import os
import yaml

"""Collection of prompts used throughout the LEAR system

PROMPT STRUCTURE:
- Static prompt definitions (like strategies, etc.) are loaded from YAML files in `src/utils/prompts/static_definitions/`.
- Dynamic prompt definitions (base prompts with variations) are loaded from YAML files in `src/utils/prompts/definitions/`.
- Each dynamic YAML file defines a base prompt and optional components (examples, comment instructions).
- The script automatically constructs zero-shot, one-shot, two-shot, and commented variations for dynamic prompts.
"""

PROMPT_DEFINITIONS_DIR = os.path.join(os.path.dirname(__file__), "prompts", "definitions")
STATIC_PROMPT_DEFINITIONS_DIR = os.path.join(os.path.dirname(__file__), "prompts", "static_definitions")

def load_dynamic_prompts(directory: str) -> dict:
    """Loads and constructs dynamic prompt variations from YAML files in the specified directory."""
    loaded_prompts = {}
    if not os.path.exists(directory):
        print(f"Warning: Dynamic prompt definitions directory not found: {directory}")
        return loaded_prompts

    for filename in os.listdir(directory):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)

                # Expect 'name' and other prompt components at top level
                if not data or not isinstance(data, dict) or 'name' not in data:
                     print(f"Warning: Skipping invalid dynamic YAML file {filename}: Must be a dictionary and contain a 'name' top-level key.")
                     continue

                # Use pop to get name and leave the rest of the data as prompt components
                name = data.pop('name')
                prompt_data = data # The rest of the keys are the prompt data

                if "base_prompt" not in prompt_data:
                    print(f"Warning: Skipping invalid dynamic YAML file {filename}: Missing 'base_prompt' key for '{name}'")
                    continue

                base = prompt_data["base_prompt"]
                one_shot = prompt_data.get("one_shot_example", "")
                two_shot = prompt_data.get("two_shot_example", "")
                comment_instr = prompt_data.get("comment_instruction", "")

                prompt_group = {
                    "zero_shot_code": base,
                    "one_shot_code": base + one_shot,
                    "two_shot_code": base + one_shot + two_shot,
                    "zero_shot_code_wcomments": base + comment_instr,
                    "one_shot_code_wcomments": base + one_shot + comment_instr,
                    "two_shot_code_wcomments": base + one_shot + two_shot + comment_instr,
                }
                loaded_prompts[name] = prompt_group

            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {filename}: {e}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    return loaded_prompts

def load_static_definitions(directory: str) -> dict:
    """Loads static prompt definitions from YAML files in the specified directory."""
    loaded_prompts = {}
    if not os.path.exists(directory):
        print(f"Warning: Static prompt definitions directory not found: {directory}")
        return loaded_prompts

    for filename in os.listdir(directory):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r') as f:
                    data = yaml.safe_load(f)

                # Expect 'name' and 'value' keys
                if not data or not isinstance(data, dict) or 'name' not in data or 'value' not in data:
                     print(f"Warning: Skipping invalid static YAML file {filename}: Should contain 'name' and 'value' top-level keys.")
                     continue

                name = data['name']
                value = data['value']

                if not isinstance(value, dict):
                     print(f"Warning: Skipping invalid static YAML file {filename}: 'value' should be a dictionary for '{name}'.")
                     continue

                # Add the value dictionary under the specified name
                if name in loaded_prompts:
                     print(f"Warning: Duplicate static definition name '{name}' found in {filename}. Overwriting.")
                loaded_prompts[name] = value

            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {filename}: {e}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    return loaded_prompts


# Load static definitions first
prompts = load_static_definitions(STATIC_PROMPT_DEFINITIONS_DIR)

# Load dynamic prompts and merge them, potentially overwriting static ones if names clash
dynamic_prompts = load_dynamic_prompts(PROMPT_DEFINITIONS_DIR)
prompts.update(dynamic_prompts)

# Example usage (optional, for testing)
if __name__ == "__main__":
    import json
    print(f"Loaded {len(prompts)} prompt groups.")
    # print(json.dumps(prompts, indent=2))
    if 'collection_simple' in prompts:
        print("\nExample: collection_simple zero_shot_code:")
        print(prompts['collection_simple']['zero_shot_code'][:200] + "...") # Print first 200 chars
    if 'evolution_strategies' in prompts and 'simple' in prompts['evolution_strategies']:
         print("\nExample: evolution_strategies simple pseudocode_prompt:")
         print(prompts['evolution_strategies']['simple']['pseudocode_prompt'][:200] + "...")
