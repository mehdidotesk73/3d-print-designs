# Models: dog poop-bag dispenser

Wall-mounted, 2-piece clamshell capsule. Cylinder axis is vertical; the
back mounts directly to the wall with two screws, the front hinges open on
a pivot offset from the parting edge and closes with a single threaded
screw, and has a dispensing slit. Each half also caps its own ends with a
hollow quarter-sphere dome (wall thickness matches the main shell), so the
closed assembly reads as a cylindrical mid-section with a true hollow
hemisphere at each tip.

The hinge is built from a generic knuckle-pivot module in `lib/canister.py`
(`knuckle_row`, `knuckle_envelope_cut`, `reinforce_seam`) -- a reusable
construction for any rotating joint on a split shell, given just an edge,
a normal, and a pin radius. See **Hinge construction** below.

| Script | Output | Purpose |
| --- | --- | --- |
| lib/canister.py | (no output) | Shared geometry: shell, dome caps, generic knuckle-pivot module, mount bosses, latch ridge/tongue, dispensing slot |
| canister_back.py | STEP/canister_back.step, STL/canister_back.stl | Wall-mount half: 2x screw holes + counterbore at the apex, hinge knuckles, latch's raised ridge |
| canister_front.py | STEP/canister_front.step, STL/canister_front.stl | Hinged half with the dispensing slit and the latch's tongue |
| hinge_pin.py | STEP/hinge_pin.step, STL/hinge_pin.stl | 3mm rod spanning the interleaved hinge knuckles |
| closing_screw.py | STEP/closing_screw.step, STL/closing_screw.stl | The latch itself: a threaded screw with a real, printable helical thread |
| dispenser_assembly.py | STEP/dispenser_assembly.step | All four parts placed in their closed, assembled position |

Build everything: `python src/dispenser_assembly.py` from the project root.
Checks: `python checks/check_dispenser.py` (topology, dimensions, dome
sealing, and interference across all four parts — all pass with zero
overlap volume, except the screw's deliberate self-tapping engagement with
the tongue, checked separately for being genuine but not excessive).

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

## Hinge construction

The hinge uses a generic knuckle-pivot module (`knuckle_row`,
`knuckle_envelope_cut`, `_seam_intersection`/`reinforce_seam` in
`lib/canister.py`): given an edge (the line two bodies meet along) and a
normal (perpendicular to the edge, bisecting the angle between the two
bodies' outer faces there), it builds an interleaved knuckle-and-pin joint
and fillets it into whichever body owns each knuckle. This is reusable
as-is for any similar rotating joint on a split shell in another project
-- pass a different edge/normal/radii and it works the same way (it's
also what the latch's own earlier pivoting-lever design used, before that
was replaced by the simpler screw-and-ridge closure below).

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

## Latch

The dispenser closes with a single threaded screw (`closing_screw.py`) --
no pivot, no flex, no separate lever. Back's closing edge (X=-R_OUT) has a
raised, solid **ridge** (`latch_ridge()`); front's closing edge has a
**tongue** (`latch_tongue()`) that reaches out over it, with a threaded
hole. Screwing the closing screw down through the tongue drives its tip
toward the ridge until it's physically blocked -- the ridge is solid and
unthreaded, so the screw simply cannot pass it. Once seated, the screw is
a rigid strut between front's tongue and back's ridge: pulling front open
would need the screw to either compress further into the ridge (blocked)
or unscrew itself (a rotation, not a pull). This replaced two earlier,
more complex closures in turn -- a cantilever snap hook (needed a flex
point to both engage and release from one swing) and a separate rigid
pivoting lever (needed its own mini hinge, pin, and interleaved knuckle
row) -- with the simplest mechanism yet: one screw doing the whole job.

- **Ridge**: a solid block, embedded `RIDGE_EMBED` past R_OUT (and past
  the wall's own curvature across the ridge's Y-span) for a genuine fused
  union with back's wall. Houses a blind, *unthreaded* pilot pocket
  (`latch_ridge_hole()`) that registers the screw's smooth tip -- this is
  what actually keeps the tongue from sliding sideways once seated, not
  just pulling straight off; a flat stop face alone wouldn't resist that.
- **Tongue**: an L-shaped cross-section -- a thin arm reaching out over
  the ridge (clear of it by `LATCH_GAP`), widening into a root that embeds
  into front's own wall where the arm meets it. Its own hole
  (`latch_tongue_hole()`) is deliberately *undersized* against the screw's
  thread minor diameter (self-tapping): the screw cuts its own channel on
  first insertion, the common, reliable approach for a small FDM-printed
  fastener -- far more robust than modeling a matching internal helical
  thread and hoping the two meshes clear each other at print tolerance.
- **Screw**: a real, printable helical thread (coarse, 2mm pitch --
  fine V-threads don't print reliably at this scale), swept via
  `Helix`+`sweep` onto a core cylinder at the thread's minor diameter, a
  smooth pilot tip below it, and a head above for turning by hand.

Checks confirm zero interference between every part pair *except* the
screw against the tongue, which is checked separately for being a
genuine, real self-tapping engagement (present and in a sane range) --
not a bug, but the whole reason the latch holds.

## Dispensing slit

12mm x 40mm stadium slot on the front's outward face.
