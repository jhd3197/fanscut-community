"""Check index.json before it is published. Standard library only.

    python scripts/validate.py            # shape and rules
    python scripts/validate.py --online   # also: each repo is public and has fanscut.json

The rules match FansCut's own reader (fanscut/community.py), which drops a bad
entry instead of failing: here a bad entry fails the check, so it never ships.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = {"merge", "supercut", "order", "canon", "character", "chronological", "cut"}
REPO = re.compile(r"^https://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9._-]+?)(?:\.git)?/?$")
TOP = {"schema", "updated", "cuts"}
CUT = {"name", "repo", "kind", "category", "tagline", "poster", "variants", "sources"}
SOURCE = {"tmdb", "tvdb", "title", "edition", "episodes", "optional"}


def text(v: object, limit: int, what: str, errors: list[str], required: bool = False) -> None:
    if v is None and not required:
        return
    if not isinstance(v, str) or (required and not v.strip()):
        errors.append(f"{what}: expected text")
    elif len(v) > limit:
        errors.append(f"{what}: over {limit} characters")
    elif any(ord(c) < 32 for c in v):
        errors.append(f"{what}: control characters")


def check_cut(i: int, cut: object, errors: list[str]) -> str | None:
    where = f"cuts[{i}]"
    if not isinstance(cut, dict):
        errors.append(f"{where}: expected an object")
        return None
    for k in sorted(set(cut) - CUT):
        errors.append(f"{where}: unknown field {k!r}")
    text(cut.get("name"), 120, f"{where}.name", errors, required=True)
    m = REPO.match(str(cut.get("repo", "")))
    if not m or ".." in str(cut.get("repo")):
        errors.append(f"{where}.repo: want https://github.com/<owner>/<name>")
    if cut.get("kind", "cut") not in KINDS:
        errors.append(f"{where}.kind: one of {', '.join(sorted(KINDS))}")
    text(cut.get("category"), 40, f"{where}.category", errors)
    text(cut.get("tagline"), 80, f"{where}.tagline", errors)
    if cut.get("poster") is not None and not str(cut["poster"]).startswith("https://"):
        errors.append(f"{where}.poster: must be https")
    variants = cut.get("variants", [])
    if not isinstance(variants, list) or len(variants) > 20:
        errors.append(f"{where}.variants: a list of up to 20 names")
    else:
        for j, v in enumerate(variants):
            text(v, 60, f"{where}.variants[{j}]", errors, required=True)
    sources = cut.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 200:
        errors.append(f"{where}.sources: a list of 1 to 200 sources")
        sources = []
    for j, s in enumerate(sources):
        sw = f"{where}.sources[{j}]"
        if not isinstance(s, dict):
            errors.append(f"{sw}: expected an object")
            continue
        for k in sorted(set(s) - SOURCE):
            errors.append(f"{sw}: unknown field {k!r}")
        ids = [k for k in ("tmdb", "tvdb") if k in s]
        if len(ids) != 1:
            errors.append(f"{sw}: exactly one of tmdb / tvdb")
        for k in ids:
            if not isinstance(s[k], int) or isinstance(s[k], bool) or s[k] < 1:
                errors.append(f"{sw}.{k}: a positive whole number")
        text(s.get("title"), 200, f"{sw}.title", errors, required=True)
        text(s.get("edition"), 50, f"{sw}.edition", errors)
        if "episodes" in s and (not isinstance(s["episodes"], int) or s["episodes"] < 1):
            errors.append(f"{sw}.episodes: a positive whole number")
        if "optional" in s and not isinstance(s["optional"], bool):
            errors.append(f"{sw}.optional: true or false")
    return f"{m.group(1)}/{m.group(2)}".lower() if m else None


def check_online(slug: str, errors: list[str]) -> None:
    """The repo must be public (FansCut installs it without a token) with a recipe."""
    url = f"https://api.github.com/repos/{slug}/contents/fanscut.json"
    req = urllib.request.Request(url, headers={"User-Agent": "fanscut-community-ci",
                                               "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20):
            pass
    except urllib.error.HTTPError as exc:
        why = ("not public, or no fanscut.json at its root" if exc.code == 404
               else f"GitHub said HTTP {exc.code}")
        errors.append(f"{slug}: {why}")
    except urllib.error.URLError as exc:
        errors.append(f"{slug}: could not reach GitHub ({exc.reason})")


def main(argv: list[str]) -> int:
    errors: list[str] = []
    try:
        doc = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"index.json: {exc}")
        return 1
    if not isinstance(doc, dict) or doc.get("schema") != 1 or not isinstance(doc.get("cuts"), list):
        print('index.json: want {"schema": 1, "cuts": [...]}')
        return 1
    for k in sorted(set(doc) - TOP):
        errors.append(f"unknown top-level field {k!r}")
    slugs: list[str] = []
    for i, cut in enumerate(doc["cuts"]):
        slug = check_cut(i, cut, errors)
        if slug:
            if slug in slugs:
                errors.append(f"cuts[{i}]: {slug} is listed twice")
            slugs.append(slug)
    if "--online" in argv:
        for slug in slugs:
            check_online(slug, errors)
    for e in errors:
        print(e)
    n = len(doc["cuts"])
    print(f"{'FAIL' if errors else 'ok'}: {n} cut{'' if n == 1 else 's'}, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
