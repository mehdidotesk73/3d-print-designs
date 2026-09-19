"""Geometry checks for the poop-bag dispenser (back, front, pin).

Run from the project root: python checks/check_dispenser.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from cadgen import read_scene, read_step
from cadgen.geometry import (
    closest_points,
    overlap_volume,
    self_intersections,
    topology_errors,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from lib.canister import (  # noqa: E402
    BACK_KNUCKLE_SEGMENTS,
    END_MARGIN,
    FRONT_KNUCKLE_SEGMENTS,
    HINGE_AXIS_X,
    HINGE_Z_MAX,
    HINGE_Z_MIN,
    KNUCKLE_R,
    LATCH_Z,
    LENGTH,
    MOUNT_HOLE_D,
    MOUNT_Z,
    PIN_BORE_Z0,
    PIN_BORE_Z1,
    PIN_R,
    R_IN,
    R_OUT,
    ROLL_DIAMETER,
    ROLL_LENGTH,
    SLOT_LEN,
    SLOT_WIDTH,
    WINDOW_Y_HIGH,
    WINDOW_Y_LOW,
)

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}: {detail}")
    if not ok:
        FAILURES.append(label)


def main() -> None:
    # Topology/dimension checks use the standalone parts (clean local frame).
    back = read_step(ROOT / "STEP" / "canister_back.step")
    front = read_step(ROOT / "STEP" / "canister_front.step")

    # Interference checks need the ACTUAL assembled placement, so pull all
    # three parts from the assembly's saved scene rather than re-deriving
    # (and risking mismatching) each part's placement transform here.
    scene = read_scene(ROOT / "STEP" / "dispenser_assembly.step")
    placed_back = scene.resolve("#canister_back").shape()
    placed_front = scene.resolve("#canister_front").shape()
    placed_pin = scene.resolve("#hinge_pin").shape()

    back_solids = back.solids()
    front_solids = front.solids()
    placed_back_solids = placed_back.solids()
    placed_front_solids = placed_front.solids()
    pin_solids = placed_pin.solids()
    check("back solid count", len(back_solids) == 1, f"{len(back_solids)} solid(s)")
    check("front solid count", len(front_solids) == 1, f"{len(front_solids)} solid(s)")

    # Sanity: the assembly places back/front with identity transforms (they're
    # already authored in world coordinates), so the standalone and
    # scene-resolved solids should occupy the same volume.
    back_solid = placed_back_solids[0]
    front_solid = placed_front_solids[0]
    pin_solid = pin_solids[0]
    check(
        "assembly places back/front as identity (no unexpected transform)",
        abs(back_solid.volume - back_solids[0].volume) < 1e-6
        and abs(front_solid.volume - front_solids[0].volume) < 1e-6,
        f"standalone volumes back={back_solids[0].volume:.4f} front={front_solids[0].volume:.4f}, "
        f"placed volumes back={back_solid.volume:.4f} front={front_solid.volume:.4f}",
    )

    # Topology and volume sanity
    for name, solid in [("back", back_solid), ("front", front_solid), ("pin", pin_solid)]:
        issues = topology_errors(solid)
        check(f"{name} topology", len(issues) == 0, f"{len(issues)} issue(s): {[i.code for i in issues]}")
        check(f"{name} positive volume", solid.volume > 0, f"volume={solid.volume:.2f} mm^3")

    crossings_back = self_intersections(back_solid)
    check("back self-intersections", len(crossings_back) == 0, f"{len(crossings_back)} crossing(s)")
    crossings_front = self_intersections(front_solid)
    check("front self-intersections", len(crossings_front) == 0, f"{len(crossings_front)} crossing(s)")

    # Roll fit: cavity ID and cylindrical length should clear the roll by CLEARANCE
    check(
        "cavity ID fits roll diameter",
        (2.0 * R_IN) > ROLL_DIAMETER,
        f"cavity ID={2.0 * R_IN:.1f} mm vs roll diameter={ROLL_DIAMETER} mm",
    )
    check(
        "cylindrical length fits roll length",
        LENGTH > ROLL_LENGTH,
        f"cylindrical length={LENGTH:.1f} mm vs roll length={ROLL_LENGTH} mm",
    )

    # Overall envelope: OD should be ~2*R_OUT across X and Y; Z span includes
    # the hemispherical dome caps (R_OUT beyond each end of the LENGTH span).
    bb_back = back_solid.bounding_box()
    bb_front = front_solid.bounding_box()
    combined_min_z = min(bb_back.min.Z, bb_front.min.Z)
    combined_max_z = max(bb_back.max.Z, bb_front.max.Z)
    expected_span = LENGTH + 2.0 * R_OUT
    check(
        "assembled axial span (cylinder + dome caps)",
        abs((combined_max_z - combined_min_z) - expected_span) < 0.01,
        f"{combined_max_z - combined_min_z:.3f} mm (expected {expected_span} mm = "
        f"{LENGTH} cylindrical + 2x{R_OUT} dome radius)",
    )

    # OD: max radial extent of back (tangent knuckle boss on the hinge edge;
    # the plain R_OUT boundary on the latch edge, since the hook itself is
    # on the front -- back's window is a cut, it adds no outward material).
    x_span_back = bb_back.max.X - bb_back.min.X
    y_extent_back = -bb_back.min.Y  # apex distance from split plane
    expected_x_span = (HINGE_AXIS_X + KNUCKLE_R) + R_OUT
    check(
        "back X span (tangent hinge knuckle to plain latch edge)",
        abs(x_span_back - expected_x_span) < 1.0,
        f"{x_span_back:.3f} mm (expected ~{expected_x_span} mm: "
        f"hinge knuckle outer reach + plain latch OD)",
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
    expected_mount_spacing = 0.5 * (LENGTH - 2.0 * END_MARGIN)
    check(
        "mount hole spacing",
        abs((MOUNT_Z[1] - MOUNT_Z[0]) - expected_mount_spacing) < 1e-9,
        f"{MOUNT_Z[1] - MOUNT_Z[0]:.3f} mm apart, at Z={MOUNT_Z}",
    )
    check(
        "mount holes clear of dome-capped ends",
        all(END_MARGIN <= z <= LENGTH - END_MARGIN for z in MOUNT_Z),
        f"Z={MOUNT_Z}, margin=[{END_MARGIN}, {LENGTH - END_MARGIN}]",
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

    # Generic hinge placement formula: axis = edge (R_OUT, 0) + normal (1, 0)
    # * pin bore radius -- see lib/canister.py.
    check(
        "hinge axis matches the edge + normal*pin_radius formula",
        abs(HINGE_AXIS_X - (R_OUT + PIN_R)) < 1e-9,
        f"HINGE_AXIS_X={HINGE_AXIS_X}, R_OUT+PIN_R={R_OUT + PIN_R}",
    )

    # Latch: at each LATCH_Z, back's window is a through-opening and front's
    # hook has real material sitting in it (the engaged/closed resting state).
    for z in LATCH_Z:
        window_pt = (-(R_OUT + 3.0), (WINDOW_Y_LOW + WINDOW_Y_HIGH) / 2.0, z)
        check(
            f"latch window through-opening on back at z={z}",
            not back_solid.is_inside(window_pt),
            f"point {window_pt} inside back = {back_solid.is_inside(window_pt)} (expect False)",
        )
        check(
            f"latch hook material present on front at z={z}",
            front_solid.is_inside(window_pt),
            f"point {window_pt} inside front = {front_solid.is_inside(window_pt)} (expect True)",
        )

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

    # Pin length vs hinge knuckle span, and clear of the domed ends
    knuckle_span = HINGE_Z_MAX - HINGE_Z_MIN
    pin_bb = pin_solid.bounding_box()
    pin_len = pin_bb.max.Z - pin_bb.min.Z
    check(
        "pin length covers knuckle span",
        pin_len >= knuckle_span,
        f"pin length={pin_len:.3f} mm, knuckle span={knuckle_span:.3f} mm",
    )
    check(
        "pin stays within END_MARGIN of the dome-capped ends",
        HINGE_Z_MIN >= END_MARGIN and HINGE_Z_MAX <= LENGTH - END_MARGIN,
        f"knuckle span=[{HINGE_Z_MIN}, {HINGE_Z_MAX}], "
        f"safe range=[{END_MARGIN}, {LENGTH - END_MARGIN}]",
    )

    # The whole point of the tangent hinge placement: the pin bore must be a
    # genuine through-channel, open to free air just past each end of the
    # knuckle row, not fully enclosed within either leaf's own wall material
    # (which is what the old centered/embedded hinge did once the dome caps
    # sealed the tube's ends -- there was nowhere to slide the pin in from).
    for z_end, z_dir, label in [(PIN_BORE_Z0, -1.0, "bottom"), (PIN_BORE_Z1, 1.0, "top")]:
        open_pt = (HINGE_AXIS_X, 0.0, z_end + z_dir * 1.0)
        check(
            f"pin bore open to free air past the {label} end of the knuckle row",
            not back_solid.is_inside(open_pt) and not front_solid.is_inside(open_pt),
            f"point {open_pt} inside back={back_solid.is_inside(open_pt)} "
            f"front={front_solid.is_inside(open_pt)} (expect both False)",
        )

    # Dome caps: each half's quarter-dome should be a hollow WALL-thick shell,
    # matching the main cylinder -- solid between R_IN and R_OUT, empty
    # inside R_IN (continuing the cavity), and empty past R_OUT.
    for solid, is_front, name in [(back_solid, False, "back"), (front_solid, True, "front")]:
        y_sign = 1.0 if is_front else -1.0
        for at_bottom, z_end in [(True, 0.0), (False, LENGTH)]:
            z_dir = -1.0 if at_bottom else 1.0
            hollow_pt = (0.0, y_sign * 10.0, z_end + z_dir * 15.0)  # dist ~18mm < R_IN=22
            wall_pt = (0.0, y_sign * 10.0, z_end + z_dir * (R_OUT - 5.0))  # dist ~22.4, in [R_IN,R_OUT]
            outside_pt = (0.0, y_sign * 10.0, z_end + z_dir * (R_OUT + 5.0))
            label = f"{name} dome at z_end={z_end}"
            check(
                f"{label}: hollow (point inside R_IN continues the cavity)",
                not solid.is_inside(hollow_pt),
                f"point {hollow_pt} inside solid = {solid.is_inside(hollow_pt)} (expect False)",
            )
            check(
                f"{label}: shell wall (point between R_IN and R_OUT is solid)",
                solid.is_inside(wall_pt),
                f"point {wall_pt} inside solid = {solid.is_inside(wall_pt)} (expect True)",
            )
            check(
                f"{label}: bounded (point past the dome radius is empty)",
                not solid.is_inside(outside_pt),
                f"point {outside_pt} inside solid = {solid.is_inside(outside_pt)} (expect False)",
            )

    # Hinge gaps: at the midpoint between consecutive knuckle segments (owned
    # by neither leaf), neither leaf should have a knuckle boss there -- a
    # probe right at the tangent knuckle axis (beyond R_OUT, so the plain
    # wall can never reach it regardless) must be empty on both back and
    # front.
    ordered = sorted(BACK_KNUCKLE_SEGMENTS + FRONT_KNUCKLE_SEGMENTS)
    gap_mids = [(ordered[i][1] + ordered[i + 1][0]) / 2.0 for i in range(len(ordered) - 1)]
    for z in gap_mids:
        probe_back = (HINGE_AXIS_X, -0.1, z)
        probe_front = (HINGE_AXIS_X, 0.1, z)
        check(
            f"hinge gap at z={z:.3f} clear on back",
            not back_solid.is_inside(probe_back),
            f"point {probe_back} inside back = {back_solid.is_inside(probe_back)} (expect False)",
        )
        check(
            f"hinge gap at z={z:.3f} clear on front",
            not front_solid.is_inside(probe_front),
            f"point {probe_front} inside front = {front_solid.is_inside(probe_front)} (expect False)",
        )

    # Knuckles are full round, not sliced in half at the canister plane: at
    # each leaf's own knuckle segment, the far side of the knuckle bump
    # (past Y=0, poking into the OTHER leaf's Y-territory, near the
    # knuckle's own outer radius) must still be solid.
    for z0, z1 in BACK_KNUCKLE_SEGMENTS:
        z = (z0 + z1) / 2.0
        far_pt = (HINGE_AXIS_X, KNUCKLE_R - 0.5, z)  # +Y side, into front's territory
        check(
            f"back knuckle at z={z:.3f} is full round (far side solid)",
            back_solid.is_inside(far_pt),
            f"point {far_pt} inside back = {back_solid.is_inside(far_pt)} (expect True)",
        )
    for z0, z1 in FRONT_KNUCKLE_SEGMENTS:
        z = (z0 + z1) / 2.0
        far_pt = (HINGE_AXIS_X, -(KNUCKLE_R - 0.5), z)  # -Y side, into back's territory
        check(
            f"front knuckle at z={z:.3f} is full round (far side solid)",
            front_solid.is_inside(far_pt),
            f"point {far_pt} inside front = {front_solid.is_inside(far_pt)} (expect True)",
        )

    # The knuckle axis sits close enough to the parting edge that every
    # knuckle boss dips inward past R_OUT into the wall band on BOTH sides
    # of the parting line -- hinge_clearance() must notch the OTHER leaf out
    # there, or the two leaves would collide. Probe a point inside that
    # dip (on the axis, radially inward of HINGE_AXIS_X by most of
    # KNUCKLE_R) at each leaf's own knuckle segments: this leaf should be
    # solid there (its own knuckle), the other leaf must be empty (notched).
    for z0, z1 in BACK_KNUCKLE_SEGMENTS:
        z = (z0 + z1) / 2.0
        dip_pt = (HINGE_AXIS_X - (KNUCKLE_R - 1.0), 0.0, z)
        check(
            f"back knuckle at z={z:.3f}: back solid in the inward dip",
            back_solid.is_inside(dip_pt),
            f"point {dip_pt} inside back = {back_solid.is_inside(dip_pt)} (expect True)",
        )
        check(
            f"back knuckle at z={z:.3f}: front notched clear in the inward dip",
            not front_solid.is_inside(dip_pt),
            f"point {dip_pt} inside front = {front_solid.is_inside(dip_pt)} (expect False, hinge_clearance())",
        )
    for z0, z1 in FRONT_KNUCKLE_SEGMENTS:
        z = (z0 + z1) / 2.0
        dip_pt = (HINGE_AXIS_X - (KNUCKLE_R - 1.0), 0.0, z)
        check(
            f"front knuckle at z={z:.3f}: front solid in the inward dip",
            front_solid.is_inside(dip_pt),
            f"point {dip_pt} inside front = {front_solid.is_inside(dip_pt)} (expect True)",
        )
        check(
            f"front knuckle at z={z:.3f}: back notched clear in the inward dip",
            not back_solid.is_inside(dip_pt),
            f"point {dip_pt} inside back = {back_solid.is_inside(dip_pt)} (expect False, hinge_clearance())",
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
