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
PIN_D = 3.0
PIN_R = PIN_D / 2 + 0.1  # 3.2mm bore for a 3mm pin
PIN_MARGIN = 1.0  # pin protrudes this far past the knuckle span on each end
KNUCKLE_W = 8.0
KNUCKLE_GAP = 1.25

BACK_KNUCKLE_SEGMENTS, FRONT_KNUCKLE_SEGMENTS = _pack_alternating_segments(
    LENGTH, END_MARGIN, KNUCKLE_W, KNUCKLE_GAP
)
_ALL_KNUCKLE_SEGMENTS = BACK_KNUCKLE_SEGMENTS + FRONT_KNUCKLE_SEGMENTS
HINGE_Z_MIN = min(z0 for z0, _ in _ALL_KNUCKLE_SEGMENTS)
HINGE_Z_MAX = max(z1 for _, z1 in _ALL_KNUCKLE_SEGMENTS)

# Wall mounting bosses (back only, at apex X=0, Y=-R_OUT)
MOUNT_HOLE_D = 4.5
MOUNT_COUNTERBORE_D = 8.0
MOUNT_COUNTERBORE_DEPTH = 2.0
MOUNT_BOSS_D = 12.0
MOUNT_BOSS_HEIGHT = 3.0
_mount_usable = LENGTH - 2.0 * END_MARGIN
MOUNT_Z = (END_MARGIN + _mount_usable * 0.25, END_MARGIN + _mount_usable * 0.75)

# Lever latch (edge at X=-R_OUT): a fully rigid pivoting lever, printed as
# its own small part, pinned to the back via a mini version of the hinge's
# own knuckle construction (knuckle_row/knuckle_envelope_cut/reinforce_seam,
# reused directly). It swings to hook over a static lip on the front --
# a positive mechanical block, replacing the old cantilever hook, which had
# to rely on a flex point to self-release (see the git history for that
# reasoning): a rigid lever needs no flex anywhere, since it's a second,
# independently-actuated degree of freedom rather than a snap that has to
# both engage AND release from the same swing motion.
LATCH_PIN_D = 2.5
LATCH_PIN_R = LATCH_PIN_D / 2.0 + 0.1
LATCH_KNUCKLE_R = 3.5
LATCH_KNUCKLE_W = 6.0
LATCH_KNUCKLE_GAP = 1.2
LATCH_FILLET_R = 1.2

# Generic knuckle placement (edge + normal * pin radius), same formula as
# the hinge: here the edge is the tube's OTHER parting line (X=-R_OUT), and
# the normal points outward (-X) at that edge.
LATCH_EDGE_X = -R_OUT
LATCH_EDGE_Y = 0.0
LATCH_NORMAL_X = -1.0
LATCH_NORMAL_Y = 0.0
LATCH_AXIS_X = LATCH_EDGE_X + LATCH_NORMAL_X * LATCH_PIN_R
LATCH_AXIS_Y = LATCH_EDGE_Y + LATCH_NORMAL_Y * LATCH_PIN_R

# Three knuckle segments (fixed, lever, fixed), centered on the tube's own
# Z midpoint -- one lever latch is plenty for a dispenser this size.
LATCH_Z_CENTER = LENGTH / 2.0
_latch_span = 3.0 * LATCH_KNUCKLE_W + 2.0 * LATCH_KNUCKLE_GAP
_latch_z0 = LATCH_Z_CENTER - _latch_span / 2.0
LATCH_FIXED_SEGMENTS = [
    (_latch_z0, _latch_z0 + LATCH_KNUCKLE_W),
    (
        _latch_z0 + 2.0 * (LATCH_KNUCKLE_W + LATCH_KNUCKLE_GAP),
        _latch_z0 + 2.0 * (LATCH_KNUCKLE_W + LATCH_KNUCKLE_GAP) + LATCH_KNUCKLE_W,
    ),
]
LATCH_LEVER_SEGMENTS = [
    (
        _latch_z0 + (LATCH_KNUCKLE_W + LATCH_KNUCKLE_GAP),
        _latch_z0 + (LATCH_KNUCKLE_W + LATCH_KNUCKLE_GAP) + LATCH_KNUCKLE_W,
    ),
]
_LEVER_Z0, _LEVER_Z1 = LATCH_LEVER_SEGMENTS[0]

LATCH_PIN_MARGIN = 1.0
LATCH_PIN_BORE_Z0 = _latch_z0 - LATCH_PIN_MARGIN - 0.5
LATCH_PIN_BORE_Z1 = _latch_z0 + _latch_span + LATCH_PIN_MARGIN + 0.5

# Catch lip (on front) and hook (on the lever), in the lever's own local Y
# (tangential, away from the split line) and X (radial) directions. Both
# stay at Y >= LATCH_LIP_Y_MIN, safely beyond every knuckle's own +Y reach
# (LATCH_KNUCKLE_R), so neither interacts with the pivot knuckles or their
# clearance cut at all. The lip and the lever's connecting shaft share the
# lever knuckle's own Z-width but occupy different lanes within it (the
# shaft has to pass by the lip's own Z on its way from the pivot to the
# hook); only the hook, at the tip, widens to cover both lanes and reach
# over the lip.
LATCH_LIP_Y_MIN = 4.0
LATCH_LIP_Y_MAX = 7.0
LATCH_LIP_REACH = 3.0  # protrudes this far beyond R_OUT
LATCH_LIP_EMBED = 1.5  # extends inboard into the wall band, past its own curvature, for a genuine fused union
LATCH_LIP_CLEARANCE = 0.4  # gap between the lip and the hook that closes over it
LATCH_HOOK_Y_MAX = LATCH_LIP_Y_MAX + LATCH_LIP_CLEARANCE + 2.5

LATCH_LIP_Z0 = _LEVER_Z0 + 3.0
LATCH_LIP_Z1 = _LEVER_Z1 - 0.5
LATCH_SHAFT_Z0 = _LEVER_Z0 + 0.5
LATCH_SHAFT_Z1 = LATCH_LIP_Z0 - 0.5
LATCH_HOOK_Z0 = LATCH_SHAFT_Z0 - 0.3
LATCH_HOOK_Z1 = LATCH_LIP_Z1 + 0.3

LATCH_SHAFT_X_OUTER = LATCH_AXIS_X - 2.0
LATCH_SHAFT_X_INNER = -(R_OUT + 0.3)  # stays clear of front's plain wall
LATCH_HOOK_X_OUTER = -(R_OUT + LATCH_LIP_REACH + LATCH_LIP_CLEARANCE)

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


# The pin (and its bore) run slightly past the knuckle segments themselves,
# so the pin can be slid in/out without its overhang catching on anything
# right at the ends of the knuckle row.
PIN_BORE_Z0 = HINGE_Z_MIN - PIN_MARGIN - 0.5
PIN_BORE_Z1 = HINGE_Z_MAX + PIN_MARGIN + 0.5

# ---------------------------------------------------------------------------
# Generic knuckle-pivot construction, reusable for any rotating joint on a
# split shell: a hinge, a latch's own pivoting lever, or anything similar in
# another project. Given an edge (a line the two bodies meet along) and a
# normal (perpendicular to the edge, bisecting the angle between the two
# bodies' outer faces there), a pivot axis is placed by translating the edge
# along the normal by the pin bore radius. Knuckle segments built at that
# axis (full-round bosses pierced by a continuous pin bore, not clipped to
# either body's half) get genuine volumetric overlap with whichever body's
# wall they're unioned onto -- no tangent-only fusion tricks needed -- and
# the near-side seam where a knuckle meets that wall can be found exactly
# from the two circles' (knuckle radius at the axis, wall radius at the
# body's own center) intersection, for reinforcement fillets.
# ---------------------------------------------------------------------------


def knuckle_segment(axis_x: float, axis_y: float, knuckle_r: float, pin_r: float,
                     z0: float, z1: float, bore_z0: float, bore_z1: float) -> bd.Shape:
    """One knuckle: a plain full-round boss pierced by a continuous pin
    bore spanning [bore_z0, bore_z1] (wider than [z0, z1] so the bore stays
    open past the ends of a whole interleaved knuckle row)."""
    boss = _z_cylinder(knuckle_r, z1 - z0, axis_x, axis_y, z0)
    bore = _z_cylinder(pin_r, bore_z1 - bore_z0, axis_x, axis_y, bore_z0)
    return boss - bore


def knuckle_row(axis_x: float, axis_y: float, knuckle_r: float, pin_r: float,
                 segments: list[tuple[float, float]], bore_z0: float, bore_z1: float) -> bd.Shape:
    """A row of knuckles at the given axis, one per segment."""
    add = None
    for z0, z1 in segments:
        piece = knuckle_segment(axis_x, axis_y, knuckle_r, pin_r, z0, z1, bore_z0, bore_z1)
        add = piece if add is None else add + piece
    return add


def knuckle_envelope_cut(axis_x: float, axis_y: float, knuckle_r: float,
                          bore_z0: float, bore_z1: float,
                          protect_segments: list[tuple[float, float]] = ()) -> bd.Shape:
    """The knuckle row's full continuous footprint (one cylinder spanning
    the whole bore span, matching the knuckle radius exactly, no segment
    gaps) MINUS `protect_segments`.

    Subtract this from a body's plain wall to clear every knuckle
    location that ISN'T this body's own -- the small gaps between segments
    included, not just the other party's specific segments, which would
    leave those gaps as plain, un-notched wall sticking out right next to
    a cleanly filleted knuckle row.

    `protect_segments` (this body's own, already-unioned-and-filleted
    segments) are excluded from the cut: cutting them too and then
    exactly refilling with knuckle_row() is equivalent in the final shape,
    but leaves OCCT nothing to fillet against at each segment's own Z
    ends. So the real sequence is: union this body's own knuckles onto the
    intact wall, fillet them, THEN subtract this (whole envelope minus
    this body's own segments) -- same final geometry, fillet runs against
    intact material. A body with no segments of its own (nothing to
    protect) just gets the plain full cut.
    """
    full = _z_cylinder(knuckle_r, bore_z1 - bore_z0, axis_x, axis_y, bore_z0)
    if not protect_segments:
        return full
    protect = None
    for z0, z1 in protect_segments:
        piece = _z_cylinder(knuckle_r, z1 - z0, axis_x, axis_y, z0)
        protect = piece if protect is None else protect + piece
    return full - protect


def _seam_intersection(axis_x: float, axis_y: float, knuckle_r: float,
                        wall_r: float, sign: float) -> tuple[float, float]:
    """Where a knuckle circle (radius knuckle_r, centered at (axis_x,
    axis_y)) crosses a wall circle (radius wall_r, centered at the
    origin). `sign` (+1/-1) selects one of the two crossing points, on
    either side of the origin-to-axis line."""
    d = (axis_x**2 + axis_y**2) ** 0.5
    ux, uy = axis_x / d, axis_y / d
    px, py = -uy, ux  # perpendicular to the origin-to-axis direction
    along = (wall_r**2 - knuckle_r**2 + d**2) / (2.0 * d)
    perp = (wall_r**2 - along**2) ** 0.5
    return along * ux + sign * perp * px, along * uy + sign * perp * py


def _select_vertical_seam_edges(body: bd.Shape, x: float, y: float,
                                 segments: list[tuple[float, float]], tol: float = 0.05) -> list:
    """Straight vertical (Z-parallel) edges of `body` at (x, y), one per
    segment's own Z span -- the seam a knuckle-to-wall reinforcement fillet
    targets."""
    target = []
    for z0, z1 in segments:
        for e in body.edges():
            vs = e.vertices()
            if len(vs) != 2:
                continue
            v0, v1 = vs
            zs = sorted((v0.Z, v1.Z))
            if abs(zs[0] - z0) > tol or abs(zs[1] - z1) > tol:
                continue
            if abs(v0.X - x) > tol or abs(v1.X - x) > tol:
                continue
            if abs(v0.Y - y) > tol or abs(v1.Y - y) > tol:
                continue
            target.append(e)
    return target


def reinforce_seam(body: bd.Shape, axis_x: float, axis_y: float, knuckle_r: float,
                    wall_r: float, sign: float, segments: list[tuple[float, float]],
                    fillet_r: float) -> bd.Shape:
    """Fillet the seam where each of this body's own knuckle bosses (at
    `segments`) meets the body's own outer wall face (radius wall_r,
    centered at the origin) -- the near side only, found via the two
    circles' intersection. Run after the knuckles are unioned on: a fillet
    needs a real edge on the combined solid, not two separate shapes.
    """
    x, y = _seam_intersection(axis_x, axis_y, knuckle_r, wall_r, sign)
    target = _select_vertical_seam_edges(body, x, y, segments)
    if not target:
        raise ValueError("reinforce_seam: no seam edges found to fillet")
    return bd.fillet(target, fillet_r)


# Hinge (edge at X=+R_OUT): the tube's own parting line at the OD, normal =
# outward radial direction (the OD is smooth/tangent-continuous across the
# parting line, so the two outer faces' bisector there is just radial).
HINGE_EDGE_X = R_OUT
HINGE_EDGE_Y = 0.0
HINGE_NORMAL_X = 1.0
HINGE_NORMAL_Y = 0.0
HINGE_AXIS_X = HINGE_EDGE_X + HINGE_NORMAL_X * PIN_R
HINGE_AXIS_Y = HINGE_EDGE_Y + HINGE_NORMAL_Y * PIN_R
HINGE_FILLET_R = 1.5


def hinge_knuckles(segments: list[tuple[float, float]]) -> bd.Shape:
    """Segments alternate between the two leaves by construction
    (BACK_KNUCKLE_SEGMENTS / FRONT_KNUCKLE_SEGMENTS), so calling this with
    one leaf's own segment list gives that leaf's knuckle row."""
    return knuckle_row(HINGE_AXIS_X, HINGE_AXIS_Y, KNUCKLE_R, PIN_R, segments, PIN_BORE_Z0, PIN_BORE_Z1)


def hinge_envelope_cut(own_segments: list[tuple[float, float]]) -> bd.Shape:
    return knuckle_envelope_cut(HINGE_AXIS_X, HINGE_AXIS_Y, KNUCKLE_R, PIN_BORE_Z0, PIN_BORE_Z1, own_segments)


def reinforce_hinge(body: bd.Shape, front: bool, segments: list[tuple[float, float]]) -> bd.Shape:
    """Only the near side (where the knuckle actually meets this leaf's
    own wall) gets filleted; the far side has no wall of this leaf's own
    to blend into (that's the other leaf's clearance pocket instead), so
    no matching edge exists there to select in the first place."""
    sign = 1.0 if front else -1.0
    return reinforce_seam(body, HINGE_AXIS_X, HINGE_AXIS_Y, KNUCKLE_R, R_OUT, sign, segments, HINGE_FILLET_R)


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


def latch_pivot_fixed() -> bd.Shape:
    """Back's fixed half of the latch pivot: full-round knuckle bosses
    (LATCH_FIXED_SEGMENTS) pierced by the latch pin bore -- the same
    knuckle_row() the hinge itself uses, just at the latch's own axis and
    a smaller radius."""
    return knuckle_row(LATCH_AXIS_X, LATCH_AXIS_Y, LATCH_KNUCKLE_R, LATCH_PIN_R,
                        LATCH_FIXED_SEGMENTS, LATCH_PIN_BORE_Z0, LATCH_PIN_BORE_Z1)


def latch_pivot_envelope_cut(protect_segments: list[tuple[float, float]] = ()) -> bd.Shape:
    """Clears the latch pivot's full footprint from a body, minus
    `protect_segments` (that body's own, already-fused knuckles, if any).
    Back passes its own LATCH_FIXED_SEGMENTS to protect them; front owns
    nothing at the pivot, so it passes nothing and gets the full cut."""
    return knuckle_envelope_cut(LATCH_AXIS_X, LATCH_AXIS_Y, LATCH_KNUCKLE_R,
                                 LATCH_PIN_BORE_Z0, LATCH_PIN_BORE_Z1, protect_segments)


def reinforce_latch_pivot(body: bd.Shape) -> bd.Shape:
    """Fillet the seam where back's fixed pivot knuckles meet back's own
    outer wall face -- same technique as reinforce_hinge(). Back occupies
    Y<=0, so sign=+1 here picks the negative-Y (back's own) crossing point,
    same convention as reinforce_hinge(front=False)."""
    return reinforce_seam(body, LATCH_AXIS_X, LATCH_AXIS_Y, LATCH_KNUCKLE_R, R_OUT, 1.0,
                           LATCH_FIXED_SEGMENTS, LATCH_FILLET_R)


def latch_lever_arm() -> bd.Shape:
    """The lever's own hook and connecting shaft (its pivot knuckle comes
    from knuckle_row() separately, in latch_lever.py). Both stay entirely
    at Y >= LATCH_KNUCKLE_R -- clear of the pivot knuckles and their
    envelope cut -- and at X beyond R_OUT, clear of front's plain wall.

    The shaft runs from the knuckle to the hook down a Z lane that avoids
    front's catch lip (latch_catch_lip()); the hook then widens in Z to
    reach over the lip from the outside, blocking it (and so the whole
    front leaf) from swinging open -- the same physical principle as the
    old hook-and-window catch, just via a separate rigid, pivoting part
    instead of an integral flexing one.
    """
    shaft = bd.Box(
        LATCH_SHAFT_X_INNER - LATCH_SHAFT_X_OUTER, LATCH_HOOK_Y_MAX, LATCH_SHAFT_Z1 - LATCH_SHAFT_Z0,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    )
    shaft = bd.Pos(LATCH_SHAFT_X_OUTER, 0.0, LATCH_SHAFT_Z0) * shaft

    hook_y0 = LATCH_LIP_Y_MAX + LATCH_LIP_CLEARANCE
    hook = bd.Box(
        LATCH_SHAFT_X_INNER - LATCH_HOOK_X_OUTER, LATCH_HOOK_Y_MAX - hook_y0, LATCH_HOOK_Z1 - LATCH_HOOK_Z0,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    )
    hook = bd.Pos(LATCH_HOOK_X_OUTER, hook_y0, LATCH_HOOK_Z0) * hook

    return shaft + hook


def latch_catch_lip() -> bd.Shape:
    """Front's static catch: a lip protruding LATCH_LIP_REACH beyond
    R_OUT, embedded LATCH_LIP_EMBED inboard of R_OUT to guarantee a
    genuine fused union with front's own curved wall (the wall's actual
    surface bows inward across the lip's Y-span, so a flat-faced lip needs
    real embed depth, not just nominal contact at Y=0). Sits entirely
    beyond the pivot knuckles' own Y-reach -- see latch_lever_arm().
    """
    x0 = -(R_OUT + LATCH_LIP_REACH)
    x1 = -R_OUT + LATCH_LIP_EMBED
    lip = bd.Box(
        x1 - x0, LATCH_LIP_Y_MAX - LATCH_LIP_Y_MIN, LATCH_LIP_Z1 - LATCH_LIP_Z0,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    )
    return bd.Pos(x0, LATCH_LIP_Y_MIN, LATCH_LIP_Z0) * lip


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
    """A hollow quarter-dome end cap for one leaf at one end of the tube.

    Radii match R_OUT/R_IN, so the two leaves' quarter-domes meet flush
    with each other AND with the main shell's own wall thickness -- once
    closed, the two Z-ends of the assembly each read as a true hollow
    hemisphere continuing the same WALL-thick shell as the cylindrical
    mid-section, not a solid plug.
    """
    z_end = 0.0 if at_bottom else LENGTH
    pad = R_OUT + 10.0

    shell = bd.Pos(0.0, 0.0, z_end) * (bd.Sphere(R_OUT) - bd.Sphere(R_IN))

    y_align = bd.Align.MIN if front else bd.Align.MAX
    y_box = bd.Pos(0.0, 0.0, z_end) * bd.Box(
        2.0 * pad, pad, 2.0 * pad, align=(bd.Align.CENTER, y_align, bd.Align.CENTER)
    )

    z_align = bd.Align.MAX if at_bottom else bd.Align.MIN
    z_box = bd.Pos(0.0, 0.0, z_end) * bd.Box(
        2.0 * pad, 2.0 * pad, pad, align=(bd.Align.CENTER, bd.Align.CENTER, z_align)
    )

    return shell & y_box & z_box
