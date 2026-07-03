# Animation Language — GVaishanth GitHub Profile

## Design Philosophy

**Motion is telemetry.** Every animation on this profile communicates data, not decoration. If something moves, it's because a system is running, a value is changing, or a process is active.

All animations belong to one family: **engineering instrumentation**. Think F1 timing screens, oscilloscope traces, radar scopes, circuit board activity lights.

---

## Animation Families

### 1. STROKE DRAW — "Data is being written"

**What it does:** A line traces itself from start to finish using `stroke-dasharray` / `stroke-dashoffset`.

**Timing:** 2.4s ease-out (`keySplines="0.4 0 0.2 1"`)

**Used for:**
- Commit telemetry chart drawing in
- Hero waveform trace
- Architecture edge paths

**Meaning:** "Data is flowing into this view right now." The viewer watches the system populate itself.

```svg
<polyline points="..." stroke="#ff3340" stroke-width="1.8"
  stroke-dasharray="400" stroke-dashoffset="400">
  <animate attributeName="stroke-dashoffset"
    values="400;0" dur="2.4s"
    calcMode="spline" keySplines="0.4 0 0.2 1"/>
</polyline>
```

---

### 2. NODE PULSE — "This node is alive"

**What it does:** A dot breathes — opacity oscillates between 0.9 and 0.4 with a 2.8s cycle.

**Timing:** 2.8s continuous, with staggered `begin` offsets (0.25s per node)

**Used for:**
- Build grid repo health dots
- Architecture diagram corner nodes
- Active timeline markers

**Meaning:** "This component is running." The stagger creates a wave — you can see which systems are healthy at a glance.

```svg
<circle cx="120" cy="50" r="7" fill="#22c55e" opacity="0.9">
  <animate attributeName="opacity"
    values="0.9;0.4;0.9" dur="2.8s"
    begin="0.25s" repeatCount="indefinite"/>
</circle>
```

---

### 3. TELEMETRY SWEEP — "Scanning for signal"

**What it does:** A thin line sweeps horizontally across a chart area, fading in and out like an oscilloscope trace.

**Timing:** 3.2s loop with `keyTimes` for hold periods

**Used for:**
- Hero waveform overlay
- Commit chart scanning line
- Language graph highlight bar

**Meaning:** "We're reading this data right now." The sweep draws attention to what's current.

```svg
<line x1="0" y1="0" x2="0" y2="100" stroke="#ff3340" stroke-width="1" opacity="0">
  <animate attributeName="x1" values="0;400;400" dur="3.2s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="60;460;460" dur="3.2s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;0.6;0.6;0" dur="3.2s"
    keyTimes="0;0.1;0.8;1" repeatCount="indefinite"/>
</line>
```

---

### 4. CIRCUIT TRACE — "Data flowing through the system"

**What it does:** A small dot travels along a predefined SVG path using `animateMotion` with `mpath`.

**Timing:** 4.4s per loop, `rotate="auto"` so the dot faces forward

**Used for:**
- Architecture diagram data packets
- Hero circuit car dot
- Widget connection lines

**Meaning:** "Information is moving between these components." The closed loop proves the system is intact.

```svg
<circle r="2.5" fill="#ff3340">
  <animateMotion dur="4.4s" repeatCount="indefinite" rotate="auto">
    <mpath href="#system-path"/>
  </animateMotion>
</circle>
```

---

### 5. GLOW PULSE — "Activity at this point"

**What it does:** A dot with a Gaussian blur filter pulses in size and opacity, creating a soft glow effect.

**Timing:** 1.8s cycle (resting heartbeat rhythm)

**Used for:**
- Live status indicator
- Active project dot
- Endpoint of drawing lines

**Meaning:** "This is the active point right now." Faster than node pulse — draws immediate attention.

```svg
<circle cx="682" cy="34" r="2.5" fill="#ff3340" opacity="0.9">
  <animate attributeName="opacity"
    values="0.9;0.3;0.9" dur="1.8s"
    repeatCount="indefinite"/>
</circle>
```

---

### 6. VALUE CYCLE — "This number is changing"

**What it does:** Three overlapping text elements crossfade in a loop, creating the illusion of a changing value.

**Timing:** 8s for slow values (lap counter), 3.2s for fast values (temperature)

**Used for:**
- Lap counter (42 → 43 → 44)
- ERS percentage (84% → 71% → 96%)
- Tyre temperature (102.4 → 102.7 → 102.1)

**Meaning:** "This is a live readout, not a static label."

```svg
<text fill="#e6edf3" opacity="1">
  84%
  <animate attributeName="opacity" values="1;1;0;0;0;1" dur="8s" repeatCount="indefinite"/>
</text>
<text fill="#e6edf3" opacity="0">
  71%
  <animate attributeName="opacity" values="0;0;1;1;0;0" dur="8s" repeatCount="indefinite"/>
</text>
<text fill="#e6edf3" opacity="0">
  96%
  <animate attributeName="opacity" values="0;0;0;0;1;1" dur="8s" repeatCount="indefinite"/>
</text>
```

---

### 7. TIMELINE PROGRESSION — "Events unfolding in order"

**What it does:** Elements fade in sequentially with staggered `begin` times, creating a loading sequence.

**Timing:** 0.6s fade, 0.4s stagger between items

**Used for:**
- Engineering principles list
- Milestone timeline
- Feature lists

**Meaning:** "Read these in order — each builds on the last." The stagger guides the eye naturally.

```svg
<text opacity="0">
  Item text
  <animate attributeName="opacity" values="0;1" dur="0.6s"
    begin="0.4s" fill="freeze"/>
</text>
```

---

### 8. BAR FILL — "Loading to capacity"

**What it does:** A rectangle's `width` animates from 0 to its final value.

**Timing:** 1.2s with 0.15s stagger per bar

**Used for:**
- Language distribution graph
- Skill bars
- Progress indicators

**Meaning:** "This is how much of the total this represents." The animation shows the comparison visually.

```svg
<rect x="150" y="32" width="280" height="10" rx="4" fill="#ff3340">
  <animate attributeName="width" from="0" to="280"
    dur="1.2s" begin="0.15s" fill="freeze"/>
</rect>
```

---

### 9. MARQUEE SCROLL — "Always more to see"

**What it does:** Text translates horizontally in an infinite loop, clipped to a container.

**Timing:** 38s continuous, `calcMode="linear"` for constant speed

**Used for:**
- Project ticker ribbon
- Scrolling announcements
- Status banners

**Meaning:** "There's always more information flowing." The endless loop suggests a live feed.

```svg
<text>
  VELOCITY ◆ CRICKET ◆ CRPAPP
  <animateTransform attributeName="transform" type="translate"
    values="0,0;-1040,0" dur="38s"
    repeatCount="indefinite" calcMode="linear"/>
</text>
```

---

## Timing System

All animations use these standard durations:

| Duration | Use | Feel |
|----------|-----|------|
| **1.8s** | Glow pulse | Heartbeat — alive |
| **2.4s** | Stroke draw | Data arriving |
| **2.8s** | Node pulse | System health |
| **3.2s** | Fast value cycle, sweep | Rapid readout |
| **4.4s** | Circuit trace | System loop |
| **8s** | Slow value cycle | Deliberate change |
| **38s** | Marquee | Ambient flow |

**Easing:** Only two easing curves exist in the system:
- **`keySplines="0.4 0 0.2 1"`** — ease-out (used for stroke draws, everything that "arrives")
- **`calcMode="linear"`** — no easing (used for continuous loops, marquee, sweeps)

**Color:** Only `#ff3340` (Ferrari red) animates. Everything else is static. This makes motion meaningful — when you see red moving, it's the active system.

---

## Rules

1. **No random animation.** Every motion communicates data: system health, data flow, or live status.
2. **Red moves, gray doesn't.** Only active elements animate in red. Static elements stay in the muted palette.
3. **Stagger creates rhythm.** When multiple elements animate, they're offset (0.25s, 0.4s, 0.5s) to create a wave pattern.
4. **Loops are infinite or freeze.** Either an animation repeats forever (system is running) or it draws once and freezes (data has arrived).
5. **Motion proves the system.** If an animation stops, the system has stopped. The viewer can diagnose health from motion alone.
6. **No bounce, no elastic.** No `keySplines` that overshoot. No spring physics. Everything is controlled, measured, engineered.
7. **Dots face forward.** `rotate="auto"` on all `animateMotion` elements so traveling dots orient along their path.
8. **Glow is subtle.** Blur radius never exceeds 6px. Opacity never exceeds 0.15 for ambient glow.

---

## Animation Map

| Widget | Animations Used |
|--------|----------------|
| **Hero banner** | Stroke draw (waveform), Glow pulse (endpoint), Circuit trace (car), Value cycle (ERS/T°/lap), Telemetry sweep |
| **current-build** | Glow pulse (status dot) |
| **build-grid** | Node pulse (6 staggered dots) |
| **garage-timeline** | Node pulse (active nodes), Stroke draw (timeline line) |
| **commit-telemetry** | Stroke draw (chart line), Glow pulse (endpoint dot) |
| **language-graph** | Bar fill (5 staggered bars) |
| **architecture** | Circuit trace (2 data packets), Node pulse (4 corner nodes) |
| **principles** | Timeline progression (5 sequential items) |
| **oss-journey** | Timeline progression (milestones), Glow pulse (current node) |
| **ticker** | Marquee scroll |

Every animation on the profile belongs to one of these 9 families. A visitor should be able to look at any moving element and immediately understand what it means.
