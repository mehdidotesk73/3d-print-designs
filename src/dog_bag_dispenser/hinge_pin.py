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


def _flange_profile() -> bd.Shape:
    """The flange's own cross-section: a PIN_HEAD_D circle with the side
    facing the tube's central axis (local -X, since the pin's own local
    frame maps directly onto world X/Y with no rotation -- see
    dispenser_assembly.py) cut off by a plane tangent to the shaft's own
    outer surface, not a plain symmetric circle.

    That inward side is exactly where a symmetric flange would start
    intersecting the dome cap's own curved shell this close to the tube's
    end (see HINGE_Z_MIN below); the outward side has no such limit, no
    matter how close to the tube's end it gets, since moving away from
    the tube's own central axis only ever increases distance from the
    dome's own center. Cutting the one risky side, rather than shrinking
    the whole circle, keeps the flange's outward reach -- what actually
    does the catching -- as generous as it was before.
    """
    r = PIN_HEAD_D / 2.0
    circle = bd.Circle(r)
    outward_half = bd.Pos(-PIN_D / 2.0, 0.0) * bd.Rectangle(
        2.0 * r, 2.0 * r, align=(bd.Align.MIN, bd.Align.CENTER)
    )
    return circle & outward_half


@step(out="../../STEP/dog_bag_dispenser/hinge_pin.step")
def hinge_pin():
    shaft = bd.Cylinder(PIN_D / 2.0, PIN_LENGTH)

    # A flat retention flange, well past the bore's own diameter on its
    # outward side so it can never enter the bore itself -- catches the
    # pin from sliding all the way through and out the far end once
    # pushed (or shaken) as far as it'll go, registering against the
    # first knuckle's own face.
    flange = bd.Pos(0.0, 0.0, _FLANGE_TOP_LOCAL_Z) * bd.extrude(_flange_profile(), amount=-PIN_HEAD_H)

    body = shaft + flange
    body.label = "hinge_pin"
    return body


if __name__ == "__main__":
    hinge_pin()
