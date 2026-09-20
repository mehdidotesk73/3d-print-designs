from cadgen import build123d as bd
from cadgen import step

from lib.canister import (
    FRONT_KNUCKLE_SEGMENTS,
    dispense_slot,
    dome_cap,
    half_shell,
    hinge_envelope_cut,
    hinge_knuckles,
    latch_tab,
    latch_tab_fastening_hole,
    reinforce_hinge,
)


@step(out="../STEP/canister_front.step")
def canister_front():
    body = half_shell(front=True)

    body = body + hinge_knuckles(FRONT_KNUCKLE_SEGMENTS)
    body = reinforce_hinge(body, front=True, segments=FRONT_KNUCKLE_SEGMENTS)
    body = body - hinge_envelope_cut(own_segments=FRONT_KNUCKLE_SEGMENTS)

    body = body + latch_tab() - latch_tab_fastening_hole()

    body = body - dispense_slot()

    body = body + dome_cap(front=True, at_bottom=True) + dome_cap(front=True, at_bottom=False)

    body.label = "canister_front"
    return body


if __name__ == "__main__":
    canister_front()
