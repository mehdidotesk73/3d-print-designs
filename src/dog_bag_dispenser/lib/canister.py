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

# Closing latch (edge at X=-R_OUT): a screw self-taps into a threaded
# SCREW FASTENING HOLE in front's TAB, then tightens until its smooth tip
# advances into a plain, oversized clearance BORE straight through back's
# own wall -- not threaded, not fastened there at all, just resting with
# clearance. This alone resists the hinge opening: the screw is rigid with
# front (fixed via the fastening thread), and its tip sits inside a
# snug-clearance hole in back, so the pair act like a dowel pin spanning
# the joint. As front tries to rotate open about the main hinge, the latch
# edge moves mostly TANGENTIALLY (not straight outward) -- and that's
# exactly the motion the bore blocks: the tip immediately meets the bore's
# own side wall rather than being free to slide.
#
# An earlier version of this raised a solid ridge on back for the screw
# tip to press into -- but back's own wall (whatever its thickness)
# already provides the depth to register the tip, so the ridge did the
# identical restraint job with extra material and extra geometry, for no
# extra strength. Dropped entirely; the bore just goes straight into the
# plain wall.
LATCH_Z_CENTER = LENGTH / 2.0
LATCH_WIDTH = 14.0  # Z extent of the whole tab/screw assembly

# The screw itself: real, printable, coarse (2mm pitch) helical threads --
# fine V-threads don't print reliably at this scale. A separate part
# (closing_screw.py).
SCREW_MAJOR_D = 5.0
SCREW_PITCH = 2.0
SCREW_THREAD_DEPTH = 0.7
SCREW_THREAD_CREST_W = 0.5  # trapezoidal profile: width of the thread's flat crest, not a knife edge --
# FDM can't reliably resolve a true point at this depth (it just rounds over anyway), and a flat crest
# isn't a stress-concentration point right where the thread takes load while self-tapping in
SCREW_MINOR_D = SCREW_MAJOR_D - 2.0 * SCREW_THREAD_DEPTH
SCREW_HEAD_D = 9.0
SCREW_HEAD_H = 3.0
SCREW_TIP_D = 3.2  # smooth pilot below the threads -- registers in back's clearance bore
SCREW_TIP_ENGAGE = 2.5  # how deep the tip seats into back's bore -- short of WALL, so it
# stays clear of poking out into the cavity

# The tab (front): a thin arm reaching to rest against back's own outer
# wall, widening into a root that embeds into front's own wall where it
# meets it.
TAB_THK = 5.0  # radial thickness -- matches the screw's threaded length
FASTENING_HOLE_D = SCREW_MINOR_D - 0.2  # slightly undersized: the screw self-taps on first insertion,
# the common, reliable approach for a small FDM-printed fastener -- far more robust than modeling a
# matching internal helical thread and hoping the two meshes clear each other at print tolerance.
TAB_EMBED = 2.5  # the root's embed depth past R_OUT into front's own wall, past its own curvature
TAB_Y_DEPTH = 8.0  # how far the tab's own arm reaches from the split line
LATCH_GAP = 1.0  # clearance between the tab's inner face and back's own outer wall -- also gives
# the screw's own helical thread room for its natural start-of-sweep overshoot (a real, if tiny,
# effect of the swept thread profile) to clear back's wall around the bore's own opening

# Back's own wall: a plain, unthreaded, oversized clearance bore straight
# through it (from its outer face into the cavity) -- large enough that
# the screw's smooth tip can never bind or thread into it. Oversized in
# length (not just diameter) so it fully pierces the wall regardless of
# the wall's own curvature this close to the split line.
BACK_BORE_D = SCREW_TIP_D + 0.4  # clearance around the screw's smooth tip
BACK_BORE_X0 = -(R_OUT + 1.0)
BACK_BORE_DEPTH = WALL + 2.0

TAB_INNER_X = -R_OUT - LATCH_GAP
TAB_OUTER_X = TAB_INNER_X - TAB_THK
TAB_ROOT_INNER_X = -(R_OUT - TAB_EMBED)

LATCH_HOLE_Y = -TAB_Y_DEPTH / 2.0  # centered within the tab's own Y span
LATCH_HOLE_Z = LATCH_Z_CENTER

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


def _x_cylinder(radius: float, length: float, y: float, z: float, x0: float) -> bd.Shape:
    """A cylinder whose axis runs along X (radially), base at x0, extending
    toward +X (inboard, toward the tube's center)."""
    cyl = bd.Cylinder(
        radius, length,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        rotation=(0.0, 90.0, 0.0),
    )
    return bd.Pos(x0, y, z) * cyl


def latch_tab() -> bd.Shape:
    """Front's tab: a thin arm reaching to rest against back's own outer
    wall (clear of it by LATCH_GAP), plus a root that embeds into front's
    own wall where the arm meets it (Y >= 0) -- an L-shape in
    cross-section. The root's own X reach is a superset of the arm's; the
    overlap between them is harmless (just redundant material from the
    union), so one box each keeps this simple rather than trimming them
    to be disjoint.
    """
    arm = bd.Box(
        TAB_INNER_X - TAB_OUTER_X, TAB_Y_DEPTH + TAB_EMBED, LATCH_WIDTH,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.CENTER),
    )
    arm = bd.Pos(TAB_OUTER_X, -TAB_Y_DEPTH, LATCH_HOLE_Z) * arm

    root = bd.Box(
        TAB_ROOT_INNER_X - TAB_OUTER_X, TAB_EMBED, LATCH_WIDTH,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.CENTER),
    )
    root = bd.Pos(TAB_OUTER_X, 0.0, LATCH_HOLE_Z) * root

    return arm + root


def latch_tab_fastening_hole() -> bd.Shape:
    """The tab's own threaded screw fastening hole -- see FASTENING_HOLE_D."""
    return _x_cylinder(FASTENING_HOLE_D / 2.0, TAB_INNER_X - TAB_OUTER_X,
                        LATCH_HOLE_Y, LATCH_HOLE_Z, TAB_OUTER_X)


def latch_back_bore() -> bd.Shape:
    """The plain, unthreaded clearance bore through back's own wall that
    the screw's smooth tip advances into once tightened -- not fastened
    there at all, just resting with clearance. This is what actually
    resists the hinge opening: the screw is rigid with front (fixed via
    the tab's fastening thread), and its tip sits inside this
    snug-clearance hole in back, so the pair act like a dowel pin spanning
    the joint -- front's latch edge moves mostly tangentially as it tries
    to swing open, and that's exactly the motion this bore blocks.
    """
    return _x_cylinder(BACK_BORE_D / 2.0, BACK_BORE_DEPTH, LATCH_HOLE_Y, LATCH_HOLE_Z, BACK_BORE_X0)


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
