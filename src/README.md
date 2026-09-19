# Models: dog poop-bag dispenser

Wall-mounted, 2-piece clamshell capsule. Cylinder axis is vertical; the
back mounts directly to the wall with two screws, the front hinges open on
one edge and snap-latches shut on the other, and has a dispensing slit.
Each half also caps its own ends with a hollow quarter-sphere dome (wall
thickness matches the main shell), so the closed assembly reads as a
cylindrical mid-section with a true hollow hemisphere at each tip.

| Script | Output | Purpose |
| --- | --- | --- |
| lib/canister.py | (no output) | Shared geometry: shell, dome caps, hinge knuckles, mount bosses, latch tab/window, dispensing slot |
| canister_back.py | STEP/canister_back.step, STL/canister_back.stl | Wall-mount half: 2x screw holes + counterbore at the apex |
| canister_front.py | STEP/canister_front.step, STL/canister_front.stl | Hinged + latching half with the dispensing slit |
| hinge_pin.py | STEP/hinge_pin.step, STL/hinge_pin.stl | 3mm rod spanning the interleaved hinge knuckles |
| dispenser_assembly.py | STEP/dispenser_assembly.step | All three parts placed in their closed, assembled position |

Build everything: `python src/dispenser_assembly.py` from the project root.
Checks: `python checks/check_dispenser.py` (topology, dimensions, dome
sealing, and back/front/pin interference — all pass with zero overlap volume).

## Key dimensions
- Sized for a roll Ø40mm x 70mm long, plus 4mm clearance on each: cavity
  ID 44mm, cylindrical length 74mm. OD 50mm, wall 3mm.
- Dome end caps: quarter-sphere per half, radius = OD/2 (25mm), so the
  closed assembly's overall axial span is 74 + 2x25 = 124mm.
- Mount holes: 2x M4.5 clearance, ~29mm apart, centered at the back's
  apex, clear of the domed ends, counterbored on the inside for the
  screw heads.
- Hinge: built as a placemaker channel (full hinge-diameter cylinder,
  subtracted from both leaves first) with alternating knuckle segments
  added back per leaf and a single continuous pin bore run through the
  whole span -- so there's no leftover plain-wall sliver in the gaps
  between knuckles on either leaf, and the through-bore is unbroken.
- Latch: 2 cantilever snap tabs on the front, catching in windows cut
  through the back's wall.
- Dispensing slit: 12mm x 40mm stadium slot on the front's outward face.
