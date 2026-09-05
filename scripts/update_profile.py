"""Automatic profile README updater for GVaishanth/GVaishanth.

Runs daily via .github/workflows/profile-updater.yml and refreshes the
marked sections of README.md using *real* public GitHub data only:

  <!-- AUTO:SPOTLIGHT:START --> ... <!-- AUTO:SPOTLIGHT:END -->
      A rotating "concept spotlight" - one shipped project per day,
      framed by the engineering concept behind it. Deterministic
      (day-of-year rotation), so it changes at most once every 24 hours.

  <!-- AUTO:RECENT:START --> ... <!-- AUTO:RECENT:END -->
      The 5 most recently pushed public repos with real dates, plus the
      languages active over the last 90 days. The profile repo itself is
      excluded so bot commits never feed the "activity" signal.

Design rules (intentional - do not loosen):
  * If nothing changed, the README is not rewritten and the workflow
    commits nothing. No content churn, no fake freshness.
  * Everything rendered is derived from the GitHub API; nothing here
    invents activity. A quiet month renders as a quiet month.
  * Failure-safe: if the API is unavailable, the run falls back to the
    committed snapshot in data/repos.json, so the profile still renders
    from recent data instead of skipping. If no snapshot exists either,
    the README is simply left untouched for the day.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CACHE = ROOT / "data" / "repos.json"

USER = "GVaishanth"
SELF_REPO = "GVaishanth"  # the profile repo; excluded from "recently active"
RECENT_COUNT = 5
STACK_WINDOW_DAYS = 90

# Curated concept framing for the rotating spotlight.
# Only repos listed here rotate; add new entries as projects ship.
SPOTLIGHTS = [
    {
        "repo": "Volt",
        "concept": "Local-first development tools",
        "line": "A development environment that lives entirely in the browser. Workspaces persist in OPFS, so no account or backend is ever required.",
    },
    {
        "repo": "VelvetStack",
        "concept": "Peer-to-peer multiplayer",
        "line": "Private card rooms over WebRTC where one host owns the state and every action is an explicit message. No accounts, no central server.",
    },
    {
        "repo": "Velocity",
        "concept": "Systems-driven game design",
        "line": "An F1 constructor-championship simulator: build the team, make the strategy calls, and live with them over a full season.",
    },
    {
        "repo": "Computer-Cricket",
        "concept": "Adaptive game AI",
        "line": "Hand cricket against an opponent that adapts to your patterns, with house-rule variants from Normal to Insane.",
    },
    {
        "repo": "CRPapp",
        "concept": "Resilient mobile engineering",
        "line": "A predictive crash-resilience framework for Android. My first Kotlin project.",
    },
    {
        "repo": "Salary_Decoder",
        "concept": "Data storytelling",
        "line": "Notebooks that turn messy inputs (salary breakups, spending logs, chat exports) into stories you can act on.",
    },
]

# Fallback one-liners for repos without a description on GitHub,
# used by the "recently active" table.
FALLBACK_FOCUS = {s["repo"]: s["line"].split(". ")[0].strip().rstrip(".")
                  for s in SPOTLIGHTS}


def fetch_repos() -> list[dict] | None:
    """Fetch public repo metadata; fall back to the on-disk cache."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "gvaishanth-profile-updater",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&sort=pushed"
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=20) as response:
            raw = json.load(response)
        repos = [
            {
                "name": r.get("name"),
                "html_url": r.get("html_url"),
                "homepage": r.get("homepage") or "",
                "description": r.get("description") or "",
                "language": r.get("language") or "",
                "pushed_at": r.get("pushed_at") or "",
            }
            for r in raw
        ]
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(repos, indent=2) + "\n", encoding="utf-8")
        print(f"Fetched {len(repos)} repos from the GitHub API.")
        return repos
    except Exception as exc:  # noqa: BLE001 - offline-safe by design
        print(f"GitHub API unavailable ({exc}).", end=" ")
        if CACHE.exists():
            print("Using cached snapshot in data/repos.json.")
            return json.loads(CACHE.read_text(encoding="utf-8"))
        print("No cache found - leaving README untouched.")
        return None


def human_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%d %b %Y")
    except ValueError:
        return "-"


def is_active(repo: dict, now: datetime) -> bool:
    try:
        pushed = datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00"))
    except ValueError:
        return False
    return (now - pushed).days <= STACK_WINDOW_DAYS


def render_spotlight(repos: list[dict], now: datetime) -> str:
    by_name = {r["name"]: r for r in repos}
    pool = [s for s in SPOTLIGHTS if s["repo"] in by_name]
    if not pool:
        return "_(spotlight unavailable; no featured repos found)_"
    pick = pool[now.toordinal() % len(pool)]
    repo = by_name[pick["repo"]]
    meta = []
    if repo["language"]:
        meta.append(f"`{repo['language']}`")
    if repo["pushed_at"]:
        meta.append(f"last push {human_date(repo['pushed_at'])}")
    meta_str = " · ".join(meta)
    live = (
        f" · **[Live ↗]({repo['homepage']})**"
        if repo["homepage"]
        else ""
    )
    return (
        f"**{pick['concept']}**: **[{pick['repo']}]({repo['html_url']})**{live}\n\n"
        f"{pick['line']}\n\n"
        f"{meta_str}\n\n"
        f"<sub>Rotates daily across shipped work. Updated by a scheduled GitHub Action.</sub>"
    )


def render_recent(repos: list[dict], now: datetime) -> str:
    public_work = [r for r in repos if r["name"] != SELF_REPO]
    recent = sorted(public_work, key=lambda r: r["pushed_at"], reverse=True)[:RECENT_COUNT]

    rows = ["| Project | Focus | Last push |", "|:--|:--|:--|"]
    for r in recent:
        focus = r["description"] or FALLBACK_FOCUS.get(r["name"], "Project")
        focus = focus.split("\n")[0].strip()
        live = f" ([demo ↗]({r['homepage']}))" if r["homepage"] else ""
        rows.append(f"| **[{r['name']}]({r['html_url']})**{live} | {focus} | {human_date(r['pushed_at'])} |")

    # Active stack: languages of repos pushed within the window,
    # ordered by most-recent use.
    languages: list[str] = []
    for r in sorted(public_work, key=lambda r: r["pushed_at"], reverse=True):
        if r["language"] and is_active(r, now) and r["language"] not in languages:
            languages.append(r["language"])
    stack = " · ".join(f"`{lang}`" for lang in languages) or "`-`"

    return (
        "\n".join(rows)
        + f"\n\n**Active over the last {STACK_WINDOW_DAYS} days:** {stack}\n\n"
        + "<sub>Refreshed daily from public GitHub activity · excludes automated commits to this profile repo.</sub>"
    )


def replace_section(content: str, tag: str, body: str) -> tuple[str, bool]:
    pattern = re.compile(
        rf"(<!--\s*AUTO:{tag}:START\s*-->).*?(<!--\s*AUTO:{tag}:END\s*-->)",
        re.DOTALL,
    )
    replacement = lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}"  # noqa: E731
    new, count = pattern.subn(replacement, content)
    if count == 0:
        print(f"Warning: marker AUTO:{tag} not found in README.md - section skipped.")
    return new, count > 0


def main() -> int:
    if not README.exists():
        print("README.md not found - nothing to update.")
        return 0

    repos = fetch_repos()
    if not repos:
        return 0

    now = datetime.now(timezone.utc)
    content = README.read_text(encoding="utf-8")
    updated = content
    updated, _ = replace_section(updated, "SPOTLIGHT", render_spotlight(repos, now))
    updated, _ = replace_section(updated, "RECENT", render_recent(repos, now))

    if updated == content:
        print("Sections already current - no changes.")
        return 0

    README.write_text(updated, encoding="utf-8")
    print("README.md updated (spotlight + recently active).")

    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write("changed=true\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
