from cadgen import build123d as bd
from cadgen import step

from canister_back import canister_back
from canister_front import canister_front
from hinge_pin import hinge_pin
from lib.canister import HINGE_AXIS_X, PIN_BORE_Z0, PIN_BORE_Z1


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

    return bd.Compound(children=[back, front, pin], label="dispenser_assembly")


if __name__ == "__main__":
    dispenser_assembly()
