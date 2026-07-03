#!/usr/bin/env python3
"""Telemetry Widgets — GVaishanth

Generates SVG dashboard components for GitHub profile.
Each widget is a self-contained UI panel — not a stat badge.
Pure stdlib. No dependencies. No plugins.

Design language: dark cards, monospace data, red accent (#ff3340),
subtle animations that communicate live status.

Widgets (9):
  1. current-build      — Live project with pulsing status dot
  2. garage-timeline    — Horizontal activity timeline, staggered pulses
  3. commit-telemetry   — 12-week line chart with draw-in animation
  4. language-graph     — Horizontal bars with fill animation
  5. architecture       — System diagram with orbiting data packets
  6. principles         — Numbered philosophy, sequential fade-in
  7. build-grid         — 6-repo health grid, color-coded pulses
  8. build-ticker       — Scrolling marquee ribbon
  9. oss-journey        — Account milestones with cycling values
"""

import json, os, sys, datetime, urllib.request
from pathlib import Path

# ── Paths ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
WIDGETS = ROOT / "assets" / "widgets"
WIDGETS.mkdir(parents=True, exist_ok=True)
USER = "GVaishanth"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

# ── Design System ─────────────────────────────────────
C_BG     = "#0b0d11"
C_CARD   = "#11151c"
C_BORDER = "#1c212d"
C_DIV    = "#181d27"
C_TEXT   = "#e6edf3"
C_SUB    = "#8b949e"
C_MUTED  = "#6e7681"
C_FAINT  = "#484f58"
C_ACCENT = "#ff3340"
C_GREEN  = "#22c55e"
C_YELLOW = "#eab308"
C_BLUE   = "#58a6ff"

MONO = "'JetBrains Mono','SF Mono',Consolas,ui-monospace,monospace"
SANS = "'Inter','SF Pro Display',system-ui,-apple-system,sans-serif"


# ── API helpers ────────────────────────────────────────
def gh_json(url):
    h = {"User-Agent": "telemetry/1.0", "Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=12) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  warn: {e}", file=sys.stderr)
        return None


def gh_gql(query, variables=None):
    if not TOKEN:
        return None
    try:
        body = json.dumps({"query": query, "variables": variables or {}}).encode()
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=body,
            headers={"Authorization": f"Bearer {TOKEN}",
                     "Content-Type": "application/json",
                     "User-Agent": "telemetry/1.0"},
        )
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read()).get("data")
    except Exception:
        return None


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;") \
                    .replace(">", "&gt;").replace('"', "&quot;")


# ── SVG card wrapper ──────────────────────────────────
def _card(w, h, content, title=None):
    hdr = f'<text x="28" y="24" fill="{C_FAINT}" font-family="{MONO}" font-size="10" letter-spacing="2">{title}</text>' if title else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
  <rect width="{w}" height="{h}" rx="14" fill="{C_CARD}"/>
  <rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="14" fill="none" stroke="{C_BORDER}"/>
  {hdr}
  {content}
</svg>'''


# ── Fallback data ─────────────────────────────────────
FALLBACK_REPOS = [
    {"name": "GVaishanth", "description": "Profile — Simulations Engineer",
     "language": "Python", "pushed_at": "2026-07-03T00:00:00Z", "size": 7461},
    {"name": "GroupDNA", "description": "WhatsApp Chat Analyzer",
     "language": "Jupyter Notebook", "pushed_at": "2026-06-29T00:00:00Z", "size": 245},
    {"name": "Salary_Decoder", "description": "Bangalore Tech Salary EDA",
     "language": "Jupyter Notebook", "pushed_at": "2026-06-29T00:00:00Z", "size": 45},
    {"name": "CRPapp", "description": "Predictive Crash Resilience",
     "language": "Kotlin", "pushed_at": "2026-06-27T00:00:00Z", "size": 22421},
    {"name": "Velocity", "description": "F1 Constructor Championship",
     "language": "JavaScript", "pushed_at": "2026-06-22T00:00:00Z", "size": 677},
    {"name": "Computer-Cricket", "description": "Hand Cricket Simulator",
     "language": "HTML", "pushed_at": "2026-06-10T00:00:00Z", "size": 939},
    {"name": "Quantum-Tic-Tac-Toe", "description": "Quantum State Resolution",
     "language": "HTML", "pushed_at": "2026-05-10T00:00:00Z", "size": 24},
]

SHORT_MAP = {"Velocity": "VEL", "Computer-Cricket": "CKT", "CRPapp": "CRP",
             "Quantum-Tic-Tac-Toe": "QTT", "GroupDNA": "DNA",
             "Salary_Decoder": "SAL", "GVaishanth": "PRO"}


# ═══════════════════════════════════════════════════════
#  1. CURRENT BUILD — pulsing status dot
#  Meaning: "This project is live right now"
#  Cycle: 1.8s = resting heartbeat
# ═══════════════════════════════════════════════════════
def build_current_build(repo):
    name = repo.get("name", "—")
    desc = (repo.get("description") or "Open source · Learning")
    desc = (desc[:72] + "…") if len(desc) > 74 else desc
    lang = repo.get("language") or "—"
    pushed_at = repo.get("pushed_at", "")
    try:
        d = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))).days
        pushed_txt = f"{d}d ago" if d > 0 else "today"
    except Exception:
        pushed_txt = "—"

    body = f'''  <rect x="0" y="0" width="4" height="120" rx="14" fill="{C_ACCENT}"/>
  <text x="32" y="32" fill="{C_FAINT}" font-family="{MONO}" font-size="10" letter-spacing="2">CURRENT BUILD</text>
  <text x="32" y="58" fill="{C_TEXT}" font-family="{SANS}" font-size="22" font-weight="650">{esc(name)}</text>
  <text x="32" y="78" fill="{C_SUB}" font-family="{SANS}" font-size="13">{esc(desc)}</text>
  <g font-family="{MONO}" font-size="11" fill="{C_SUB}" text-anchor="end">
    <text x="692" y="38"><tspan fill="{C_ACCENT}">●</tspan> ACTIVE</text>
    <text x="692" y="58"><tspan fill="{C_MUTED}">●</tspan> {esc(lang)}</text>
    <text x="692" y="78" fill="{C_FAINT}">updated {pushed_txt}</text>
  </g>
  <!-- heartbeat pulse: 1.8s cycle -->
  <circle cx="682" cy="34" r="2.5" fill="{C_ACCENT}" opacity="0.9">
    <animate attributeName="opacity" values="0.9;0.3;0.9" dur="1.8s" repeatCount="indefinite"/>
  </circle>'''
    return _card(720, 120, body)


# ═══════════════════════════════════════════════════════
#  2. GARAGE TIMELINE — staggered node pulses
#  Meaning: "Each node is independently alive"
#  Cycle: 3s × 0.5s stagger
# ═══════════════════════════════════════════════════════
def build_garage_timeline(repos):
    def parse(r):
        try:
            return datetime.datetime.fromisoformat(
                r.get("pushed_at", "2000-01-01T00:00:00Z").replace("Z", "+00:00"))
        except Exception:
            return datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)

    now = datetime.datetime.now(datetime.timezone.utc)
    items = []
    for r in repos[:6]:
        days = max(0, (now - parse(r)).days)
        t = max(0.02, min(1.0, 1.0 - days / 90.0))
        short = SHORT_MAP.get(r["name"], r["name"][:3].upper())
        items.append({"short": short, "days": days, "t": t, "active": days <= 21})

    W, H, L, R, y0 = 720, 110, 36, 684, 54
    nodes = ""
    for i, it in enumerate(items):
        x = L + it["t"] * (R - L)
        fill = C_ACCENT if it["active"] else C_CARD
        stroke = C_ACCENT if it["active"] else "#2a303c"
        label = C_SUB if it["active"] else C_MUTED

        pulse = ""
        if it["active"]:
            pulse = f'''<circle cx="{x:.1f}" cy="{y0:.1f}" r="12" fill="{C_ACCENT}" opacity="0">
    <animate attributeName="opacity" values="0;0.12;0" dur="3s" repeatCount="indefinite" begin="{i*0.5}s"/>
    <animate attributeName="r" values="6;14;6" dur="3s" repeatCount="indefinite" begin="{i*0.5}s"/>
  </circle>'''
        nodes += f'''  {pulse}
  <circle cx="{x:.1f}" cy="{y0:.1f}" r="6" fill="{fill}" stroke="{stroke}" stroke-width="1.7"/>
  <text x="{x:.1f}" y="{y0-14:.1f}" text-anchor="middle" fill="{label}" font-family="{MONO}" font-size="10.5" font-weight="600">{it["short"]}</text>
  <text x="{x:.1f}" y="{y0+22:.1f}" text-anchor="middle" fill="{C_FAINT}" font-family="{MONO}" font-size="9">{it["days"]}d</text>
'''

    body = f'''<text x="28" y="24" fill="{C_FAINT}" font-family="{MONO}" font-size="10" letter-spacing="2">GARAGE — ACTIVITY</text>
  <text x="692" y="24" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">90d → now</text>
  <line x1="{L}" y1="{y0}" x2="{R}" y2="{y0}" stroke="{C_DIV}" stroke-width="2"/>
  {nodes}'''
    return _card(W, H, body)


# ═══════════════════════════════════════════════════════
#  3. COMMIT TELEMETRY — draw-in line chart
#  Meaning: "Data is flowing into this chart"
#  Cycle: 2.4s draw-in (one-shot, then pulses)
# ═══════════════════════════════════════════════════════
def build_commit_telemetry(series=None):
    if series is None or len(series) < 2:
        series = [1, 0, 3, 5, 2, 4, 0, 1, 6, 3, 2, 4]
        sample = True
    else:
        sample = False

    W, H = 720, 138
    pl, pr, pt, pb = 48, 24, 34, 28
    pw, ph = W - pl - pr, H - pt - pb
    n = len(series)
    mv = max(1, max(series))

    pts = []
    for i, v in enumerate(series):
        x = pl + i / max(n - 1, 1) * pw
        y = pt + ph * (1 - v / mv)
        pts.append(f"{x:.1f},{y:.1f}")

    points = " ".join(pts)
    area = points + f" {pl+pw:.1f},{pt+ph:.1f} {pl:.1f},{pt+ph:.1f}"
    total = sum(series)
    label = "sample data" if sample else f"total {total} · 12 wk"
    path_len = int(pw * 1.15)
    grid = "".join(
        f'<line x1="{pl}" y1="{pt+ph*g:.1f}" x2="{pl+pw:.1f}" y2="{pt+ph*g:.1f}" stroke="{C_DIV}" stroke-width="0.7"/>'
        for g in [0, 0.5, 1])
    ey = pt + ph * (1 - series[-1] / mv)

    body = f'''<text x="28" y="26" fill="{C_FAINT}" font-family="{MONO}" font-size="10" letter-spacing="2">COMMIT TELEMETRY</text>
  <text x="692" y="26" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">{label}</text>
  {grid}
  <polygon points="{area}" fill="{C_ACCENT}" opacity="0.06"/>
  <!-- draw-in: line appears over 2.4s with ease-out -->
  <polyline points="{points}" fill="none" stroke="{C_ACCENT}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"
    stroke-dasharray="{path_len}" stroke-dashoffset="{path_len}">
    <animate attributeName="stroke-dashoffset" values="{path_len};0" dur="2.4s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>
  </polyline>
  <!-- endpoint dot appears after draw completes, then pulses -->
  <circle cx="{pl+pw:.1f}" cy="{ey:.1f}" r="2.8" fill="{C_ACCENT}" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0.55;1" dur="3.4s" begin="2.4s" repeatCount="indefinite"/>
  </circle>
  <text x="24" y="{pt+4:.1f}" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">{mv}</text>
  <text x="24" y="{pt+ph+3:.1f}" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">0</text>
  <text x="{pl}" y="128" fill="{C_FAINT}" font-family="{MONO}" font-size="9">-12w</text>
  <text x="{pl+pw:.1f}" y="128" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">now</text>'''
    return _card(W, H, body)


# ═══════════════════════════════════════════════════════
#  4. LANGUAGE DISTRIBUTION — bars fill with stagger
#  Meaning: "Language data is loading progressively"
#  Cycle: 1.2s × 0.15s stagger
# ═══════════════════════════════════════════════════════
def build_language_graph(repos):
    lang_map = {}
    total_kb = 0
    for r in repos:
        lang = r.get("language", "Other") or "Other"
        kb = r.get("size", 0)
        lang_map[lang] = lang_map.get(lang, 0) + kb
        total_kb += kb

    lang_list = sorted(lang_map.items(), key=lambda x: x[1], reverse=True)
    W, H = 720, 110
    colors = [C_ACCENT, C_BLUE, C_GREEN, C_YELLOW, "#a78bfa"]
    rows = ""
    max_kb = max(v for _, v in lang_list) if lang_list else 1
    y0 = 32
    for i, (lang, kb) in enumerate(lang_list[:5]):
        pct = kb / total_kb * 100 if total_kb > 0 else 0
        bar_w = max(4, (kb / max_kb) * 400)
        col = colors[i % len(colors)]
        rows += f'''
  <text x="28" y="{y0+i*16}" fill="{C_SUB}" font-family="{MONO}" font-size="10.5">{esc(lang[:14])}</text>
  <!-- bar fills from 0 → width with stagger delay -->
  <rect x="150" y="{y0+i*16-8}" width="{bar_w:.0f}" height="10" rx="4" fill="{col}" opacity="0.7">
    <animate attributeName="width" from="0" to="{bar_w:.0f}" dur="1.2s" begin="{i*0.15}s" fill="freeze"/>
  </rect>
  <text x="562" y="{y0+i*16}" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">{pct:.0f}% · {kb}kb</text>'''
        y0 += 16

    body = f'''<text x="28" y="22" fill="{C_FAINT}" font-family="{MONO}" font-size="10" letter-spacing="2">LANGUAGES</text>
  <text x="692" y="22" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">{len(lang_map)} langs · {total_kb}kb total</text>
  {rows}'''
    return _card(W, H, body)


# ═══════════════════════════════════════════════════════
#  5. ARCHITECTURE — orbiting data packets
#  Meaning: "The system loop is closed and running"
#  Cycle: 4.4s continuous, two packets offset by 1.1s
# ═══════════════════════════════════════════════════════
def build_architecture():
    nodes = [(100, 96, "CORE"), (260, 96, "RENDER"),
             (100, 176, "NETWORK"), (260, 176, "SIM")]
    edges = [(0, 1), (1, 3), (3, 2), (2, 0)]

    svg_nodes = ""
    for x, y, label in nodes:
        svg_nodes += f'''    <rect x="{x}" y="{y}" width="92" height="30" rx="8" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="{x+46}" y="{y+19}" text-anchor="middle" fill="{C_SUB}" font-family="{MONO}" font-size="10.5">{label}</text>
'''
    svg_edges = ""
    path_d = ""
    for a, b in edges:
        x1, y1 = nodes[a][0] + 46, nodes[a][1] + 15
        x2, y2 = nodes[b][0] + 46, nodes[b][1] + 15
        svg_edges += f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C_BORDER}" stroke-width="1.2"/>\n'
        path_d += f"M {x1},{y1} L {x2},{y2} "

    metrics = [("Canvas", "60 fps"), ("Physics", "120 Hz"),
               ("WebRTC", "P2P"), ("Memory", "&lt; 45MB")]
    svg_metrics = "".join(
        f'    <text x="420" y="{104+i*22}" fill="{C_MUTED}" font-family="{MONO}" font-size="10.5">{k} · {v}</text>\n'
        for i, (k, v) in enumerate(metrics))

    body = f'''<text x="28" y="26" fill="{C_FAINT}" font-family="{MONO}" font-size="10" letter-spacing="2">ARCHITECTURE — VELOCITY</text>
  <text x="692" y="26" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">ES6 · 22 modules · 52 files</text>
  <g>
    <path id="arch-path" d="{path_d.strip()}" fill="none"/>
    {svg_edges}{svg_nodes}
    <!-- two data packets orbit the loop, offset by 1.1s -->
    <circle r="2.5" fill="{C_ACCENT}">
      <animateMotion dur="4.4s" repeatCount="indefinite" rotate="auto">
        <mpath href="#arch-path"/>
      </animateMotion>
    </circle>
    <circle r="2.5" fill="{C_ACCENT}" opacity="0.7">
      <animateMotion dur="4.4s" repeatCount="indefinite" rotate="auto" begin="1.1s">
        <mpath href="#arch-path"/>
      </animateMotion>
    </circle>
  </g>
  {svg_metrics}
  <text x="692" y="164" fill="{C_FAINT}" font-family="{MONO}" font-size="8" text-anchor="end">data flow — live system map</text>'''
    return _card(720, 170, body)


# ═══════════════════════════════════════════════════════
#  6. ENGINEERING PRINCIPLES — sequential fade-in
#  Meaning: "Read these in order"
#  Cycle: 0.6s × 0.4s stagger (one-shot)
# ═══════════════════════════════════════════════════════
def build_principles():
    principles = [
        ("Systems first", "Start with the loop that runs every frame"),
        ("Authority model", "One source of truth — compensate everywhere else"),
        ("Checkpoint early", "Assume the process will die — save atomically"),
        ("60fps is law", "Canvas over DOM, frame budget over features"),
        ("Ship, then clean", "v1 messy → v4 architecture"),
    ]
    W, H = 720, 160
    y0 = 40
    items = ""
    for i, (title, desc) in enumerate(principles):
        y = y0 + i * 22
        items += f'''
  <circle cx="28" cy="{y-4}" r="4" fill="none" stroke="{C_ACCENT}" stroke-width="1.2" opacity="0">
    <animate attributeName="opacity" values="0;1" dur="0.6s" begin="{i*0.4}s" fill="freeze"/>
  </circle>
  <text x="28" y="{y-1}" text-anchor="middle" fill="{C_ACCENT}" font-family="{MONO}" font-size="7" font-weight="700" opacity="0">
    {i+1}
    <animate attributeName="opacity" values="0;1" dur="0.6s" begin="{i*0.4}s" fill="freeze"/>
  </text>
  <text x="44" y="{y}" fill="{C_SUB}" font-family="{MONO}" font-size="10.5" opacity="0">
    <tspan fill="{C_TEXT}" font-weight="600">{esc(title)}</tspan> — {esc(desc)}
    <animate attributeName="opacity" values="0;1" dur="0.6s" begin="{i*0.4}s" fill="freeze"/>
  </text>'''

    body = f'''<text x="28" y="26" fill="{C_FAINT}" font-family="{MONO}" font-size="10" letter-spacing="2">ENGINEERING PRINCIPLES</text>
  {items}'''
    return _card(W, H, body)


# ═══════════════════════════════════════════════════════
#  7. BUILD GRID — color-coded repo health
#  Meaning: "Each repo is independently healthy"
#  Cycle: 2.8s × 0.25s stagger
# ═══════════════════════════════════════════════════════
def build_project_grid(repos):
    now = datetime.datetime.now(datetime.timezone.utc)
    items = []
    for r in repos[:6]:
        short = SHORT_MAP.get(r["name"], r["name"][:3].upper())
        try:
            pushed = datetime.datetime.fromisoformat(
                r.get("pushed_at", "2000-01-01T00:00:00Z").replace("Z", "+00:00"))
            days = max(0, (now - pushed).days)
        except Exception:
            days = 99
        if days <= 21:
            col, label = C_GREEN, "OK"
        elif days <= 60:
            col, label = C_YELLOW, "IDLE"
        else:
            col, label = C_MUTED, "QUIET"
        items.append((short, col, label, days))
    while len(items) < 6:
        items.append(("—", "#2a303c", "—", 0))

    W, H = 720, 100
    x0, gap, y = 52, 108, 50
    cells = ""
    for i, (short, col, label, days) in enumerate(items):
        cx = x0 + i * gap
        delay = i * 0.25
        cells += f'''
  <circle cx="{cx}" cy="{y}" r="7" fill="{col}" opacity="0.9">
    <animate attributeName="opacity" values="0.9;0.4;0.9" dur="2.8s" begin="{delay}s" repeatCount="indefinite"/>
  </circle>
  <text x="{cx}" y="{y+24}" text-anchor="middle" fill="{C_SUB}" font-family="{MONO}" font-size="10">{esc(short)}</text>
  <text x="{cx}" y="{y+38}" text-anchor="middle" fill="{C_FAINT}" font-family="{MONO}" font-size="8.5">{label} · {days}d</text>'''

    body = f'''<text x="28" y="24" fill="{C_FAINT}" font-family="{MONO}" font-size="10" letter-spacing="2">BUILD GRID</text>
  <text x="692" y="24" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">health · 6 repos</text>
  {cells}'''
    return _card(W, H, body)


# ═══════════════════════════════════════════════════════
#  8. BUILD TICKER — scrolling marquee
#  Meaning: "There's always more to see"
#  Cycle: 38s continuous loop
# ═══════════════════════════════════════════════════════
def build_ticker(repos):
    names = [r["name"].upper().replace("-", "_") for r in repos[:6]]
    if not names:
        names = ["VELOCITY", "COMPUTER_CRICKET", "CRPAPP", "QUANTUM", "GROUPDNA", "SALARY"]
    text = "  ◆  ".join(names) + "  ◆  BUILD · RACE · DOMINATE  ◆  " + "  ◆  ".join(names)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="44" viewBox="0 0 720 44" role="img">
  <defs><clipPath id="tc"><rect x="0" y="0" width="720" height="44" rx="12"/></clipPath></defs>
  <rect width="720" height="44" rx="12" fill="{C_CARD}"/>
  <rect x=".5" y=".5" width="719" height="43" rx="12" fill="none" stroke="{C_BORDER}"/>
  <g clip-path="url(#tc)">
    <text x="0" y="27" fill="{C_FAINT}" font-family="{MONO}" font-size="11" letter-spacing="0.3">
      {text}
      <animateTransform attributeName="transform" type="translate" values="0,0;-1040,0" dur="38s" repeatCount="indefinite" calcMode="linear"/>
    </text>
  </g>
</svg>'''


# ═══════════════════════════════════════════════════════
#  9. OSS JOURNEY — milestones with cycling stats
#  Meaning: "Current position in journey"
#  Cycle: 3s pulse on latest milestone
# ═══════════════════════════════════════════════════════
def build_oss_journey(repos, user_data=None):
    total_repos = len(repos)
    now = datetime.datetime.now(datetime.timezone.utc)
    created = datetime.datetime(2025, 11, 1, tzinfo=datetime.timezone.utc)
    days_active = (now - created).days
    total_mb = sum(r.get("size", 0) for r in repos) / 1024

    langs = set()
    for r in repos:
        if r.get("language"):
            langs.add(r["language"])

    milestones = [
        ("Nov 25", "Account created"),
        ("Dec 25", "First repo"),
        ("Jan 26", "Velocity v1"),
        ("Mar 26", "Multiplayer"),
        ("May 26", "Quantum TT"),
        ("Jul 26", f"{total_repos} repos"),
    ]

    W, H = 720, 180

    # stats row
    stats_x = [100, 230, 360, 490, 620]
    stats_v = [total_repos, f"{total_mb:.1f}", len(langs), "—", days_active]
    stats_l = ["REPOS", "MB CODE", "LANGS", "STARS", "DAYS"]
    stats = "".join(
        f'    <text x="{sx}" y="50" text-anchor="middle" fill="{C_TEXT}" font-family="{MONO}" font-size="18" font-weight="600">{sv}</text>\n'
        f'    <text x="{sx}" y="62" text-anchor="middle" fill="{C_FAINT}" font-family="{MONO}" font-size="8">{sl}</text>\n'
        for sx, sv, sl in zip(stats_x, stats_v, stats_l))

    # timeline
    timeline = ""
    for i, (date, desc) in enumerate(milestones[:6]):
        x = 50 + i * 132
        y = 80
        active = (i == len(milestones) - 1)
        fill = C_ACCENT if active else C_MUTED
        stroke = C_ACCENT if active else C_BORDER

        pulse = ""
        if active:
            pulse = f'''  <circle cx="{x}" cy="{y}" r="14" fill="{C_ACCENT}" opacity="0">
    <animate attributeName="opacity" values="0;0.15;0" dur="3s" repeatCount="indefinite"/>
    <animate attributeName="r" values="6;16;6" dur="3s" repeatCount="indefinite"/>
  </circle>
'''
        if i < 5:
            nx = 50 + (i + 1) * 132
            lc = C_ACCENT if active else C_DIV
            timeline += f'  <line x1="{x+5}" y1="{y}" x2="{nx-5}" y2="{y}" stroke="{lc}" stroke-width="1.2" stroke-dasharray="4,3"/>\n'

        timeline += f'''  {pulse}  <circle cx="{x}" cy="{y}" r="5" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
  <text x="{x}" y="{y-16}" text-anchor="middle" fill="{C_SUB}" font-family="{MONO}" font-size="9">{esc(date)}</text>
  <text x="{x}" y="{y+24}" text-anchor="middle" fill="{C_MUTED}" font-family="{MONO}" font-size="8.5">{esc(desc)}</text>
'''

    body = f'''<text x="28" y="26" fill="{C_FAINT}" font-family="{MONO}" font-size="10" letter-spacing="2">OPEN SOURCE JOURNEY</text>
  <text x="692" y="26" fill="{C_FAINT}" font-family="{MONO}" font-size="9" text-anchor="end">{days_active}d · {len(langs)} langs</text>
  <g font-family="{MONO}" text-anchor="middle">
    {stats}
  </g>
  <line x1="50" y1="70" x2="670" y2="70" stroke="{C_DIV}" stroke-width="0.7"/>
  {timeline}'''
    return _card(W, H, body)


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════
def main():
    now = datetime.datetime.now(datetime.timezone.utc)

    repos = gh_json(f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30&type=owner") or []
    repos = [r for r in repos if not r.get("fork")
             and r.get("name", "").lower() != USER.lower()]
    if not repos:
        repos = FALLBACK_REPOS
        print("  (using fallback repo data)")

    user_data = gh_json(f"https://api.github.com/users/{USER}")

    # 1. Current Build
    out = build_current_build(repos[0])
    (WIDGETS / "current-build.svg").write_text(out, encoding="utf-8")
    print(f"✓ current-build.svg — {repos[0]['name']}")

    # 2. Garage Timeline
    out = build_garage_timeline(repos)
    (WIDGETS / "garage-timeline.svg").write_text(out, encoding="utf-8")
    print("✓ garage-timeline.svg")

    # 3. Commit Telemetry
    series = None
    try:
        if TOKEN:
            start = now - datetime.timedelta(weeks=12)
            q = """query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$from, to:$to) {
      contributionCalendar { weeks { contributionDays { contributionCount } } }
    }
  }
}"""
            d = gh_gql(q, {"login": USER,
                           "from": start.isoformat(),
                           "to": now.isoformat()})
            if d and d.get("user"):
                weeks = d["user"]["contributionsCollection"][
                    "contributionCalendar"]["weeks"]
                series = [
                    sum(x["contributionCount"] for x in w["contributionDays"])
                    for w in weeks[-12:]]
    except Exception:
        pass
    out = build_commit_telemetry(series)
    (WIDGETS / "commit-telemetry.svg").write_text(out, encoding="utf-8")
    print(f"✓ commit-telemetry.svg — {'live' if series else 'sample'}")

    # 4. Language Graph
    out = build_language_graph(repos)
    (WIDGETS / "language-graph.svg").write_text(out, encoding="utf-8")
    print("✓ language-graph.svg")

    # 5. Architecture
    out = build_architecture()
    (WIDGETS / "architecture.svg").write_text(out, encoding="utf-8")
    print("✓ architecture.svg")

    # 6. Principles
    out = build_principles()
    (WIDGETS / "principles.svg").write_text(out, encoding="utf-8")
    print("✓ principles.svg")

    # 7. Build Grid
    out = build_project_grid(repos)
    (WIDGETS / "build-grid.svg").write_text(out, encoding="utf-8")
    print("✓ build-grid.svg")

    # 8. Build Ticker
    out = build_ticker(repos)
    (WIDGETS / "ticker.svg").write_text(out, encoding="utf-8")
    print("✓ ticker.svg")

    # 9. OSS Journey
    out = build_oss_journey(repos, user_data)
    (WIDGETS / "oss-journey.svg").write_text(out, encoding="utf-8")
    print("✓ oss-journey.svg")

    print(f"\n  All 9 widgets → assets/widgets/")
    print(f"  Pure SVG — no JS, no CSS, no dependencies.")
    print(f"  Animations: native <animate> / <animateMotion> / <animateTransform>.")
    print(f"  Refresh: GitHub Actions every 6 hours.")


if __name__ == "__main__":
    main()
