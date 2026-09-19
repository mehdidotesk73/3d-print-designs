from cadgen import build123d as bd
from cadgen import step

from lib.canister import BACK_KNUCKLE_SEGMENTS, FRONT_KNUCKLE_SEGMENTS, PIN_D, PIN_MARGIN

# Span exactly the interleaved knuckle row (plus a small margin), not the full
# tube length: the ends are now domed and closed, so the pin must stay clear
# of them rather than poking through into the dome material.
_ALL_KNUCKLE_SEGMENTS = BACK_KNUCKLE_SEGMENTS + FRONT_KNUCKLE_SEGMENTS
_KNUCKLE_Z_MIN = min(z0 for z0, _ in _ALL_KNUCKLE_SEGMENTS)
_KNUCKLE_Z_MAX = max(z1 for _, z1 in _ALL_KNUCKLE_SEGMENTS)
PIN_LENGTH = (_KNUCKLE_Z_MAX - _KNUCKLE_Z_MIN) + 2.0 * PIN_MARGIN


@step(out="../STEP/hinge_pin.step")
def hinge_pin():
    body = bd.Cylinder(PIN_D / 2.0, PIN_LENGTH)
    body.label = "hinge_pin"
    return body


if __name__ == "__main__":
    hinge_pin()
