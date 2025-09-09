"""
Test cases for NetLogoVerifier.
"""

# Basic test cases from original file
basic_test_cases = [
    ('lt random 20 rt random 20 fd (1 + random-float 0.5)', True),
    ('fd (1 + random 10)', True),
    ('fd random 10 + 5', True),
    ('fd (random 10 * 0.5)', True),
    ('fd (1 + 2)', True),
    ('fd (1 + random-float 0.5 + 1)', True),
    ('fd (1 - random 5)', True),
    ('fd ()', False),
    ('fd (1 ++ 2)', False),
    ('fd (1 + die)', False),
    ('fd (1 + random-float ask)', False),
]

# New advanced test cases based on code_generation prompt
advanced_test_cases = [
    # Advanced Trigonometric Expressions
    ('fd 1 rt sin (random 90)', True),
    ('fd random-float 2 rt sin (random 90) fd 1', True),
    ('rt cos (random 60) lt sin (random 45)', True),
    ('fd 1 rt (sin (random 90) * 45)', True),  # Nested trig with multiplication
    ('fd 1 rt (sin random 90) * 45', True), 
    ('rt sin random cos random 45', True),    # this is the same as rt (sin (random (cos (random 45))))
    
    # Multi-Stage Movement Sequences
    ('fd 1 rt cos (random 60) * 30 fd 2 lt sin (random 45) * 20', True),
    ('fd 1 rt random 45 fd 2 lt random 30 fd 1 rt random-float 90', True),
    ('lt random-float 45 fd 1 rt random 30 fd 2 bk 1', True),  # Back movement
    ('fd 1 + random 2 rt 90 fd random-float 1 lt random 45', True),
    
    # Sensor-Responsive Conditionals
    ('ifelse item 0 input > 0 [lt (45 - item 0 input / 2) fd 1] [rt random 45 fd 2]', True),
    ('ifelse item 0 input > item 2 input [fd 1 rt random 30] [fd 2 lt random 45]', True),
    ('ifelse item 1 input > 0 [fd (item 1 input / 5 + 1)] [rt random 360 fd 1]', True),
    ('ifelse item 0 input > 0 [ifelse item 1 input > 0 [fd 1] [rt 90 fd 1]] [lt 90 fd 1]', True),
    ('ifelse item 0 input > 0 [ifelse item 0 input < 5 [fd 1] [fd 0.5]] [rt random 45 fd 1]', True),
    
    # Complex Mathematical Relationships
    ('fd (1 + random-float 0.5) * (1 + random-float 0.5)', True),
    ('rt (random 45 + random 45) / 2', True),  # Average of two random values
    ('fd (1 + (random 10 / 5)) * 0.5', True),  # Nested parentheses
    ('rt (random 90) * 0.5 + (random 45) * 0.5', True),  # Too complex for current parser
    ('fd (1 + sin (random 90) * 0.5)', True),  # Trig within arithmetic
    
    # Edge Cases and Extreme Patterns
    ('fd random-float 2 * sin (random 90) * cos (random 45)', True),  # Multiple trig functions
    # Simplified expressions that the verifier can handle
    ('rt random 45', True),  # Simple random without parentheses
    ('fd random 10', True),  # Simple random without parentheses
    ('rt ((sin random 90) * 45) / ((cos random 45) + 0.1)', True),  # Overly complex expression
    ('ifelse item 0 input > 0 [ifelse item 1 input > 0 [ifelse item 2 input > 0 [fd 1] [fd 2]] [fd 3]] [fd 4]', True),  # Triple nested ifelse
    
    # Invalid Syntax or Dangerous Patterns
    ('fd of turtle 0', False),  # "of" primitive
    ('fd (1 + ask turtles [fd 1])', False),  # ask primitive
    ('set x random 10 fd x', False),  # variable creation
    ('fd heading of turtle 1', False),  # of primitive
    ('fd 1 rt 90 die', False),  # dangerous primitive
    ('fd 1 rt 90 while [true] [fd 1]', False),  # infinite loop
    
    # Multiple if-else Statements
    ("(ifelse item 0 input > 0 [fd 1] item 1 input > 0 [rt 90 fd 1])", True),
    ("(ifelse item 0 input > 0 fd 1] item 1 input > 0 [rt 90 fd 1])", False),  # Syntax error (missing '[')
    ("(ifelse-value item 0 input > 0 [1 + 2] item 1 input > 0 [sin random 360] [0])", True),
    ("(ifelse item 0 input > 10 and item 1 input < 5 [fd 1] item 2 input != 0 [rt 45 fd 2] [lt 45 fd 1])", True), # Complex condition with logical operator
    # Corrected: Added missing closing parenthesis and whitespace
    ("(ifelse item 2 input != 0 [ fd 1 ] item 0 input != 0 and item 0 input < item 1 input [ lt 15 fd 0.5 ] item 1 input != 0 [ rt 15 fd 0.5 ] [ fd 1 ])", True),   

    # New ifelse and Parentheses Test Cases
    ('ifelse (item 0 input > 0) [fd 1] [rt 90]', True), # Simple ifelse with parentheses around condition
    ('ifelse item 0 input > 0 [fd (1 + random 5)] [rt (45 + random 45)]', True), # Parentheses within blocks
    ('ifelse (item 0 input > 0 and item 1 input < 10) [fd 1] [rt 90]', True), # Parentheses around complex condition
    ('ifelse item 0 input > 0 [ifelse (item 1 input > 5) [fd 1] [bk 1]] [rt 180]', True), # Nested ifelse with parentheses in inner condition
    ('ifelse (item 0 input > 0) [ fd 1 ] (item 1 input > 0) [ rt 90 ]', False), # Incorrect syntax - missing brackets/parentheses for else-if structure
    ('ifelse item 0 input > 0 [ fd (1 + (random 5 / 2)) ] [ rt (90 - (random 10 * 2)) ]', True), # Nested parentheses within blocks
    ('ifelse (item 0 input > (item 1 input + 5)) [fd 1] [rt 90]', True), # Parentheses in comparison
    ('ifelse item 0 input > 0 [fd 1] rt 90', False), # Missing brackets for else block
    ('ifelse (item 0 input > 0 [fd 1] [rt 90])', False), # Incorrect placement of outer parentheses

    # Nested ifelse Test Cases (Increasing Complexity)
    ('ifelse item 0 input > 0 [ ifelse item 1 input > 0 [ fd 1 ] [ rt 90 ] ] [ bk 1 ]', True), # Simple double nest
    ('ifelse (item 0 input > 0) [ ifelse (item 1 input > 0) [ fd 1 ] [ rt 90 ] ] [ bk 1 ]', True), # Double nest with outer condition parentheses
    ('ifelse item 0 input > 0 [ ifelse (item 1 input > 0) [ fd (1 + random 2) ] [ rt (random 90) ] ] [ bk (random-float 1) ]', True), # Double nest with inner condition and command parentheses
    ('ifelse item 0 input > 0 [ ifelse item 1 input > 0 [ fd 1 ] [ rt 90 ] ] [ ifelse item 2 input > 0 [ bk 1 ] [ lt 90 ] ]', True), # Double nest in both main branches
    ('ifelse item 0 input > 0 and item 1 input < 10 [ ifelse item 2 input != 0 [ fd 1 ] [ rt 90 ] ] [ bk 1 ]', True), # Double nest with complex outer condition (no parentheses)
    ('ifelse (item 0 input > 0 and item 1 input < 10) [ ifelse (item 2 input != 0) [ fd 1 ] [ rt 90 ] ] [ bk 1 ]', True), # Double nest with complex outer condition (with parentheses)
    ('ifelse item 0 input > 0 [ ifelse item 1 input > 0 [ ifelse item 2 input > 0 [ fd 1 ] [ rt 90 ] ] [ bk 1 ] ] [ lt 90 ]', True), # Simple triple nest
    ('ifelse (item 0 input > 0) [ ifelse (item 1 input > 0) [ ifelse (item 2 input > 0) [ fd 1 ] [ rt 90 ] ] [ bk 1 ] ] [ lt 90 ]', True), # Triple nest with parentheses around conditions
    ('ifelse item 0 input > 0 [ ifelse item 1 input > 0 [ fd 1 ] [ rt 90 ] ifelse item 2 input > 0 [ bk 1 ] [ lt 90 ] ]', False), # Invalid syntax: second ifelse needs brackets
    ('ifelse item 0 input > 0 [ ifelse item 1 input > 0 [ ifelse item 2 input > 0 [ ifelse item 3 input > 0 [ fd 1 ] [ rt 90 ] ] [ bk 1 ] ] [ lt 90 ] ] [ fd 2 ]', True), # Quadruple nest
    
    # Most advanced, real examples
    ("""
ifelse item 0 food-observations < item 0 poison-observations and item 0 food-observations > 0 
  [lt 10 fd 1]
  [ifelse item 1 food-observations < item 1 poison-observations and item 1 food-observations > 0 
    [rt 10 fd 1]
    [ifelse item 2 food-observations < item 2 poison-observations and item 2 food-observations > 0 
      [fd 1]
      [ifelse item 0 poison-observations > 0 [lt 20]
        [ifelse item 1 poison-observations > 0 [rt 20]
          [ifelse item 2 poison-observations > 0 [bk 1]
            [lt random 20 rt random 20 fd 1]
          ]
        ]
      ]
    ]
  ]""", True),
    ("""
ifelse weight > 10 [
  ifelse xcor = 0 and ycor = 0 [
    rt random 20 lt random 20 fd 1
  ][
    lt towards [0 0] fd 1
  ]
][
  (ifelse item 0 input-resource-distances < item 1 input-resource-distances and item 0 input-resource-distances < item 2 input-resource-distances [
    lt 20 fd 1
  ] item 1 input-resource-distances < item 0 input-resource-distances and item 1 input-resource-distances < item 2 input-resource-distances [
    rt 20 fd 1
  ] [
    fd 1
  ])
])
]""", True),
    (
"""
(ifelse item 2 food-observations > 0 and item 2 poison-observations = 0 
  [ fd 1 ]
  [
    (ifelse item 0 poison-observations = 0 and item 1 poison-observations = 0 and item 2 poison-observations = 0 
      [ 
        (ifelse item 0 food-observations > item 1 food-observations and item 0 food-observations > item 2 food-observations 
          [ lt 20 ]
          [
            (ifelse item 1 food-observations > item 0 food-observations and item 1 food-observations > item 2 food-observations 
              [ rt 20 ]
              [ fd 1 ]
            )
          ]
        )
      ]
      [
        (ifelse item 0 poison-observations > 0 and item 1 poison-observations > 0 and item 2 poison-observations > 0 
          [ rt random-float 60 - 30 ]
          [
            (ifelse item 0 poison-observations = 0 and item 2 poison-observations > 0 and item 1 poison-observations > 0 
              [ lt 20 ]
              [
                (ifelse item 1 poison-observations = 0 and item 0 poison-observations > 0 and item 2 poison-observations > 0 
                  [ rt 20 ]
                  [
                    (ifelse item 2 poison-observations > 0 
                      [ 
                        (ifelse item 0 poison-observations < item 1 poison-observations 
                          [ lt 20 ]
                          [ rt 20 ]
                        )
                      ]
                      [ fd 1 ]
                    )
                  ]
                )
              ]
            )
          ]
        )
      ]
    )
  ]
)
fd 1
""", True),
    
    ("""
ifelse item 0 input > 0 and item 1 input <= 45 [
  lt (item 0 input * 45 / 100)
  fd (item 0 input / 2)
] [
  ifelse item 0 input > 0 and item 1 input > 315 [
    rt (item 0 input * 45 / 100)
    fd (item 0 input / 2)
  ] [
    rt (45 * sin (random-float 90))
    fd (0.5 + random-float 1.5)
    if random-float 1 < 0.3 [
      bk 0.5
    ]
  ])
    """, True),
    ("""
ifelse item 0 input > 0 and item 0 input <= 45 [
  lt (item 0 input)
  fd (item 1 input)
] [
  ifelse item 0 input > 315 and item 0 input <= 360 [
    rt (360 - item 0 input)
    fd (item 1 input)
  ] [
    rt (45 * sin (random-float 90))
    fd (0.5 + random-float 1.5)
    if random-float 1 < 0.3 [
      bk 0.5
    ]
  ]
]
""", True),
],
("""
 (ifelse min input-resource-distances <= 5 [
    (ifelse item (position (min input-resource-distances) input-resource-distances) input-resource-types) = "gold" [rt random 10 fd 1]
           [item (position (min input-resource-distances) input-resource-distances) input-resource-types) = "silver" [lt random 10 fd 1]
           [fd 1]
  )
  weight > 50 [rt 180 fd 1]
  [
    (ifelse min input-resource-distances <= 20 [
      ifelse item (position (min input-resource-distances) input-resource-distances) input-resource-types) = "crystal" 
        [rt random 20 fd 1]
        [lt random 20 fd 1]
    ]
    [fd 1]
  ]
))
""", False), # should be wrong
# Examples from the prompt to validate separately
prompt_examples = [
    'fd random-float 2 rt sin (random 90) fd 1',
    'ifelse item 0 input > 0 [lt (45 - item 0 input / 2) fd 1] [rt random 45 fd 2]',
    'fd 1 rt (sin (random 90) * 45) fd random-float 3',
    'fd 1 rt cos (random 60) * 30 fd 2 lt sin (random 45) * 20'
]
