# GVaishanth — GitHub Profile Redesign

## Vision

**The profile IS the product.** Not a document about engineering — an engineering artifact itself.

When an experienced GitHub user lands here, they should immediately understand:
1. This person builds simulations
2. This person thinks in systems
3. This person ships polished work
4. This person understands motion as information

No badges. No "Hi I'm". No stats plugins. No generic developer aesthetics.

The profile is a **telemetry dashboard** that tells the story of an engineer through motion, data, and deliberate design.

---

## Design System

### Colors
```
Background:    #0b0d11  (GitHub dark, but warmer)
Card surface:  #11151c  (elevated surfaces)
Border:        #1c212d  (edge definition)
Divider:       #181d27  (internal separation)

Primary text:  #e6edf3  (GitHub's light text)
Secondary:     #8b949e  (descriptions)
Tertiary:      #6e7681  (metadata)
Faint:         #484f58  (section labels)

Accent:        #ff3340  (Ferrari red — ONLY for active/live)
Green:         #22c55e  (healthy systems)
Blue:          #58a6ff  (secondary data)
Purple:        #a78bfa  (quantum/AI)
Orange:        #f97316  (data/analysis)
```

**Rule:** Red only animates. Everything else is static. Motion = meaning.

### Typography
```
Data/labels:   JetBrains Mono (or SF Mono fallback)
Prose:         Inter (or SF Pro Display fallback)
```

### Animation Language
9 families. All purposeful. All from engineering instrumentation:
1. **Stroke Draw** — "Data is being written" (2.4s ease-out)
2. **Node Pulse** — "This node is alive" (2.8s × stagger)
3. **Telemetry Sweep** — "Scanning for signal" (3.2s)
4. **Circuit Trace** — "Data flowing through system" (4.4s loop)
5. **Glow Pulse** — "Activity at this point" (1.8s heartbeat)
6. **Value Cycle** — "This number is changing" (8s crossfade)
7. **Timeline Progression** — "Events unfolding in order" (0.6s stagger)
8. **Bar Fill** — "Loading to capacity" (1.2s stagger)
9. **Marquee Scroll** — "Always more to see" (38s continuous)

---

## Profile Structure

### 1. Mission Control (Hero)
Not a banner. An actual telemetry dashboard with:
- Animated waveform drawing in (stroke draw)
- Pulsing status dot (glow pulse)
- Circuit trace with orbiting car (circuit trace)
- Cycling telemetry values (value cycle)
- System metrics panel

This IS the introduction. The visitor doesn't read "I build simulations" — they see a simulation dashboard that proves it.

### 2. The Garage
Not a skills list. A tool wall with numbered stations:
- Each domain as a physical tool slot
- No percentages, no bars, no charts
- Just honest labels: what I do, with what tools
- Blockquote aesthetic, monospace tags

### 3. Blueprints
Not a "how I think" text section. A system diagram that:
- Shows the architecture of Velocity
- Has animated data packets orbiting the loop
- Proves the system works through motion
- Engineering table mapping approach → rule → implementation

### 4. Featured Builds
Not images + text. Apple-style product cards:
- Each project as a premium product page
- Cover image, complexity meter, tech pills
- Architecture summary, stats row
- "Did You Know" facts
- PLAY and GITHUB buttons
- Each with unique accent color

### 5. Black Box
Not a "lessons learned" list. A flight recorder:
- Numbered findings from v1→v4 refactors
- Forensic tone: "Evidence" rows
- Double-border ASCII headers
- Each lesson is a recovered data point

### 6. On Air
Not "currently working on." A broadcast studio:
- Live session table with signal indicators
- Progress bar ASCII art
- Build grid widget (pulsing health dots)
- Garage timeline widget (activity positions)
- Ticker ribbon (scrolling project names)

### 7. Horizon
Not "future plans." A fading gradient into uncertainty:
- Dotted arrows fading out
- Blockquote exploration items
- "exploring, not promising" disclaimer
- Soft, open-ended tone

---

## Technical Implementation

### SVG Components (all handcrafted)
- `hero-simulations.svg` — Main dashboard (1280×480)
- `current-build.svg` — Live project card (720×120)
- `build-grid.svg` — 6-repo health grid (720×100)
- `garage-timeline.svg` — Activity timeline (720×110)
- `commit-telemetry.svg` — 12-week chart (720×138)
- `language-graph.svg` — Bar chart (720×110)
- `oss-journey.svg` — Milestone timeline (720×180)
- `architecture.svg` — System diagram (720×170)
- `principles.svg` — Philosophy card (720×160)
- `ticker.svg` — Scrolling ribbon (720×44)
- `showcase-*.svg` — 6 product cards (800×720 each)

### GitHub Action
- Runs every 6 hours
- Fetches repo data via REST API
- Fetches contribution calendar via GraphQL
- Regenerates all SVG widgets
- Commits back with `[skip ci]`
- Pure Python stdlib, zero dependencies

### PNG Fallbacks
- Every SVG has a PNG equivalent
- GitHub renders PNG when SVG animations aren't supported
- Generated via cairosvg in the workflow

---

## What Makes This Iconic

1. **The profile proves the engineer's skills by existing.** The SVG telemetry, the F1 aesthetic, the architecture diagrams — they're not decoration, they're evidence.

2. **Every animation communicates data.** If something moves, it's because a system is running, a value is changing, or a process is active. No decorative motion.

3. **No external dependencies.** No github-readme-stats. No shields.io. No typing GIFs. No Spotify widgets. Everything is handcrafted SVG + pure Markdown.

4. **The sections flow like a product landing page.** Not a resume. A journey: mission → tools → architecture → products → lessons → current → future.

5. **Each section has a unique visual identity.** Mission Control (terminal), Garage (tool wall), Blueprints (technical drawings), Showroom (gallery), Black Box (forensics), On Air (broadcast), Horizon (open sky).

6. **Apple/Linear-level polish.** Real typography hierarchy. Real spacing systems. Real animation physics. No bounce, no elastic, no overshoot. Controlled, measured, engineered.

7. **The animation language is unified.** 9 families, 7 durations, 2 easings. A visitor can diagnose system health from motion alone.

---

## Files to Create

1. `README.md` — The profile itself
2. `assets/hero-simulations.svg` — Hero dashboard
3. `assets/hero-simulations.png` — Hero fallback
4. `assets/widgets/*.svg` — 9 widget SVGs
5. `assets/widgets/*.png` — 9 widget PNGs
6. `assets/showcase-*.svg` — 6 product cards
7. `assets/showcase-*.png` — 6 product card PNGs
8. `assets/cover-*.png` — Project covers (already exist)
9. `scripts/build_widgets.py` — Widget generator
10. `.github/workflows/widgets.yml` — Auto-refresh action
11. `ANIMATION_LANGUAGE.md` — Documentation (optional)

---

## Success Metrics

- A recruiter remembers it after one week → The telemetry dashboard is unforgettable
- A developer bookmarks it → They want to see how it works
- People fork it → They've never seen a profile that IS a product

This isn't a GitHub profile. It's an engineering artifact that happens to live on GitHub.
