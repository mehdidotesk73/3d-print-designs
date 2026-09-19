# Models: dog poop-bag dispenser

Wall-mounted, 2-piece clamshell capsule. Cylinder axis is vertical; the
back mounts directly to the wall with two screws, the front hinges open on
an external tangent pivot and hook-latches shut, and has a dispensing
slit. Each half also caps its own ends with a hollow quarter-sphere dome
(wall thickness matches the main shell), so the closed assembly reads as
a cylindrical mid-section with a true hollow hemisphere at each tip.

| Script | Output | Purpose |
| --- | --- | --- |
| lib/canister.py | (no output) | Shared geometry: shell, dome caps, hinge knuckles, mount bosses, latch hook/window, dispensing slot |
| canister_back.py | STEP/canister_back.step, STL/canister_back.stl | Wall-mount half: 2x screw holes + counterbore at the apex |
| canister_front.py | STEP/canister_front.step, STL/canister_front.stl | Hinged + latching half with the dispensing slit |
| hinge_pin.py | STEP/hinge_pin.step, STL/hinge_pin.stl | 3mm rod spanning the interleaved hinge knuckles |
| dispenser_assembly.py | STEP/dispenser_assembly.step | All three parts placed in their closed, assembled position |

Build everything: `python src/dispenser_assembly.py` from the project root.
Checks: `python checks/check_dispenser.py` (topology, dimensions, dome
sealing, and back/front/pin interference — all pass with zero overlap volume).

Preview: an interactive STL viewer (three.js) is published as a Claude
Artifact — see the conversation for the link. Chromium snapshot rendering
in this sandbox needs `python3 scripts/snapshot_shim.py step snapshot ...`
(env-specific `executable_path` + `CADGEN_DAEMON=0` workaround) rather than
plain `cadgen step snapshot`.

## Key dimensions
- Sized for a roll Ø40mm x 70mm long, plus 4mm clearance on each: cavity
  ID 44mm, cylindrical length 74mm. OD 50mm, wall 3mm.
- Dome end caps: hollow quarter-sphere per half (outer radius = OD/2 =
  25mm, same 3mm wall as the main shell), so the closed assembly's
  overall axial span is 74 + 2x25 = 124mm.
- Mount holes: 2x M4.5 clearance, ~29mm apart, centered at the back's
  apex, clear of the domed ends, counterbored on the inside for the
  screw heads.
- Hinge: the pivot axis is external and tangent to the tube's OD (not
  centered on the parting edge) -- `HINGE_AXIS_X = R_OUT + KNUCKLE_R -
  HINGE_OVERLAP`, a small deliberate overlap rather than exact tangency,
  which OCCT can't fillet. A centered/embedded pivot would leave the pin
  bore fully enclosed once the dome caps exist, with nowhere to slide the
  pin in from, and would make each leaf's body sweep back through the
  pin's own space while swinging; the external placement fixes both.
  Each knuckle is a FULL ROUND boss (a real hinge barrel, not sliced in
  half at the parting plane): built from that leaf's own half-annulus
  (matching wall thickness and half-plane elsewhere) unioned with an
  unclipped knuckle circle. Only the near side (where the knuckle meets
  this leaf's own wall) is filleted smooth -- that's a genuine junction.
  The far side (facing the other leaf) is trimmed so it never dips inside
  R_OUT in the first place, so it can never overlap the other leaf's
  territory there; no compensating clearance cut on the other leaf is
  needed, and back/front interference checks out at exactly zero volume.
  Knuckles alternate between the two leaves (back gets segments 1,3,5...,
  front gets 2,4...) with a single continuous pin bore run through the
  whole span, open to free air past both ends of the knuckle row.
- Latch: a cantilever hook on the front (2.5mm arm, 3.5mm asymmetric
  drop-hook catch) catches through a window cut in the back's wall. A
  single flex point (the hook's own arm) is the most durable arrangement
  for a catch that self-engages during the closing swing -- a fully rigid
  hook can't self-release from pure rotation about a fixed pivot (trace
  the latch edge's arc: the same path is retraced open and shut, so a
  catch that blocks it one way blocks it the other unless something
  flexes).
- Dispensing slit: 12mm x 40mm stadium slot on the front's outward face.
