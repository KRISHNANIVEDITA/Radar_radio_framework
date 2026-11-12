#!/usr/bin/env python3
"""Submit the CORSIKA simulations described by an EventConfig object."""

from itertools import product
import os
import shutil
import subprocess
from pathlib import Path


def submit_corsika(event, software_home=None):
    """Submit every prepared zenith–azimuth combination to HTCondor."""
    if software_home is None:
        software_home = Path(__file__).resolve().parents[2]

    module_dir = software_home / "modules" / "CORSIKA"
    submit_file = module_dir / "run_corsika.submit"
    run_script = module_dir / "run_corsika.sh"
    atmosphere_file = software_home / "utilities" / "atm_summer.dat"

    output_root = Path(event.corsika_output_root)
    error_dir = output_root / "error_files"
    error_dir.mkdir(parents=True, exist_ok=True)

    for required_file in (submit_file, run_script, atmosphere_file):
        if not required_file.is_file():
            raise FileNotFoundError(required_file)

    if not os.access(run_script, os.X_OK):
        raise PermissionError(f"not executable: {run_script}")

    condor_submit = shutil.which("condor_submit")
    if condor_submit is None:
        raise FileNotFoundError("condor_submit was not found in PATH")

    environment = os.environ.copy()
    environment["SOFTWARE_HOME"] = str(software_home)

    geometries = product(event.zenith_angles, event.azimuth_angles)

    for run_number, simulation_name in enumerate(event.simulation_names(),start=1):
        simulation_dir = output_root / simulation_name
        run_tag = f"{run_number:06d}"

        run_file = simulation_dir / f"RUN{run_tag}.inp"
        reas_file = simulation_dir / f"SIM{run_tag}.reas"
        antenna_file = simulation_dir / "antenna.list"

        for required_file in (run_file, reas_file, antenna_file):
            if not required_file.is_file():
                raise FileNotFoundError(required_file)

        command = [
            condor_submit,
            str(submit_file),
            f"RUN_CORSIKA_SH={run_script}",
            f"ERROR_DIR={error_dir}",
            f"INPUT_FILE={run_file}",
            f"RUN_NR={run_tag}",
            f"ATMOS_FILE={atmosphere_file}",
            f"REAS_FILE={reas_file}",
            f"LIST_FILE={antenna_file}",
            f"OUTPUT_DIR={simulation_dir}/",
            f"LOG_NAME={simulation_name}",
        ]

        subprocess.run(command, check=True, env=environment)
        print(f"Submitted {simulation_name}")