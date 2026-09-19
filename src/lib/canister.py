"""Shared geometry for the poop-bag dispenser: two half-cylinder shells
(back mounts to a wall, front hinges + latches onto it) that together form
a full tube around a bag roll.

Frame: cylinder axis is Z (vertical against the wall). The split plane is
XZ (Y=0), containing the axis. Back occupies Y<=0, front occupies Y>=0.
Both edges of the split sit at X=+R_OUT (hinge) and X=-R_OUT (latch).
The back's apex (X=0, Y=-R_OUT) is tangent to the wall; the front's apex
(X=0, Y=+R_OUT) carries the dispensing slit.
"""

from __future__ import annotations

from cadgen import build123d as bd

# Canister shell
R_OUT = 38.0
WALL = 3.0
R_IN = R_OUT - WALL
LENGTH = 45.0

# Hinge (edge at X=+R_OUT), pin parallel to Z
KNUCKLE_R = 4.0
KNUCKLE_CLEARANCE_R = 4.3
PIN_D = 3.0
PIN_R = PIN_D / 2 + 0.1  # 3.2mm bore for a 3mm pin
KNUCKLE_W = 8.0
KNUCKLE_GAP = 1.25

_seg_starts = []
_z = 0.0
for _ in range(5):
    _seg_starts.append(_z)
    _z += KNUCKLE_W + KNUCKLE_GAP
BACK_KNUCKLE_SEGMENTS = [
    (_seg_starts[0], _seg_starts[0] + KNUCKLE_W),
    (_seg_starts[2], _seg_starts[2] + KNUCKLE_W),
    (_seg_starts[4], _seg_starts[4] + KNUCKLE_W),
]
FRONT_KNUCKLE_SEGMENTS = [
    (_seg_starts[1], _seg_starts[1] + KNUCKLE_W),
    (_seg_starts[3], _seg_starts[3] + KNUCKLE_W),
]

# Wall mounting bosses (back only, at apex X=0, Y=-R_OUT)
MOUNT_HOLE_D = 4.5
MOUNT_COUNTERBORE_D = 8.0
MOUNT_COUNTERBORE_DEPTH = 2.0
MOUNT_BOSS_D = 12.0
MOUNT_BOSS_HEIGHT = 3.0
MOUNT_Z = (LENGTH * 0.5 - 15.0, LENGTH * 0.5 + 15.0)  # 7.5, 37.5 -> 30mm apart

# Latch (edge at X=-R_OUT): front has snap tabs, back has receiving windows
LATCH_Z = (LENGTH * 0.25, LENGTH * 0.75)  # 11.25, 33.75
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
