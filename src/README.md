# Models: dog poop-bag dispenser

Wall-mounted, 2-piece clamshell capsule. Cylinder axis is vertical; the
back mounts directly to the wall with two screws, the front hinges open on
a pivot offset from the parting edge and hook-latches shut, and has a
dispensing slit. Each half also caps its own ends with a hollow
quarter-sphere dome (wall thickness matches the main shell), so the closed
assembly reads as a cylindrical mid-section with a true hollow hemisphere
at each tip.

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
- Hinge: a generic construction given an edge (the line the two leaves'
  outer surfaces meet along, here the tube's own parting line at X=R_OUT)
  and a hinge normal (perpendicular to the edge, bisecting the two outer
  faces' angle there -- for this tube, just the outward radial direction).
  1. **Generation**: slice the hinge's full-length bulk cylinder (radius
     `KNUCKLE_R`) into knuckle segments (`_pack_alternating_segments`,
     pushed apart by a gap for clearance), pierce all of them with a single
     continuous pin bore.
  2. **Placement**: each knuckle's own longitudinal axis starts on the
     edge, then moves along the hinge normal by the pin bore radius --
     `HINGE_AXIS_X = R_OUT + PIN_R`. Segments alternate between the two
     leaves (back gets 1,3,5..., front gets 2,4...); each knuckle is a
     plain FULL ROUND boss (not clipped to either leaf's half, like a real
     hinge barrel), unioned onto its leaf.
  3. **Reinforcement**: `reinforce_hinge()` fillets the seam edge where the
     knuckle's own cylindrical face meets that leaf's own outer wall face
     -- found by the two circles' (KNUCKLE_R at the axis, R_OUT at the
     tube's own center) intersection, selecting the near-side crossing per
     segment directly on the unioned solid's edges. Only the near side is
     filleted; the far side has no wall of this leaf's own to blend into.
  4. **Envelope cut**: because the axis sits so close to the edge, every
     knuckle boss dips inward past R_OUT into the wall band on **both**
     sides of the parting line, not just the side it's unioned onto.
     `hinge_envelope_cut()` subtracts the hinge's full continuous
     footprint (one cylinder spanning the whole hinge span, no per-segment
     gaps) from the leaf, minus its own already-built segments, clearing
     the other leaf's territory *and* the small gaps between segments
     alike -- cutting only the other leaf's specific segments (an earlier
     version of this) left those gaps as plain, un-notched wall sticking
     out right next to the cleanly filleted knuckles. This runs *after*
     the knuckles are unioned and filleted (not before), because filleting
     needs intact wall material to blend into at each segment's own Z
     ends; cutting the full envelope first and re-adding the exact same
     shape at those ends is equivalent in the final geometry, but leaves
     OCCT nothing to fillet against right at the boundary.

  Checks confirm zero back/front interference and that the gaps, the other
  leaf's territory, and the fillet all land exactly where computed. A
  single continuous pin bore spans the whole hinge, open to free air past
  both ends of the knuckle row.
- Latch: a cantilever hook on the front (2.5mm arm, 3.5mm asymmetric
  drop-hook catch) catches through a window cut in the back's wall. A
  single flex point (the hook's own arm) is the most durable arrangement
  for a catch that self-engages during the closing swing -- a fully rigid
  hook can't self-release from pure rotation about a fixed pivot (trace
  the latch edge's arc: the same path is retraced open and shut, so a
  catch that blocks it one way blocks it the other unless something
  flexes).
- Dispensing slit: 12mm x 40mm stadium slot on the front's outward face.
