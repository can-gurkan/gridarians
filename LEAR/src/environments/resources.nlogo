extensions [ py table fp rnd ]

__includes [
  "env_utils/evolution.nls"
  "env_utils/logging.nls"
  "env_utils/prompt_config.nls"
]

globals [
  generation
  generation-stats
  best-rule
  best-rule-fitness
  best-resource-score
  error-log
  community-chest
  init-rule
  init-pseudocode
]

breed [llm-agents llm-agent]  ;; Agents collect resources
breed [resources resource] ;; Resources on the map

llm-agents-own [
  input-resource-distances
  input-resource-types
  input
  distance-from-center
  rule        ;; Movement strategy (mutation variable)
  inventory        ;; Table mapping resource types to amounts
  weight          ;; Total weight carried
  resource-score  ;; Total points (deposited + held) accounting for score decay
  resource-deposited ;; Total points (deposited) accounting for score decay
  parent-rule
  parent-id
  pseudocode ;; descriptive text rule
  parent-pseudocode ;; pseudocode associated with the parent
  lifetime        ;; age of agent
]

resources-own [
  resource-kind  ;; Type of resource (silver, gold, crystal)
]

;;; ========== SETUP PROCEDURES ==========


to setup-params
  if use-config-file? [
    carefully [
      run word "setup-params-" config-file
    ] [
      user-message word config-file " is not a valid config file."
    ]
  ]
end


to setup
  clear-all

  py:setup py:python
  py:run "import os"
  py:run "import sys"
  py:run "from pathlib import Path"
  py:run "sys.path.append(os.path.dirname(os.path.abspath('..')))"

  py:run "from src.mutation.mutate_code import mutate_code"

  set init-rule "lt random 20 rt random 20 fd 1"
  set init-pseudocode "Take left turn randomly within 0-20 degrees, then take right turn randomly within 0-20 degrees and move forward 1"
  set generation-stats []
  set error-log []
  set best-resource-score 0


  setup-environment
  setup-resources
  setup-llm-agents
  if logging? [ setup-logger get-additional-params ]
  write-prompt-config prompt-type prompt-name
  reset-ticks
end

to setup-environment
  ;; Define the chest as a 3x3 patch area in the center
  set community-chest patches with [abs pxcor <= 1 and abs pycor <= 1]

  let outline patches with [(abs pxcor = 2 and (abs pycor <= 2)) or (abs pycor = 2 and (abs pxcor <= 2))]

  ;; Color the chest area
  ask community-chest [
    set pcolor brown
    set plabel-color white
  ]

  ask outline [ set pcolor 44 ]
end

to setup-resources
  ;; Create different types of resources randomly
  let resource-types ["silver" "gold" "crystal"]

  repeat num-resources [  ;; Spawn resources dynamically
    let spawn-location one-of patches with [not any? turtles-here]
    if spawn-location != nobody [
      create-resources 1 [
        ;move-to spawn-location
        setxy 0 0
        fd resource-radius
        set resource-kind one-of resource-types
        set shape resource-kind
        set color (ifelse-value (resource-kind = "silver") [gray]
                              (resource-kind = "gold") [yellow]
                              [cyan])
        set size 1.5
        ;set label resource-kind  ;; Show type above the resource (DEBUGGING)
      ]
    ]
  ]
end

to setup-llm-agents
  create-llm-agents num-llm-agents [
    ;setxy random-xcor random-ycor
    setxy 0 0
    set shape "person"
    set color blue
    set size 1.25

    set rule init-rule
    set parent-rule "na"
    set pseudocode init-pseudocode
    set parent-pseudocode "na"

    init-agent-params ;; init with empty inventory, zero weight, and zero resource-score
  ]
end

to init-agent-params
  set inventory table:make
  set weight 0
  set resource-score 0
  set resource-deposited 0
end

;; create more resources if environment is lacking sufficient amount
to replenish-resources
  if count resources < num-resources [  ;; Check if we are below target resource count
    let missing-resources (num-resources - count resources)

    repeat missing-resources [
      let spawn-location one-of patches with [not any? turtles-here]
      if spawn-location != nobody [
        create-resources 1 [
          ;move-to spawn-location
          setxy 0 0
          fd resource-radius
          set resource-kind one-of ["silver" "gold" "crystal"]

          ;; Assign visual properties
          if resource-kind = "silver" [ set shape "silver" set color gray ]
          if resource-kind = "gold" [ set shape "gold" set color yellow ]
          if resource-kind = "crystal" [ set shape "crystal" set color cyan ]

          set size 1.5
          ;; set label resource-kind
        ]
      ]
    ]
  ]
end

;;; ========== GO PROCEDURE ==========
to go
  do-plotting
  ask llm-agents [
    set lifetime lifetime + 1
    set distance-from-center distancexy 0 0
    set resource-score resource-score - (weight * 0.25)  ;; Lose resource-score at a rate of 25% of total weight
    set resource-deposited resource-deposited - (weight * 0.25)  ;; Lose resource-deposited at a rate of 25% of total weight

    ;; set resource-score resource-score - (weight ^ 1.5 * 0.1) ;; exponential loss (higher weights are punished more)
    ;; if weight > 2 [ set resource-score resource-score - ((weight - 2) * 0.3) ] ;; start losing weight once over a threshold
    set input get-observation
    set input-resource-distances first input
    set input-resource-types last input
    ;;if energy <= 0 [ die ]
    run-rule

    set resource-score max (list 0 resource-score)
  ]
  evolve-agents
  replenish-resources
  tick
end


;;; ========== OBSERVATION VECTOR REPORTERS ==========

to-report get-observation  ;; returns list of two flat lists (distances and types), each index correspond to each as resource-distance, resource-type
  let dist 7
  let angle 20
  let obs []
  let distances []
  let types []

  ;; Observe in three directions: left, right, center
  foreach [-20 40 -20] [a ->
    rt a
    let result get-in-cone dist angle
    ;; set obs lput result obs
    set distances lput item 0 result distances
    set types lput item 1 result types
  ]

  ;; Also observe distance/angle to chest
  let chest-dist distancexy 0 0
  carefully [let chest-heading towardsxy 0 0] [let chest-heading 0]  ;; Angle to face the chest

  ;; print(obs)
  report (list distances types)
end

;;; Detects nearest resource in a given cone & returns (distance, type)
to-report get-in-cone [dist angle]
  let closest-resource nobody
  let closest-distance dist
  let closest-type "none"

  ;; Find the closest resource in the vision cone
  let cone other resources in-cone dist angle
  let f min-one-of cone [distance myself]

  if f != nobody [
    set closest-resource f
    set closest-distance distance f
    set closest-type [resource-kind] of f
  ]

  ;; Return a list (distance, resource type)
  report (list closest-distance closest-type)
end



;;; ========== RUN LLM-GENERATED STRATEGY ==========
to run-rule
  carefully [
    run rule

    ;; Always attempt to pick up and deposit if conditions are met
    pick-up
    deposit
  ] [
    ;; Log any execution errors
    let error-info (word
      "ERROR WHILE RUNNING RULE: " rule
      " | Agent: " who
      " | Tick: " ticks
      " | Fitness: " resource-score
      " | Total Resource Value Deposited (With Decay): " resource-deposited
      " | Weight: " weight
      " | Lifetime: " lifetime
      " | Resource Input Distances: " input-resource-distances
      " | Resource Input Types: " input-resource-types
      " | Error: " error-message
    )
    if ticks mod ticks-per-generation = 1 [

      if verbose? [ print error-info ]
      set error-log lput error-info error-log
    ]
  ]
end


;;; ========== PICK UP RESOURCES ==========
to pick-up
  let resource-here one-of resources-here  ;; Find a nearby resource

  if resource-here != nobody [
    let kind [resource-kind] of resource-here
    let value 0
    let weight-addition 0.2  ;; Base weight


    if kind = "silver" [ set value 1 ]
    if kind = "gold" [ set value 2  set weight-addition 0.3] ;; gold slow agents more
    if kind = "crystal" [ set value 4 set weight-addition 0.5 ]  ;; Crystals slow agents most

    table:put inventory kind ((table:get-or-default inventory kind 0) + 1)


    ;; ----- Resource Score calculation: incremented when picking up
    set resource-score resource-score + value
    ;; print (word "PICKED UP: " kind " | New Score: " resource-score) ## DEBUGGING!!!

;    let keys table:keys inventory
;    foreach keys [ key ->
;      let val (ifelse-value (key = "silver") [1] (key = "gold") [2] [4])
;      set resource-score resource-score + (table:get inventory key) * val
;    ]

    set weight weight + weight-addition

    ;; Remove the resource
    ask resource-here [ die ]
  ]
end

;;; ========== DEPOSIT RESOURCES ==========
to deposit
  if member? patch-here community-chest [
    let keys table:keys inventory
    foreach keys [ key ->
      ;; resource-deposited incremented only when deposited
      let val (ifelse-value (key = "silver") [1] (key = "gold") [2] [4])
      set resource-deposited resource-deposited + (table:get inventory key) * val
      table:remove inventory key
    ]

    ;; Reset weight and energy
    set weight 0
  ]
end

;;; ========== EVOLUTION ==========

to evolve-agents
  if ticks >= 1 and ticks mod ticks-per-generation = 0 [

    let parents select-agents
    let kill-num length parents

    let kill-dict agent-dict min-n-of kill-num llm-agents [fitness]
    let best-dict agent-dict turtle-set parents
    let new-agent-ids []


    foreach parents [ parent ->
      ask parent [
        let my-parent-id who
        let my-rule rule
        let my-pseudocode pseudocode

        hatch 1 [
          set parent-id my-parent-id
          set parent-rule my-rule
          set parent-pseudocode my-pseudocode
          set rule mutate-rule
          init-agent-params  ;; base params for agent (new inventory, 0 weight, 0 resource-score)

          set new-agent-ids lput who new-agent-ids
        ]
      ]
    ]

    ask min-n-of kill-num llm-agents with [not member? who new-agent-ids] [fitness] [ die ]

    let new-dict agent-dict llm-agents with [member? who new-agent-ids]
    update-generation-stats
    log-metrics (list best-dict new-dict kill-dict)
    ask llm-agents [
      setxy 0 0
      set resource-score 0
      set weight 0
    ]
  ]
end



;;; ========== REPORTER HELPERS =========

to-report fitness
  report resource-score
end

to-report mean-fitness
  report mean [fitness] of llm-agents
end

to-report get-additional-params
  report (list
    list "num-food-sources" num-resources
    list "init-rule" init-rule
    list "init-pseudocode" init-pseudocode
  )
end



;;; ========== LOGGING & REPORTING ==========

to-report create-agent-dict [name agent-list]
  let agents-sub-dict table:make
  foreach agent-list [agent-data ->
    let agent-id item 1 (item 0 agent-data)
    let agent-key word "Agent " agent-id
    table:put agents-sub-dict agent-key agent-data
  ]
  let agents-super-dict table:make
  table:put agents-super-dict name agents-sub-dict
  report agents-super-dict
end


;;; ============== GENERATION METRICS ==============

to-report get-generation-metrics
  let keys ["generation" "best rule" "mean fitness" "best fitness" "error log"]
  let values ifelse-value any? llm-agents [
    (list
      generation
      best-rule
      mean-fitness
      max [fitness] of llm-agents
      error-log)
  ] [
    (list generation "na" 0 0 0 [])
  ]
  report fp:zip keys values
end

;;; ========== PLOTTING ==========

to do-plotting
  if ticks mod ticks-per-generation = 0 [
    set-current-plot "Mean Resource Score of Agents"
    set-current-plot-pen "Mean Score"
    plotxy generation mean [resource-score] of llm-agents
    set-current-plot-pen "Max Score"
    plotxy generation max [resource-score] of llm-agents
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
229
10
638
420
-1
-1
12.152
1
10
1
1
1
0
1
1
1
-16
16
-16
16
1
1
1
ticks
30.0

BUTTON
107
178
172
211
go
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
0

BUTTON
34
178
100
211
setup
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SWITCH
34
128
205
161
logging?
logging?
0
1
-1000

SLIDER
34
10
206
43
num-resources
num-resources
0
100
50.0
1
1
NIL
HORIZONTAL

SLIDER
34
88
205
121
num-llm-agents
num-llm-agents
0
100
12.0
1
1
NIL
HORIZONTAL

SLIDER
34
49
205
82
ticks-per-generation
ticks-per-generation
0
500
500.0
1
1
NIL
HORIZONTAL

INPUTBOX
35
359
205
419
experiment-name
resources_test
1
0
String

PLOT
723
133
1148
395
Mean Resource Score of Agents
generation
resource score
0.0
10.0
0.0
10.0
true
true
"" ""
PENS
"Mean Score" 1.0 0 -955883 true "" ""
"Max Score" 1.0 0 -14070903 true "" ""

MONITOR
723
87
803
132
generation
generation
17
1
11

CHOOSER
35
303
203
348
llm-type
llm-type
"groq" "claude"
0

SWITCH
35
266
204
299
text-based-evolution
text-based-evolution
1
1
-1000

CHOOSER
34
468
204
513
selection
selection
"tournament" "fitness-prop"
0

SLIDER
34
518
204
551
num-parents
num-parents
0
10
1.0
1
1
NIL
HORIZONTAL

SLIDER
35
555
204
588
tournament-size
tournament-size
0
100
12.0
1
1
NIL
HORIZONTAL

SLIDER
35
592
204
625
selection-pressure
selection-pressure
0
1
0.8
0.10
1
NIL
HORIZONTAL

SWITCH
214
468
373
501
use-config-file?
use-config-file?
1
1
-1000

INPUTBOX
213
509
372
569
config-file
NIL
1
0
String

SWITCH
384
468
548
501
verbose?
verbose?
0
1
-1000

SWITCH
35
227
204
260
llm-mutation?
llm-mutation?
0
1
-1000

SLIDER
35
425
205
458
resource-radius
resource-radius
0
25
12.0
1
1
NIL
HORIZONTAL

INPUTBOX
560
465
789
525
prompt-type
NIL
1
0
String

INPUTBOX
560
530
789
590
prompt-name
NIL
1
0
String

@#$#@#$#@
## WHAT IS IT?

(a general understanding of what the model is trying to show or explain)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

crate
false
0
Rectangle -7500403 true true 45 45 255 255
Rectangle -16777216 false false 45 45 255 255
Rectangle -16777216 false false 60 60 240 240
Line -16777216 false 180 60 180 240
Line -16777216 false 150 60 150 240
Line -16777216 false 120 60 120 240
Line -16777216 false 210 60 210 240
Line -16777216 false 90 60 90 240
Polygon -7500403 true true 75 240 240 75 240 60 225 60 60 225 60 240
Polygon -16777216 false false 60 225 60 240 75 240 240 75 240 60 225 60

crystal
false
0
Rectangle -7500403 true true 90 90 210 270
Polygon -1 true false 210 270 255 240 255 60 210 90
Polygon -13345367 true false 90 90 45 60 45 240 90 270
Polygon -11221820 true false 45 60 90 30 210 30 255 60 210 90 90 90

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

gold
false
0
Circle -7500403 true true 0 0 300

hex
false
0
Polygon -7500403 true true 0 150 75 30 225 30 300 150 225 270 75 270

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

silver
false
0
Circle -7500403 true true 90 90 120

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.4.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180

gold
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
1
@#$#@#$#@
