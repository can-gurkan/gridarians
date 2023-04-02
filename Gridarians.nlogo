extensions[cgp fp palette math]

globals [
  grid-size
  available-cell-types
  num-balls
  num-walls
  sensing-distance
  time vis tin low

  num-pre-updates
  threshold-pre-cell-death
  threshold-pre-cell-birth
  delta-pre-cell-health

  num-updates
  threshold-cell-death
  threshold-cell-birth
  delta

  threshold-cell-type-inc
  threshold-cell-type-dec
  threshold-cell-dir-inc
  threshold-cell-dir-dec

  num-body-inputs
  num-body-outputs
  num-body-cols
  num-body-rows
  body-lvlsback
]

breed[gridarians gridarian]
breed[cells cell]
breed[walls wall]
breed[balls ball]

gridarians-own[
  my-score
]

cells-own [
  cell-type
  direction
  health
  id
  is-cutpoint?
]

to init-params
  set grid-size 25
  set available-cell-types [2 3 4 5 6]
  set num-balls 5
  set num-walls 10
  set sensing-distance 3

  ;; Pre-Birth Params
  set num-pre-updates 6
  set threshold-pre-cell-death -0.6
  set threshold-pre-cell-birth 0.2
  set delta-pre-cell-health 0.2

  ;; Lifetime params
  set num-updates 1
  set threshold-cell-death -0.4
  set threshold-cell-birth 0.2
  set delta 0.1

  set threshold-cell-type-inc 0.5
  set threshold-cell-type-dec -0.5
  set threshold-cell-dir-inc 0.5
  set threshold-cell-dir-dec -0.5

  ;; Body CGP Parameters
  set num-body-inputs 5
  set num-body-outputs 3
  set num-body-cols 6
  set num-body-rows 3
  set body-lvlsback 2
end

to setup
  clear-all
  init-params
  resize-grid grid-size
  ;init-custom-robot
  init-bodies init-num-agents
  setup-random-walls
  setup-random-balls
  visualize-cells
  reset-ticks
end

to resize-grid [n]
  resize-world (-1 * n) n (-1 * n) n
  set-patch-size (11.5 * 50) / (2 * n)
end

to setup-box-walls
  let box-edge max-pxcor - 1
  ask patches with [(abs pxcor = box-edge or abs pycor = box-edge) and
    abs pxcor <= box-edge and abs pycor <= box-edge]
  [ set pcolor gray ]
end

to setup-random-walls
  ask n-of num-walls patches with [not any? turtles-here][
    sprout-walls 1 [
      set shape "square"
      set color grey
    ]
  ]
end

to setup-random-balls
  ask n-of num-balls patches with [not any? turtles-here][
    sprout-balls 1 [
      set shape "circle"
      set color yellow
    ]
  ]
end

;; 1: seed-cell
;; 2: mover
;; 3: rotator
;; 4: sensor
;; 5: compute
;; 6: interact

to init-custom-robot
  create-gridarians 1 [
    let seed-patch patch-at 0 0
    let cell-list [[0 0 1] [-1 -1 2] [1 1 4] [1 2 4]]
    setxy ([pxcor] of seed-patch) ([pycor] of seed-patch)
    set heading 0
    set color white
    ;set hidden? true
    let index 0
    hatch-cells 4[
      set id [who] of myself
      let my-patch patch-at (xcor + item 0 item index cell-list) (xcor + item 1  item index cell-list)
      ;setxy (xcor + item index item 0 cell-list) (xcor + item index item 1 cell-list)
      setxy ([pxcor] of my-patch) ([pycor] of my-patch)
      set cell-type item 2 item index cell-list
      set direction 0
      create-link-from myself [tie hide-link]
      set index index + 1
    ]
    ;embody
  ]
end

to init-bodies [num]
  create-gridarians num [
    let seed-patch one-of patches with [count turtles-here = 0]
    set my-score 0
    move-to seed-patch
    set heading 0
    set color white
    set shape "dot"
    hatch-cells 1 [
      set id [who] of myself
      set cell-type 1
      set direction 0
      set health 1
      set shape "dot"
      create-link-from myself [tie hide-link]
    ]
    ;(cgp:random-brain <inputs> <outputs> <columsback> <rows> <cols> [0 1 2 3 4])
    (cgp:random-brain num-body-inputs num-body-outputs body-lvlsback num-body-rows num-body-cols [0 5 6 10 12 19])
    ;(cgp:random-brain-n 0 num-body-inputs num-body-outputs body-lvlsback num-body-rows num-body-cols [0 5 6 10 12 19])

    repeat random 10 [
      mutate-body 1 0
    ]
  ]
end

to update-body [pre?]
  ask link-neighbors [
    let cell-vars get-cell-vars-list
    print cell-vars
    let cell-updates []
    ask myself [set cell-updates cgp:evaluate cell-vars]
    print cell-updates
    let update-list decode-cell-updates pre? cell-updates
    print update-list
    update-cell-vars update-list
  ]
end

to-report get-cell-vars-list
  let encoded-type encode-var cell-type (fput 1 available-cell-types)
  let encoded-direction encode-var heading [0 90 180 270]
  let my-id id
  let avg-cell-health mean [health] of cells with [id = my-id]
  let agent-score ([my-score] of myself) / (1 + mean [my-score] of gridarians)
  report (list health encoded-type encoded-direction avg-cell-health agent-score)
end

to-report encode-var [var lst]
  report -1 + (2 / (length lst - 1)) * (item 0 fp:find-indices [x -> x = var] lst)
end

to-report decode-cell-updates [pre? lst]
  ;; [health type direction]
  let h sign (item 0 lst) * ifelse-value pre? [delta-pre-cell-health][delta]
  let t item 1 lst
  set t (ifelse-value t >= threshold-cell-type-inc [1] t <= threshold-cell-type-dec [-1][0])
  let d item 2 lst
  set d (ifelse-value d >= threshold-cell-dir-inc [1] d <= threshold-cell-dir-dec [-1][0])
  report (list h t d)
end

to update-cell-vars [lst]
  set health trunc (health + (item 0 lst))
  if cell-type != 1 [set cell-type add-cell-vars cell-type (item 1 lst) available-cell-types]
  ;; adjust direction for rot cells

  (ifelse cell-type = 2 or cell-type = 4 [
    set heading add-cell-vars heading ((item 2 lst) * 90) [0 90 180 270]
    ] cell-type = 3 [
    set direction add-cell-vars direction ((item 2 lst) * 180) [90 270]
    ])
  update-cell-symbol
end

to-report add-cell-vars [v i lst]
  if not member? i [-1 0 1 -90 90 -180 180] [print "cell var update error" report false]
  if i = 0 [report v]
  let max-val max lst
  let min-val min lst
  (ifelse (v + i) <= max-val and (v + i) >= min-val [report v + i]
    (v + i) > max-val [report min-val]
    [report max-val])
end

to update-cell-symbol
  if cell-type = 2 [
    set shape "arrow2"
  ]
  if cell-type = 3 [
    ifelse direction = 90 [set shape "clock-wise"][set shape "counter-clock-wise"]
  ]
  if cell-type = 4 [
    set shape "T"
  ]
  if cell-type = 5 [
    set shape "square3"
  ]
  if cell-type = 6 [
    set shape "x"
  ]
end

to mutate-body [birth-prob death-prob]
  if random-float 1 < birth-prob and count link-neighbors <= max-cells-per-body [
    let possible-locs patch-set [neighbors4 with [count turtles-here = 0]] of link-neighbors
    ;print possible-locs
    set possible-locs possible-locs with [available?]
    if any? possible-locs [
      ;print possible-locs
      let loc one-of possible-locs
      ;print loc
      hatch-cells 1 [
        move-to loc
        set id [who] of myself
        create-link-from myself [tie hide-link]
        set cell-type one-of available-cell-types
        if cell-type = 2 [
          set direction one-of [0 90 180 270]
          set shape "arrow2"
        ]
        if cell-type = 3 [
          set direction one-of [90 270]
          ifelse direction = 90 [set shape "clock-wise"][set shape "counter-clock-wise"]
        ]
        if cell-type = 4 [
          set direction one-of [0 90 180 270]
          set shape "T"
        ]
        if cell-type = 5 [
          set direction 0
          set shape "square3"
        ]
        if cell-type = 6 [
          set direction one-of [0 90 180 270]
          set shape "x"
        ]
        set heading direction
      ]
    ]
  ]
  if random-float 1 < death-prob [
    if any? link-neighbors with [cell-type != 1] [
      let iid [id] of one-of link-neighbors
      find-cutpoints iid
      ask one-of link-neighbors with [cell-type != 1] [
        if not is-cutpoint? [die]
      ]
    ]
  ]
end

to-report available?
  report (ifelse-value
    self = nobody [false]
    count turtles-here > 0 [false]
    [true]
  )
end

to visualize-cells
  ;let color-list [blue green red yellow cyan magenta brown orange lime sky pink]
  let color-list palette:scheme-colors "Qualitative" "Set1" min list 9 (count gridarians)
  ask patches [
    set pcolor black
    if count cells-here = 1 and check-overlap [
      let c one-of cells-here
      (ifelse cell-visualization = "by-cell-type" [
        (ifelse [cell-type] of c = 1 [set pcolor orange]
          [cell-type] of c = 2 [set pcolor green]
          [cell-type] of c = 3 [set pcolor green - 1]
          [cell-type] of c = 4 [set pcolor blue]
          [cell-type] of c = 5 [set pcolor magenta]
          [cell-type] of c = 6 [set pcolor red]
          [set pcolor black])
        ]
        cell-visualization = "by-agent" [
          let cid [id] of c mod 9 ;change later
          set pcolor item cid color-list
      ])
    ]
  ]
  ifelse visualize-cell-type-symbol? [
    ask cells [set hidden? false]
  ] [
    ask cells [set hidden? true]
    ask gridarians [set hidden? true]
  ]
end

to go
  ask gridarians [
    if random-float 1 < 0.2 [
      mutate-body 0.4 0.6
    ]
    sense
    interact
    ;move-random
    move-morph-limited
    ;move-morph
  ]
  replenish-balls
  visualize-cells
  tick
end

to sense
  let obs get-observation-vector
end

to-report get-observation-vector
  let inputs []
  if any? link-neighbors with [cell-type = 4][
    foreach sort link-neighbors with [cell-type = 4] [sensor ->
      ask sensor [set inputs lput get-sensor-input inputs]
    ]
  ]
  ;print inputs
  report inputs
end

;; 0: empty
;; 1: my cell
;; 2: other cell
;; 3: wall
;; 4: ball

to-report get-sensor-input
  let flag? true
  let dist 0
  let input []
  while [flag?][
    set dist dist + 1
    set input list dist 0
    ifelse patch-ahead dist != nobody [
      ask patch-ahead dist [
        if any? turtles-here [
          let i 5
          let my-id 0.1
          if any? cells-here [
            set my-id [id] of one-of cells-here
          ]
          (ifelse any? cells-here with [id = my-id] [set i 1]
            any? cells-here with [id != my-id] [set i 2]
            any? walls-here [set i 3]
            any? balls-here [set i 4]
            [set i 5])
          set input list dist i
          set flag? false
        ]
      ]
    ] [
      set input list dist 3
      ;print dist
      set flag? false
    ]
    if dist >= sensing-distance [set flag? false]
  ]
  report input
end

to interact
  let score 0
  if any? link-neighbors with [cell-type = 6] [
    ask link-neighbors with [cell-type = 6] [
      if any? neighbors4 with [any? balls-here] [
        ask neighbors4 with [any? balls-here] [
          ask balls-here [die]
          set score score + 1
        ]
      ]
    ]
    set my-score my-score + score
  ]
end

to move-random
  let dir one-of [0 45 90 135 180 225 270 315]
  let cw? one-of [true false]
  let rot? ifelse-value random-float 1 < 0.2 [true][false]
  change-pos dir
  if rot? [rotate cw?]
end

to move-morph-limited
  let dir get-pos-dir
  change-pos dir
  let cw? get-rot-dir
  rotate cw?
end

to-report get-pos-dir
  let bool-list [0 0 0 0]
  let dir-list  [0 90 180 270]
  foreach range 4 [i ->
    if any? link-neighbors with [cell-type = 2 and heading = item i dir-list][
      if random-float 1 < 0.5 [
        set bool-list replace-item i bool-list 1
      ]
      ;set bool-list replace-item i bool-list 1
    ]
  ]
  let xv (ifelse-value
    item 1 bool-list = 1 and item 3 bool-list = 0 [1]
    item 1 bool-list = 0 and item 3 bool-list = 1 [-1]
    [0])
  let yv (ifelse-value
    item 0 bool-list = 1 and item 2 bool-list = 0 [1]
    item 0 bool-list = 0 and item 2 bool-list = 1 [-1]
    [0])
  ;print bool-list
  report ifelse-value not (xv = 0 and yv = 0) [atan xv yv] ["stop"]
end

to-report get-rot-dir
  let r? false
  let l? false
  if any? link-neighbors with [cell-type = 3 and direction = 90]  [if random-float 1 < 0.3 [set r? true]]
  if any? link-neighbors with [cell-type = 3 and direction = 270] [if random-float 1 < 0.3 [set l? true]]
  ifelse r? xor l? [
    report ifelse-value r? [true] [false]
  ] [
    report "stop"
  ]
end

to move-morph
  let dirs get-pos-vecs
  ;print dirs
  foreach dirs [d -> change-pos d]
  let rots get-rot-vecs
  ;print rots
  foreach rots [cw? -> rotate cw?]
end

to-report get-pos-vecs
  let vecs []
  let dir-list  [0 90 180 270]
  foreach dir-list [d ->
    if any? link-neighbors with [cell-type = 2 and heading = d][
      let n count link-neighbors with [cell-type = 2 and heading = d]
      repeat n [
        if random-float 1 < 0.5 [
          set vecs lput d vecs
        ]
      ]
    ]
  ]
  report ifelse-value empty? vecs [["stop"]][vecs]
end

to-report get-rot-vecs
  let vecs []
  let dir-list [90 270]
  let cw?-list [true false]
  foreach range 2 [i ->
    if any? link-neighbors with [cell-type = 3 and direction = item i dir-list][
      let n count link-neighbors with [cell-type = 3 and direction = item i dir-list]
      repeat n [
        if random-float 1 < 0.3 [
          set vecs lput (item i cw?-list) vecs
        ]
      ]
    ]
  ]
  report ifelse-value empty? vecs [["stop"]][vecs]
end

to change-pos [dir]
  if dir != "stop"[
    if check-pos-change? dir [
      move-to patch-at-heading-and-distance dir 1
    ]
  ]
end

to rotate [cw?]
  if cw? != "stop" [
    if check-rotate? xcor ycor cw? [
      ifelse cw? [ rt 90 ] [ lt 90 ]
    ]
  ]
end

to-report check-pos-change? [dir]
  let flag true
  ask link-neighbors [
    let patch-to-check patch-at-heading-and-distance dir 1
    if not check-patch? patch-to-check [ set flag false ]
  ]
  report flag
end

to-report check-rotate? [x0 y0 cw?]
  let flag true
  ask link-neighbors [
    let patch-to-check ifelse-value cw? [
      patch (x0 - y0 + ycor) (y0 + x0 - xcor)
    ] [
      patch (x0 + y0 - ycor) (y0 - x0 + xcor)
    ]
    if not check-patch? patch-to-check [ set flag false ]
  ]
  report flag
end

to-report check-patch? [next-patch]
  let my-id id
  report (ifelse-value
    next-patch = nobody [false]
    ([count cells-here with [id != my-id ]] of next-patch >= 1) or
    ([any? walls-here] of next-patch) or
    ([any? balls-here] of next-patch) [false]
    [true]
  )
end

to-report check-overlap
  (ifelse count turtles-here with [breed != cells] > 1 [
    print "overlap error"
    report false
    ]
    count cells-here > 1 [
      print "overlap error"
      report false
    ] [
      report true
    ])
end

to replenish-balls
  if count balls < num-balls [
    let n num-balls - (count balls)
    ask n-of n patches with [not any? turtles-here][
      sprout-balls 1 [
        set shape "circle"
        set color yellow
      ]
    ]
  ]
end

to find-cutpoints [iid]
  ;; Tarjan's algorithm for find articulation points
  ask cells with [id = iid] [set is-cutpoint? false]
  let n count cells with [id = iid]
  set time 0
  set vis map [-> false] range n
  set tin map [-> -1] range n
  set low map [-> -1] range n
  foreach range n [i ->
    if not (item i vis) [
      dfs iid i -1
    ]
  ]
end

to dfs [iid v p]
  ;; Depth-First-Search Tree algorithm
  set vis replace-item v vis true
  set time time + 1
  set tin replace-item v tin time
  set low replace-item v low time
  let children 0
  foreach adj iid v [ti ->
    if ti != p [
      ifelse item ti vis [
        set low replace-item v low (min list (item v low) (item ti tin))
      ] [
        dfs iid ti v
        set low replace-item v low (min list (item v low) (item ti low))
        if item ti low >= item v tin and p != -1 [
          ask get-vertex iid v [
            set is-cutpoint? true
          ]
        ]
        set children children + 1
      ]
    ]
  ]
  if p = -1 and children > 1 [
    ask get-vertex iid v [
      set is-cutpoint? true
    ]
  ]
end

to-report adj [iid i]
  ;; Returns adjacency list
  let tlist sort cells with [id = iid]
  let v item i tlist
  let pn [neighbors4] of v
  let alist []
  let wlist []
  ask pn [
    if any? cells-here with [id = iid] [
      set alist lput (one-of cells-here with [id = iid]) alist
    ]
  ]
  foreach alist [a ->
    set wlist lput (item 0 fp:find-indices [x -> x = a] tlist) wlist
  ]
  report wlist
end

to-report get-vertex [iid i]
  ;; Returns cell from vertex number
  report item i sort cells with [id = iid]
end

to-report trunc [x]
  if x < -1 [set x -1]
  if x > 1 [set x 1]
  report x
end

to-report sign [x]
  report math:signum x
end


to test
  ;test-fd-move
  test-change-pos
  test-rotate
  tick
end

to test-change-pos
  ask gridarians [
    ;let dir one-of [0 90 180 270]
    let dir one-of [0 45 90 135 180 225 270 315]
    print check-pos-change? dir
    if check-pos-change? dir [
      move-to patch-at-heading-and-distance dir 1
    ]
  ]
  visualize-cells
end

to test-rotate
  ask gridarians [
    ;setxy (max-pxcor - 1) (min-pycor + 1)
    let dir one-of [true false]
    ;let dir one-of [0 45 90 135 180 225 270 315]
    print check-rotate? xcor ycor dir
    if check-rotate? xcor ycor dir [
      ifelse dir [ rt 90 ] [ lt 90 ]
    ]
  ]
  visualize-cells
end



to draw-cells
  if mouse-down? [
    ask patch mouse-xcor mouse-ycor [
      set pcolor white
    ]
    display
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
285
10
879
605
-1
-1
11.5
1
10
1
1
1
0
0
0
1
-25
25
-25
25
1
1
1
ticks
15.0

BUTTON
135
95
235
130
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
15
95
115
130
NIL
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

BUTTON
15
320
118
355
NIL
draw-cells
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
135
150
235
185
NIL
test
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SWITCH
15
200
235
233
visualize-cell-type-symbol?
visualize-cell-type-symbol?
0
1
-1000

CHOOSER
15
240
153
285
cell-visualization
cell-visualization
"by-cell-type" "by-agent"
0

SLIDER
15
15
175
48
init-num-agents
init-num-agents
0
30
3.0
1
1
NIL
HORIZONTAL

SLIDER
15
55
175
88
max-cells-per-body
max-cells-per-body
0
100
15.0
1
1
NIL
HORIZONTAL

@#$#@#$#@
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow2
true
0
Polygon -7500403 true true 150 15 75 105 135 105 135 270 165 270 165 105 225 105

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

circuit
false
0
Rectangle -7500403 true true 15 15 30 285
Rectangle -7500403 true true 30 15 285 30
Rectangle -7500403 true true 30 270 285 285
Rectangle -7500403 true true 270 30 285 285
Rectangle -7500403 true true 44 127 104 187
Rectangle -7500403 true true 115 45 187 110
Rectangle -7500403 true true 188 181 250 241
Rectangle -7500403 true true 137 107 162 285
Rectangle -7500403 true true 60 185 86 225
Rectangle -7500403 true true 60 225 138 250
Rectangle -7500403 true true 207 154 231 185
Rectangle -7500403 true true 207 130 273 154

circuit2
false
0
Rectangle -7500403 true true 15 15 30 285
Rectangle -7500403 true true 30 15 285 30
Rectangle -7500403 true true 30 270 285 285
Rectangle -7500403 true true 270 30 285 285
Circle -7500403 true true 116 71 67
Circle -7500403 true true 71 161 67
Circle -7500403 true true 161 161 67
Polygon -7500403 true true 45 270 90 210 75 210 30 270 30 270
Polygon -7500403 true true 270 270 225 210 210 210 255 270 165 270
Polygon -7500403 true true 141 30 141 75 156 75 156 30 141 30

clock-wise
true
0
Circle -7500403 false true 60 60 180
Polygon -7500403 true true 223 205 283 115 163 115 223 205

counter-clock-wise
true
0
Circle -7500403 false true 60 60 180
Polygon -7500403 true true 223 93 283 183 163 183 223 93

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

die 1
false
0
Rectangle -7500403 true true 45 45 255 255
Circle -16777216 true false 129 129 42

dot
false
0
Circle -7500403 true true 90 90 120

eyeball
false
0
Circle -1 true false 22 20 248
Circle -7500403 true true 83 81 122
Circle -16777216 true false 122 120 44

eyeball2
false
0
Circle -1 true false 32 29 236
Circle -13791810 true false 88 85 122
Circle -16777216 true false 127 124 44

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

orbit 1
true
0
Circle -7500403 true true 116 11 67
Circle -7500403 false true 41 41 218

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

reverse-triangle
false
0
Polygon -7500403 true true 150 270 15 45 285 45

sensor
true
0
Circle -7500403 true true 0 -165 300
Rectangle -7500403 true true 135 105 165 300

sensor2
true
0
Circle -7500403 true true 0 -180 300
Rectangle -7500403 true true 135 105 165 300
Circle -16777216 true false 30 -150 240

small-arrow
true
0
Polygon -7500403 true true 150 75 105 150 195 150
Polygon -7500403 true true 135 149 135 225 139 234 147 239 154 239 161 234 165 226 165 149

small-reverse-triangle
true
0
Polygon -7500403 true true 150 255 45 90 255 90

spinner
true
0
Polygon -7500403 true true 150 0 105 75 195 75
Polygon -7500403 true true 135 74 135 150 139 159 147 164 154 164 161 159 165 151 165 74

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

square-dot
false
0
Circle -7500403 true true 90 90 120
Rectangle -7500403 true true 0 0 30 300
Rectangle -7500403 true true 0 270 300 300
Rectangle -7500403 true true 270 0 300 300
Rectangle -7500403 true true 0 0 300 30

square3
false
0
Rectangle -7500403 true true 0 0 30 300
Rectangle -7500403 true true 0 270 300 300
Rectangle -7500403 true true 270 0 300 300
Rectangle -7500403 true true 0 0 300 30

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

t
true
0
Polygon -7500403 true true 150 105 75 105 135 105 135 270 165 270 165 105 225 105
Rectangle -7500403 true true 60 90 240 105

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

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.3.0
@#$#@#$#@
setup-random repeat 20 [ go ]
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
@#$#@#$#@
1
@#$#@#$#@
