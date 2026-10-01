> Archived prototype. See STATUS.txt for the current fit status.

# Pegboard peg family v1

These are original, light-duty first-print models for a standard round-hole pegboard with nominal 1/4 inch holes on a 1 inch grid. The set compares a plain round cap with square and diamond caps while keeping the mounting geometry identical.

## Print the calibration pieces first

Import `calibration-all-five.stl` into Bambu Studio. It contains five separate test plugs arranged from smallest to largest when viewed left to right:

1. 5.80 mm
2. 5.95 mm
3. 6.10 mm
4. 6.25 mm
5. 6.40 mm

Individual calibration files are also included if you prefer to print one size at a time. Test with gentle hand pressure. Stop if a plug needs force that could damage the pegboard. The best size should enter smoothly, resist wobbling, and pull out without damaging the hole.

The three usable pegs currently use a conservative 6.10 mm stem. After the calibration print, the models should be regenerated with the winning size.

## Bambu Studio starting settings

- Material: PLA for the first fit and style test
- Layer height: 0.20 mm
- Walls: 4
- Top and bottom shells: 5
- Infill: 25 percent gyroid
- Orientation: leave the files upright as imported
- Supports: off
- Brim: 4 to 6 mm if the tall pegs do not adhere reliably

Print one usable peg before printing the full set. These upright models are intended for keys, cords, scissors, and other light objects. The next revision can be optimized for heavier loads after the stem fit and board thickness are confirmed.

## Files

- `peg-round-6.10mm.stl`: classic circular retaining cap
- `peg-square-6.10mm.stl`: 12 mm square retaining cap
- `peg-diamond-6.10mm.stl`: rotated square retaining cap
- `calibration-all-five.stl`: all five test diameters on one plate
- `calibration-*.stl`: individual test plugs

## Measurements to record after printing

- Winning stem diameter
- Pegboard thickness
- Usable clearance behind the pegboard
- Whether the 23 mm arm is long enough
- Which end shape looks best on camera and holds an item most securely

This first version uses friction fit rather than a locking barb. Once the measurements above are known, the shared attachment can become a reusable Fusion 360 component for later hooks, cups, and brackets.
