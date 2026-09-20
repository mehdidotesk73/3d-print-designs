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
    R_OUT,
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
    # screw points as it's driven in, from the tab's outer face toward
    # back); the tip's end then lands at its seated depth within back's
    # own clearance bore, measured from back's actual outer wall surface
    # (-R_OUT) -- not BACK_BORE_X0, which has an extra 1mm overshoot
    # margin baked in purely so the subtracted bore cylinder fully
    # penetrates back's wall regardless of local curvature.
    screw = closing_screw()
    screw = screw.rotate(bd.Axis.Y, -90.0)
    tip_end_x = -R_OUT + SCREW_TIP_ENGAGE
    screw = bd.Pos(tip_end_x, LATCH_HOLE_Y, LATCH_HOLE_Z) * screw
    screw.label = "closing_screw"

    return bd.Compound(children=[back, front, pin, screw], label="dispenser_assembly")


if __name__ == "__main__":
    dispenser_assembly()
