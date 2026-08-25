#!/usr/bin/env python3
"""Replace rho and RSP columns in a FRED material.inp with MCsquare values."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from opentps.core.io.scannerReader import readScanner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("scanner", type=Path)
    parser.add_argument("--energy", type=float, default=100.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    calibration = readScanner(str(args.scanner))
    lines = args.input.read_text().splitlines()

    material_rows: list[tuple[int, list[str]]] = []
    for line_number, line in enumerate(lines):
        fields = line.split()
        if fields and fields[0] == "mat:":
            if len(fields) != 18:
                raise ValueError(
                    f"Line {line_number + 1}: expected 18 fields, got {len(fields)}"
                )
            material_rows.append((line_number, fields))

    if not material_rows:
        raise ValueError("No 'mat:' rows found")

    hu = np.asarray([float(fields[1]) for _, fields in material_rows])
    density = np.asarray(calibration.convertHU2MassDensity(hu), dtype=float)
    rsp = np.asarray(calibration.convertHU2RSP(hu, energy=args.energy), dtype=float)

    for (line_number, fields), rho_value, rsp_value in zip(
        material_rows, density, rsp
    ):
        fields[2] = f"{rho_value:.9g}"
        fields[3] = f"{rsp_value:.9g}"
        lines[line_number] = " ".join(fields)

    args.output.write_text("\n".join(lines) + "\n")
    print(f"Wrote {len(material_rows)} calibrated rows to {args.output}")
    print(f"Energy: {args.energy:g} MeV")


if __name__ == "__main__":
    main()
