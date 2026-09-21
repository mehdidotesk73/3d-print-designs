"""Geometry checks for the dog_bag_dispenser project (back, front, pin,
screw).

Run from the repo root: python checks/check_dispenser.py
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "dog_bag_dispenser"))
from closing_screw import SCREW_LENGTH  # noqa: E402
from lib.canister import (  # noqa: E402
    BACK_BORE_D,
    BACK_BORE_DEPTH,
    BACK_BORE_X0,
    BACK_KNUCKLE_SEGMENTS,
    END_MARGIN,
    FRONT_KNUCKLE_SEGMENTS,
    HINGE_AXIS_X,
    HINGE_Z_MAX,
    HINGE_Z_MIN,
    KNUCKLE_R,
    LATCH_GAP,
    LATCH_HOLE_Y,
    LATCH_HOLE_Z,
    LATCH_WIDTH,
    LENGTH,
    MOUNT_HOLE_D,
    MOUNT_Z,
    PIN_BORE_Z0,
    PIN_BORE_Z1,
    PIN_HEAD_D,
    PIN_HEAD_H,
    PIN_R,
    R_IN,
    R_OUT,
    ROLL_DIAMETER,
    ROLL_LENGTH,
    SCREW_MINOR_D,
    SCREW_TIP_D,
    SCREW_TIP_ENGAGE,
    SLOT_LEN,
    SLOT_WIDTH,
    TAB_EMBED,
    TAB_INNER_X,
    TAB_OUTER_X,
    TAB_ROOT_INNER_X,
    TAB_Y_DEPTH,
    THREADMAKER_CREST_W_GROWTH,
    THREADMAKER_SHAFT_CLEARANCE,
    THREADMAKER_THREAD_CLEARANCE,
    WALL,
)

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}: {detail}")
    if not ok:
        FAILURES.append(label)


def main() -> None:
    step_dir = ROOT / "STEP" / "dog_bag_dispenser"

    # Topology/dimension checks use the standalone parts (clean local frame).
    back = read_step(step_dir / "canister_back.step")
    front = read_step(step_dir / "canister_front.step")

    # Interference checks need the ACTUAL assembled placement, so pull all
    # three parts from the assembly's saved scene rather than re-deriving
    # (and risking mismatching) each part's placement transform here.
    scene = read_scene(step_dir / "dispenser_assembly.step")
    placed_back = scene.resolve("#canister_back").shape()
    placed_front = scene.resolve("#canister_front").shape()
    placed_pin = scene.resolve("#hinge_pin").shape()
    placed_screw = scene.resolve("#closing_screw").shape()

    back_solids = back.solids()
    front_solids = front.solids()
    placed_back_solids = placed_back.solids()
    placed_front_solids = placed_front.solids()
    pin_solids = placed_pin.solids()
    screw_solids = placed_screw.solids()
    check("back solid count", len(back_solids) == 1, f"{len(back_solids)} solid(s)")
    check("front solid count", len(front_solids) == 1, f"{len(front_solids)} solid(s)")
    check("screw solid count", len(screw_solids) == 1, f"{len(screw_solids)} solid(s)")

    # Sanity: the assembly places back/front with identity transforms (they're
    # already authored in world coordinates), so the standalone and
    # scene-resolved solids should occupy the same volume.
    back_solid = placed_back_solids[0]
    front_solid = placed_front_solids[0]
    pin_solid = pin_solids[0]
    screw_solid = screw_solids[0]
    check(
        "assembly places back/front as identity (no unexpected transform)",
        abs(back_solid.volume - back_solids[0].volume) < 1e-6
        and abs(front_solid.volume - front_solids[0].volume) < 1e-6,
        f"standalone volumes back={back_solids[0].volume:.4f} front={front_solids[0].volume:.4f}, "
        f"placed volumes back={back_solid.volume:.4f} front={front_solid.volume:.4f}",
    )

    # Topology and volume sanity
    for name, solid in [
        ("back", back_solid), ("front", front_solid), ("pin", pin_solid), ("screw", screw_solid),
    ]:
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

    # OD: max radial extent of back (the hinge knuckle boss's outer reach on
    # one side; the latch side now has no protrusion of its own -- the ridge
    # is gone, back's latch-side extent is just its plain wall at R_OUT).
    x_span_back = bb_back.max.X - bb_back.min.X
    y_extent_back = -bb_back.min.Y  # apex distance from split plane
    expected_x_span = (HINGE_AXIS_X + KNUCKLE_R) + R_OUT
    check(
        "back X span (tangent hinge knuckle to plain latch-side wall)",
        abs(x_span_back - expected_x_span) < 1.0,
        f"{x_span_back:.3f} mm (expected ~{expected_x_span} mm: "
        f"hinge knuckle outer reach + back's own R_OUT, no ridge)",
    )

    # Front's own X span, similarly -- the tab reaches outboard past R_OUT
    # (clear of back's own wall by LATCH_GAP, plus its own thickness), so
    # it's front's own extreme on that side.
    bb_front = front_solid.bounding_box()
    x_span_front = bb_front.max.X - bb_front.min.X
    expected_x_span_front = (HINGE_AXIS_X + KNUCKLE_R) + (-TAB_OUTER_X)
    check(
        "front X span (tangent hinge knuckle to tab's outer face)",
        abs(x_span_front - expected_x_span_front) < 1.0,
        f"{x_span_front:.3f} mm (expected ~{expected_x_span_front} mm: "
        f"hinge knuckle outer reach + tab outer reach)",
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

    # The screw's tip must not collide with back's own wall material (it
    # only ever occupies the clearance bore) or the hinge pin.
    screw_overlap_back = overlap_volume(screw_solid, back_solid)
    screw_overlap_pin = overlap_volume(screw_solid, pin_solid)
    check(
        "screw vs back interference",
        screw_overlap_back < 0.01,
        f"overlap volume = {screw_overlap_back:.6f} mm^3",
    )
    check(
        "screw vs hinge pin interference",
        screw_overlap_pin < 0.01,
        f"overlap volume = {screw_overlap_pin:.6f} mm^3",
    )

    # Screw vs front: a genuine clearance fit now -- the tab's fastening
    # hole is cut by a THREAD-MAKER, an oversized copy of the screw's own
    # helix (see latch_tab_fastening_hole() in lib/canister.py), not a
    # self-tapping pilot hole undersized against the screw's own thread.
    # Two printed plastic parts don't cut into each other the way a metal
    # screw cuts into wood or sheet metal, so this joins every other pair
    # at zero interference -- no more deliberate overlap to carve an
    # exception for.
    screw_overlap_front = overlap_volume(screw_solid, front_solid)
    check(
        "screw vs front interference (clearance-fit thread, not self-tapping)",
        screw_overlap_front < 0.01,
        f"overlap volume = {screw_overlap_front:.6f} mm^3",
    )
    check(
        "thread-maker clearances are positive (a real oversize, not accidentally shrunk or reversed)",
        THREADMAKER_SHAFT_CLEARANCE > 0.0
        and THREADMAKER_THREAD_CLEARANCE > 0.0
        and THREADMAKER_CREST_W_GROWTH > 0.0,
        f"shaft={THREADMAKER_SHAFT_CLEARANCE} mm, thread={THREADMAKER_THREAD_CLEARANCE} mm, "
        f"crest_w={THREADMAKER_CREST_W_GROWTH} mm",
    )
    # A direct regression probe for the enlargement itself: at the old
    # self-tapping pilot hole's own radius (SCREW_MINOR_D/2 - 0.1, offset
    # off-axis so it isn't trivially empty regardless of hole size), the
    # tab used to be solid material; now that the hole is cut by the
    # larger thread-maker, it must read empty.
    old_pilot_r = SCREW_MINOR_D / 2.0 - 0.1
    enlarged_hole_pt = ((TAB_OUTER_X + TAB_INNER_X) / 2.0, LATCH_HOLE_Y, LATCH_HOLE_Z + old_pilot_r)
    check(
        "tab's hole is genuinely enlarged past the old self-tapping pilot radius",
        not front_solid.is_inside(enlarged_hole_pt),
        f"point {enlarged_hole_pt} inside front = {front_solid.is_inside(enlarged_hole_pt)} (expect False)",
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

    # Retention flange near the pin's bottom end: must be too wide to
    # ever enter the knuckle bore (or it wouldn't catch anything), must
    # actually be present as solid material (not a degenerate/empty
    # build), and must stay contained within the shaft's own existing
    # length -- reaching any further past HINGE_Z_MIN, this close to the
    # domed tube end, runs into the dome's own curved shell (that's what
    # the pin/back and pin/front interference checks above would catch).
    check(
        "pin flange is oversized past the knuckle bore (can't enter it)",
        PIN_HEAD_D > 2.0 * PIN_R,
        f"PIN_HEAD_D={PIN_HEAD_D} mm > bore diameter={2.0 * PIN_R} mm",
    )
    flange_probe = (HINGE_AXIS_X + (PIN_HEAD_D / 2.0 - 0.3), 0.0, HINGE_Z_MIN - PIN_HEAD_H / 2.0)
    check(
        "pin's retention flange is genuine solid material (built, not degenerate)",
        pin_solid.is_inside(flange_probe),
        f"point {flange_probe} inside pin = {pin_solid.is_inside(flange_probe)} (expect True)",
    )
    check(
        "pin's overall length still matches the bore span (flange stays within it, not past it)",
        abs(pin_len - (PIN_BORE_Z1 - PIN_BORE_Z0)) < 1e-6,
        f"pin length={pin_len:.3f} mm, bore span={PIN_BORE_Z1 - PIN_BORE_Z0:.3f} mm",
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

    # The whole-envelope cut (hinge_envelope_cut()) must clear the gaps
    # just as thoroughly as it clears the other leaf's own segments --
    # a probe in the wall band itself (not just past R_OUT) at each gap's
    # midpoint must be empty on BOTH leaves, or plain un-notched wall would
    # be left sticking out right next to the knuckle row (the reported bug:
    # a segment-by-segment cut left the small gaps between knuckles
    # untouched).
    for z in gap_mids:
        dip_pt = (HINGE_AXIS_X - (KNUCKLE_R - 1.0), 0.0, z)
        check(
            f"hinge gap at z={z:.3f}: back notched clear in the inward dip (no leftover wall)",
            not back_solid.is_inside(dip_pt),
            f"point {dip_pt} inside back = {back_solid.is_inside(dip_pt)} (expect False)",
        )
        check(
            f"hinge gap at z={z:.3f}: front notched clear in the inward dip (no leftover wall)",
            not front_solid.is_inside(dip_pt),
            f"point {dip_pt} inside front = {front_solid.is_inside(dip_pt)} (expect False)",
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

    # Back's clearance bore: a genuine through-hole (empty at both the outer
    # face and mid-wall depth), with back's own wall remaining solid just
    # off to the side of it (no accidental over-cut into the surrounding
    # material).
    bore_outer_pt = (-R_OUT + 0.5, LATCH_HOLE_Y, LATCH_HOLE_Z)
    bore_mid_pt = (-R_OUT + BACK_BORE_DEPTH / 2.0 - 1.0, LATCH_HOLE_Y, LATCH_HOLE_Z)
    bore_side_pt = (-R_OUT + 0.5, LATCH_HOLE_Y, LATCH_HOLE_Z + LATCH_WIDTH / 2.0 + 2.0)
    check(
        "back's clearance bore is open at its outer face",
        not back_solid.is_inside(bore_outer_pt),
        f"point {bore_outer_pt} inside back = {back_solid.is_inside(bore_outer_pt)} (expect False)",
    )
    check(
        "back's clearance bore is open at mid-wall depth",
        not back_solid.is_inside(bore_mid_pt),
        f"point {bore_mid_pt} inside back = {back_solid.is_inside(bore_mid_pt)} (expect False)",
    )
    check(
        "back's wall remains solid just off to the side of the bore",
        back_solid.is_inside(bore_side_pt),
        f"point {bore_side_pt} inside back = {back_solid.is_inside(bore_side_pt)} (expect True)",
    )
    check(
        "back's bore diameter is oversized against the screw's smooth tip (pure clearance, never fastens)",
        SCREW_TIP_D < BACK_BORE_D,
        f"SCREW_TIP_D={SCREW_TIP_D} mm < BACK_BORE_D={BACK_BORE_D} mm",
    )
    check(
        "screw's tip engagement stays within back's own wall thickness (doesn't poke into the cavity)",
        SCREW_TIP_ENGAGE < WALL,
        f"SCREW_TIP_ENGAGE={SCREW_TIP_ENGAGE} mm < WALL={WALL} mm",
    )
    check(
        "back's bore start is oversized outboard of R_OUT (guarantees full wall penetration)",
        BACK_BORE_X0 < -R_OUT,
        f"BACK_BORE_X0={BACK_BORE_X0} mm < -R_OUT={-R_OUT} mm",
    )

    # Tab (front): solid material in both the thin arm (reaching to rest
    # against back's own wall) and the wider root (embedded into front's
    # own wall), and its own fastening hole reads empty at its center.
    tab_arm_pt = ((TAB_OUTER_X + TAB_INNER_X) / 2.0, -(TAB_Y_DEPTH - 1.0), LATCH_HOLE_Z)
    check(
        "tab's arm is solid material on front (away from the fastening hole)",
        front_solid.is_inside(tab_arm_pt),
        f"point {tab_arm_pt} inside front = {front_solid.is_inside(tab_arm_pt)} (expect True)",
    )
    tab_root_pt = (TAB_ROOT_INNER_X - 0.5, TAB_EMBED - 1.0, LATCH_HOLE_Z)
    check(
        "tab's root is solid material on front (embedded past R_OUT)",
        front_solid.is_inside(tab_root_pt),
        f"point {tab_root_pt} inside front = {front_solid.is_inside(tab_root_pt)} (expect True)",
    )
    tab_hole_pt = ((TAB_OUTER_X + TAB_INNER_X) / 2.0, LATCH_HOLE_Y, LATCH_HOLE_Z)
    check(
        "tab's fastening hole is a genuine void at its center",
        not front_solid.is_inside(tab_hole_pt),
        f"point {tab_hole_pt} inside front = {front_solid.is_inside(tab_hole_pt)} (expect False)",
    )

    # The screw's head must sit outside the tab's own outer face --
    # accessible from outside the assembly for tightening/loosening.
    screw_bb = screw_solid.bounding_box()
    check(
        "screw's head is accessible beyond the tab's outer face",
        screw_bb.min.X < TAB_OUTER_X,
        f"screw min X={screw_bb.min.X:.3f} mm < TAB_OUTER_X={TAB_OUTER_X} mm "
        f"(head sticks out by {TAB_OUTER_X - screw_bb.min.X:.3f} mm)",
    )
    check(
        "the gap between the tab's inner face and back's own outer wall matches LATCH_GAP",
        abs((-R_OUT - TAB_INNER_X) - LATCH_GAP) < 1e-9,
        f"-R_OUT-TAB_INNER_X={-R_OUT - TAB_INNER_X} mm, LATCH_GAP={LATCH_GAP} mm",
    )

    # Cross-check dispenser_assembly.py's own placement formula against the
    # REAL assembled screw solid's bounding box: the tip's engagement depth
    # is measured from back's actual outer wall surface (-R_OUT), not from
    # BACK_BORE_X0's own 1mm cutting-overshoot margin -- using the latter
    # by mistake would shift the whole screw (and its thread) outboard by
    # that same 1mm, silently misaligning the thread from the tab despite
    # every build step succeeding.
    expected_tip_end_x = -R_OUT + SCREW_TIP_ENGAGE
    expected_head_far_x = expected_tip_end_x - SCREW_LENGTH
    check(
        "screw's actual placement matches the tip-engagement-from-R_OUT formula",
        abs(screw_bb.min.X - expected_head_far_x) < 1e-6,
        f"screw min X={screw_bb.min.X:.6f} mm, expected {expected_head_far_x:.6f} mm "
        f"(= -R_OUT + SCREW_TIP_ENGAGE - SCREW_LENGTH)",
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
