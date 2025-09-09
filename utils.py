import anthropic
import dotenv
import os
import re
import ast

dotenv.load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_text(prompt):
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=8192,
        temperature=0.8,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text

def read_prompt(prompt_name, vars):
    with open(f"prompts/{prompt_name}.txt", "r") as file:
        content = file.read()
        # Replace placeholder with actual max parts value
        #content = content.replace("{{MAX_NUM_PARTS}}", str(vars["MAX_NUM_PARTS"]))
        for key, value in vars.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        #print(content)
        return content

def get_robot_configuration(prompt):
    # Extract text from <robot_configuration> tag
    response = generate_text(prompt)
    pattern = r'<robot_configuration>(.*?)</robot_configuration>'
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return ast.literal_eval(match.group(1).strip())
    else:
        return response  # Return full response if tag not found

def get_positions(configuration):
    return [part[:2] for part in configuration]

def check_robot_configuration(configuration):
    # Check that all parts are connected
    """
    Check that a robot configuration is valid according to the specified rules.
    
    Args:
        configuration: List of tuples representing robot parts [x, y, type, direction]
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    if not configuration:
        return False
    
    # Check that all tuples consist of four integers
    for part in configuration:
        if not isinstance(part, (list, tuple)) or len(part) != 4:
            return False
        if not all(isinstance(x, int) for x in part):
            return False
    
    # Check that the first tuple's third element is a 1 (seed component)
    if configuration[0][2] != 1:
        return False
    
    # Check that none of the other tuple's third element is a 1, but are either 2, 3, 4, or 6
    for part in configuration[1:]:
        part_type = part[2]
        if part_type == 1 or part_type not in [2, 3, 4, 6]:
            return False
    
    # Check direction constraints
    for part in configuration:
        part_type = part[2]
        direction = part[3]
        # For propulsion (2) and sensor (4) components, direction must be 0, 1, 2, or 3
        if part_type in [2, 4] and direction not in [0, 1, 2, 3]:
            return False
        # For rotator (3) components, direction must be 0 or 1
        if part_type == 3 and direction not in [0, 1]:
            return False
    
    # Check that all parts are connected without diagonal connections
    positions = set((part[0], part[1]) for part in configuration)
    
    # Build adjacency graph
    adjacency = {pos: [] for pos in positions}
    for pos in positions:
        x, y = pos
        # Check four adjacent positions (no diagonals)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            if neighbor in positions:
                adjacency[pos].append(neighbor)
    
    # Check connectivity using BFS from the first position
    start_pos = (configuration[0][0], configuration[0][1])
    visited = set()
    queue = [start_pos]
    visited.add(start_pos)
    
    while queue:
        current = queue.pop(0)
        for neighbor in adjacency[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    # All positions should be reachable from the start position
    return len(visited) == len(positions)

def init_robot(max_num_parts):
    prompt = read_prompt("init_body_v1", {"MAX_NUM_PARTS": max_num_parts})
    configuration = get_robot_configuration(prompt)
    if check_robot_configuration(configuration):
        return configuration
    else:
        return None
    
def modify_robot(max_num_parts, configuration):
    prompt = read_prompt("modify_body_v2", {"MAX_NUM_PARTS": max_num_parts, "CFG": configuration})
    new_cfg = get_robot_configuration(prompt)
    if check_robot_configuration(new_cfg):
        return new_cfg
    else:
        return configuration
    
def get_allowed_actions(configuration):
    action_counts = {"N_UP": 0, "N_RIGHT": 0, "N_DOWN": 0, "N_LEFT": 0, "N_CW": 0, "N_CCW": 0}
    for part in configuration:
        if part[2] == 2:
            if part[3] == 0:
                action_counts["N_UP"] += 1
            elif part[3] == 1:
                action_counts["N_DOWN"] += 1
            elif part[3] == 2:
                action_counts["N_LEFT"] += 1
            elif part[3] == 3:
                action_counts["N_RIGHT"] += 1
        elif part[2] == 3:
            if part[3] == 0:
                action_counts["N_CW"] += 1
            elif part[3] == 1:
                action_counts["N_CCW"] += 1
    return action_counts

def check_actions(configuration, actions):
    action_counts = get_allowed_actions(configuration)
    # Map action strings to count keys
    action_mapping = {
        "up": "N_UP", "right": "N_RIGHT", "down": "N_DOWN", 
        "left": "N_LEFT", "cw": "N_CW", "ccw": "N_CCW"
    }
    # Count occurrences of each action in the actions list
    action_list_counts = {key: 0 for key in action_counts.keys()}
    for action in actions:
        if action in action_mapping:
            action_list_counts[action_mapping[action]] += 1
    # Check if all action requirements are satisfied
    return all(action_counts[key] >= action_list_counts[key] for key in action_counts)

def get_num_sensors(configuration):
    return sum(1 for part in configuration if part[2] == 4)

def construct_sensor_prompt(configuration):
    sensor_prompt = ""
    for part in configuration:
        if part[2] == 4:
            dir = ["up", "right", "down", "left"][part[3]]
            sensor_prompt += f"The sensor is at {part[0]}, {part[1]} and is pointing {dir}.\n"
    return sensor_prompt

def init_rule(configuration, sensor_dist):
    n_actions = get_allowed_actions(configuration)
    n_sensors = get_num_sensors(configuration)
    sensor_prompt = construct_sensor_prompt(configuration)
    prompt = read_prompt("init_rule_v1", {"SENSOR_DIST": sensor_dist, "SENSOR_PROMPT": sensor_prompt, "N_SENSORS": n_sensors, "N_UP": n_actions["N_UP"], "N_DOWN": n_actions["N_DOWN"], "N_RIGHT": n_actions["N_RIGHT"], "N_LEFT": n_actions["N_LEFT"], "N_CW": n_actions["N_CW"], "N_CCW": n_actions["N_CCW"]})
    response = generate_text(prompt)
    pattern = r'<code>(.*?)</code>'
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        print("No code found in response")
        return response  # Return full response if tag not found
    
def modify_rule(rule, configuration, sensor_dist):
    n_actions = get_allowed_actions(configuration)
    n_sensors = get_num_sensors(configuration)
    sensor_prompt = construct_sensor_prompt(configuration)
    prompt = read_prompt("modify_rule_v1", {"RULE": rule, "SENSOR_DIST": sensor_dist, "SENSOR_PROMPT": sensor_prompt, "N_SENSORS": n_sensors, "N_UP": n_actions["N_UP"], "N_DOWN": n_actions["N_DOWN"], "N_RIGHT": n_actions["N_RIGHT"], "N_LEFT": n_actions["N_LEFT"], "N_CW": n_actions["N_CW"], "N_CCW": n_actions["N_CCW"]})
    response = generate_text(prompt)
    pattern = r'<code>(.*?)</code>'
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        print("No code found in response")
        return response  # Return full response if tag not found


if __name__ == "__main__":
    #prompt = "You are tasked with generating a robot configuration for a 2D grid-based environment. The configuration will be represented as a list of four-tuples, each describing a body part of the robot.\n\nFirst, let's establish the maximum number of parts the robot can have:\n\n<max_num_parts>\n{{MAX_NUM_PARTS}}\n</max_num_parts>\n\nBefore we begin, let's review the body part types and their encodings:\n1. Seed or root component\n2. Propulsion component\n3. Rotator component\n4. Sensor component\n6. Interaction component\n\nNow, follow these steps to generate the robot configuration:\n\n1. Start with the seed component:\n   - Place it at coordinates (0,0)\n   - It must be of type 1 (Seed)\n   - Set its direction to 0\n   - This will always be represented as [0,0,1,0]\n\n2. Add additional body parts up to the maximum number, ensuring that:\n   - All parts are connected (adjacent) to at least one other part\n   - There are no diagonal connections\n   - X and Y coordinates are integers\n   - Body part types are integers: 2, 3, 4, or 6\n   - Set appropriate directions:\n     - Rotator components (type 3): 0 (clockwise) or 1 (counterclockwise)\n     - Propulsion and sensor components (types 2 and 4): 0 (up), 1 (right), 2 (down), or 3 (left)\n\n3. Optimize the robot configuration:\n   - Place sensor (type 4) and interaction (type 6) components on the outer parts of the robot\n   - Ensure sensor components' directions point away from the robot's body\n   - Balance the number of movement components for speed without hindering maneuverability\n\nProvide the final configuration in the specified format. Do not include comments.\n\n<robot_design_process>\n1. List out each body part type and its characteristics:\n   - Type 1 (Seed): Always at (0,0), direction 0\n   - Type 2 (Propulsion): Directions 0-3 (up, right, down, left)\n   - Type 3 (Rotator): Directions 0-1 (clockwise, counterclockwise)\n   - Type 4 (Sensor): Directions 0-3 (up, right, down, left)\n   - Type 6 (Interaction): No specific direction\n\n2. For each additional part (up to MAX_NUM_PARTS):\n   a. Consider placement:\n      - List available adjacent positions\n      - Choose position that maintains connectivity\n   b. Determine type:\n      - Consider current robot needs (propulsion, sensing, interaction)\n      - Ensure a balanced distribution of types\n   c. Set direction:\n      - For type 2 and 4, choose direction that points away from the body\n      - For type 3, alternate between clockwise and counterclockwise\n      - For type 6, no direction needed\n\n3. Verify configuration:\n   - Check that all parts are connected\n   - Ensure no diagonal connections\n   - Confirm all coordinates are integers\n   - Validate that body part types are 2, 3, 4, or 6\n   - Verify directions are set correctly for each type\n\n4. Optimize configuration:\n   - Review sensor and interaction component placements\n   - Adjust sensor directions to point outward\n   - Evaluate propulsion component distribution for balanced movement\n   - Make any final adjustments to improve overall design\n</robot_design_process>\n\nPresent your final robot configuration in the following format:\n\n<robot_configuration>\n[[x1, y1, type1, direction1], [x2, y2, type2, direction2], ..., [xn, yn, typen, directionn]]\n</robot_configuration>\n\nEnsure that your configuration adheres to all the specified constraints and optimization guidelines."
    #prompt = read_prompt("init_body_v1", {"MAX_NUM_PARTS": 15})
    #body = get_robot_configuration(prompt)
    body = [[0, 0, 1, 0], [0, 1, 2, 0], [1, 1, 3, 0], [1, 0, 4, 1], [2, 0, 6, 0], [2, 1, 2, 1], [0, 2, 4, 3], [1, 2, 3, 1]]
    print(body)
    print(get_num_sensors(body))
    print(get_allowed_actions(body))
    print(construct_sensor_prompt(body))
    print(check_actions(body, ["up", "down", "cw", "ccw", "up"]))
    #prompt2 = read_prompt("modify_body_v2", {"MAX_NUM_PARTS": 15, "CFG": body})
    #print(get_robot_configuration(prompt2))
    rule = init_rule(body, 7)
    print(rule)
    new_rule = modify_rule(rule, body, 7)
    print(new_rule)
    #exec(rule)
    #actions = move([(1, 4), (2, 0)])
    #print(actions)
    #print(check_actions(body, actions))
    