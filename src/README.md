# Models: dog poop-bag dispenser

Wall-mounted, 2-piece clamshell capsule. Cylinder axis is vertical; the
back mounts directly to the wall with two screws, the front hinges open on
a pivot offset from the parting edge and latches shut against a rigid
pivoting lever, and has a dispensing slit. Each half also caps its own
ends with a hollow quarter-sphere dome (wall thickness matches the main
shell), so the closed assembly reads as a cylindrical mid-section with a
true hollow hemisphere at each tip.

Both the hinge and the latch's own pivot are built from the same generic
knuckle-pivot module in `lib/canister.py` (`knuckle_row`,
`knuckle_envelope_cut`, `reinforce_seam`) -- a reusable construction for
any rotating joint on a split shell, given just an edge, a normal, and a
pin radius. See **Hinge & latch pivot construction** below.

| Script | Output | Purpose |
| --- | --- | --- |
| lib/canister.py | (no output) | Shared geometry: shell, dome caps, generic knuckle-pivot module, mount bosses, latch lever/lip, dispensing slot |
| canister_back.py | STEP/canister_back.step, STL/canister_back.stl | Wall-mount half: 2x screw holes + counterbore at the apex, hinge knuckles, latch's fixed pivot knuckles |
| canister_front.py | STEP/canister_front.step, STL/canister_front.stl | Hinged half with the dispensing slit and the latch's catch lip |
| hinge_pin.py | STEP/hinge_pin.step, STL/hinge_pin.stl | 3mm rod spanning the interleaved hinge knuckles |
| latch_lever.py | STEP/latch_lever.step, STL/latch_lever.stl | The rigid pivoting latch lever: a pivot knuckle + a hook reaching over front's catch lip |
| latch_pin.py | STEP/latch_pin.step, STL/latch_pin.stl | 2.5mm rod spanning the latch lever's own pivot knuckles |
| dispenser_assembly.py | STEP/dispenser_assembly.step | All five parts placed in their closed, assembled position |

Build everything: `python src/dispenser_assembly.py` from the project root.
Checks: `python checks/check_dispenser.py` (topology, dimensions, dome
sealing, and interference across all five parts — all pass with zero
overlap volume).

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

## Hinge & latch pivot construction

Both the main hinge and the latch's own pivot use the same generic
knuckle-pivot module (`knuckle_row`, `knuckle_envelope_cut`,
`_seam_intersection`/`reinforce_seam` in `lib/canister.py`): given an edge
(the line two bodies meet along) and a normal (perpendicular to the edge,
bisecting the angle between the two bodies' outer faces there), it builds
an interleaved knuckle-and-pin joint and fillets it into whichever body
owns each knuckle. This is reusable as-is for any similar rotating joint
on a split shell in another project -- pass a different edge/normal/radii
and it works the same way.

1. **Generation**: `knuckle_row()` slices the joint's full-length bulk
   cylinder (a given knuckle radius) into segments (pushed apart by a gap
   for clearance), pierces all of them with a single continuous pin bore.
2. **Placement**: each knuckle's own longitudinal axis starts on the edge,
   then moves along the normal by the pin bore radius --
   `axis = edge + normal * pin_radius`. Segments interleave between the
   two parties that share the joint; each knuckle is a plain FULL ROUND
   boss (not clipped to either body's half, like a real hinge barrel),
   unioned onto whichever body owns it.
3. **Reinforcement**: `reinforce_seam()` fillets the seam edge where a
   knuckle's own cylindrical face meets its owning body's outer wall face
   -- found by the two circles' (knuckle radius at the axis, wall radius
   at the body's own center) intersection, selecting the near-side
   crossing per segment directly on the unioned solid's edges. Only the
   near side is filleted; the far side has no wall of that body's own to
   blend into.
4. **Envelope cut**: because the axis sits close to the edge, every
   knuckle boss dips inward past the wall radius on **both** sides of the
   parting line, not just the side it's unioned onto. `knuckle_envelope_cut()`
   subtracts the joint's full continuous footprint (one cylinder spanning
   the whole span, no per-segment gaps) from a body, minus that body's own
   already-built segments, clearing the other party's territory *and* the
   small gaps between segments alike -- cutting only the other party's
   specific segments left those gaps as plain, un-notched wall sticking
   out right next to the cleanly filleted knuckles. This runs *after* a
   body's own knuckles are unioned and filleted (not before), because
   filleting needs intact wall material to blend into at each segment's
   own Z ends; cutting the full envelope first and re-adding the exact
   same shape at those ends is equivalent in the final geometry, but
   leaves OCCT nothing to fillet against right at the boundary.

**Hinge** (edge at X=R_OUT, normal = outward radial): `HINGE_AXIS_X = R_OUT
+ PIN_R`. Segments alternate between the two leaves (back gets 1,3,5...,
front gets 2,4...), each a full-round boss unioned onto its own leaf and
filleted via `reinforce_hinge()`. A single continuous pin bore spans the
whole hinge, open to free air past both ends of the knuckle row.

**Latch pivot** (edge at X=-R_OUT, normal = outward radial, mirrored):
`LATCH_AXIS_X = -R_OUT - LATCH_PIN_R`, a smaller-radius version of the
same joint (`LATCH_KNUCKLE_R=3.5` vs `KNUCKLE_R=4.0`). Three segments
(fixed, lever, fixed): the two outer ones are back's own, fused and
filleted the same way as a hinge leaf; the middle one belongs to neither
back nor front -- it's the separate **latch lever** part's own pivot
knuckle, free to rotate once the latch pin is through all three.

Checks confirm zero interference everywhere and that the gaps, the other
party's territory, and every fillet land exactly where computed.

## Latch

A fully rigid pivoting lever (`latch_lever.py`), pinned to the back via
its own mini hinge-style pivot (above), replaces the earlier cantilever
snap hook. Its hook swings to sit radially outboard of a static catch lip
on the front (`latch_catch_lip()`), with genuine radial (X) overlap
between the two and only a small Y clearance gap -- if front's edge tries
to lift away from back (swing open), the lip runs straight into the
hook's material before it can separate.

No flex anywhere: the lever is a second, independently-actuated degree of
freedom, not a snap that has to both engage AND release from the same
swing motion. (A single rigid catch on a *fixed* pivot -- the earlier
hook -- can't do that: trace the latch edge's own arc as the leaf swings
and the same path is retraced in reverse to open, so a catch that blocks
it one way blocks it the other unless something flexes. A lever you
operate independently sidesteps the problem instead of working around it.)

The lever's shaft (connecting its pivot knuckle to the hook) and the
front's catch lip run down separate Z "lanes" within the lever knuckle's
own width, since the shaft has to pass by the lip's own Z on its way from
the pivot to the hook; only the hook, at the tip, widens to cover both
lanes and reach over the lip. Both the lip and the hook sit entirely at
Y beyond every pivot knuckle's own reach, so neither interacts with the
knuckle row or its envelope cut, and both stay radially outboard of R_OUT,
clear of the front's plain wall -- except the lip's own inboard edge,
which is deliberately embedded past its outer curvature (the wall's
actual surface bows inward across the lip's Y-span) for a genuine fused
union, not just nominal contact.

## Dispensing slit

12mm x 40mm stadium slot on the front's outward face.
