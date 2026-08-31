"""Save representative HU-to-RSP values for the MCsquare calibration."""

from opentps.core.io.scannerReader import readScanner
from opentps.core.processing.doseCalculation.doseCalculationConfig import (
    DoseCalculationConfig,
)


ENERGY_MEV = 150.0
OUTPUT_FILE = "hu_rsp_150MeV.txt"

# Representative HU values spanning air, lung, soft tissue, and bone.
# Tissue labels are approximate; the RSP values come from the active calibration.
IMPORTANT_HU = [
    ("Air", -1024),
    ("Lung", -700),
    ("Adipose", -100),
    ("Calibration RSP=1 point", None),
    ("Water HU", 0),
    ("Soft tissue", 40),
    ("Trabecular bone", 300),
    ("Bone", 700),
    ("Dense bone", 1000),
    ("Very dense bone", 1500),
    ("High-HU material", 2000),
]


def main():
    calibration = readScanner(DoseCalculationConfig().scannerFolder)
    water_equivalent_hu = float(
        calibration.convertRSP2HU(1.0, energy=ENERGY_MEV)
    )

    lines = [
        "MCsquare HU-to-RSP relation",
        f"Scanner calibration: {DoseCalculationConfig().scannerFolder}",
        f"Proton energy: {ENERGY_MEV:g} MeV",
        "",
        f"{'Description':<28} {'HU':>10} {'RSP':>12}",
        f"{'-' * 28} {'-' * 10} {'-' * 12}",
    ]

    for description, hu in IMPORTANT_HU:
        hu_value = water_equivalent_hu if hu is None else float(hu)
        rsp = float(calibration.convertHU2RSP(hu_value, energy=ENERGY_MEV))
        lines.append(f"{description:<28} {hu_value:>10.3f} {rsp:>12.8f}")

    report = "\n".join(lines) + "\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as output:
        output.write(report)

    print(report, end="")
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
