from cadgen import build123d as bd
from cadgen import step

from lib.canister import HINGE_Z_MIN, PIN_BORE_Z0, PIN_BORE_Z1, PIN_D, PIN_HEAD_D, PIN_HEAD_H

# Matches the bore exactly: open at both ends past the knuckle row (see
# HINGE_AXIS_X in lib/canister.py), so the pin can be slid straight in
# after the two leaves are brought together, from the open (headless) end.
PIN_LENGTH = PIN_BORE_Z1 - PIN_BORE_Z0

# Local Z=-PIN_LENGTH/2 is the shaft's own bottom face, which lands at
# world Z=PIN_BORE_Z0 once placed (see dispenser_assembly.py). The
# retention flange's own outer (shallower) face sits at this same local
# offset plus (HINGE_Z_MIN - PIN_BORE_Z0), landing at world Z=HINGE_Z_MIN
# -- flush against the first knuckle's own solid material -- and stays
# within the shaft's own existing length rather than extending past it
# (past HINGE_Z_MIN, this close to the domed tube end, a feature wider
# than the plain shaft starts intersecting the dome's own curved shell).
_FLANGE_TOP_LOCAL_Z = -PIN_LENGTH / 2.0 + (HINGE_Z_MIN - PIN_BORE_Z0)


@step(out="../../STEP/dog_bag_dispenser/hinge_pin.step")
def hinge_pin():
    shaft = bd.Cylinder(PIN_D / 2.0, PIN_LENGTH)

    # A flat retention flange, well past the bore's own diameter so it
    # can never enter the bore itself -- catches the pin from sliding all
    # the way through and out the far end once pushed (or shaken) as far
    # as it'll go, registering against the first knuckle's own face.
    flange = bd.Pos(0.0, 0.0, _FLANGE_TOP_LOCAL_Z) * bd.Cylinder(
        PIN_HEAD_D / 2.0, PIN_HEAD_H, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)
    )

    body = shaft + flange
    body.label = "hinge_pin"
    return body


if __name__ == "__main__":
    hinge_pin()
