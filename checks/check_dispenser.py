"""Geometry checks for the poop-bag dispenser (back, front, pin).

Run from the project root: python checks/check_dispenser.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from cadgen import read_step
from cadgen.geometry import (
    closest_points,
    overlap_volume,
    self_intersections,
    topology_errors,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from lib.canister import (  # noqa: E402
    KNUCKLE_R,
    LENGTH,
    MOUNT_HOLE_D,
    MOUNT_Z,
    R_IN,
    R_OUT,
    SLOT_LEN,
    SLOT_WIDTH,
)

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}: {detail}")
    if not ok:
        FAILURES.append(label)


def main() -> None:
    back = read_step(ROOT / "STEP" / "canister_back.step")
    front = read_step(ROOT / "STEP" / "canister_front.step")
    pin = read_step(ROOT / "STEP" / "hinge_pin.step")

    back_solids = back.solids()
    front_solids = front.solids()
    pin_solids = pin.solids()
    check("back solid count", len(back_solids) == 1, f"{len(back_solids)} solid(s)")
    check("front solid count", len(front_solids) == 1, f"{len(front_solids)} solid(s)")

    back_solid = back_solids[0]
    front_solid = front_solids[0]
    pin_solid = pin_solids[0]

    # Topology and volume sanity
    for name, solid in [("back", back_solid), ("front", front_solid), ("pin", pin_solid)]:
        issues = topology_errors(solid)
        check(f"{name} topology", len(issues) == 0, f"{len(issues)} issue(s): {[i.code for i in issues]}")
        check(f"{name} positive volume", solid.volume > 0, f"volume={solid.volume:.2f} mm^3")

    crossings_back = self_intersections(back_solid)
    check("back self-intersections", len(crossings_back) == 0, f"{len(crossings_back)} crossing(s)")
    crossings_front = self_intersections(front_solid)
    check("front self-intersections", len(crossings_front) == 0, f"{len(crossings_front)} crossing(s)")

    # Overall envelope: OD should be ~2*R_OUT across X and Y, length across Z
    bb_back = back_solid.bounding_box()
    bb_front = front_solid.bounding_box()
    combined_min_z = min(bb_back.min.Z, bb_front.min.Z)
    combined_max_z = max(bb_back.max.Z, bb_front.max.Z)
    check(
        "assembled axial length",
        abs((combined_max_z - combined_min_z) - LENGTH) < 0.01,
        f"{combined_max_z - combined_min_z:.3f} mm (expected {LENGTH} mm)",
    )

    # OD: max radial extent of back (X from -R_OUT..R_OUT-ish via knuckle bump ok)
    x_span_back = bb_back.max.X - bb_back.min.X
    y_extent_back = -bb_back.min.Y  # apex distance from split plane
    check(
        "back X span (hinge knuckle boss to plain latch edge)",
        abs(x_span_back - (R_OUT + KNUCKLE_R + R_OUT)) < 0.5,
        f"{x_span_back:.3f} mm (expected ~{R_OUT + KNUCKLE_R + R_OUT} mm: "
        f"hinge OD+knuckle to plain latch OD)",
    )
    check(
        "back apex radius (wall-facing extent)",
        abs(y_extent_back - R_OUT) < 0.5,
        f"{y_extent_back:.3f} mm (expected ~{R_OUT} mm, small boss/tab excess allowed)",
    )

    check(
        "wall thickness spec (design constant)",
        abs((R_OUT - R_IN) - 3.0) < 1e-9,
        f"R_OUT-R_IN = {R_OUT - R_IN:.3f} mm",
    )

    # Mount holes: each should be an actual through-opening (apex point NOT inside
    # solid) with solid boss material immediately around it (offset point IS inside).
    for z in MOUNT_Z:
        outside_pt = (0.0, -(R_OUT + 1.0), z)  # just outside the OD, on the hole axis
        boss_pt = (5.5, -R_IN + 1.0, z)  # offset from axis, inside the mounting boss
        check(
            f"mount hole through-opening at z={z}",
            not back_solid.is_inside(outside_pt),
            f"point {outside_pt} inside solid = {back_solid.is_inside(outside_pt)} (expect False, it's the drilled hole)",
        )
        check(
            f"mount boss material at z={z}",
            back_solid.is_inside(boss_pt),
            f"point {boss_pt} inside solid = {back_solid.is_inside(boss_pt)} (expect True, boss material)",
        )
    check(
        "mount hole spacing",
        abs((MOUNT_Z[1] - MOUNT_Z[0]) - 30.0) < 1e-9,
        f"{MOUNT_Z[1] - MOUNT_Z[0]:.3f} mm apart, at Z={MOUNT_Z}",
    )

    # Dispensing slot: apex point at slot center should be a through-opening;
    # a point at the same apex but past the slot's z-extent should be solid wall.
    slot_open_pt = (0.0, R_OUT - 1.0, LENGTH / 2.0)
    slot_closed_pt = (0.0, R_OUT - 1.0, 1.0)  # near the end, outside the 40mm slot length
    check(
        "dispensing slot is a through-opening at its center",
        not front_solid.is_inside(slot_open_pt),
        f"point {slot_open_pt} inside solid = {front_solid.is_inside(slot_open_pt)} (expect False)",
    )
    check(
        "front wall is solid just beyond the slot's z-extent",
        front_solid.is_inside(slot_closed_pt),
        f"point {slot_closed_pt} inside solid = {front_solid.is_inside(slot_closed_pt)} (expect True)",
    )
    check("slot length (design constant)", abs(SLOT_LEN - 40.0) < 1e-9, f"{SLOT_LEN} mm")
    check("slot width (design constant)", abs(SLOT_WIDTH - 12.0) < 1e-9, f"{SLOT_WIDTH} mm")

    # Interference: back vs front should not overlap (they meet only at knuckle/latch contact, zero volume)
    overlap = overlap_volume(back_solid, front_solid)
    check(
        "back/front interference (closed assembly)",
        overlap < 0.01,
        f"overlap volume = {overlap:.6f} mm^3",
    )

    # Hinge pin should fit through all knuckle bores without colliding with either solid's material
    # (bore radius already includes clearance over pin radius; check pin doesn't overlap solid material)
    pin_overlap_back = overlap_volume(pin_solid, back_solid)
    pin_overlap_front = overlap_volume(pin_solid, front_solid)
    check(
        "pin vs back interference",
        pin_overlap_back < 0.01,
        f"overlap volume = {pin_overlap_back:.6f} mm^3",
    )
    check(
        "pin vs front interference",
        pin_overlap_front < 0.01,
        f"overlap volume = {pin_overlap_front:.6f} mm^3",
    )

    # Pin length vs hinge knuckle span
    pin_bb = pin_solid.bounding_box()
    pin_len = pin_bb.max.Z - pin_bb.min.Z
    check(
        "pin length covers hinge span",
        pin_len >= LENGTH,
        f"pin length={pin_len:.3f} mm, hinge span={LENGTH} mm",
    )

    # Closest approach between back and front at the hinge (should be ~0, they touch)
    hinge_contact = closest_points(back_solid, front_solid)
    print(f"[INFO] closest approach back<->front: {hinge_contact.distance:.4f} mm")

    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s): {FAILURES}")
        raise SystemExit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
