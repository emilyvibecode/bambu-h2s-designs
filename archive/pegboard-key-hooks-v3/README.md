> Archived prototype. See STATUS.txt for the current fit status.

# Version 3 — pegboard key hooks

Open **Pegboard-key-hooks-v3-H2S-PLA-Wood.3mf** as a project in Bambu Studio and retain its settings. It contains two small key hooks using the same upper attachments as the V2 AirGradient fit tests. This is a pegboard key-hook prototype, not the completed AirGradient holder.

## Print

Configured for your stock Bambu H2S, 0.4 mm nozzle, Textured PEI Plate, and Bambu PLA Wood. Side-down orientation, 0.20 mm layers, five walls, 35% gyroid, no supports, no brim. Slice Plate, check the preview, then Print Plate and choose the actual PLA Wood spool. No print was started automatically.

The saved project was reopened and sliced successfully in Bambu Studio: approximately **11 minutes 6 seconds total for both hooks**, **3.0 g model filament**, and no plate warnings. Actual startup/purge use and time can vary. The CLI repeats its T65535 diagnostic for the manufacturer end sequence; its result reports Success.

## Identify and fit

- **A: one bottom notch.** 2.0 mm upper attachment, matching V2 A.
- **B: two bottom notches.** 2.4 mm upper attachment, matching V2 B.
- Both have a 6 mm thick front body, rounded key hook, and approximately 20 mm projection in front of the board.

Let the plate cool before removing. Try A first, then B. Tip the bottom toward yourself roughly 25–35 degrees, feed the upper tip through the hole, and straighten gently. Use a hole away from wall supports with approximately 8 mm or more clear space behind the board. Do not force it.

First confirm that the upper tip enters, the body seats, and the bent return catches. If B fits, start with a few keys close to the board, over a clear surface, and inspect for movement, bending, or cracking. Neither variant has a verified load rating; the slender pegboard attachment remains the limiting feature. Do not suspend the AirGradient from this prototype. A single attachment can swivel; report that too.

## Design and checks

The complete upper shape above y=-5 mm is unchanged from V2; the new lower shape adds a rounded J arm with a 4.6 mm profile and 6 mm print thickness. It prints flat without unsupported islands. Each STL is one connected, watertight, consistently wound solid with positive volume. Editable OpenSCAD outlines are included; Python generator: work/design_key_hooks_v3.py.

The full new silhouette was checked along the saved V2 path against a conservative 6.6 mm board / 6.0 mm hole envelope. The extra thick front portion was separately checked against the entire board slab, ensuring it never relies on passing through the hole. A passed 1,575 sampled poses; B passed 1,785. This is sampled geometry verification, not a physical fit, retention, durability, or strength test. Reports are in geometry-and-motion-check.json and result.json.

Nominal reference board: Triton TPB-4N, 6.35 mm thickness and hole diameter. The user's working metal rack photos informed the shape; its dimensions were not copied exactly from photographs.
