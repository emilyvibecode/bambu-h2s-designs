> Archived prototype. See STATUS.txt for the current fit status.

# AirGradient pegboard attachment — version 2 fit tests

Open **AirGradient-v2-fit-tests-H2S-PLA-Wood.3mf** as a project in Bambu Studio, keeping its settings. Click Slice Plate, review, then Print Plate and select the actual PLA Wood spool. The file is configured for the stock H2S 0.4 mm nozzle, Textured PEI Plate, Bambu PLA Wood, 0.20 mm layers, five walls, and no supports or brim. Keep both pieces lying on their flat sides as supplied.

Bambu Studio reopened and sliced the saved project successfully: approximately 7 minutes 26 seconds total estimated time, 0.78 g model filament. Actual preparation and purging can vary. The slice report has no plate warnings. The CLI logs contain the same T65535 parser diagnostic for the manufacturer end sequence as the first project; the slicer returned Success. The project is editable, not a pre-sliced print job.

## What changed

- Short, rounded return with a 3 mm centerline bend radius and 5 mm total centerline rise.
- Longer neck to clear the board during insertion.
- Single upper attachment only; no lower locating pin yet.
- A has one notch in the bottom of the grip and a 2.0 mm section.
- B has two notches and a 2.4 mm section.

These are experimental unloaded insertion coupons, not finished hooks or an AirGradient mount. Their small sections are deliberately for diagnosing fit; neither PLA Wood strength nor secure retention has been established. Do not hang the AirGradient from them.

## Test after cooling

1. Start with A, identifiable by ONE notch at the bottom. The bent tip points upward and toward the board; the grip hangs downward in front of the board.
2. Tilt the bottom toward yourself, roughly 25–35 degrees away from vertical. Feed the tip through an unobstructed hole while gradually straightening the grip. See how-to-fit-v2.png.
3. Stop if it binds. Do not force it or enlarge the board's hole.
4. Repeat with B, which has TWO bottom notches.
5. Report separately for A and B: does the tip enter, does the grip straighten, does the return catch behind the board, and does it feel loose?

Use a hole with at least approximately 8 mm of clear space behind the back of the board, away from mounting rails or studs. The simulated paths used at most 6.4 mm behind the modeled board; extra clearance allows for real geometry and hand movement.

## Verification and limits

The reference is the user's Triton TPB-4N board, nominally 6.35 mm thick with 6.35 mm round holes. Photos IMG_8876–8878 informed the rounded shape; this is not a dimensionally exact copy of the metal rack.

A conservative collision model uses a 6.6 mm thick board and 6.0 mm diameter hole. The circular hole is reduced to a side-view channel that accommodates the complete square extrusion thickness. A path search tests translation and rotation, followed by 21 intermediate samples per path segment. A passed 1,575 poses; B passed 1,785 poses. This is a sampled geometric check, not a proof of continuous clearance or a real fit test. It excludes surface roughness, print variation, board irregularities, supports behind the board, hand access, retention under load, and material flex/strength.

Both exported meshes are watertight with positive volume. Bambu Studio detects two objects, printed 2.0 and 2.4 mm high. Original editable outlines are supplied as .scad files; the generator and exact path checks are in work/design_hook_v2.py. Full reports are in geometry-and-motion-check.json and result.json.

Do not reuse version 1 for further prints. The next design decision depends on the physical results of these two coupons.
