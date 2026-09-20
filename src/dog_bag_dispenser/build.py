"""Builds this project only: rebuilds its CAD models and exports a fresh
STL for every part into stl/, alongside this script (committed to git,
so index.html can serve and let people download them).

Run: python src/dog_bag_dispenser/build.py

After this -- and whenever viewer.json's part descriptions change -- run
scripts/build_html.py from the repo root to refresh index.html with the
new meshes/text.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
ROOT = PROJECT_DIR.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from project_build import build_models, export_stls  # noqa: E402

# One entrypoint per independently-exported model -- running each
# rebuilds everything it depends on (cadgen rebuilds only what's stale).
MODEL_ENTRYPOINTS = [
    PROJECT_DIR / "dispenser_assembly.py",
]

# STEP stems to export as STL -- every part a person should be able to
# view/download, not just the root assembly.
STL_EXPORTS = [
    "canister_back",
    "canister_front",
    "closing_screw",
    "hinge_pin",
    "dispenser_assembly",
]


def main() -> None:
    build_models(ROOT, MODEL_ENTRYPOINTS)
    export_stls(ROOT, ROOT / "STEP" / PROJECT_DIR.name, PROJECT_DIR / "stl", STL_EXPORTS)
    print("[build] done -- run scripts/build_html.py from the repo root to refresh index.html")


if __name__ == "__main__":
    main()
