from cadgen import build123d as bd
from cadgen import step

from lib.canister import (
    BACK_KNUCKLE_SEGMENTS,
    dome_cap,
    half_shell,
    hinge_knuckles,
    latch_windows,
    mount_features,
)


@step(out="../STEP/canister_back.step")
def canister_back():
    body = half_shell(front=False)

    body = body + hinge_knuckles(front=False, segments=BACK_KNUCKLE_SEGMENTS)

    mount_add, mount_cut = mount_features()
    body = body + mount_add - mount_cut

    body = body - latch_windows()

    body = body + dome_cap(front=False, at_bottom=True) + dome_cap(front=False, at_bottom=False)

    body.label = "canister_back"
    return body


if __name__ == "__main__":
    canister_back()
