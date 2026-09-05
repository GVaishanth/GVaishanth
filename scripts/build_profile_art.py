"""Build the dynamic GitHub-profile telemetry HUD.

Every scheduled run fetches public GitHub repository activity and composites
the currently-active project name onto the telemetry HUD panel
(assets/profile/current-build.png), using current-build-bg.png as the
evergreen background. Hero and project cards are permanent assets and are
never touched.

Fixes vs. previous version
--------------------------
1. Fallback "sort" keys are now UNIX EPOCH (0.0) instead of the strings
   "4"/"3"/"2"/"1". Under the old scheme, if the API call succeeded but a
   featured repo was missing from the response (rename, transient error),
   its fallback key "4" lexicographically outranked real ISO timestamps
   like "2026-08-01T..." and the HUD displayed the wrong active project.
2. The composited PNG is now optimised on write (stripped metadata,
   capped at 1600px wide) — the old pipeline shipped ~1.1 MB panels.
3. Temp-file cleanup is guaranteed with try/finally.
"""
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json
import os
import subprocess
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
        # sort = 0.0 means "no data" — it can never outrank a real timestamp.
        name: {"language": lang, "pushed": "LIVE", "sort": 0.0}
        for name, lang in (
            ("Volt", "TypeScript"),
            ("Velocity", "JavaScript"),
            ("Computer-Cricket", "HTML"),
            ("VelvetStack", "JavaScript"),
        )
    }
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "gvaishanth-profile-art",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(
            "https://api.github.com/users/GVaishanth/repos?per_page=100&type=owner",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            repos = json.load(response)
    except Exception:
        return fallback

    found = {}
    for repo in repos:
        name = repo.get("name")
        if name not in FEATURED:
            continue
        pushed_at = repo.get("pushed_at") or ""
        try:
            dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            human = dt.strftime("%d %b %Y")
            sort_key = dt.timestamp()
        except ValueError:
            human, sort_key = "LIVE", 0.0
        found[name] = {
            "language": repo.get("language") or "Web",
            "pushed": human,
            "sort": sort_key,
        }
    return {**fallback, **found}


def update_current_build(build_name, meta):
    """Composite active-project telemetry onto the HUD background."""
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
    <text x="980" y="200" text-anchor="middle" fill="#79e95d" font-family="{MONO}" font-size="28" font-weight="700" letter-spacing="0.18em">CURRENTLY BUILDING</text>
    <text x="980" y="325" text-anchor="middle" fill="#f4f7f4" font-family="{FONT}" font-size="96" font-weight="700" letter-spacing="0.02em">{escape(build_name)}</text>
    <text x="980" y="405" text-anchor="middle" fill="#a4b2a6" font-family="{FONT}" font-size="36" font-weight="400" letter-spacing="0.01em">{escape(meta['language'])} · last pushed {escape(meta['pushed'])}</text>
  </g>
</svg>"""

    tmp_svg = ROOT / "tmp_hud_overlay.svg"
    out_png = OUT / "current-build.png"
    try:
        tmp_svg.write_text(svg_overlay, encoding="utf-8")
        subprocess.run(
            [
                "convert",
                "-background", "none", str(bg_path), str(tmp_svg),
                "-composite",
                # Slim the output: strip metadata, cap width, recompress.
                "-strip",
                "-resize", "1600x>",
                "PNG24:" + str(out_png),
            ],
            check=True,
        )
    finally:
        tmp_svg.unlink(missing_ok=True)

    print(f"  -> HUD updated: {build_name} ({meta['language']} · {meta['pushed']})")


def main():
    snapshot = github_snapshot()
    current = max(FEATURED, key=lambda repo: snapshot[repo]["sort"])
    print(f"Active build detected: {current}")
    update_current_build(current, snapshot[current])
    print("Profile telemetry sync completed.")


if __name__ == "__main__":
    main()
