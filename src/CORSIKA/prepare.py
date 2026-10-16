#!/usr/bin/env python3
"""Prepare CORSIKA/CoREAS input files without running CORSIKA.

Expected project layout when this file is stored as ``src/CORSIKA/prepare.py``::

    SOFTWARE/
    ├── src/CORSIKA/prepare.py
    ├── utilities/local/RUN000001.inp
    ├── utilities/local/SIM000001.reas
    ├── utilities/local/example.list
    └── output_files/make_corsika/
    
Give an event_id "O1", zenith_angle/s, azimuth_angle/s, energy, seed, /path/to/store/corsikaoutputs/, showercore_X[North], showercore_Y[West]: 
Example:
    python prepare.py O1 "0,10" "0,90" 10000000 100 \
        /pnfs/iihe/radar/store/user/knivedita/RET/airshowers 10 0
"""

from __future__ import annotations

import argparse
import math
import re
import shutil
from pathlib import Path


def parse_number_list(value: str, name: str) -> list[str]:
    """Convert a comma-separated argument into validated numeric strings."""
    values = [item.strip() for item in value.split(",") if item.strip()]
    if not values:
        raise ValueError(f"{name} must contain at least one value")

    for item in values:
        try:
            float(item)
        except ValueError as exc:
            raise ValueError(f"invalid {name} value: {item!r}") from exc

    return values


def replace_single_card(lines: list[str], card: str, value: str) -> None:
    """Replace one CORSIKA steering card and require exactly one match."""
    pattern = re.compile(rf"^\s*{re.escape(card)}\s+")
    matches = [index for index, line in enumerate(lines) if pattern.match(line)]

    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one {card} line in RUN template; "
            f"found {len(matches)}"
        )

    lines[matches[0]] = f"{card} {value}"


def update_run_file(
    run_file: Path,
    run_number: int,
    energy_text: str,
    zenith: str,
    azimuth: str,
    base_seed: int,
) -> None:
    """Update the event parameters and three random-number seeds."""
    lines = run_file.read_text(encoding="utf-8").splitlines()

    replace_single_card(lines, "RUNNR", str(run_number))
    replace_single_card(lines, "ERANGE", f"{energy_text} {energy_text}")
    replace_single_card(lines, "MAGNET", "8.46 54.14")
    replace_single_card(lines, "THETAP", f"{zenith} {zenith}")
    replace_single_card(lines, "PHIP", f"{azimuth} {azimuth}")

    seed_pattern = re.compile(r"^\s*SEED\s+")
    seed_indices = [
        index for index, line in enumerate(lines) if seed_pattern.match(line)
    ]

    if len(seed_indices) != 3:
        raise ValueError(
            f"expected exactly three SEED lines in {run_file}; "
            f"found {len(seed_indices)}"
        )

    for offset, line_index in enumerate(seed_indices):
        lines[line_index] = f"SEED {base_seed + offset} 0 0"

    run_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_antenna_file(
    template_file: Path,
    output_file: Path,
    core_x_m: float,
    core_y_m: float,
) -> None:
    """Shift every antenna so that the shower core becomes the new origin."""
    core_x_cm = core_x_m * 100.0
    core_y_cm = core_y_m * 100.0
    output_lines: list[str] = []
    antenna_count = 0

    for line_number, line in enumerate(
        template_file.read_text(encoding="utf-8").splitlines(), start=1
    ):
        parts = line.split()

        if len(parts) >= 6 and parts[0] == "AntennaPosition" and parts[1] == "=":
            try:
                antenna_x_cm = float(parts[2])
                antenna_y_cm = float(parts[3])
            except ValueError as exc:
                raise ValueError(
                    f"invalid antenna coordinates on line {line_number} "
                    f"of {template_file}"
                ) from exc

            shifted_x_cm = antenna_x_cm - core_x_cm
            shifted_y_cm = antenna_y_cm - core_y_cm
            z_value = parts[4]
            antenna_label = " ".join(parts[5:])

            output_lines.append(
                "AntennaPosition = "
                f"{shifted_x_cm:.1f} {shifted_y_cm:.1f} "
                f"{z_value} {antenna_label}"
            )
            antenna_count += 1
        else:
            # Preserve comments, blank lines, and other configuration lines.
            output_lines.append(line)

    if antenna_count == 0:
        raise ValueError(f"no AntennaPosition lines found in {template_file}")

    output_file.write_text("\n".join(output_lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create CORSIKA, CoREAS, and shifted antenna input files. "
            "This command does not run CORSIKA."
        )
    )
    parser.add_argument("event_id", help="Event prefix, for example c6")
    parser.add_argument(
        "zeniths", help='Comma-separated zenith angles, for example "0,10"'
    )
    parser.add_argument(
        "azimuths", help='Comma-separated azimuth angles, for example "0,90"'
    )
    parser.add_argument("energy_gev", help="Primary energy in GeV")
    parser.add_argument("seed", type=int, help="Base seed for the three SEED lines")
    parser.add_argument("storage_dir", type=Path, help="External output directory")
    parser.add_argument("core_x_m", type=float, help="Shower-core X in metres")
    parser.add_argument("core_y_m", type=float, help="Shower-core Y in metres")
    parser.add_argument(
        "--software-home",
        type=Path,
        help=(
            "Override the software root. Normally inferred from "
            "src/CORSIKA/prepare.py."
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    zeniths = parse_number_list(args.zeniths, "zenith")
    azimuths = parse_number_list(args.azimuths, "azimuth")

    try:
        energy_gev = float(args.energy_gev)
    except ValueError as exc:
        raise ValueError(f"invalid energy: {args.energy_gev!r}") from exc

    if energy_gev <= 0:
        raise ValueError("energy must be greater than zero")

    if args.software_home is None:
        # prepare.py is expected at SOFTWARE/src/CORSIKA/prepare.py.
        software_home = Path(__file__).resolve().parents[2]
    else:
        software_home = args.software_home.expanduser().resolve()

    make_corsika_dir = software_home / "output_files" / "make_corsika"
    template_dir = software_home / "utilities" / "local"
    run_template = template_dir / "RUN000001.inp"
    reas_template = template_dir / "SIM000001.reas"
    antenna_template = template_dir / "example.list"
    storage_dir = args.storage_dir.expanduser().resolve()

    for required_file in (run_template, reas_template, antenna_template):
        if not required_file.is_file():
            raise FileNotFoundError(f"required template not found: {required_file}")

    make_corsika_dir.mkdir(parents=True, exist_ok=True)
    storage_dir.mkdir(parents=True, exist_ok=True)

    energy_exponent = math.log10(energy_gev) + 9.0
    energy_label = f"{energy_exponent:.1f}"

    print("--------------------------------")
    print(f"Event ID         : {args.event_id}")
    print(f"Zenith angles    : {' '.join(zeniths)}")
    print(f"Azimuth angles   : {' '.join(azimuths)}")
    print(f"Energy           : {args.energy_gev} GeV")
    print(f"Energy exponent  : {energy_label}")
    print(f"Seeds            : {args.seed}, {args.seed + 1}, {args.seed + 2}")
    print(f"Core position    : ({args.core_x_m}, {args.core_y_m}) m")
    print(f"Template folder  : {template_dir}")
    print(f"Local folder     : {make_corsika_dir}")
    print(f"Storage folder   : {storage_dir}")
    print("--------------------------------")

    run_number = 1

    for zenith in zeniths:
        for azimuth in azimuths:
            simulation_name = (
                f"{args.event_id}e{energy_label}z{zenith}a{azimuth}"
            )
            local_dir = make_corsika_dir / simulation_name
            store_dir = storage_dir / simulation_name

            local_dir.mkdir(parents=True, exist_ok=True)
            store_dir.mkdir(parents=True, exist_ok=True)

            run_tag = f"{run_number:06d}"
            run_file = local_dir / f"RUN{run_tag}.inp"
            reas_file = local_dir / f"SIM{run_tag}.reas"
            antenna_file = local_dir / "antenna.list"

            shutil.copy2(run_template, run_file)
            shutil.copy2(reas_template, reas_file)

            update_run_file(
                run_file=run_file,
                run_number=run_number,
                energy_text=args.energy_gev,
                zenith=zenith,
                azimuth=azimuth,
                base_seed=args.seed,
            )
            create_antenna_file(
                template_file=antenna_template,
                output_file=antenna_file,
                core_x_m=args.core_x_m,
                core_y_m=args.core_y_m,
            )

            print(f"Prepared simulation : {simulation_name}")
            print(f"RUN input          : {run_file}")
            print(f"REAS input         : {reas_file}")
            print(f"Antenna list       : {antenna_file}")
            print(f"Storage directory  : {store_dir}")
            print()

            run_number += 1

    print("All CORSIKA input files created successfully.")
    print("CORSIKA has not been executed.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(f"Error: {error}") from error
