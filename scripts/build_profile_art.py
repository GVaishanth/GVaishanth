"""Build the GitHub-profile visual system.

The design language takes its cues from G. Vaishanth's avatar: graphite black,
voxel-green geometry, a red / amber / green motion ring, a cricket ball, and
binary-code rain. The workflow runs this script every six hours so repository
metadata in the hero, cards, and live-status panel stays current.

Run locally:
    python scripts/build_profile_art.py
"""
from datetime import datetime
from html import escape
from pathlib import Path
import json
import os
import subprocess
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "profile"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "DejaVu Sans"
MONO = "DejaVu Sans Mono"
FEATURED = ("Volt", "Velocity", "Computer-Cricket", "VelvetStack")

# Avatar-inspired palette: charcoal surface, voxel green, racing red and amber.
INK = "#070a09"
PANEL = "#101512"
GREEN = "#79e95d"
GREEN_DARK = "#234f28"
MINT = "#a9ff92"
RED = "#e53c3c"
AMBER = "#f2b51d"
CREAM = "#eef2e8"
MUTED = "#9ca89e"


def github_snapshot():
    """Fetch featured-repository facts; remain usable offline or rate-limited."""
    fallback = {
        "Volt": {"language": "TypeScript", "pushed": "LIVE", "sort": ""},
        "Velocity": {"language": "JavaScript", "pushed": "LIVE", "sort": ""},
        "Computer-Cricket": {"language": "HTML", "pushed": "LIVE", "sort": ""},
        "VelvetStack": {"language": "JavaScript", "pushed": "LIVE", "sort": ""},
    }
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "gvaishanth-profile-art"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(
            "https://api.github.com/users/GVaishanth/repos?per_page=100&type=owner", headers=headers
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            repos = json.load(response)
        found = {}
        for repo in repos:
            name = repo.get("name")
            if name not in FEATURED:
                continue
            pushed_at = repo.get("pushed_at") or ""
            human = datetime.fromisoformat(pushed_at.replace("Z", "+00:00")).strftime("%d %b %Y") if pushed_at else "LIVE"
            found[name] = {"language": repo.get("language") or "Web", "pushed": human, "sort": pushed_at}
        return {**fallback, **found}
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError):
        return fallback


def wrap(width, height, body, defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <defs>{defs}</defs>
  {body}
</svg>'''


def save(name, content, width):
    svg = OUT / f"{name}.svg"
    svg.write_text(content, encoding="utf-8")
    # Remove volatile metadata: a no-change refresh must not produce a commit.
    subprocess.run([
        "convert", "-background", "none", str(svg), "-strip",
        "-define", "png:exclude-chunk=date,time", "-resize", f"{width}x", str(OUT / f"{name}.png"),
    ], check=True)


def defs(extra=""):
    return f'''
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#090d0a"/><stop offset=".52" stop-color="#111812"/><stop offset="1" stop-color="#070908"/></linearGradient>
      <radialGradient id="halo" cx="78%" cy="44%" r="62%"><stop stop-color="#79e95d" stop-opacity=".19"/><stop offset=".48" stop-color="#1e632a" stop-opacity=".07"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
      <linearGradient id="green" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#c9ffaf"/><stop offset=".45" stop-color="#79e95d"/><stop offset="1" stop-color="#2a8537"/></linearGradient>
      <linearGradient id="race" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#f2b51d"/><stop offset=".48" stop-color="#e53c3c"/><stop offset="1" stop-color="#79e95d"/></linearGradient>
      <filter id="glow"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      <filter id="shadow"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#000" flood-opacity=".65"/></filter>
      <pattern id="grain" width="10" height="10" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#d7ead7" opacity=".05"/><circle cx="7" cy="4" r=".5" fill="#d7ead7" opacity=".035"/></pattern>
      {extra}'''


def cube(x, y, size=30, opacity=1):
    """A small isometric voxel, echoing the avatar's central green blocks."""
    h = size * .27
    return f'''<g opacity="{opacity}" filter="url(#shadow)">
      <path d="M{x} {y+h} L{x+size/2} {y} L{x+size} {y+h} L{x+size/2} {y+2*h}" fill="#b9ff9f"/>
      <path d="M{x} {y+h} L{x+size/2} {y+2*h} L{x+size/2} {y+size} L{x} {y+size-h}" fill="#3d983f"/>
      <path d="M{x+size/2} {y+2*h} L{x+size} {y+h} L{x+size} {y+size-h} L{x+size/2} {y+size}" fill="#1b5428"/>
    </g>'''


def binary_rain(x, y, width, height, color=GREEN, columns=10):
    bits = []
    for i in range(columns):
        cx = x + 8 + i * (width / columns)
        top = y + (i % 4) * 7
        length = height * (.26 + ((i * 7) % 6) / 12)
        bits.append(f'<path d="M{cx:.1f} {top:.1f}v{length:.1f}" stroke="{color}" stroke-opacity="{.16 + (i%4)*.09:.2f}"/>')
        for j in range(4 + i % 4):
            bits.append(f'<text x="{cx-3:.1f}" y="{top+18+j*15:.1f}" fill="{color}" fill-opacity="{.28 + (j%2)*.16:.2f}" font-family="{MONO}" font-size="8">{(i+j)%2}</text>')
    return ''.join(bits)


def avatar_motif(cx, cy, scale=1, rain=True):
    """Abstract avatar: tri-colour motion ring surrounding a voxel signal."""
    s = scale
    voxels = [(0, 1), (1, 0), (2, 1), (0, 2), (1, 2), (2, 2), (3, 2), (0, 3), (1, 3), (3, 3), (4, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)]
    cubes = ''.join(cube(cx + (gx-2)*31*s, cy - 50*s + gy*26*s, 28*s, 1 if (gx,gy)!=(2,3) else .2) for gx,gy in voxels)
    rain_svg = binary_rain(cx-105*s, cy+84*s, 210*s, 100*s, columns=12) if rain else ""
    return f'''<g>
      <circle cx="{cx}" cy="{cy}" r="{126*s}" fill="#050705" stroke="#304334" stroke-opacity=".48"/>
      <!-- Deliberately angular ring segments echo the avatar's red / amber / green track. -->
      <g fill="#f2b51d"><rect x="{cx-126*s}" y="{cy-58*s}" width="{12*s}" height="{70*s}" rx="{5*s}"/><rect x="{cx-112*s}" y="{cy-84*s}" width="{37*s}" height="{12*s}" rx="{5*s}"/></g>
      <g fill="#e53c3c"><rect x="{cx-54*s}" y="{cy-120*s}" width="{76*s}" height="{12*s}" rx="{5*s}"/><rect x="{cx+24*s}" y="{cy-108*s}" width="{43*s}" height="{12*s}" rx="{5*s}"/></g>
      <g fill="#79e95d"><rect x="{cx+104*s}" y="{cy+10*s}" width="{12*s}" height="{55*s}" rx="{5*s}"/><rect x="{cx+50*s}" y="{cy+92*s}" width="{56*s}" height="{12*s}" rx="{5*s}"/></g>
      <circle cx="{cx+68*s}" cy="{cy-78*s}" r="{10*s}" fill="#eff2e8" stroke="#a5aa9c" stroke-width="{1*s}"/>
      <path d="M{cx+60*s} {cy-82*s}q{8*s} {-9*s} {16*s} 0M{cx+59*s} {cy-75*s}q{9*s} {7*s} {18*s} 0" fill="none" stroke="#bdc1b6" stroke-width="{1*s}"/>
      {cubes}{rain_svg}
    </g>'''


def hero(current):
    body = f'''<rect width="1600" height="620" rx="30" fill="url(#bg)"/><rect width="1600" height="620" rx="30" fill="url(#grain)"/><rect width="1600" height="620" rx="30" fill="url(#halo)"/>
      <path d="M0 497 C240 337 422 612 694 438 S1160 262 1640 424" fill="none" stroke="url(#race)" stroke-opacity=".44" stroke-width="2"/>
      <path d="M0 509 C240 349 422 624 694 450 S1160 274 1640 436" fill="none" stroke="#d7efd6" stroke-opacity=".13"/>
      <g transform="translate(84 82)"><rect width="247" height="38" rx="19" fill="#79e95d" fill-opacity=".1" stroke="#79e95d" stroke-opacity=".55"/><circle cx="23" cy="19" r="5" fill="#79e95d" filter="url(#glow)"/><text x="42" y="24" fill="#baffad" font-family="{MONO}" font-size="13" letter-spacing="1.5">PROFILE / SYSTEM ONLINE</text></g>
      <text x="85" y="238" fill="#f2f6ef" font-family="{FONT}" font-size="66" font-weight="700">G. Vaishanth</text>
      <text x="89" y="293" fill="#b1c0b4" font-family="{FONT}" font-size="25">Building systems that race, play, and stay local.</text>
      <text x="89" y="354" fill="#8cf579" font-family="{MONO}" font-size="16" letter-spacing="2">SIMULATE  ·  CONNECT  ·  ITERATE</text>
      <g transform="translate(89 414)"><rect width="154" height="45" rx="9" fill="#17311c" stroke="#79e95d" stroke-opacity=".5"/><text x="77" y="29" text-anchor="middle" fill="#d8ffd2" font-family="{MONO}" font-size="13">LOCAL-FIRST</text>
        <rect x="169" width="143" height="45" rx="9" fill="#311f12" stroke="#f2b51d" stroke-opacity=".55"/><text x="241" y="29" text-anchor="middle" fill="#ffe5a3" font-family="{MONO}" font-size="13">SIMULATIONS</text>
        <rect x="327" width="129" height="45" rx="9" fill="#361417" stroke="#e53c3c" stroke-opacity=".55"/><text x="391" y="29" text-anchor="middle" fill="#ffb8b8" font-family="{MONO}" font-size="13">WEB GAMES</text></g>
      <text x="90" y="541" fill="#647568" font-family="{MONO}" font-size="12" letter-spacing="1.2">CURRENT BUILD / {escape(current.upper())}</text>
      {avatar_motif(1280, 293, 1.34, True)}
      <text x="1280" y="561" text-anchor="middle" fill="#aab8ab" font-family="{MONO}" font-size="12" letter-spacing="2">VOXEL / MOTION / CODE</text>'''
    save("hero-systems", wrap(1600, 620, body, defs()), 1600)


def current_build(build, meta):
    body = f'''<rect width="1200" height="174" rx="22" fill="url(#bg)"/><rect width="1200" height="174" rx="22" fill="url(#grain)"/>
      <path d="M0 173H1200" stroke="#79e95d" stroke-opacity=".42"/>
      <g transform="translate(44 43)"><circle cx="35" cy="35" r="31" fill="#0d1710" stroke="#79e95d" stroke-opacity=".7"/><circle cx="35" cy="35" r="9" fill="#79e95d" filter="url(#glow)"/></g>
      <text x="120" y="56" fill="#9cae9e" font-family="{MONO}" font-size="13" letter-spacing="2.4">CURRENT BUILD / LIVE SIGNAL</text>
      <text x="120" y="105" fill="#f2f6ef" font-family="{FONT}" font-size="37" font-weight="700">{escape(build)}</text>
      <text x="120" y="136" fill="#b0beb2" font-family="{FONT}" font-size="18">{escape(meta['language'])} · last pushed {escape(meta['pushed'])}</text>
      <g transform="translate(894 49)"><rect width="250" height="66" rx="16" fill="#16311b" stroke="#79e95d" stroke-opacity=".55"/><path d="M22 33h33" stroke="#79e95d" stroke-width="2"/><circle cx="58" cy="33" r="4" fill="#79e95d"/><text x="82" y="29" fill="#aaff9c" font-family="{MONO}" font-size="12" letter-spacing="1.4">AUTO REFRESH</text><text x="82" y="49" fill="#efffec" font-family="{MONO}" font-size="13">EVERY 6 HOURS</text></g>'''
    save("current-build", wrap(1200, 174, body, defs()), 1200)


def card(name, eyebrow, title, line1, line2, tags, colour, meta, motif):
    chip_x = 36
    chips = []
    for tag in tags:
        w = max(90, 17 + len(tag)*8)
        chips.append(f'<g transform="translate({chip_x} 371)"><rect width="{w}" height="33" rx="16" fill="{colour}" fill-opacity=".10" stroke="{colour}" stroke-opacity=".57"/><text x="{w/2}" y="22" text-anchor="middle" fill="#dae7dc" font-family="{MONO}" font-size="11">{escape(tag)}</text></g>')
        chip_x += w + 13
    body = f'''<rect width="1200" height="460" rx="24" fill="url(#bg)"/><rect width="1200" height="460" rx="24" fill="url(#grain)"/>
      <path d="M0 421 C208 290 396 487 621 361 S976 215 1220 318" fill="none" stroke="{colour}" stroke-opacity=".25" stroke-width="2"/>
      <g transform="translate(36 35)"><rect width="{max(190, len(eyebrow)*9+28)}" height="30" rx="15" fill="{colour}" fill-opacity=".12" stroke="{colour}" stroke-opacity=".5"/><text x="16" y="20" fill="{colour}" font-family="{MONO}" font-size="12" letter-spacing="1.5">{escape(eyebrow)}</text></g>
      <text x="36" y="145" fill="#f2f6ef" font-family="{FONT}" font-size="44" font-weight="700">{escape(title)}</text>
      <text x="38" y="191" fill="#bdc9bf" font-family="{FONT}" font-size="20">{escape(line1)}</text><text x="38" y="223" fill="#bdc9bf" font-family="{FONT}" font-size="20">{escape(line2)}</text>
      {motif}{''.join(chips)}
      <text x="36" y="438" fill="#718174" font-family="{MONO}" font-size="11" letter-spacing="1.65">SYNCED FROM GITHUB  /  {escape(meta['language'].upper())}  /  {escape(meta['pushed'].upper())}</text>'''
    save(f"card-{name}", wrap(1200, 460, body, defs()), 1200)


def section(name, number, title, note, colour, graphic):
    body = f'''<rect width="1200" height="144" rx="20" fill="url(#bg)"/><rect width="1200" height="144" rx="20" fill="url(#grain)"/>
      <path d="M0 143H1200" stroke="{colour}" stroke-opacity=".42"/><g transform="translate(30 30)"><rect width="54" height="54" rx="16" fill="{colour}" fill-opacity=".12" stroke="{colour}" stroke-opacity=".58"/><text x="27" y="35" text-anchor="middle" fill="{colour}" font-family="{MONO}" font-size="16" font-weight="700">{number}</text></g>
      <text x="107" y="55" fill="#f0f5ee" font-family="{FONT}" font-size="27" font-weight="700">{escape(title)}</text>
      <text x="109" y="82" fill="#9aab9e" font-family="{MONO}" font-size="12" letter-spacing="1">{escape(note)}</text><path d="M108 105H492" stroke="#3a493c"/>
      {graphic}<text x="1168" y="121" text-anchor="end" fill="#718174" font-family="{MONO}" font-size="10" letter-spacing="1.6">GVAISHANTH / PROFILE</text>'''
    # Section dividers are SVG-only: crisp text and no redundant fallback file.
    (OUT / f"section-{name}.svg").write_text(wrap(1200, 144, body, defs()), encoding="utf-8")


def make_sections():
    section("current-focus", "01", "CURRENT FOCUS", "LOCAL-FIRST TOOLS · SIMULATIONS · SOCIAL WEB", GREEN, f'''<g transform="translate(712 25)">{avatar_motif(190, 47, .34, False)}<path d="M0 101H400" stroke="#79e95d" stroke-opacity=".35" stroke-dasharray="3 8"/><text x="0" y="125" fill="#7f9382" font-family="{MONO}" font-size="10">BUILD</text><text x="130" y="125" fill="#7f9382" font-family="{MONO}" font-size="10">PLAY</text><text x="260" y="125" fill="#7f9382" font-family="{MONO}" font-size="10">CONNECT</text></g>''')
    section("selected-builds", "02", "SELECTED BUILDS", "FOUR SYSTEMS, FOUR DIFFERENT KINDS OF PLAY", AMBER, '''<g transform="translate(715 38)"><path d="M0 60 C83 -8 160 106 240 42 S378 16 448 58" fill="none" stroke="url(#race)" stroke-width="5" stroke-linecap="round"/><g fill="#0e1510" stroke="#79e95d"><rect x="8" y="8" width="68" height="36" rx="10"/><rect x="123" y="49" width="68" height="36" rx="10"/><rect x="240" y="17" width="68" height="36" rx="10"/><rect x="367" y="45" width="68" height="36" rx="10"/></g><text x="42" y="32" text-anchor="middle" fill="#9fff91" font-family="DejaVu Sans Mono" font-size="11">VOLT</text><text x="157" y="73" text-anchor="middle" fill="#ffcf69" font-family="DejaVu Sans Mono" font-size="11">VEL</text><text x="274" y="41" text-anchor="middle" fill="#ff8787" font-family="DejaVu Sans Mono" font-size="11">CKT</text><text x="401" y="69" text-anchor="middle" fill="#9fff91" font-family="DejaVu Sans Mono" font-size="11">VST</text></g>''')
    section("engineering-notes", "03", "ENGINEERING NOTES", "THE LOOP THAT TURNS INPUT INTO BETTER SYSTEMS", RED, '''<g transform="translate(720 27)"><circle cx="175" cy="45" r="42" fill="none" stroke="#e53c3c" stroke-opacity=".58" stroke-width="3"/><path d="M175 3a42 42 0 0 1 41 42" fill="none" stroke="#79e95d" stroke-width="5"/><path d="M216 45l-10 -7m10 7l-8 10" stroke="#79e95d" stroke-width="3"/><path d="M28 45H126M224 45H420" stroke="#f2b51d" stroke-opacity=".64" stroke-width="2"/><circle cx="28" cy="45" r="6" fill="#f2b51d"/><circle cx="420" cy="45" r="6" fill="#79e95d"/><text x="0" y="92" fill="#879889" font-family="DejaVu Sans Mono" font-size="10">INPUT</text><text x="143" y="92" fill="#879889" font-family="DejaVu Sans Mono" font-size="10">MODEL</text><text x="320" y="92" fill="#879889" font-family="DejaVu Sans Mono" font-size="10">ITERATE</text></g>''')
    section("workshop", "04", "MORE FROM THE WORKSHOP", "EXPERIMENTS, DATA PROJECTS, AND EARLIER BUILDS", GREEN, f'''<g transform="translate(706 20)"><g>{cube(0, 18, 31)}{cube(35, 8, 31)}{cube(70, 18, 31)}{cube(105, 8, 31)}{cube(140, 18, 31)}{cube(175, 8, 31)}{cube(210, 18, 31)}</g>{binary_rain(0, 64, 255, 55, columns=8)}</g>''')


def main():
    snapshot = github_snapshot()
    current = max(FEATURED, key=lambda repo: snapshot[repo]["sort"])
    hero(current)
    current_build(current, snapshot[current])
    make_sections()

    # Each card receives a project-specific avatar-inspired scene.
    volt_scene = f'''<g transform="translate(922 48)"><rect width="232" height="222" rx="28" fill="#0b170c" stroke="#79e95d" stroke-opacity=".5"/><path d="M25 35H207M25 68H160" stroke="#79e95d" stroke-opacity=".3"/>{binary_rain(25, 78, 180, 108, columns=9)}<g transform="translate(87 56)">{cube(0, 0, 38)}{cube(41, 10, 38)}{cube(20, 42, 38)}</g></g>'''
    velocity_scene = '''<g transform="translate(910 44)"><circle cx="122" cy="117" r="102" fill="#0e1110" stroke="#344136"/><path d="M34 157A103 103 0 0 1 48 62" fill="none" stroke="#f2b51d" stroke-width="13" stroke-linecap="round"/><path d="M65 35A103 103 0 0 1 188 45" fill="none" stroke="#e53c3c" stroke-width="13" stroke-linecap="round"/><path d="M207 74A103 103 0 0 1 150 211" fill="none" stroke="#79e95d" stroke-width="13" stroke-linecap="round"/><path d="M52 137 C105 42 153 200 212 96" fill="none" stroke="#eff2e8" stroke-opacity=".75" stroke-width="3"/><path d="M128 93l21 17-21 17-21-17z" fill="#e53c3c" filter="url(#glow)"/></g>'''
    cricket_scene = '''<g transform="translate(910 40)"><rect width="245" height="235" rx="29" fill="#101710" stroke="#79e95d" stroke-opacity=".45"/><path d="M123 211V41" stroke="#d5b46e" stroke-width="42" stroke-opacity=".75"/><path d="M65 115H181" stroke="#edf1e8" stroke-opacity=".34"/><circle cx="158" cy="73" r="25" fill="#f2eee2" stroke="#cfc7b6" stroke-width="2"/><path d="M140 72q18-17 36 0M141 80q18 17 35 0" fill="none" stroke="#b9b1a1" stroke-width="2"/><path d="M53 190A95 95 0 0 1 43 79" fill="none" stroke="#f2b51d" stroke-width="9"/><path d="M193 189A95 95 0 0 0 204 123" fill="none" stroke="#79e95d" stroke-width="9"/><path d="M116 177v-55m14 55v-55m-7 0v-12" stroke="#e53c3c" stroke-width="4"/></g>'''
    velvet_scene = '''<g transform="translate(920 45)"><circle cx="118" cy="111" r="105" fill="#0f1510" stroke="#3d5140"/><path d="M30 143A101 101 0 0 1 56 53" fill="none" stroke="#f2b51d" stroke-width="10"/><path d="M70 32A101 101 0 0 1 182 43" fill="none" stroke="#e53c3c" stroke-width="10"/><path d="M199 71A101 101 0 0 1 145 207" fill="none" stroke="#79e95d" stroke-width="10"/><g transform="translate(72 72) rotate(-12 40 55)"><rect width="80" height="110" rx="9" fill="#e9eee3"/><text x="15" y="35" fill="#152216" font-family="DejaVu Sans" font-size="29">A</text><text x="40" y="82" text-anchor="middle" fill="#e53c3c" font-family="DejaVu Sans" font-size="44">♠</text></g><g transform="translate(109 84) rotate(11 40 55)"><rect width="80" height="110" rx="9" fill="#dce6d9"/><text x="15" y="35" fill="#152216" font-family="DejaVu Sans" font-size="29">Q</text><text x="40" y="82" text-anchor="middle" fill="#e53c3c" font-family="DejaVu Sans" font-size="44">♥</text></g></g>'''
    card("volt", "VOLT / LOCAL-FIRST ENVIRONMENT", "Your browser, your workspace.", "Terminal, files, databases, and code—kept local.", "Built to work like a system, not a tab.", ["TYPESCRIPT", "OPFS", "WASM"], GREEN, snapshot["Volt"], volt_scene)
    card("velocity", "VELOCITY / RACE CONTROL", "Constructor Championship", "The race is a feedback loop: data, decision, delta.", "Build a season one consequential lap at a time.", ["STRATEGY", "TELEMETRY", "CANVAS"], RED, snapshot["Velocity"], velocity_scene)
    card("cricket", "COMPUTER CRICKET / CLUB", "Hand cricket, in full colour.", "Seven modes, adaptive AI, and a score worth chasing.", "From a quick over to private online leagues.", ["7 MODES", "WEBRTC", "SEASONS"], AMBER, snapshot["Computer-Cricket"], cricket_scene)
    card("velvet", "VELVET STACK / CARD ROOM", "Play the room.", "A social table for poker, rummy, UNO, and more.", "Solo, local, or online—no account needed.", ["POKER", "RUMMY", "UNO"], GREEN, snapshot["VelvetStack"], velvet_scene)
    print(f"Generated avatar-inspired profile assets in {OUT}")


if __name__ == "__main__":
    main()
