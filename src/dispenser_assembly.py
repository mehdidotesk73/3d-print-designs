from cadgen import build123d as bd
from cadgen import step

from canister_back import canister_back
from canister_front import canister_front
from closing_screw import closing_screw
from hinge_pin import hinge_pin
from lib.canister import (
    HINGE_AXIS_X,
    LATCH_HOLE_Y,
    LATCH_HOLE_Z,
    PIN_BORE_Z0,
    PIN_BORE_Z1,
    RIDGE_OUTER_X,
    SCREW_TIP_ENGAGE,
)


@step(out="../STEP/dispenser_assembly.step")
def dispenser_assembly():
    back = canister_back()
    back.label = "canister_back"

    front = canister_front()
    front.label = "canister_front"

    pin_z_center = (PIN_BORE_Z0 + PIN_BORE_Z1) / 2.0
    pin = hinge_pin()
    pin = bd.Pos(HINGE_AXIS_X, 0.0, pin_z_center) * pin
    pin.label = "hinge_pin"

    # Local frame: Z=0 is the tip's own end, increasing toward the head.
    # Rotating -90 about Y maps local +Z to world -X (the direction the
    # screw points as it's driven in, from the tongue's outer face toward
    # the ridge); the tip's end then lands at its seated depth within the
    # ridge's blind hole.
    screw = closing_screw()
    screw = screw.rotate(bd.Axis.Y, -90.0)
    tip_end_x = RIDGE_OUTER_X + SCREW_TIP_ENGAGE
    screw = bd.Pos(tip_end_x, LATCH_HOLE_Y, LATCH_HOLE_Z) * screw
    screw.label = "closing_screw"

    return bd.Compound(children=[back, front, pin, screw], label="dispenser_assembly")


if __name__ == "__main__":
    dispenser_assembly()
