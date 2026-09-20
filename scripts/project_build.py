"""Shared plumbing for each project's own src/<project>/build.py.

A project's build.py stays a short, declarative list (its model
entrypoints and STL export stems); the actual subprocess calls live here
once instead of being copy-pasted into every project.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def build_models(root: Path, entrypoints: list[Path]) -> None:
    """Rerun each entrypoint script -- cadgen rebuilds only what's stale,
    so this is cheap when nothing changed."""
    for entry in entrypoints:
        print(f"[build] {entry.relative_to(root)}")
        subprocess.run([sys.executable, str(entry), "--force"], cwd=entry.parent, check=True)


def export_stls(root: Path, step_dir: Path, stl_dir: Path, stems: list[str]) -> None:
    """Export STEP/<stem>.step -> stl_dir/<stem>.stl for each stem, via
    cadgen's own STL door."""
    stl_dir.mkdir(parents=True, exist_ok=True)
    for stem in stems:
        step_path = step_dir / f"{stem}.step"
        out_path = stl_dir / f"{stem}.stl"
        print(f"[export] {step_path.relative_to(root)} -> {out_path.relative_to(root)}")
        subprocess.run(
            ["cadgen", "stl", "build", str(step_path), str(out_path), "--force"],
            cwd=root, check=True,
        )
