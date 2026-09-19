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

# Latch (edge at X=-R_OUT): a hook on the front catches through a window in
# the back. Front's arm flexes in Y (its thin dimension); back's window is
# a plain cut, not a separate flexing feature -- a single flex point is the
# most durable arrangement for a hook that self-engages during the closing
# swing (see latch_hooks() for why a fully rigid catch can't self-release
# from pure rotation about a fixed pivot).
LATCH_Z = (END_MARGIN + _mount_usable * 0.25, END_MARGIN + _mount_usable * 0.75)
HOOK_WIDTH = 12.0
HOOK_ARM_THK = 2.5  # was TAB_THK=1.8 on the old cantilever -- thicker, sturdier arm
HOOK_REACH = 6.0  # protrusion past the OD edge
HOOK_CATCH_LEN = 4.0  # catch's inward hook length past the arm's own tip
HOOK_CATCH_DROP = 3.5  # catch drops this far past the arm's bottom face -- asymmetric, one-sided
HOOK_EMBED = 2.0  # extends the arm's base into the wall so it truly fuses, not just touches at an edge
WINDOW_Z_MARGIN = 0.5  # window is 1mm wider than the hook
WINDOW_Y_HIGH = HOOK_ARM_THK / 2.0 + 0.5  # clearance -- the arm just passes through here
WINDOW_Y_LOW = -(HOOK_ARM_THK / 2.0 + HOOK_CATCH_DROP) + 0.3  # slight interference for snap retention

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

# Hinge axis placement: NOT centered on the parting edge. A centered pin
# bore is half-embedded in each leaf's own wall thickness, which (a) has no
# opening to the outside once the dome caps exist -- the bore is a fully
# enclosed channel with nowhere to slide the pin in from -- and (b) makes
# each leaf's own body sweep back through the pin's own territory as it
# swings, limiting rotation range. Placing the axis externally, tangent to
# the tube's OD, fixes both: the knuckle bumps sit outside the tube's own
# wall material entirely (nothing to embed the pin bore in beyond the
# knuckle row itself, so it opens to free air at both ends of the row), and
# neither leaf's main body ever sweeps back across the tangent point during
# rotation. HINGE_OVERLAP is a small deliberate overlap (not exact
# mathematical tangency, which produces a degenerate/self-touching profile
# that OCCT can't fillet) so the knuckle boss has a genuine face to fuse
# and fillet against, not just a tangent line.
HINGE_OVERLAP = 1.0
HINGE_AXIS_X = R_OUT + KNUCKLE_R - HINGE_OVERLAP
HINGE_FILLET_R = 1.5
KNUCKLE_CLEARANCE_R = KNUCKLE_R + 0.3  # cut into the OTHER leaf, see hinge_clearance()

_HINGE_IX = (R_OUT**2 - KNUCKLE_R**2 + HINGE_AXIS_X**2) / (2.0 * HINGE_AXIS_X)
_HINGE_IY = (R_OUT**2 - _HINGE_IX**2) ** 0.5


def _knuckle_profile(front: bool) -> bd.Shape:
    """2D cross-section for one leaf's knuckle: THIS leaf's own annulus
    half (matching wall thickness and half-plane elsewhere -- same clip
    half_shell() uses) unioned with a FULL ROUND knuckle-diameter circle
    placed tangent to (with a small robust overlap into) the tube's OD.
    Only the annulus is clipped to this leaf's half; the knuckle bump
    itself stays a complete circle, like a real hinge barrel, not sliced
    in half at the parting plane.

    The overlap between the knuckle circle and R_OUT is filleted on THIS
    leaf's own side (where the clipped annulus actually meets the
    knuckle) so the transition is smooth, not a sharp reentrant corner.
    The knuckle's other side pokes past Y=0 into the other leaf's
    territory unfilleted (there's no annulus material of this leaf's own
    there for it to blend into) -- hinge_clearance() removes the resulting
    small overlap from the other leaf rather than slicing the knuckle.
    """
    pad = R_OUT + 10.0
    align_y = bd.Align.MIN if front else bd.Align.MAX
    rect = bd.Rectangle(2.0 * pad, pad, align=(bd.Align.CENTER, align_y))
    own_annulus = (bd.Circle(R_OUT) - bd.Circle(R_IN)) & rect

    knuckle = bd.Pos(HINGE_AXIS_X, 0.0) * bd.Circle(KNUCKLE_R)
    combined = own_annulus + knuckle

    own_iy = _HINGE_IY if front else -_HINGE_IY

    def _near(v, x: float, y: float, tol: float = 0.05) -> bool:
        return abs(v.X - x) < tol and abs(v.Y - y) < tol

    fillet_verts = [v for v in combined.vertices() if _near(v, _HINGE_IX, own_iy)]
    return bd.fillet(fillet_verts, HINGE_FILLET_R)


def hinge_knuckles(front: bool, segments: list[tuple[float, float]]) -> bd.Shape:
    """One leaf's knuckle bosses: its half of the alternating segment list,
    each a full-round extrusion of that leaf's own knuckle profile, plus a
    single continuous pin bore run through the whole hinge span (open at
    both ends past the knuckle row, so the pin can be slid straight in
    after the two leaves are brought together -- see HINGE_AXIS_X above).
    """
    profile = _knuckle_profile(front)
    add = None
    for z0, z1 in segments:
        piece = bd.extrude(profile, amount=z1 - z0)
        piece = bd.Pos(0.0, 0.0, z0) * piece
        add = piece if add is None else add + piece

    bore = _z_cylinder(PIN_R, PIN_BORE_Z1 - PIN_BORE_Z0, HINGE_AXIS_X, 0.0, PIN_BORE_Z0)
    return add - bore


def hinge_clearance(other_segments: list[tuple[float, float]]) -> bd.Shape:
    """Cut into THIS leaf at the OTHER leaf's knuckle Z-segments, clearing
    room for that leaf's full-round knuckle boss (whose fillet dips
    slightly past R_OUT on both sides of the hinge plane, not just its own
    leaf's side -- see _knuckle_profile). A plain oversized cylinder, not
    the fancy filleted profile: it only needs to clear, not look good.
    """
    cut = None
    for z0, z1 in other_segments:
        piece = _z_cylinder(KNUCKLE_CLEARANCE_R, z1 - z0, HINGE_AXIS_X, 0.0, z0)
        cut = piece if cut is None else cut + piece
    return cut


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


def _hook(z_center: float) -> bd.Shape:
    """One hook: a cantilever arm (flexes in Y, its thin dimension) with an
    asymmetric catch dropping further -Y at the tip. Box axes: X = radial
    reach, Y = flex/catch direction, Z = axial width.

    A single rigid hook can't self-release from a fixed-pivot rotation:
    trace the latch edge's own arc as the leaf swings and the same path is
    retraced in reverse to open, so a catch that blocks it one way blocks
    it both ways unless something flexes momentarily. Putting that flex in
    one sturdy, short cantilever arm (not the old thin blade) is the
    durable version of that same necessity -- a true zero-flex hook would
    need a second degree of freedom (axial slide, a separate release
    action) rather than pure swing-to-close.
    """
    x_outer = -R_OUT
    blade_x_max = x_outer + HOOK_EMBED
    arm = bd.Box(
        HOOK_REACH + HOOK_EMBED, HOOK_ARM_THK, HOOK_WIDTH,
        align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER),
    )
    arm = bd.Pos(blade_x_max, 0.0, z_center) * arm

    catch_thk = HOOK_ARM_THK + HOOK_CATCH_DROP
    catch = bd.Box(
        HOOK_CATCH_LEN, catch_thk, HOOK_WIDTH,
        align=(bd.Align.MAX, bd.Align.MAX, bd.Align.CENTER),
    )
    catch = bd.Pos(x_outer - HOOK_REACH + HOOK_CATCH_LEN, HOOK_ARM_THK / 2.0, z_center) * catch

    return arm + catch


def latch_hooks() -> bd.Shape:
    """Front leaf: cantilever hooks at the latch edge."""
    add = None
    for z in LATCH_Z:
        piece = _hook(z)
        add = piece if add is None else add + piece
    return add


def latch_windows() -> bd.Shape:
    """Back leaf: cut receiving windows at the latch edge for the front
    hooks. Clears the FULL radial wall thickness (plus margin) at each
    latch position, so no leftover back material can collide with the
    front hook's embed depth regardless of exact hook geometry.
    """
    x_min = -(R_OUT + 2.0)
    x_max = -(R_IN - 2.0)
    width_x = x_max - x_min
    cut = None
    for z in LATCH_Z:
        window = bd.Box(
            width_x,
            WINDOW_Y_HIGH - WINDOW_Y_LOW,
            HOOK_WIDTH + 2.0 * WINDOW_Z_MARGIN,
            align=(bd.Align.MIN, bd.Align.MIN, bd.Align.CENTER),
        )
        window = bd.Pos(x_min, WINDOW_Y_LOW, z) * window
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
