class LEARPrompts:
    """Collection of prompts used throughout the LEAR system"""

    def __init__(self):
        # Evolution goals used in text-based evolution
        self.evolution_goals = (
            "Optimize movement for food, balance exploration, keep commands simple."
        )

        # Chain of thought prompt for langchain providers
        self.langchain_cot_system = "You are a NetLogo expert."
        self.langchain_cot_template = """Evolve code:\n{original_code}\n\nInputs: {inputs}"""

        self.evolution_performance = "Energy: {energy}, Food: {food}, Lifetime: {lifetime}, Efficiency: {efficiency:.2f}"
        self.evolution_movement_pattern = "moves {direction} {value}"
        self.evolution_movement_pattern_none = "no movement"
        self.evolution_goals_prompt = (
            "Optimize movement for food, balance exploration, keep commands simple."
        )

        # Code analysis prompts
        self.code_analysis_system_message = """You are a NetLogo expert specializing in analyzing agent behavior code. 
Provide clear, natural language descriptions of NetLogo code patterns, explaining what the code does in simple terms."""

        self.code_analysis_user_message = """Analyze this NetLogo code and describe what it does:
{original_code}

Focus on:
1. Movement patterns and conditions
2. Decision-making logic
3. Use of variables and reporters
4. Overall behavior strategy

Provide a clear, concise description that a non-programmer could understand."""

        # LLM-based explanation prompts
        self.explanation_system_message = """You are a NetLogo expert analyzing agent behavior. Provide clear, concise explanations of agent movement patterns and their effectiveness in collecting food."""

        self.explanation_user_message = """Analyze the agent's behavior and environment:

Current Movement: {movement_pattern}
Performance: {performance_metrics}
Previous Movement (if any): {parent_pattern}

Explain:
1. How effective is the current movement pattern?
2. How well does it respond to the environment?
3. What improvements could make it more effective?

Keep the explanation concise and focused on behavior analysis."""

        self.langchain_system_message = "You are a NetLogo expert."
        self.langchain_user_message_evolution = (
            """Evolve code:\n{original_code}\n\nAnalysis: {evolution_description}"""
        )

        self.langchain_user_message = """Evolve code:\n{original_code}\n\nInputs: {inputs}"""

        self.groq_prompt = """You are an expert NetLogo movement code generator. Generate code:
- Movement: fd/forward, rt/right, lt/left
- Reporters: random, random-float, sin, cos
Format: [command] [number | reporter]

INPUT CONTEXT:
- Current rule: {}
- Food: {} (0 = no food, lower = closer)

Generate ONLY the code."""

        self.groq_prompt1 = """Modify NetLogo movement rule:
1. Use only existing variables
2. Use only fd, rt, lt
3. Consider food distances (0 = no food)
4. Only movement commands
5. < 100 chars, no comments

rule: {} 
input: {}"""

        self.groq_prompt2 = """You are an expert NetLogo coder. You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. Improve the given agent movement code following these precise specifications:

INPUT CONTEXT:
- Current rule: {}
- Food sensor readings: {}
  - Input list contains three values representing distances to food in three cone regions of 20 degrees each
  - The first item in the input list is the distance to the nearest food in the left cone, the second is the right cone, and the third is the front cone
  - Each value encodes the distance to nearest food source where a value of 0 indicates no food
  - Non-zero lower values indicate closer food
  - Use these to inform movement strategy

CONSTRAINTS:
1. Do not include code to kill or control any other agents
2. Do not include code to interact with the environment
3. Do not include code to change the environment
4. Do not include code to create new agents
5. Do not include code to create new food sources
6. Do not include code to change the rules of the simulation

EXAMPLES OF VALID PATTERNS:
Current Rule: fd 1 rt random 45 fd 2 lt 30
Valid: ifelse item 0 input != 0 [rt 15 fd 0.5] [rt random 30 lt random 30 fd 5]
Why: Turns right and goes forward a little to reach food if the first element of input list contains a non-zero value, else moves forward in big steps and turns randomly to explore

INVALID EXAMPLES:
❌ ask turtle 1 [die]
❌ ask other turtles [die]
❌ set energy 100
❌ hatch-food 5
❌ clear-all

STRATEGIC GOALS:
1. Balance exploration and food-seeking behavior
2. Respond to sensor readings intelligently
3. Combine different movement patterns

Generate ONLY the movement code. Code must be runnable in NetLogo in the context of a turtle."""


        self.groq_prompt = """You are an expert NetLogo movement code generator. Generate code:
- Movement: fd/forward, rt/right, lt/left
- Reporters: random, random-float, sin, cos
Format: [command] [number | reporter]

INPUT CONTEXT:
- Current rule: {}
- Food: {} (0 = no food, lower = closer)

Generate ONLY the code."""

        self.groq_prompt1 = """Modify NetLogo movement rule:
1. Use only existing variables
2. Use only fd, rt, lt
3. Consider food distances (0 = no food)
4. Only movement commands
5. < 100 chars, no comments

rule: {} 
input: {}"""
        
        self.groq_prompt_leif = """You are an expert NetLogo coder. You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible and avoid running into poison deposits. Improve the given agent movement code following these precise specifications:

INPUT CONTEXT:
- Current rule: {}
- The agent has access to two variables containing information about its environment: {}
  - food-observations is a list that contains three elements representing distances to food in three cone regions of 20 degrees each.
  - poison-observations is a list that contains three elements representing distances to poison in three cone regions of 20 degrees each.
  - The first item in these lists gives the distances to the nearest food or poison in the left cone, the second is the right cone, and the third is the front cone
  - Each value encodes the distance to nearest food or poison source where a value of 0 indicates no food or poison
  - Non-zero lower values indicate closer to food or poison
  - Use these to inform movement strategy

CONSTRAINTS:
1. Do not include code to kill or control any other agents
2. Do not include code to interact with the environment
3. Do not include code to change the environment
4. Do not include code to create new agents
5. Do not include code to create new food sources
6. Do not include code to change the rules of the simulation

EXAMPLES OF VALID PATTERNS:
Current Rule: fd 1 rt random 45 fd 2 lt 30
Valid: ifelse item 0 input != 0 [rt 15 fd 0.5] [rt random 30 lt random 30 fd 5]
Why: Turns right and goes forward a little to reach food if the first element of input list contains a non-zero value, else moves forward in big steps and turns randomly to explore

INVALID EXAMPLES:
❌ ask turtle 1 [die]
❌ ask other turtles [die]
❌ set energy 100
❌ hatch-food 5
❌ clear-all

STRATEGIC GOALS:
1. Balance exploration and food-seeking behavior
2. Respond to sensor readings intelligently
3. Combine different movement patterns

Generate ONLY the movement code. Code must be runnable in NetLogo in the context of a turtle."""




        self.groq_prompt_resource = """ You are an expert in NetLogo, designing intelligent agents that collect resources efficiently. 
        Each agent has a resource-score that decays based on a percentage of their current weight, which increases as they collect resources. 
        Depositing their resources at the chest in the center of the map will reset their weight to 0.

Given an agent in a resource-collection environment, generate a NetLogo strategy that balances:
1. Collecting resources efficiently (gold, silver, crystals).
        - Crystals have a higher weight
2. Managing weight to optimize movement.
3. Depositing resources at the community chest before resource-score decays.

The strategy should be **compact, effective, and adaptive**. Output only valid NetLogo code.

##### EACH AGENT HAS ACCESS TO THE FOLLOWING VARIABLES #########
input       ;; observations
rule        ;; Movement strategy (mutation variable)
inventory        ;; Table mapping resource types to amounts
weight          ;; Total weight carried
resource-score  ;; Total points (deposited + held)
parent-rule
parent-id
lifetime        ;; age of agent

EXAMPLES OF VALID PATTERNS:
Current Rule: fd 1 rt random 45 fd 2 lt 30
Valid:
let value0 first item 0 input
let resource0 last item 0 input

let value1 first item 1 input
let resource1 last item 1 input

let value2 first item 2 input
let resource2 last item 2 input

ifelse (weight > 50) [
  face patch 0 0
  fd 5
] [
  ifelse (resource0 = "gold" and value0 > 0) [
    rt 15
    fd 0.5
  ] [
    ifelse (resource1 = "crystal" and value1 > 0) [
      rt random 20
      fd 1
    ] [
      ifelse (resource2 = "gold" and value2 > 0) [
        lt 10
        fd 2
      ] [
        rt random 30
        lt random 30
        fd 5
      ]
    ]
  ]
]

Why: This code extracts both numerical values and resource types from the input list, prioritizes movement based on resource-specific conditions, and ensures agents return to the chest when weight exceeds 10.

CONSTRAINTS:
1. Do not include code to kill or control any other agents
2. Do not include code to interact with the environment
3. Do not include code to change the environment
4. Do not include code to create new agents
5. Do not include code to create new resources
6. Do not include code to change the rules of the simulation
7. Do not include any of the following primitives: ['die', 'kill', 'create', 'hatch', 'sprout', 'ask', 'of', 'with', 'run', 'runresult','file', 'import', 'export', 'clear', 'reset', 'setup', 'go']
8. Do not call any variables that the agent does not have access to.

###### AGENT DETAILS ######
Current Rule of Agent: {}
input: {}
  - First three values in input represent distances to resources in three cone regions of 20 degrees each
  - The first item in the input list is the distance to the nearest resource in the left cone, the second is the right cone, and the third is the front cone
  - Each value encodes the distance to nearest resource where a value of 0 indicates no resource
  - Non-zero lower values indicate closer resource
  - Use these to inform movement strategy


**Your GOAL is to mutate the strategy so that the agent maximizes resource-score.**

"""

        self.claude_prompt = """You are an expert NetLogo movement code generator. Generate code:
- Movement: fd/forward, rt/right, lt/left
- Reporters: random, random-float, sin, cos
Format: [command] [number | reporter]

INPUT CONTEXT:
- Current rule: {}
- Food: {} (0 = no food, lower = closer)

Generate ONLY the code."""

        self.claude_prompt1 = """Modify NetLogo movement rule:
1. Use only fd, rt, lt, random N
2. Keep expressions simple
3. Positive numbers only
4. Format: fd/rt/lt -> number or random N

CURRENT STATE:
- Rule: {}
- Food: {}
        
Return ONLY the code."""

        self.claude_prompt2 = """You are an expert NetLogo agent movement behavior generator creating sophisticated patterns.

CORE:
Movement: fd/forward, rt/right, lt/left
Math: random, random-float, sin, cos
Format: [command] [number | expression]

CURRENT STATE:
Rule: {0}
Sensor: {1} (left, front, right, 0 = no food, lower = closer)

Return ONLY the code."""

        self.claude_prompt3 = """You are an expert NetLogo coder. You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. Improve the given agent movement code following these precise specifications:

INPUT CONTEXT:
- Current rule: {}
- Food sensor readings: {}
  - Input list contains three values representing distances to food in three cone regions of 20 degrees each
  - The first item in the input list is the distance to the nearest food in the left cone, the second is the right cone, and the third is the front cone
  - Each value encodes the distance to nearest food source where a value of 0 indicates no food
  - Non-zero lower values indicate closer food
  - Use these to inform movement strategy

CONSTRAINTS:
1. Do not include code to kill or control any other agents
2. Do not include code to interact with the environment
3. Do not include code to change the environment
4. Do not include code to create new agents
5. Do not include code to create new food sources
6. Do not include code to change the rules of the simulation

EXAMPLES OF VALID PATTERNS:
Current Rule: fd 1 rt random 45 fd 2 lt 30
Valid: ifelse item 0 input != 0 [rt 15 fd 0.5] [rt random 30 lt random 30 fd 5]
Why: Turns right and goes forward a little to reach food if the first element of input list contains a non-zero value, else moves forward in big steps and turns randomly to explore

INVALID EXAMPLES:
❌ ask turtle 1 [die]
❌ ask other turtles [die]
❌ set energy 100
❌ hatch-food 5
❌ clear-all

STRATEGIC GOALS:
1. Balance exploration and food-seeking behavior
2. Respond to sensor readings intelligently
3. Combine different movement patterns

Generate ONLY the movement code. Code must be runnable in NetLogo in the context of a turtle."""
