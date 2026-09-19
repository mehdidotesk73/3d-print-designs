"""Shared geometry for the poop-bag dispenser: two half-cylinder shells
(back mounts to a wall, front hinges + latches onto it) that together form
a capsule around a bag roll -- a cylindrical mid-section capped by a
hemispherical dome at each end (each half contributing its own quarter-dome).

Frame: cylinder axis is Z (vertical against the wall). The split plane is
XZ (Y=0), containing the axis. Back occupies Y<=0, front occupies Y>=0.
Both edges of the split sit at X=+R_OUT (hinge) and X=-R_OUT (latch).
The back's apex (X=0, Y=-R_OUT) is tangent to the wall; the front's apex
(X=0, Y=+R_OUT) carries the dispensing slit.

Roll fit: the roll's diameter runs across the cavity ID (X/Y), and the
roll's length runs along the cylinder axis (Z) -- the opposite of the
first draft, corrected per the roll's actual proportions (short diameter,
long axis).
"""

from __future__ import annotations

from cadgen import build123d as bd

# Roll fit and clearance
ROLL_DIAMETER = 40.0
ROLL_LENGTH = 70.0
CLEARANCE = 4.0  # added to both the cavity ID and the axial length

# Canister shell
WALL = 3.0
R_IN = (ROLL_DIAMETER + CLEARANCE) / 2.0
R_OUT = R_IN + WALL
LENGTH = ROLL_LENGTH + CLEARANCE

# Hemispherical end caps: each half contributes a quarter-dome, radius R_OUT,
# so the closed assembly's ends read as a true half-sphere.
END_MARGIN = 8.0  # keep hinge/mount/latch features clear of the domed ends


def _pack_alternating_segments(
    length: float,
    margin: float,
    width: float,
    gap: float,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Pack width-wide segments (with gap between) into [margin, length-margin],
    centered, alternating A/B starting with A. Returns (a_segments, b_segments).
    """
    usable = length - 2.0 * margin
    n = max(3, int((usable + gap) // (width + gap)))
    span = n * width + (n - 1) * gap
    start = (length - span) / 2.0
    segments = []
    z = start
    for _ in range(n):
        segments.append((z, z + width))
        z += width + gap
    a = [seg for i, seg in enumerate(segments) if i % 2 == 0]
    b = [seg for i, seg in enumerate(segments) if i % 2 == 1]
    return a, b


# Hinge (edge at X=+R_OUT), pin parallel to Z
KNUCKLE_R = 4.0
KNUCKLE_CLEARANCE_R = 4.3
PIN_D = 3.0
PIN_R = PIN_D / 2 + 0.1  # 3.2mm bore for a 3mm pin
PIN_MARGIN = 1.0  # pin protrudes this far past the knuckle span on each end
KNUCKLE_W = 8.0
KNUCKLE_GAP = 1.25

BACK_KNUCKLE_SEGMENTS, FRONT_KNUCKLE_SEGMENTS = _pack_alternating_segments(
    LENGTH, END_MARGIN, KNUCKLE_W, KNUCKLE_GAP
)

# Wall mounting bosses (back only, at apex X=0, Y=-R_OUT)
MOUNT_HOLE_D = 4.5
MOUNT_COUNTERBORE_D = 8.0
MOUNT_COUNTERBORE_DEPTH = 2.0
MOUNT_BOSS_D = 12.0
MOUNT_BOSS_HEIGHT = 3.0
_mount_usable = LENGTH - 2.0 * END_MARGIN
MOUNT_Z = (END_MARGIN + _mount_usable * 0.25, END_MARGIN + _mount_usable * 0.75)

# Latch (edge at X=-R_OUT): front has snap tabs, back has receiving windows
LATCH_Z = (END_MARGIN + _mount_usable * 0.25, END_MARGIN + _mount_usable * 0.75)
TAB_WIDTH = 10.0
TAB_THK = 1.8
TAB_REACH = 6.0  # protrusion past the OD edge
BARB_LEN = 2.0
BARB_PROUD = 1.0  # each side beyond TAB_THK/2
WINDOW_Z_MARGIN = 0.5  # window is 1mm wider than the tab
WINDOW_Y_HALF = TAB_THK / 2 + BARB_PROUD - 0.3  # slight interference for snap retention

# Dispensing slit (front apex X=0, Y=+R_OUT)
SLOT_LEN = 40.0
SLOT_WIDTH = 12.0


def half_shell(front: bool) -> bd.Shape:
    """The plain 180-degree tube half: front is Y>=0, back is Y<=0."""
    ring = bd.Circle(R_OUT) - bd.Circle(R_IN)
    pad = R_OUT + 10.0
    align_y = bd.Align.MIN if front else bd.Align.MAX
    rect = bd.Rectangle(2.0 * pad, pad, align=(bd.Align.CENTER, align_y))
    half_ring = ring & rect
    return bd.extrude(half_ring, amount=LENGTH)


def _z_cylinder(radius: float, height: float, x: float, y: float, z0: float) -> bd.Shape:
    cyl = bd.Cylinder(radius, height, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    return bd.Pos(x, y, z0) * cyl


def _y_cylinder(radius: float, height: float, x: float, y0: float, z: float) -> bd.Shape:
    cyl = bd.Cylinder(
        radius,
        height,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        rotation=(-90.0, 0.0, 0.0),
    )
    return bd.Pos(x, y0, z) * cyl


def hinge_features(own_segments: list[tuple[float, float]], other_segments: list[tuple[float, float]]) -> tuple[bd.Shape, bd.Shape]:
    """Returns (bosses_with_bores_to_add, clearance_to_cut) for one leaf's hinge edge."""
    add = None
    for z0, z1 in own_segments:
        h = z1 - z0
        boss = _z_cylinder(KNUCKLE_R, h, R_OUT, 0.0, z0)
        bore = _z_cylinder(PIN_R, h + 1.0, R_OUT, 0.0, z0 - 0.5)
        piece = boss - bore
        add = piece if add is None else add + piece

    cut = None
    for z0, z1 in other_segments:
        h = z1 - z0
        piece = _z_cylinder(KNUCKLE_CLEARANCE_R, h, R_OUT, 0.0, z0)
        cut = piece if cut is None else cut + piece

    # The plain wall edge between knuckle segments still reaches X=R_OUT,Y=0
    # (the small KNUCKLE_GAP slivers aren't covered by either the boss bore
    # above or the other leaf's clearance cut), which would pinch the pin.
    # Cut a continuous PIN_R channel across the whole hinge span on both
    # leaves so the pin has clearance everywhere it passes, not just inside
    # the discrete knuckle segments. Extend it by PIN_MARGIN (plus a hair)
    # past the segments themselves, matching how far the pin overhangs them.
    all_segments = own_segments + other_segments
    span_z0 = min(s[0] for s in all_segments) - PIN_MARGIN - 0.5
    span_z1 = max(s[1] for s in all_segments) + PIN_MARGIN + 0.5
    channel = _z_cylinder(PIN_R, span_z1 - span_z0, R_OUT, 0.0, span_z0)
    cut = channel if cut is None else cut + channel

    return add, cut


def mount_features() -> tuple[bd.Shape, bd.Shape]:
    """Returns (bosses_to_add, holes_to_cut) for the back's wall-mount screws."""
    inner_face_y = -R_IN  # apex inner surface (cavity-facing)
    boss_inner_y = inner_face_y + MOUNT_BOSS_HEIGHT  # boss's own inner (cavity) face

    add = None
    cut = None
    for z in MOUNT_Z:
        boss = _y_cylinder(MOUNT_BOSS_D / 2.0, MOUNT_BOSS_HEIGHT, 0.0, inner_face_y, z)
        add = boss if add is None else add + boss

        hole_len = WALL + MOUNT_BOSS_HEIGHT + 4.0
        hole = _y_cylinder(MOUNT_HOLE_D / 2.0, hole_len, 0.0, -(R_OUT + 2.0), z)

        cb_start = boss_inner_y - 1.0
        cb = _y_cylinder(MOUNT_COUNTERBORE_D / 2.0, MOUNT_COUNTERBORE_DEPTH + 1.0, 0.0, cb_start, z)

        piece = hole + cb
        cut = piece if cut is None else cut + piece

    return add, cut


TAB_EMBED = 2.0  # extends the tab base into the wall so it truly fuses, not just touches at an edge


def _tab(z_center: float) -> bd.Shape:
    # Box axes: X = radial reach, Y = flex thickness (toward/away from the back), Z = axial width.
    x_outer = -R_OUT
    blade_x_max = x_outer + TAB_EMBED
    blade = bd.Box(TAB_REACH + TAB_EMBED, TAB_THK, TAB_WIDTH, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER))
    blade = bd.Pos(blade_x_max, 0.0, z_center) * blade

    barb_thk = TAB_THK + 2.0 * BARB_PROUD
    barb = bd.Box(BARB_LEN, barb_thk, TAB_WIDTH, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER))
    barb = bd.Pos(x_outer - TAB_REACH + BARB_LEN, 0.0, z_center) * barb

    return blade + barb


def latch_tabs() -> bd.Shape:
    """Front leaf: cantilever snap tabs at the latch edge."""
    add = None
    for z in LATCH_Z:
        piece = _tab(z)
        add = piece if add is None else add + piece
    return add


def latch_windows() -> bd.Shape:
    """Back leaf: cut receiving windows at the latch edge for the front tabs.

    Clears the FULL radial wall thickness (plus margin) at each latch
    position, so no leftover back material can collide with the front
    tab's embed depth regardless of exact tab geometry.
    """
    x_min = -(R_OUT + 2.0)
    x_max = -(R_IN - 2.0)
    width_x = x_max - x_min
    cut = None
    for z in LATCH_Z:
        window = bd.Box(
            width_x,
            2.0 * WINDOW_Y_HALF,
            TAB_WIDTH + 2.0 * WINDOW_Z_MARGIN,
            align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER),
        )
        window = bd.Pos(x_min, 0.0, z) * window
        cut = window if cut is None else cut + window
    return cut


def dispense_slot() -> bd.Shape:
    """Front leaf: dispensing slit centered on the outward-facing apex."""
    straight_len = SLOT_LEN - SLOT_WIDTH
    rect = bd.Rectangle(SLOT_WIDTH, straight_len)
    c1 = bd.Pos(0.0, straight_len / 2.0) * bd.Circle(SLOT_WIDTH / 2.0)
    c2 = bd.Pos(0.0, -straight_len / 2.0) * bd.Circle(SLOT_WIDTH / 2.0)
    stadium = rect + c1 + c2

    depth = (R_OUT - R_IN) + 6.0
    prism = bd.extrude(stadium, amount=depth)
    prism = prism.rotate(bd.Axis.X, -90.0)
    return bd.Pos(0.0, R_IN - 3.0, LENGTH / 2.0) * prism


def dome_cap(front: bool, at_bottom: bool) -> bd.Shape:
    """A quarter-sphere end cap for one leaf at one end of the tube.

    Radius matches R_OUT, so the two leaves' quarter-domes meet flush and,
    once closed, the two Z-ends of the assembly each read as a true
    hemisphere. Solid (not hollow): it seals the cavity's ends rather than
    continuing the bore into the dome.
    """
    z_end = 0.0 if at_bottom else LENGTH
    pad = R_OUT + 10.0

    sphere = bd.Pos(0.0, 0.0, z_end) * bd.Sphere(R_OUT)

    y_align = bd.Align.MIN if front else bd.Align.MAX
    y_box = bd.Pos(0.0, 0.0, z_end) * bd.Box(
        2.0 * pad, pad, 2.0 * pad, align=(bd.Align.CENTER, y_align, bd.Align.CENTER)
    )

    z_align = bd.Align.MAX if at_bottom else bd.Align.MIN
    z_box = bd.Pos(0.0, 0.0, z_end) * bd.Box(
        2.0 * pad, 2.0 * pad, pad, align=(bd.Align.CENTER, bd.Align.CENTER, z_align)
    )

    return sphere & y_box & z_box
