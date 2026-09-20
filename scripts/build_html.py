"""Builds viewer_data.js: scans every src/<project>/viewer.json and its
stl/ folder, and writes one generated JS file with (a) every project's
part metadata (name/description/details/spec) and (b) a base64 payload
of every part's mesh, for index.html's offline 3D preview -- loaded via
<script src>, not fetch(): fetch()/XHR of a local file is blocked by the
browser under file:// (no CORS for that scheme), but a script load isn't,
which is what lets the preview work with index.html opened directly from
disk.

Run from the repo root: python scripts/build_html.py

Run this after any src/<project>/build.py run, and after editing any
project's viewer.json, to keep index.html in sync. Projects are
discovered automatically -- add a new one just by giving it its own
src/<project>/viewer.json + stl/ (via that project's own build.py); no
edit needed here or in index.html itself.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT_PATH = ROOT / "viewer_data.js"


def load_project(viewer_json: Path) -> tuple[dict, dict[str, str]]:
    project = json.loads(viewer_json.read_text())
    stl_dir = viewer_json.parent / "stl"
    stl_data = {}
    for part in project["parts"]:
        stl_path = stl_dir / part["stl"]
        if not stl_path.exists():
            raise FileNotFoundError(
                f"{project['id']}: part {part['id']!r} references {stl_path.relative_to(ROOT)}, "
                f"which doesn't exist -- run {viewer_json.parent.relative_to(ROOT)}/build.py first"
            )
        rel = stl_path.relative_to(ROOT).as_posix()
        part["stl"] = rel  # rewrite stem -> full repo-relative path index.html can load/link directly
        stl_data[rel] = base64.b64encode(stl_path.read_bytes()).decode("ascii")
    return project, stl_data


def main() -> None:
    projects = []
    stl_data: dict[str, str] = {}
    for viewer_json in sorted(SRC.glob("*/viewer.json")):
        project, project_stl_data = load_project(viewer_json)
        projects.append(project)
        stl_data.update(project_stl_data)
        print(f"[build] {viewer_json.relative_to(ROOT)}: {len(project['parts'])} part(s)")

    if not projects:
        raise SystemExit(f"no src/*/viewer.json found under {SRC.relative_to(ROOT)}")

    payload = "window.PROJECTS = " + json.dumps(projects) + ";\n"
    payload += "window.STL_DATA = " + json.dumps(stl_data) + ";\n"
    OUT_PATH.write_text(payload)
    print(f"[build] wrote {OUT_PATH.relative_to(ROOT)} ({len(projects)} project(s), {len(stl_data)} mesh(es))")


if __name__ == "__main__":
    main()
