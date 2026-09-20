from cadgen import build123d as bd
from cadgen import step

from canister_back import canister_back
from canister_front import canister_front
from hinge_pin import hinge_pin
from latch_lever import latch_lever
from latch_pin import latch_pin
from lib.canister import (
    HINGE_AXIS_X,
    LATCH_AXIS_X,
    LATCH_AXIS_Y,
    LATCH_PIN_BORE_Z0,
    LATCH_PIN_BORE_Z1,
    PIN_BORE_Z0,
    PIN_BORE_Z1,
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

    lever = latch_lever()
    lever.label = "latch_lever"

    latch_pin_z_center = (LATCH_PIN_BORE_Z0 + LATCH_PIN_BORE_Z1) / 2.0
    lpin = latch_pin()
    lpin = bd.Pos(LATCH_AXIS_X, LATCH_AXIS_Y, latch_pin_z_center) * lpin
    lpin.label = "latch_pin"

    return bd.Compound(children=[back, front, pin, lever, lpin], label="dispenser_assembly")


if __name__ == "__main__":
    dispenser_assembly()
