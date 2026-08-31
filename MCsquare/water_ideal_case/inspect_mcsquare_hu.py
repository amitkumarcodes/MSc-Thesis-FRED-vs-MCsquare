"""Explain MCsquare's density, material, SP, and RSP for one HU value."""

import argparse
from bisect import bisect_right

from opentps.core.io.scannerReader import readScanner
from opentps.core.processing.doseCalculation.doseCalculationConfig import (
    DoseCalculationConfig,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hu", type=float, default=0.0)
    parser.add_argument("--energy", type=float, default=150.0)
    return parser.parse_args()


def main():
    args = parse_args()
    calibration = readScanner(DoseCalculationConfig().scannerFolder)

    hu_boundaries, materials = calibration.getHU2MaterialConversion()
    material_index = bisect_right(hu_boundaries, args.hu) - 1
    material_index = max(0, min(material_index, len(materials) - 1))
    material = materials[material_index]

    density = float(calibration.convertHU2MassDensity(args.hu))
    material_sp = float(calibration.convertHU2SP(args.hu, energy=args.energy))
    water_sp = float(calibration.waterSP(energy=args.energy))
    rsp = float(calibration.convertHU2RSP(args.hu, energy=args.energy))
    reconstructed_rsp = density * material_sp / water_sp

    print("MCsquare HU calibration details")
    print(f"HU:                         {args.hu:g}")
    print(f"Proton energy:              {args.energy:g} MeV")
    print(f"Assigned material:          {material.name}")
    print(f"MCsquare material ID:       {material.number}")
    print(f"HU-calibrated density:      {density:.8f} g/cm^3")
    print(f"Material reference density: {material.density:.8f} g/cm^3")
    print(f"Assigned-material SP:       {material_sp:.8f}")
    print(f"MCsquare water SP:          {water_sp:.8f}")
    print(f"SP ratio:                   {material_sp / water_sp:.8f}")
    print(f"RSP from MCsquare:          {rsp:.8f}")
    print()
    print("Check:")
    print(
        f"RSP = density x material_SP / water_SP\n"
        f"    = {density:.8f} x {material_sp:.8f} / {water_sp:.8f}\n"
        f"    = {reconstructed_rsp:.8f}"
    )


if __name__ == "__main__":
    main()
