# Models: dog poop-bag dispenser

Wall-mounted, 2-piece clamshell canister. Cylinder axis is vertical; the
back mounts directly to the wall with two screws, the front hinges open on
one edge and snap-latches shut on the other, and has a dispensing slit.

| Script | Output | Purpose |
| --- | --- | --- |
| lib/canister.py | (no output) | Shared geometry: shell, hinge knuckles, mount bosses, latch tab/window, dispensing slot |
| canister_back.py | STEP/canister_back.step, STL/canister_back.stl | Wall-mount half: 2x screw holes + counterbore at the apex |
| canister_front.py | STEP/canister_front.step, STL/canister_front.stl | Hinged + latching half with the dispensing slit |
| hinge_pin.py | STEP/hinge_pin.step, STL/hinge_pin.stl | 3mm x 48mm rod through the interleaved hinge knuckles |
| dispenser_assembly.py | STEP/dispenser_assembly.step | All three parts placed in their closed, assembled position |

Build everything: `python src/dispenser_assembly.py` from the project root.
Checks: `python checks/check_dispenser.py` (topology, dimensions, and
back/front/pin interference — all pass with zero overlap volume).

## Key dimensions
- Cavity ID 70mm, OD 76mm, wall 3mm, axial length 45mm (fits a single bag
  roll up to ~65mm OD x ~40mm wide).
- Mount holes: 2x M4.5 clearance, 30mm apart, centered at the back's apex,
  counterbored on the inside for the screw heads.
- Hinge: 5 interleaved knuckles (3 on back, 2 on front) bored for a 3mm pin.
- Latch: 2 cantilever snap tabs on the front, catching in windows cut
  through the back's wall.
- Dispensing slit: 12mm x 40mm stadium slot on the front's outward face.
