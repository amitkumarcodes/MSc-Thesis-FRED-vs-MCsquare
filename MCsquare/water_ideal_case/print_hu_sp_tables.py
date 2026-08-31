"""Save MCsquare SP and RSP tables for selected HU values."""

from opentps.core.io.scannerReader import readScanner
from opentps.core.processing.doseCalculation.doseCalculationConfig import (
    DoseCalculationConfig,
)


HU_VALUES = [-1024.0, -700.0, -100.0, -43.038, 0.0, 40.0,
             300.0, 700.0, 1000.0, 1500.0, 2000.0]
ENERGIES_MEV = [100.0, 150.0, 200.0]


def main():
    calibration = readScanner(DoseCalculationConfig().scannerFolder)

    # File 1: stopping power at 150 MeV
    sp_150_lines = [
        "MCsquare HU-to-SP",
        "Proton energy: 150 MeV",
        "",
        f"{'HU':>10} {'SP':>14}",
        f"{'-' * 10} {'-' * 14}",
    ]
    for hu in HU_VALUES:
        sp = float(calibration.convertHU2SP(hu, energy=150.0))
        sp_150_lines.append(f"{hu:10.3f} {sp:14.8f}")

    with open("hu_sp_150MeV.txt", "w", encoding="utf-8") as output:
        output.write("\n".join(sp_150_lines) + "\n")

    # File 2: RSP and stopping power at 100, 150, and 200 MeV
    headers = ["HU"]
    for energy in ENERGIES_MEV:
        headers.extend([f"RSP_{energy:g}MeV", f"SP_{energy:g}MeV"])

    comparison_lines = [
        "MCsquare HU-to-RSP and HU-to-SP",
        "Proton energies: 100, 150, and 200 MeV",
        "",
        " ".join(f"{header:>14}" for header in headers),
        " ".join("-" * 14 for _ in headers),
    ]

    for hu in HU_VALUES:
        values = [f"{hu:14.3f}"]
        for energy in ENERGIES_MEV:
            rsp = float(calibration.convertHU2RSP(hu, energy=energy))
            sp = float(calibration.convertHU2SP(hu, energy=energy))
            values.extend([f"{rsp:14.8f}", f"{sp:14.8f}"])
        comparison_lines.append(" ".join(values))

    with open("hu_rsp_sp_100_150_200MeV.txt", "w", encoding="utf-8") as output:
        output.write("\n".join(comparison_lines) + "\n")

    print("\n".join(sp_150_lines))
    print("\nSaved: hu_sp_150MeV.txt")
    print("Saved: hu_rsp_sp_100_150_200MeV.txt")


if __name__ == "__main__":
    main()
