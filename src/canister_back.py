from cadgen import build123d as bd
from cadgen import step

from lib.canister import (
    BACK_KNUCKLE_SEGMENTS,
    dome_cap,
    half_shell,
    hinge_envelope_cut,
    hinge_knuckles,
    latch_back_bore,
    mount_features,
    reinforce_hinge,
)


@step(out="../STEP/canister_back.step")
def canister_back():
    body = half_shell(front=False)

    body = body + hinge_knuckles(BACK_KNUCKLE_SEGMENTS)
    body = reinforce_hinge(body, front=False, segments=BACK_KNUCKLE_SEGMENTS)
    body = body - hinge_envelope_cut(own_segments=BACK_KNUCKLE_SEGMENTS)

    body = body - latch_back_bore()

    mount_add, mount_cut = mount_features()
    body = body + mount_add - mount_cut

    body = body + dome_cap(front=False, at_bottom=True) + dome_cap(front=False, at_bottom=False)

    body.label = "canister_back"
    return body


if __name__ == "__main__":
    canister_back()
