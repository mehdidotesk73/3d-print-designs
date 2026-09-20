from cadgen import build123d as bd
from cadgen import step

from lib.canister import (
    LATCH_AXIS_X,
    LATCH_AXIS_Y,
    LATCH_KNUCKLE_R,
    LATCH_LEVER_SEGMENTS,
    LATCH_PIN_BORE_Z0,
    LATCH_PIN_BORE_Z1,
    LATCH_PIN_R,
    knuckle_row,
    latch_lever_arm,
)


@step(out="../STEP/latch_lever.step")
def latch_lever():
    knuckle = knuckle_row(LATCH_AXIS_X, LATCH_AXIS_Y, LATCH_KNUCKLE_R, LATCH_PIN_R,
                           LATCH_LEVER_SEGMENTS, LATCH_PIN_BORE_Z0, LATCH_PIN_BORE_Z1)
    body = knuckle + latch_lever_arm()

    # The arm's shaft passes directly over the knuckle's own pin bore on its
    # way from the pivot to the hook -- re-cut the bore after the union so
    # the pin channel stays open through the shaft too, not just the boss.
    bore = bd.Cylinder(
        LATCH_PIN_R, LATCH_PIN_BORE_Z1 - LATCH_PIN_BORE_Z0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    bore = bd.Pos(LATCH_AXIS_X, LATCH_AXIS_Y, LATCH_PIN_BORE_Z0) * bore
    body = body - bore

    body.label = "latch_lever"
    return body


if __name__ == "__main__":
    latch_lever()
