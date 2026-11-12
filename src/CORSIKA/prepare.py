#!/usr/bin/env python3
"""Create CORSIKA/CoREAS inputs from an EventConfig object."""

from itertools import product
import math
import re
import shutil
from pathlib import Path


def replace_card(text: str, card: str, value: str) -> str:
    """Replace one CORSIKA steering card."""
    pattern = rf"(?m)^\s*{re.escape(card)}\s+.*$"
    updated, count = re.subn(pattern, f"{card} {value}", text)

    if count != 1:
        raise ValueError(f"expected one {card} line; found {count}")

    return updated


def update_run_file(
    run_file: Path,
    run_number: int,
    energy: str,
    zenith: str,
    azimuth: str,
    seed: int,
) -> None:
    """Insert the event parameters into a copied RUN template."""
    text = run_file.read_text()

    cards = {
        "RUNNR": str(run_number),
        "ERANGE": f"{energy} {energy}",
        "MAGNET": "8.46 54.14",
        "THETAP": f"{zenith} {zenith}",
        "PHIP": f"{azimuth} {azimuth}",
    }

    for card, value in cards.items():
        text = replace_card(text, card, value)

    seed_index = 0

    def replace_seed(_: re.Match[str]) -> str:
        nonlocal seed_index
        new_line = f"SEED {seed + seed_index} 0 0"
        seed_index += 1
        return new_line

    text, seed_count = re.subn(
        r"(?m)^\s*SEED\s+.*$",
        replace_seed,
        text,
    )

    if seed_count != 3:
        raise ValueError(f"expected three SEED lines; found {seed_count}")

    run_file.write_text(text)


def create_antenna_file(
    template: Path,
    output: Path,
    core_x_m: float,
    core_y_m: float,
) -> None:
    """Shift antenna coordinates so the shower core is the origin."""
    shifted_lines = []
    antenna_count = 0

    for line in template.read_text().splitlines():
        parts = line.split()

        if parts[:2] != ["AntennaPosition", "="]:
            shifted_lines.append(line)
            continue

        if len(parts) < 6:
            raise ValueError(f"invalid antenna line: {line}")

        x_cm = float(parts[2]) - core_x_m * 100
        y_cm = float(parts[3]) - core_y_m * 100

        shifted_lines.append(
            f"AntennaPosition = {x_cm:.1f} {y_cm:.1f} "
            f"{parts[4]} {' '.join(parts[5:])}"
        )
        antenna_count += 1

    if antenna_count == 0:
        raise ValueError(f"no antennas found in {template}")

    output.write_text("\n".join(shifted_lines) + "\n")

def prepare_corsika(event, software_home=None):
    """Prepare every zenith–azimuth combination in an EventConfig."""
    if software_home is None:
        software_home = Path(__file__).resolve().parents[2]

    template_dir = software_home / "utilities" / "local"
    run_template = template_dir / "RUN000001.inp"
    reas_template = template_dir / "SIM000001.reas"

    antenna_template = Path(event.antenna_template)
    if not antenna_template.is_absolute():
        antenna_template = software_home / antenna_template

    for required_file in (run_template, reas_template, antenna_template):
        if not required_file.is_file():
            raise FileNotFoundError(required_file)

    output_root = Path(event.corsika_output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    energy = f"{event.energy_gev:g}"
    energy_label = f"{math.log10(event.energy_gev) + 9:.1f}"
    geometries = product(event.zenith_angles, event.azimuth_angles)

    for run_number, (zenith, azimuth) in enumerate(geometries, start=1):
        zenith_text = f"{float(zenith):g}"
        azimuth_text = f"{float(azimuth):g}"

        if hasattr(event, "simulation_name"):
            simulation_name = event.simulation_name(zenith, azimuth)
        else:
            simulation_name = (
                f"{event.event_id}e{energy_label}"
                f"z{zenith_text}a{azimuth_text}"
            )

        simulation_dir = output_root / simulation_name
        simulation_dir.mkdir(parents=True, exist_ok=True)

        run_tag = f"{run_number:06d}"
        run_file = simulation_dir / f"RUN{run_tag}.inp"
        reas_file = simulation_dir / f"SIM{run_tag}.reas"
        antenna_file = simulation_dir / "antenna.list"

        shutil.copy2(run_template, run_file)
        shutil.copy2(reas_template, reas_file)

        update_run_file(
            run_file,
            run_number,
            energy,
            zenith_text,
            azimuth_text,
            event.seed,
        )

        create_antenna_file(
            antenna_template,
            antenna_file,
            event.core_x_north_m,
            event.core_y_west_m,
        )
