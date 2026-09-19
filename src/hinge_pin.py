from cadgen import build123d as bd
from cadgen import step

from lib.canister import PIN_BORE_Z0, PIN_BORE_Z1, PIN_D

# Matches the bore exactly: open at both ends past the knuckle row (see
# HINGE_AXIS_X in lib/canister.py), so the pin can be slid straight in
# after the two leaves are brought together.
PIN_LENGTH = PIN_BORE_Z1 - PIN_BORE_Z0


@step(out="../STEP/hinge_pin.step")
def hinge_pin():
    body = bd.Cylinder(PIN_D / 2.0, PIN_LENGTH)
    body.label = "hinge_pin"
    return body


if __name__ == "__main__":
    hinge_pin()
