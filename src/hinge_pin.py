from cadgen import build123d as bd
from cadgen import step

from lib.canister import LENGTH, PIN_D

PIN_LENGTH = LENGTH + 3.0


@step(out="../STEP/hinge_pin.step")
def hinge_pin():
    body = bd.Cylinder(PIN_D / 2.0, PIN_LENGTH)
    body.label = "hinge_pin"
    return body


if __name__ == "__main__":
    hinge_pin()
