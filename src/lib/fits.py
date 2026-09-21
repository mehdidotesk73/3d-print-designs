"""Shared FDM fit/clearance constants for this repo's printer (Creality
Ender 3 V3 SE, PLA, hobbyist/uncalibrated dimensional accuracy).

These are process facts, not facts about any one project's geometry --
every project in this repo should pull its clearance numbers from here
rather than picking its own, so a lesson learned on one print (a pin too
tight, a thread that wouldn't turn in at all) improves every future part
instead of staying local to the project that happened to hit it. Revise
the numbers here when real prints show they're off; every project that
imports them picks up the correction on its next build.

A project's own script reaches this module the same way
src/dog_bag_dispenser/build.py reaches scripts/project_build.py --
explicit sys.path.insert, since a script run directly only gets its own
directory on the import path, not the rest of src/. From a project's own
src/<project>/lib/canister.py (two directories below src/<project>/,
three below src/), that's:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "lib"))
    from fits import TIGHT_CLEARANCE, NORMAL_CLEARANCE, LOOSE_CLEARANCE

(count the ".parent"s up to src/ from wherever the importing file
actually lives, then append "lib")

Three named fits, by how the mating surfaces are meant to behave once
assembled -- not by which specific feature they happen to be on:

TIGHT  -- a pin (or pin-like feature) meant to go in snugly and STAY
          there by friction once seated: a hinge pin through its
          knuckle bore, a press-fit dowel. Should still go in by hand
          without forcing a thin feature to the point of snapping it,
          but shouldn't rattle loose either. (First cut at 0.1mm radial
          on the hinge pin bore printed "pretty tough to push through" --
          not broken, but tighter than intended. Loosened here.)
NORMAL -- flat/parallel surfaces meant to slide against each other by
          design intent: a lid in a groove, a latch bolt sliding in its
          own channel. Easy to move on purpose, not wobbly at rest.
NORMAL_CLEARANCE has no prior real-print data point yet in this repo;
          treat it as a starting estimate until a part using it prints.
LOOSE  -- surfaces that need to slide/turn past each other comfortably
          despite real printed texture (helical threads, coarse-
          tolerance features), or parts meant to move relative to one
          another without tight motion guidance (a drawer in a box).
          Generous on purpose -- precision isn't the goal here, free
          movement is. (First cut at 0.15mm growth on a self-cut internal
          thread's shaft/crest "had no chance" of accepting the mating
          screw -- nowhere near enough. Loosened substantially here.)

Values are radial (or per-side) unless noted -- double for a diametral
or two-sided gap (e.g. a pin's bore diameter = pin diameter +
2*TIGHT_CLEARANCE).
"""

TIGHT_CLEARANCE = 0.15
NORMAL_CLEARANCE = 0.25
LOOSE_CLEARANCE = 0.4
