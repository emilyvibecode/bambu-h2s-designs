#!/usr/bin/env python3
"""Generate a first-print pegboard calibration set and three light-duty pegs.

The meshes are deliberately dependency-free so the deliverables can be
regenerated in a stock Python installation. Units are millimetres.
"""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "pegboard-peg-family-v1"
SEGMENTS = 64


class Mesh:
    def __init__(self) -> None:
        self.vertices: list[tuple[float, float, float]] = []
        self.faces: list[tuple[int, int, int]] = []

    def add_vertex(self, p: tuple[float, float, float]) -> int:
        self.vertices.append(p)
        return len(self.vertices) - 1

    def add_triangle(self, a: int, b: int, c: int) -> None:
        self.faces.append((a, b, c))

    def add_frustum(self, z0: float, z1: float, r0: float, r1: float) -> None:
        lower = []
        upper = []
        for i in range(SEGMENTS):
            angle = 2 * math.pi * i / SEGMENTS
            lower.append(self.add_vertex((r0 * math.cos(angle), r0 * math.sin(angle), z0)))
            upper.append(self.add_vertex((r1 * math.cos(angle), r1 * math.sin(angle), z1)))

        bottom_center = self.add_vertex((0.0, 0.0, z0))
        top_center = self.add_vertex((0.0, 0.0, z1))
        for i in range(SEGMENTS):
            j = (i + 1) % SEGMENTS
            self.add_triangle(bottom_center, lower[j], lower[i])
            self.add_triangle(lower[i], lower[j], upper[j])
            self.add_triangle(lower[i], upper[j], upper[i])
            self.add_triangle(top_center, upper[i], upper[j])

    def add_box(self, sx: float, sy: float, z0: float, z1: float, angle_deg: float = 0.0) -> None:
        angle = math.radians(angle_deg)
        ca, sa = math.cos(angle), math.sin(angle)

        def rot(x: float, y: float, z: float) -> tuple[float, float, float]:
            return (x * ca - y * sa, x * sa + y * ca, z)

        raw = [
            (-sx / 2, -sy / 2, z0), (sx / 2, -sy / 2, z0),
            (sx / 2, sy / 2, z0), (-sx / 2, sy / 2, z0),
            (-sx / 2, -sy / 2, z1), (sx / 2, -sy / 2, z1),
            (sx / 2, sy / 2, z1), (-sx / 2, sy / 2, z1),
        ]
        v = [self.add_vertex(rot(*p)) for p in raw]
        quads = [
            (0, 3, 2, 1), (4, 5, 6, 7),
            (0, 1, 5, 4), (1, 2, 6, 5),
            (2, 3, 7, 6), (3, 0, 4, 7),
        ]
        for a, b, c, d in quads:
            self.add_triangle(v[a], v[b], v[c])
            self.add_triangle(v[a], v[c], v[d])

    def translated(self, dx: float, dy: float, dz: float = 0.0) -> "Mesh":
        result = Mesh()
        result.vertices = [(x + dx, y + dy, z + dz) for x, y, z in self.vertices]
        result.faces = list(self.faces)
        return result

    def extend(self, other: "Mesh") -> None:
        offset = len(self.vertices)
        self.vertices.extend(other.vertices)
        self.faces.extend((a + offset, b + offset, c + offset) for a, b, c in other.faces)

    def write_ascii_stl(self, path: Path, name: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="ascii", newline="\n") as f:
            f.write(f"solid {name}\n")
            for ia, ib, ic in self.faces:
                a, b, c = self.vertices[ia], self.vertices[ib], self.vertices[ic]
                ux, uy, uz = (b[i] - a[i] for i in range(3))
                vx, vy, vz = (c[i] - a[i] for i in range(3))
                nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
                length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
                nx, ny, nz = nx / length, ny / length, nz / length
                f.write(f"  facet normal {nx:.8g} {ny:.8g} {nz:.8g}\n")
                f.write("    outer loop\n")
                for p in (a, b, c):
                    f.write(f"      vertex {p[0]:.8g} {p[1]:.8g} {p[2]:.8g}\n")
                f.write("    endloop\n  endfacet\n")
            f.write(f"endsolid {name}\n")


def calibration_peg(diameter: float) -> Mesh:
    m = Mesh()
    # 1.2 mm nose taper makes insertion easier without changing the tested diameter.
    m.add_frustum(0.0, 1.2, max(1.8, diameter / 2 - 0.55), diameter / 2)
    m.add_frustum(1.2, 9.0, diameter / 2, diameter / 2)
    # Head size tracks stem size so loose pieces remain identifiable.
    head_diameter = 9.0 + (diameter - 5.8) * 5.0
    m.add_frustum(9.0, 10.2, diameter / 2, head_diameter / 2)
    m.add_frustum(10.2, 13.0, head_diameter / 2, head_diameter / 2)
    return m


def useful_peg(stem_diameter: float, end_style: str) -> Mesh:
    m = Mesh()
    # Mounting stem: 9 mm long, suitable for measuring actual insertion depth.
    m.add_frustum(0.0, 1.2, max(1.8, stem_diameter / 2 - 0.55), stem_diameter / 2)
    m.add_frustum(1.2, 9.0, stem_diameter / 2, stem_diameter / 2)

    # Rounded shoulder and collar spread the bending load at the board face.
    m.add_frustum(9.0, 11.0, stem_diameter / 2, 5.5)
    m.add_frustum(11.0, 13.2, 5.5, 5.5)
    m.add_frustum(13.2, 15.0, 5.5, 3.1)

    # 23 mm usable arm, short enough for an upright first print.
    m.add_frustum(15.0, 38.0, 3.1, 3.1)

    if end_style == "round":
        m.add_frustum(37.0, 39.0, 3.1, 6.2)
        m.add_frustum(39.0, 42.0, 6.2, 6.2)
        m.add_frustum(42.0, 43.0, 6.2, 5.3)
    elif end_style == "square":
        # Overlap the arm by 1 mm so slicers merge the volumes.
        m.add_box(12.0, 12.0, 37.0, 41.0, 0.0)
    elif end_style == "diamond":
        m.add_box(11.5, 11.5, 37.0, 41.0, 45.0)
    else:
        raise ValueError(end_style)
    return m


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    diameters = [5.80, 5.95, 6.10, 6.25, 6.40]

    plate = Mesh()
    for index, diameter in enumerate(diameters):
        peg = calibration_peg(diameter)
        peg.write_ascii_stl(OUT / f"calibration-{diameter:.2f}mm.stl", f"calibration_{diameter:.2f}mm")
        plate.extend(peg.translated((index - 2) * 18.0, 0.0))
    plate.write_ascii_stl(OUT / "calibration-all-five.stl", "calibration_all_five")

    # 6.10 mm is a conservative initial fit for a nominal 6.35 mm hole.
    # After the test, regenerate these with the winning diameter if needed.
    for style in ("round", "square", "diamond"):
        useful_peg(6.10, style).write_ascii_stl(
            OUT / f"peg-{style}-6.10mm.stl", f"peg_{style}_6_10mm"
        )

    print(f"Generated {len(list(OUT.glob('*.stl')))} STL files in {OUT}")


if __name__ == "__main__":
    main()
