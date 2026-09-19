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

# Generic hinge placement: given an edge (a line the two bodies meet along)
# and a hinge normal (perpendicular to the edge, bisecting the angle
# between the two bodies' outer faces at that edge), the knuckle axis is
# the edge translated along the normal by the pin bore radius. Here the
# edge is the tube's own parting line at the OD (X=R_OUT, Y=0, running the
# full length in Z) and the normal is the outward radial direction at that
# point (the tube's own OD is smooth/tangent-continuous across the parting
# line, so the two outer faces' bisector is just the radial direction).
HINGE_EDGE_X = R_OUT
HINGE_EDGE_Y = 0.0
HINGE_NORMAL_X = 1.0
HINGE_NORMAL_Y = 0.0
HINGE_AXIS_X = HINGE_EDGE_X + HINGE_NORMAL_X * PIN_R
HINGE_AXIS_Y = HINGE_EDGE_Y + HINGE_NORMAL_Y * PIN_R
HINGE_FILLET_R = 1.5

# Where the knuckle's own KNUCKLE_R circle crosses the tube's own R_OUT
# circle in cross-section -- this is the seam edge that hinge reinforcement
# fillets on each leaf's own (near) side. Extruded along Z, each crossing
# point becomes a straight vertical edge per knuckle segment.
_HINGE_D = ((HINGE_AXIS_X - 0.0) ** 2 + (HINGE_AXIS_Y - 0.0) ** 2) ** 0.5
_HINGE_IX = (R_OUT**2 - KNUCKLE_R**2 + _HINGE_D**2) / (2.0 * _HINGE_D)
_HINGE_IY = (R_OUT**2 - _HINGE_IX**2) ** 0.5

def _knuckle_segment(z0: float, z1: float) -> bd.Shape:
    """One knuckle: a plain full-round boss (a slice of the hinge's bulk
    cylinder) pierced by the continuous pin bore. Not clipped to either
    leaf's half -- it's a real hinge barrel, round all the way around, like
    a piano hinge's knuckle. Its axis sits inside the tube's own wall band
    (KNUCKLE_R is bigger than the axis's offset past the OD), so it always
    has genuine volumetric overlap with whichever leaf's wall it's unioned
    onto -- no tangent-only tricks needed to fuse them.
    """
    boss = _z_cylinder(KNUCKLE_R, z1 - z0, HINGE_AXIS_X, HINGE_AXIS_Y, z0)
    bore = _z_cylinder(PIN_R, PIN_BORE_Z1 - PIN_BORE_Z0, HINGE_AXIS_X, HINGE_AXIS_Y, PIN_BORE_Z0)
    return boss - bore


def hinge_knuckles(segments: list[tuple[float, float]]) -> bd.Shape:
    """The hinge bulk cylinder, sliced into knuckles (one per segment,
    already pushed apart by the segment packer's gaps) and pierced by the
    pin bore. Segments alternate between the two leaves by construction
    (BACK_KNUCKLE_SEGMENTS / FRONT_KNUCKLE_SEGMENTS), so calling this with
    one leaf's own segment list gives that leaf's knuckle row.
    """
    add = None
    for z0, z1 in segments:
        piece = _knuckle_segment(z0, z1)
        add = piece if add is None else add + piece
    return add


def hinge_envelope_cut(own_segments: list[tuple[float, float]]) -> bd.Shape:
    """The hinge's full continuous footprint (a single cylinder at the
    hinge axis, matching the knuckle boss's own radius exactly, spanning
    the whole pin bore span with no segment gaps and no per-leg split)
    MINUS this leaf's own segments.

    Subtracting the whole continuous envelope -- not just the other leaf's
    specific segments, the previous approach -- is what actually clears
    the small gaps between segments: cutting only the other leaf's
    footprint left those gaps as plain, un-notched wall sticking out right
    next to the knuckle row, a visible leftover once the knuckles
    themselves were cleanly filleted.

    This leaf's own segments are excluded from the cut (not cut-then-
    exactly-refilled by hinge_knuckles(), which is equivalent in the final
    shape but leaves OCCT nothing to fillet against at each segment's Z
    ends -- the wall face reinforce_hinge() blends into would already be
    cut away right at that boundary). So the actual sequence is: add this
    leaf's own knuckles onto the still-intact wall, fillet them, THEN
    subtract this (whole envelope minus this leaf's own segments) to clear
    everywhere else -- same final geometry, but the fillet runs against
    intact material.
    """
    full = _z_cylinder(KNUCKLE_R, PIN_BORE_Z1 - PIN_BORE_Z0, HINGE_AXIS_X, HINGE_AXIS_Y, PIN_BORE_Z0)
    protect = None
    for z0, z1 in own_segments:
        piece = _z_cylinder(KNUCKLE_R, z1 - z0, HINGE_AXIS_X, HINGE_AXIS_Y, z0)
        protect = piece if protect is None else protect + piece
    return full - protect


def reinforce_hinge(body: bd.Shape, front: bool, segments: list[tuple[float, float]]) -> bd.Shape:
    """Hinge reinforcement: fillet the seam edge where each of THIS leaf's
    own knuckle bosses meets the leaf's own outer wall face. Runs after the
    knuckles are unioned on and the other leaf's clearance is cut, since a
    fillet needs a real edge on the combined solid to work with -- there's
    nothing to fillet between two separate, not-yet-unioned shapes.

    Only the near side (where the knuckle actually meets this leaf's own
    wall) gets filleted; the far side has no wall of this leaf's own to
    blend into (that's the other leaf's clearance pocket instead), so no
    matching edge exists there to select in the first place.
    """
    own_iy = _HINGE_IY if front else -_HINGE_IY
    tol = 0.05
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
            if abs(v0.X - _HINGE_IX) > tol or abs(v1.X - _HINGE_IX) > tol:
                continue
            if abs(v0.Y - own_iy) > tol or abs(v1.Y - own_iy) > tol:
                continue
            target.append(e)
    if not target:
        raise ValueError("reinforce_hinge: no seam edges found to fillet")
    return bd.fillet(target, HINGE_FILLET_R)


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
