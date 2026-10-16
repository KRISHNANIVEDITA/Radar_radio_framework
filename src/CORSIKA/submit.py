#!/usr/bin/env python3
"""Submit one prepared CORSIKA event to HTCondor.

This command is intentionally separate from ``prepare.py``. CORSIKA is
submitted only when the user explicitly runs this file.
!! Remember to change path to CORSIKA in the module/run_corsika.sh
Expected project layout when stored as ``src/CORSIKA/submit.py``::

    SOFTWARE/
    ├── src/CORSIKA/submit.py
    ├── modules/CORSIKA/run_corsika.sh
    ├── modules/CORSIKA/run_corsika.submit
    ├── utilities/atm_summer.dat
    └── output_files/
        ├── make_corsika/<SIMULATION_NAME>/
        └── CORSIKA/error_files/

Example:
    python submit.py c6e18.0z0a0 000001 \
        /pnfs/iihe/radar/store/user/knivedita/RET/airshowers
"""

from __future__ import annotations
import argparse
import os
import shlex
import shutil
import subprocess
from pathlib import Path


def normalize_run_number(value: str) -> str:
    """Return a CORSIKA run number as a six-digit string."""
    try:
        run_number = int(value)
    except ValueError as exc:
        raise ValueError(f"invalid run number: {value!r}") from exc

    if not 1 <= run_number <= 999999:
        raise ValueError("run number must be between 1 and 999999")

    return f"{run_number:06d}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Submit one prepared CORSIKA event to HTCondor."
    )
    parser.add_argument(
        "simulation_name",
        help="Prepared simulation directory, for example c6e18.0z0a0",
    )
    parser.add_argument(
        "run_number",
        help="CORSIKA run number, for example 1 or 000001",
    )
    parser.add_argument(
        "storage_root",
        type=Path,
        help="Root directory in which the simulation output will be stored",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print and validate the command without submitting it",
    )
    parser.add_argument(
        "--software-home",
        type=Path,
        help=(
            "Override the software root. Normally inferred from "
            "src/CORSIKA/submit.py."
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run_tag = normalize_run_number(args.run_number)

    if args.software_home is None:
        # submit.py is expected at SOFTWARE/src/CORSIKA/submit.py.
        software_home = Path(__file__).resolve().parents[2]
    else:
        software_home = args.software_home.expanduser().resolve()

    corsika_module_dir = software_home / "modules" / "CORSIKA"
    submit_file = corsika_module_dir / "run_corsika.submit"
    run_corsika_script = corsika_module_dir / "run_corsika.sh"

    event_dir = (
        software_home
        / "output_files"
        / "make_corsika"
        / args.simulation_name
    )
    input_file = event_dir / f"RUN{run_tag}.inp"
    reas_file = event_dir / f"SIM{run_tag}.reas"
    antenna_file = event_dir / "antenna.list"
    atmosphere_file = software_home / "utilities" / "atm_summer.dat"

    error_dir = software_home / "output_files" / "CORSIKA" / "error_files"
    storage_root = args.storage_root.expanduser().resolve()
    output_dir = storage_root / args.simulation_name

    required_files = (
        submit_file,
        run_corsika_script,
        input_file,
        reas_file,
        antenna_file,
        atmosphere_file,
    )
    missing_files = [path for path in required_files if not path.is_file()]
    if missing_files:
        missing_text = "\n".join(f"  - {path}" for path in missing_files)
        raise FileNotFoundError(f"required files not found:\n{missing_text}")

    if not os.access(run_corsika_script, os.X_OK):
        raise PermissionError(
            f"runner is not executable: {run_corsika_script}\n"
            f"Run: chmod +x {shlex.quote(str(run_corsika_script))}"
        )

    error_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    condor_submit = shutil.which("condor_submit")
    if condor_submit is None:
        if args.dry_run:
            condor_submit = "condor_submit"
        else:
            raise FileNotFoundError("condor_submit was not found in PATH")

    command = [
        condor_submit,
        str(submit_file),
        f"RUN_CORSIKA_SH={run_corsika_script}",
        f"ERROR_DIR={error_dir}",
        f"INPUT_FILE={input_file}",
        f"RUN_NR={run_tag}",
        f"ATMOS_FILE={atmosphere_file}",
        f"REAS_FILE={reas_file}",
        f"LIST_FILE={antenna_file}",
        f"OUTPUT_DIR={output_dir}/",
        f"LOG_NAME={args.simulation_name}",
    ]

    print("--------------------------------")
    print("CORSIKA submission")
    print(f"Simulation       : {args.simulation_name}")
    print(f"RUN number       : {run_tag}")
    print(f"Input file       : {input_file}")
    print(f"REAS file        : {reas_file}")
    print(f"Antenna list     : {antenna_file}")
    print(f"Atmosphere file  : {atmosphere_file}")
    print(f"Output directory : {output_dir}")
    print(f"Error directory  : {error_dir}")
    print("--------------------------------")
    print(shlex.join(command))

    if args.dry_run:
        print("Nothing was submitted.")
        return

    subprocess.run(command, check=True)
    print(f"Submitted CORSIKA simulation: {args.simulation_name}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Error: {error}") from error
