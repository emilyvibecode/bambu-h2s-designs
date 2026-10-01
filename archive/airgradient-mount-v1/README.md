> Archived prototype. See STATUS.txt for the current fit status.

# AirGradient pegboard mount — first fit test

These are small, unloaded fit coupons for the pegboard attachment. They are not the completed AirGradient mount and have no tested load rating.

## Configured project for your printer and spool

Use **AirGradient-H2S-PLA-Wood.3mf** instead of the older model-only 3MF. Open it as a project so Bambu Studio loads the included settings.

Configured for the unchanged Bambu Lab H2S, 0.4 mm hardened-steel nozzle, Textured PEI Plate shown in your screenshots, and Bambu PLA Wood (Clay Brown). It includes the installed Bambu profiles, five walls, 0.20 mm layers, 35% gyroid, five top/bottom layers, no supports, no brim, and one filament. Color is a visual approximation.

The configured project was exported by Bambu Studio 02.08.02.61, reopened by its CLI and successfully sliced. Its report estimates 12 minutes 13 seconds including modeled preparation and approximately 3.49 g of model filament; actual preparation/purge use can vary. All three models were detected at 3.6 mm height. The CLI logs also report a T65535 parser message for the manufacturer's unchanged end-of-print unload command; the slice report returns success with no plate warnings. This deliverable contains the editable project, not pre-sliced machine instructions: slice it in the GUI before printing.

1. Open the configured file as a project.
2. Click Slice Plate and review the preview.
3. Click Print Plate, select your connected H2S, and map the filament to the slot holding Clay Brown PLA Wood (or the external spool if used).

The spool label specifies drying at 60°C for 8 hours. PLA Wood is being used here for an unloaded fit test, not a verified load-bearing mount.

## Older geometry-only files

Open `hook-tests-all-three.3mf` as geometry in Bambu Studio, or import one of the individual STL files. The 3MF contains models only, not a configured or sliced printer job. Keep your H2S printer profile and select the nozzle size, build plate and PLA profile that match your actual equipment and spool.

- Keep the supplied side-down orientation: each part lies flat and is 3.6 mm tall on the print bed.
- Use 0.20 mm layers, 5 walls, 5 top/bottom layers and 35% gyroid infill with a 0.4 mm nozzle. These slender pieces will be largely solid because of the walls.
- Supports off. Add a small brim only if adhesion requires it.
- Slice and inspect the preview before sending the print. The slicer provides the actual time estimate.
- Let the bed cool, then remove the parts and any brim.

## Which test is which?

The parts are separate named objects in the 3MF. From left to right in the original arrangement:

1. Shortest hook reach: 3.2 mm board (about 1/8 inch).
2. Medium hook reach: 4.8 mm board (about 3/16 inch).
3. Longest hook reach: 6.4 mm board (about 1/4 inch).

Each includes 0.4 mm clearance beyond its nominal board thickness. These assume approximately 6.35 mm round holes, 25.4 mm center spacing, and empty space behind the board. Those dimensions have not been measured on your board. The hook and lower pin have a 3.6 mm square cross-section; these are deliberately clearance-fit rather than friction-fit.

## Try the fit

Hold the long spine vertically against the front of the board, with the bent hook at the top, pointing upward behind the board. Tilt the bottom away from the board, insert the upper hook, and gently rotate the bottom toward the board so the straight pin enters the hole immediately below. Do not force it. Stop if the hook cannot pass through the hole or the board begins to crumble.

Choose the smallest board-thickness version that seats fully with slight clearance. Note whether the hook catches behind the board, the lower pin lines up, and the spine rests against the front. Record any interference during insertion and approximate clearance behind the board. Do not hang the AirGradient from this test piece.

## Full mount design to finish after fit confirmation

The planned adapter uses two load-bearing upper hooks and lower locating pins. The lower pins primarily resist rocking; they should not be assumed to share the vertical load equally. A separate, side-printed hook component preserves favorable layer orientation instead of printing an entire backplate flat with upright hooks. The hook-to-plate joint is still to be designed.

The device interface will use two M4 screw heads at the manufacturer's left/right keyhole spacing (60 mm), with screw-head clearance verified on the actual case. The backplate will leave the cable route and top/bottom vents clear. Approximate plate dimensions discussed earlier are provisional. Screw length, head geometry, nut retention and final plate thickness remain to be specified.

PLA is the available material. Physical fit and an unloaded assembly check precede a supported load test with a substitute weight. Neither mesh validation nor slicer settings establish a load rating.

Reference: https://www.airgradient.com/documentation/kb/mount-airgradient-one/

## Editable source and checks

Each STL has a matching OpenSCAD source. The generator is `work/generate_airgradient_hook_tests.py` in the workspace. It triangulates a continuous polygon into one solid per coupon; the validation report checks closed edges, consistent winding, positive volume and dimensions. Physical fit, strength, and a Bambu Studio slice have not been verified.
