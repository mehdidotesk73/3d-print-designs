from cadgen import build123d as bd
from cadgen import step

from lib.canister import (
    LATCH_GAP,
    SCREW_HEAD_D,
    SCREW_HEAD_H,
    SCREW_MAJOR_D,
    SCREW_MINOR_D,
    SCREW_PITCH,
    SCREW_THREAD_CREST_W,
    SCREW_TIP_D,
    SCREW_TIP_ENGAGE,
    TAB_THK,
)

# Local frame: Z=0 is the tip's own end (the deepest point once seated in
# back's clearance bore), increasing toward the head. Placed in the
# assembly by rotating -90 about Y (mapping local +Z to world -X) and
# translating so the tip lands at its seated depth -- see
# dispenser_assembly.py.
TIP_LEN = LATCH_GAP + SCREW_TIP_ENGAGE
THREAD_LEN = TAB_THK
SCREW_LENGTH = TIP_LEN + THREAD_LEN + SCREW_HEAD_H


def _threaded_shank(z0: float, length: float) -> bd.Shape:
    """A cylinder at the thread's minor (root) diameter, with a real
    helical rib swept onto it at the major diameter -- coarse (2mm pitch,
    trapezoidal profile with a flat crest, not a knife edge), matching
    what prints reliably at this scale rather than a fine, accurate
    V-thread.
    """
    core_r = SCREW_MINOR_D / 2.0
    crest_r = SCREW_MAJOR_D / 2.0
    core = bd.Cylinder(core_r, length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))

    helix = bd.Helix(pitch=SCREW_PITCH, height=length, radius=core_r)
    with bd.BuildSketch(bd.Plane.XZ) as prof:
        with bd.BuildLine():
            p0 = (core_r, -SCREW_PITCH / 4.0)
            p1 = (crest_r, -SCREW_THREAD_CREST_W / 2.0)
            p2 = (crest_r, SCREW_THREAD_CREST_W / 2.0)
            p3 = (core_r, SCREW_PITCH / 4.0)
            bd.Polyline(p0, p1, p2, p3, p0)
        bd.make_face()
    rib = bd.sweep(prof.sketch, path=helix, is_frenet=False)

    shank = core + rib
    return bd.Pos(0.0, 0.0, z0) * shank


@step(out="../../STEP/dog_bag_dispenser/closing_screw.step")
def closing_screw():
    tip = bd.Cylinder(SCREW_TIP_D / 2.0, TIP_LEN, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))

    thread = _threaded_shank(TIP_LEN, THREAD_LEN)

    head = bd.Cylinder(
        SCREW_HEAD_D / 2.0, SCREW_HEAD_H,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    head = bd.Pos(0.0, 0.0, TIP_LEN + THREAD_LEN) * head

    body = tip + thread + head
    body.label = "closing_screw"
    return body


if __name__ == "__main__":
    closing_screw()
