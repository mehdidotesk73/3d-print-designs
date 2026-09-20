"""Builds the distributable STL bundle for the repo's HTML viewer
(index.html): rebuilds each project's CAD models, exports fresh STL files
into src/stl/, and regenerates src/stl/viewer_data.js -- the base64
payload the viewer embeds so its 3D preview works with the page opened
directly from disk (no local server: a plain fetch() of a local file is
blocked under file://, but a <script src> load isn't, so the STL bytes
travel as an embedded JS object instead of a fetched JSON file).

Run from the project root: python scripts/build_viewer_bundle.py

Add a new project's entrypoint script to MODEL_ENTRYPOINTS, and its
parts' stems to STL_EXPORTS, when a new project is added to the repo.
index.html's own PROJECTS/parts list needs the matching entries added by
hand -- this script only builds and exports the mesh data, it doesn't
author the viewer's part descriptions.
"""

from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# One entrypoint script per project -- running it rebuilds every model it
# depends on (cadgen rebuilds only what's stale, so this is cheap when
# nothing changed).
MODEL_ENTRYPOINTS = [
    ROOT / "src" / "dispenser_assembly.py",
]

# STEP stems to export as STL into src/stl/ -- every part a person should
# be able to view/download in index.html, not just the root assembly.
STL_EXPORTS = [
    "canister_back",
    "canister_front",
    "closing_screw",
    "hinge_pin",
    "dispenser_assembly",
]

STL_OUT_DIR = ROOT / "src" / "stl"


def build_models() -> None:
    for entry in MODEL_ENTRYPOINTS:
        print(f"[build] {entry.relative_to(ROOT)}")
        subprocess.run([sys.executable, str(entry), "--force"], cwd=entry.parent, check=True)


def export_stls() -> list[Path]:
    STL_OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_paths = []
    for stem in STL_EXPORTS:
        step_path = ROOT / "STEP" / f"{stem}.step"
        out_path = STL_OUT_DIR / f"{stem}.stl"
        print(f"[export] {step_path.relative_to(ROOT)} -> {out_path.relative_to(ROOT)}")
        subprocess.run(
            ["cadgen", "stl", "build", str(step_path), str(out_path), "--force"],
            cwd=ROOT, check=True,
        )
        out_paths.append(out_path)
    return out_paths


def write_viewer_data(stl_paths: list[Path]) -> None:
    data = {}
    for path in stl_paths:
        rel = path.relative_to(ROOT).as_posix()
        data[rel] = base64.b64encode(path.read_bytes()).decode("ascii")
    js_path = STL_OUT_DIR / "viewer_data.js"
    js_path.write_text("window.STL_DATA = " + json.dumps(data) + ";\n")
    print(f"[build] wrote {js_path.relative_to(ROOT)} ({len(data)} part(s))")


def main() -> None:
    build_models()
    stl_paths = export_stls()
    write_viewer_data(stl_paths)
    print("[build] done -- open index.html in a browser to view/download parts")


if __name__ == "__main__":
    main()
