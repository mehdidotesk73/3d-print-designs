from cadgen import build123d as bd
from cadgen import step

from lib.canister import (
    LATCH_GAP,
    SCREW_HEAD_D,
    SCREW_HEAD_GAP,
    SCREW_HEAD_H,
    SCREW_MAJOR_D,
    SCREW_MINOR_D,
    SCREW_THREAD_CREST_W,
    SCREW_TIP_D,
    SCREW_TIP_ENGAGE,
    TAB_THK,
    threaded_shank,
)

# Local frame: Z=0 is the tip's own end (the deepest point once seated in
# back's clearance bore), increasing toward the head. Placed in the
# assembly by rotating -90 about Y (mapping local +Z to world -X) and
# translating so the tip lands at its seated depth -- see
# dispenser_assembly.py.
TIP_LEN = LATCH_GAP + SCREW_TIP_ENGAGE
THREAD_LEN = TAB_THK
SCREW_LENGTH = TIP_LEN + THREAD_LEN + SCREW_HEAD_GAP + SCREW_HEAD_H


@step(out="../../STEP/dog_bag_dispenser/closing_screw.step")
def closing_screw():
    tip = bd.Cylinder(SCREW_TIP_D / 2.0, TIP_LEN, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))

    thread = bd.Pos(0.0, 0.0, TIP_LEN) * threaded_shank(
        SCREW_MINOR_D / 2.0, SCREW_MAJOR_D / 2.0, SCREW_THREAD_CREST_W, THREAD_LEN
    )

    head = bd.Cylinder(
        SCREW_HEAD_D / 2.0, SCREW_HEAD_H,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    head = bd.Pos(0.0, 0.0, TIP_LEN + THREAD_LEN + SCREW_HEAD_GAP) * head

    body = tip + thread + head
    body.label = "closing_screw"
    return body


if __name__ == "__main__":
    closing_screw()
