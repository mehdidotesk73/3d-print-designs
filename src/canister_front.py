from cadgen import build123d as bd
from cadgen import step

from lib.canister import (
    FRONT_KNUCKLE_SEGMENTS,
    dispense_slot,
    dome_cap,
    half_shell,
    hinge_knuckles,
    latch_hooks,
)


@step(out="../STEP/canister_front.step")
def canister_front():
    body = half_shell(front=True)

    body = body + hinge_knuckles(front=True, segments=FRONT_KNUCKLE_SEGMENTS)

    body = body + latch_hooks()

    body = body - dispense_slot()

    body = body + dome_cap(front=True, at_bottom=True) + dome_cap(front=True, at_bottom=False)

    body.label = "canister_front"
    return body


if __name__ == "__main__":
    canister_front()
