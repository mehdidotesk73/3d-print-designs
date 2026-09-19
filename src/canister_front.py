from cadgen import build123d as bd
from cadgen import step

from lib.canister import (
    BACK_KNUCKLE_SEGMENTS,
    FRONT_KNUCKLE_SEGMENTS,
    dispense_slot,
    dome_cap,
    half_shell,
    hinge_features,
    latch_tabs,
)


@step(out="../STEP/canister_front.step")
def canister_front():
    body = half_shell(front=True)

    knuckles_add, knuckles_cut = hinge_features(FRONT_KNUCKLE_SEGMENTS, BACK_KNUCKLE_SEGMENTS)
    body = body + knuckles_add - knuckles_cut

    body = body + latch_tabs()

    body = body - dispense_slot()

    body = body + dome_cap(front=True, at_bottom=True) + dome_cap(front=True, at_bottom=False)

    body.label = "canister_front"
    return body


if __name__ == "__main__":
    canister_front()
