"""Build the 4K dynamic GitHub-profile telemetry HUD.

The profile visual system uses evergreen 4K photorealistic AI studio renders
featuring G. Vaishanth's authentic 16-cube Voxel Creature Logo (from Git1stPfp.png).
This automated workflow NEVER touches or overwrites the permanent photorealistic
hero and project showcase cards (hero-systems.png, card-volt.png, etc.).

Every 6 hours, it fetches public GitHub repository activity and dynamically
composites the currently active project onto the 4K telemetry HUD panel
(current-build.png) using current-build-bg.png as the evergreen background.
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


def github_snapshot():
    """Fetch featured-repository facts; remain usable offline or rate-limited."""
    fallback = {
        "Volt": {"language": "TypeScript", "pushed": "LIVE", "sort": "4"},
        "Velocity": {"language": "JavaScript", "pushed": "LIVE", "sort": "3"},
        "Computer-Cricket": {"language": "HTML", "pushed": "LIVE", "sort": "2"},
        "VelvetStack": {"language": "JavaScript", "pushed": "LIVE", "sort": "1"},
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
    except Exception:
        return fallback


def update_current_build(build_name, meta):
    """Dynamically composite active project telemetry onto the 4K HUD background."""
    width, height = 1952, 544
    bg_path = OUT / "current-build-bg.png"
    if not bg_path.exists():
        print(f"Warning: {bg_path} not found. Skipping composite.")
        return

    svg_overlay = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <filter id="drop-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000000" flood-opacity="0.85"/>
    </filter>
  </defs>
  <g filter="url(#drop-shadow)">
    <text x="980" y="200" text-anchor="middle" fill="#79e95d" font-family="{MONO}" font-size="28" font-weight="700" letter-spacing="0.18em">CURRENT BUILD / LIVE SIGNAL</text>
    <text x="980" y="325" text-anchor="middle" fill="#f4f7f4" font-family="{FONT}" font-size="96" font-weight="700" letter-spacing="0.02em">{escape(build_name)}</text>
    <text x="980" y="405" text-anchor="middle" fill="#a4b2a6" font-family="{FONT}" font-size="36" font-weight="400" letter-spacing="0.01em">{escape(meta['language'])} · last pushed {escape(meta['pushed'])}</text>
  </g>
</svg>"""

    tmp_svg = ROOT / "tmp_hud_overlay.svg"
    tmp_svg.write_text(svg_overlay, encoding="utf-8")

    out_png = OUT / "current-build.png"
    subprocess.run([
        "convert", "-background", "none", str(bg_path), str(tmp_svg),
        "-composite", str(out_png)
    ], check=True)

    if tmp_svg.exists():
        tmp_svg.unlink()
    print(f"  -> Dynamic 4K Telemetry HUD updated: {build_name} ({meta['language']} · {meta['pushed']})")


def main():
    snapshot = github_snapshot()
    current = max(FEATURED, key=lambda repo: snapshot[repo]["sort"])
    print(f"Active GitHub Build Detected: {current}")
    update_current_build(current, snapshot[current])
    print("Profile telemetry HUD sync completed.")


if __name__ == "__main__":
    main()
