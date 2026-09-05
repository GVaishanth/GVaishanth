"""Generate the animated SVG banners for the GitHub profile.

Outputs (regenerate any time with `python scripts/build_banner.py`):
  * assets/profile/banner-animated.svg — hero banner. Terminal-style typing
    rotates through the engineering concepts behind shipped projects, with a
    sliding caret, a pulsing status dot and a one-time load-in.
  * assets/profile/divider.svg       — thin section divider with a slow
    travelling pulse.

Technical ground rules for GitHub READMEs (the reason this file exists):
  * GitHub strips all JavaScript and every external reference (fonts, CDNs,
    images) from anything proxied through camo. The ONLY portable animation
    vehicles are CSS keyframes and SMIL inside a standalone, self-contained
    SVG referenced with <img>. This banner uses SMIL for the typing clockwork
    (calcMode="discrete" gives exact per-character steps, with zero reliance
    on CSS geometry properties, which some renderers ignore inside clip/mask
    geometry) and CSS only for decorative fades that are safe to lose.
  * `prefers-reduced-motion` swaps the animated layer for a fully static,
    readable banner via CSS `display` toggling (SMIL itself cannot be
    cancelled by CSS, so the animated group is hidden instead).
  * All timings are computed from CONCEPTS below — edit the list and re-run;
    the keyTimes rebalance automatically.
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "profile"
OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# Edit these, then re-run. Everything else (timing, keyTimes) is derived.
# ----------------------------------------------------------------------------
NAME = "G. VAISHANTH"
TAGLINE = "Local-first web apps · Interactive front-ends · Mobile tools"
STATUS = "building in public"
CONCEPTS = [
    "$ local-first development tools",
    "$ peer-to-peer multiplayer",
    "$ systems-driven game design",
    "$ adaptive game ai",
    "$ resilient mobile engineering",
    "$ data storytelling",
]

# Palette — GitHub dark, deliberately restrained.
BG = "#0d1117"
GRID = "#161b22"
TEXT = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#3fb950"
MONO_TEXT = "#7ee787"

# Layout
W, H = 1280, 360
MONO_SIZE = 26
CHAR_W = 16          # monospace advance estimate at MONO_SIZE
TYPE_SECONDS = 1.8   # typing duration per line
SLOT_SECONDS = 6.0   # total window per line (typing included)
FONT_SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

LINE_X = 118
LINE_Y = 256
CLIP_TOP = LINE_Y - 30
CLIP_H = 44
CARET_W = 11


def _smil_steps(values: list[str], end_frac: float) -> tuple[str, str]:
    """values/keyTimes pair: step through `values` by `end_frac`, then hold."""
    n = len(values)
    key_times = [f"{end_frac * k / (n - 1):.4f}" for k in range(n)]
    key_times[-1] = "1"  # hold final value until the cycle wraps
    return ";".join(values), ";".join(key_times)


def build_banner() -> str:
    slot_frac = SLOT_SECONDS / (SLOT_SECONDS * len(CONCEPTS))
    cycle = SLOT_SECONDS * len(CONCEPTS)

    groups: list[str] = []
    for i, line in enumerate(CONCEPTS):
        n_chars = len(line)
        full_w = n_chars * CHAR_W + CARET_W + 4  # small overshoot: guarantee full reveal
        begin = f"{-i * SLOT_SECONDS:g}s"        # negative begin: stagger mid-cycle
        # Opacity: visible only inside this line's slot.
        opacity_smil = (
            f'<animate attributeName="opacity" values="1;0" '
            f'keyTimes="0;{slot_frac:.4f}" calcMode="discrete" '
            f'dur="{cycle:g}s" begin="{begin}" repeatCount="indefinite"/>'
        )
        # Typing reveal: clip rect width steps through one character per tick.
        width_values = [f"{CHAR_W * k}" for k in range(n_chars + 1)] + [f"{full_w}"]
        widths, width_times = _smil_steps(width_values, TYPE_SECONDS / (SLOT_SECONDS * len(CONCEPTS)))
        # Caret rides the same schedule along the front edge.
        caret_positions = [f"{LINE_X + CHAR_W * k}" for k in range(n_chars + 1)] + [f"{LINE_X + full_w}"]

        groups.append(f"""  <g class="anim">
    {opacity_smil}
    <clipPath id="c{i}">
      <rect x="{LINE_X}" y="{CLIP_TOP}" width="0" height="{CLIP_H}">
        <animate attributeName="width" values="{widths}" keyTimes="{width_times}"
                 calcMode="discrete" dur="{cycle:g}s" begin="{begin}" repeatCount="indefinite"/>
      </rect>
    </clipPath>
    <text x="{LINE_X}" y="{LINE_Y}" clip-path="url(#c{i})" fill="{MONO_TEXT}"
          font-family="{FONT_MONO}" font-size="{MONO_SIZE}">{escape(line)}</text>
    <rect x="{LINE_X}" y="{LINE_Y - 26}" width="{CARET_W}" height="30" fill="{ACCENT}">
      <animate attributeName="x" values="{";".join(caret_positions)}" keyTimes="{width_times}"
               calcMode="discrete" dur="{cycle:g}s" begin="{begin}" repeatCount="indefinite"/>
    </rect>
  </g>""")

    anim_groups = "\n".join(groups)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(NAME)} — {escape(TAGLINE)}">
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{GRID}" stroke-width="1"/>
    </pattern>
    <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.05"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <style>
      .rm{{display:none}}
      .bar{{transform-origin:83px 92px;animation:barIn .8s ease-out both}}
      @keyframes barIn{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
      .fadeUp{{opacity:0;animation:fadeUp .7s ease-out .1s forwards}}
      @keyframes fadeUp{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
      .dot{{animation:dot 1.6s ease-in-out infinite}}
      @keyframes dot{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
      .sheen{{animation:sheen 14s linear infinite}}
      @keyframes sheen{{from{{transform:translateX(0)}}to{{transform:translateX({W + 260}px)}}}}
      @media (prefers-reduced-motion:reduce){{
        *{{animation:none!important}}
        .anim{{display:none}}
        .rm{{display:block}}
        .fadeUp{{opacity:1}}
      }}
    </style>
  </defs>

  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <rect class="sheen" x="-260" y="0" width="260" height="{H}" fill="url(#sheen)"/>

  <!-- status -->
  <text x="{W - 80}" y="62" text-anchor="end" fill="{MUTED}" font-family="{FONT_MONO}" font-size="16">{escape(STATUS)}</text>
  <circle class="dot" cx="{W - 94 - len(STATUS) * 9.5:.0f}" cy="56" r="6" fill="{ACCENT}"/>

  <!-- accent bar + identity -->
  <rect class="bar" x="80" y="92" width="6" height="140" fill="{ACCENT}"/>
  <g class="fadeUp">
    <text x="{LINE_X - 2}" y="146" fill="{TEXT}" font-family="{FONT_SANS}" font-size="54" font-weight="700" letter-spacing="2">{escape(NAME)}</text>
    <text x="{LINE_X}" y="196" fill="{MUTED}" font-family="{FONT_SANS}" font-size="24">{escape(TAGLINE)}</text>
  </g>

  <!-- animated typing rotation (one group per concept, staggered) -->
{anim_groups}

  <!-- static fallback for prefers-reduced-motion -->
  <g class="rm">
    <text x="{LINE_X}" y="{LINE_Y}" fill="{MONO_TEXT}" font-family="{FONT_MONO}" font-size="{MONO_SIZE}">{escape(CONCEPTS[0])}</text>
  </g>
</svg>
"""


def build_divider() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="12" viewBox="0 0 {W} 12" role="img" aria-label="section divider">
  <defs>
    <linearGradient id="pulse" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{ACCENT}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
    </linearGradient>
    <style>
      .p{{animation:sweep 8s linear infinite}}
      @keyframes sweep{{from{{transform:translateX(-140px)}}to{{transform:translateX({W}px)}}}}
      @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
    </style>
  </defs>
  <rect x="0" y="5" width="{W}" height="2" fill="#21262d"/>
  <rect class="p" x="0" y="5" width="140" height="2" fill="url(#pulse)"/>
</svg>
"""


def main() -> None:
    banner = OUT / "banner-animated.svg"
    divider = OUT / "divider.svg"
    banner.write_text(build_banner(), encoding="utf-8")
    divider.write_text(build_divider(), encoding="utf-8")
    print(f"wrote {banner.relative_to(ROOT)} ({banner.stat().st_size / 1024:.1f} KB)")
    print(f"wrote {divider.relative_to(ROOT)} ({divider.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
