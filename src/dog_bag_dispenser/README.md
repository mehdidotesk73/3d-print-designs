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

This project lives at `src/dog_bag_dispenser/` -- one of possibly several
projects in this repo, each with its own `lib/`, model scripts, and
generated STL bundle. See `/index.html` and `scripts/build_html.py` at
the repo root for how every project's parts get surfaced in one viewer.

| Script | Output | Purpose |
| --- | --- | --- |
| lib/canister.py | (no output) | Shared geometry: shell, dome caps, generic knuckle-pivot module, mount bosses, latch tab/back-bore, dispensing slot |
| canister_back.py | STEP/dog_bag_dispenser/canister_back.step | Wall-mount half: 2x screw holes + counterbore at the apex, hinge knuckles, latch's plain clearance bore |
| canister_front.py | STEP/dog_bag_dispenser/canister_front.step | Hinged half with the dispensing slit and the latch's tab |
| hinge_pin.py | STEP/dog_bag_dispenser/hinge_pin.step | 3mm rod spanning the interleaved hinge knuckles |
| closing_screw.py | STEP/dog_bag_dispenser/closing_screw.step | The latch itself: a threaded screw with a real, printable helical thread |
| dispenser_assembly.py | STEP/dog_bag_dispenser/dispenser_assembly.step | All four parts placed in their closed, assembled position |
| build.py | src/dog_bag_dispenser/stl/*.stl | Rebuilds every model above and exports a fresh, committed STL per part |
| viewer.json | (no output) | Per-part name/description/details/spec text for index.html's viewer -- edited by hand |

Build everything: `python src/dog_bag_dispenser/build.py` from the repo
root (or from anywhere -- it resolves its own paths). Checks:
`python checks/check_dispenser.py` (topology, dimensions, dome sealing,
and interference across all four parts — all pass with zero overlap
volume, including the screw against the tab's own genuine internal
thread).

Preview: `/index.html` at the repo root is an interactive STL viewer
(three.js) checked into git, with a tab per project and a subtab per
part -- clone the repo and open it directly in a browser, no server
needed, to view and download each part's `.stl`. After running this
project's `build.py`, run `python scripts/build_html.py` from the repo
root to fold the fresh meshes (and this project's `viewer.json` text)
into `/viewer_data.js`, which `index.html` reads via `<script src>`
rather than `fetch()` (local `fetch()` is blocked under `file://`, a
script load isn't). Chromium snapshot rendering in this sandbox needs
`python3 scripts/snapshot_shim.py step snapshot ...` (env-specific
`executable_path` + `CADGEN_DAEMON=0` workaround) rather than plain
`cadgen step snapshot`.

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
was replaced by the simpler screw-and-tab closure below).

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

**Pin** (`hinge_pin.py`): a plain `PIN_D` rod matching the bore's own
span, plus a retention **flange** (`PIN_HEAD_D`/`PIN_HEAD_H`) near its
bottom end -- wide enough that it can never enter the knuckle bore, so it
catches the pin from being pushed or shaken all the way through and out
the far side. Its outer face sits flush with `HINGE_Z_MIN`, right where
the first knuckle's own solid material begins, and it stays *within* the
shaft's own existing overhang length rather than reaching past it: this
close to the tube's domed end, any feature wider than the plain shaft
starts intersecting the dome's own curved shell if it reaches too far
past `HINGE_Z_MIN` (the dome cap's radius from the tube's central axis
narrows quickly here, tighter than it looks from the knuckle row's own,
narrower radial reach). The pin's other end stays plain -- that's the end
you slide it in from.

## Latch

The dispenser closes with a single threaded screw (`closing_screw.py`) --
no pivot, no flex, no separate lever. Front's closing edge has a **tab**
(`latch_tab()`) that reaches across the split line to rest against back's
own outer wall (clear of it by `LATCH_GAP`), with a threaded **screw
fastening hole** (`latch_tab_fastening_hole()`). Back's closing edge
(X=-R_OUT) just has a plain, unthreaded clearance **bore**
(`latch_back_bore()`) straight through its own wall -- no raised feature
at all. Screwing the closing screw into the tab's fastening hole makes the
screw rigid with front; as it tightens, its smooth tip advances into
back's bore and comes to rest there with clearance, not fastened to back
in any way.

That alone is enough to resist the hinge opening. Front pivots open about
the main hinge (the opposite edge), so as it swings, the latch edge moves
mostly *tangentially*, not radially outward -- and tangential motion is
exactly what the bore's own side wall blocks: the screw's tip immediately
meets it rather than being free to slide away. The screw-and-tip pair acts
like a dowel pin spanning the joint. An earlier version of this raised a
solid ridge on back for the screw tip to press into as a hard stop, but
back's own wall (whatever its thickness) already provides the depth to
register the tip the same way -- the ridge did the identical restraint job
with extra material and extra geometry, for no extra strength, so it was
dropped. This replaced two earlier, more complex closures in turn -- a
cantilever snap hook (needed a flex point to both engage and release from
one swing) and a separate rigid pivoting lever (needed its own mini hinge,
pin, and interleaved knuckle row) -- with the simplest mechanism yet: one
screw doing the whole job, no raised features on either leaf.

- **Tab**: an L-shaped cross-section -- a thin arm reaching out to rest
  against back's own wall (clear of it by `LATCH_GAP`), widening into a
  root that embeds `TAB_EMBED` past R_OUT into front's own wall where the
  arm meets it. Its own fastening hole is a genuine internal thread, not a
  self-tapping pilot hole -- see below.
- **Back's bore**: a plain, unthreaded, oversized clearance bore straight
  through back's own wall (`BACK_BORE_D`, `BACK_BORE_DEPTH`) -- large
  enough that the screw's smooth tip can never bind or thread into it, and
  oversized in length (not just diameter) so it fully pierces the wall
  regardless of the wall's own curvature this close to the split line.
  `SCREW_TIP_ENGAGE` (how deep the tip seats) stays short of `WALL`, so the
  tip never pokes out into the cavity.
- **Screw**: a real, printable helical thread (coarse, 2mm pitch,
  trapezoidal flat-crest profile -- fine V-threads, or a knife-edge crest,
  don't print reliably at this scale), swept via `Helix`+`sweep`, a smooth
  pilot tip below it (uniform with the thread's own core diameter, no
  step), and a head above for turning by hand.

**The tab's fastening hole is cut by a THREAD-MAKER** (`threaded_shank()`
in `lib/canister.py`, shared with the real screw), not sized as a
self-tapping pilot hole. Two printed plastic parts don't cut into each
other the way a metal screw cuts into wood or sheet metal, and FDM's own
layered, anisotropic strength makes that even less reliable -- so instead,
`latch_tab_fastening_hole()` builds an oversized copy of the screw's own
helix (same pitch, same profile shape, same handedness, via the same
`threaded_shank()` function, just with the shaft, thread crest, and crest
width each independently grown by a `THREADMAKER_*_CLEARANCE` constant,
then unioned) and subtracts it from the tab. Because the thread-maker is
strictly larger than the real screw at every point along that same helix,
the resulting hole is a true internal thread with real clearance -- the
screw turns freely into it, rather than being expected to cut its own way
in.

Getting the thread-maker's helix to actually line up with the real
screw's took care on the placement math (both are placed with the exact
same `rotate(-90, Y)` + translate used for the real screw in
`dispenser_assembly.py`, so they share the same phase, not just the same
pitch) and on where each one *starts*: a swept helix's start cap (an OCCT
quirk, not a design feature) can flare slightly wider than the
sweep's own steady-state cross-section, and since both the tab's own
physical edge and the real screw's own thread start at the exact same
world X, that flare landed right where the cut boundary mattered most,
leaving a small residual overlap despite the thread-maker being oversized
everywhere else. `THREADMAKER_START_PAD` fixes this by pushing the
thread-maker's own start out past the tab's edge into the open `LATCH_GAP`
air gap, so whatever the flare's exact shape is, it lands somewhere that
cuts nothing rather than right at the tab's own boundary.

Checks confirm zero interference across every part pair, including the
screw against the tab -- no more self-tapping exception to carve out.
Dedicated checks also cross-verify the screw's actual assembled placement
(its bounding box) against the tip-engagement formula in
`dispenser_assembly.py`, since the placement math there has to measure
engagement depth from back's real outer wall surface (-R_OUT), not from
the bore's own oversized cutting margin -- getting that wrong would
silently shift the whole screw (and its thread) off the tab despite every
build step succeeding -- and confirm the thread-maker's own clearances are
genuinely positive (a real oversize, not accidentally shrunk or reversed).

## Dispensing slit

12mm x 40mm stadium slot on the front's outward face.
