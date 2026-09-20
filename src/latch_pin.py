from cadgen import build123d as bd
from cadgen import step

from lib.canister import LATCH_PIN_BORE_Z0, LATCH_PIN_BORE_Z1, LATCH_PIN_D

# Matches the bore exactly: open at both ends past the knuckle row (see
# LATCH_AXIS_X in lib/canister.py), so the pin can be slid straight in
# after the lever is seated between the back's fixed knuckles.
LATCH_PIN_LENGTH = LATCH_PIN_BORE_Z1 - LATCH_PIN_BORE_Z0


@step(out="../STEP/latch_pin.step")
def latch_pin():
    body = bd.Cylinder(LATCH_PIN_D / 2.0, LATCH_PIN_LENGTH)
    body.label = "latch_pin"
    return body


if __name__ == "__main__":
    latch_pin()
