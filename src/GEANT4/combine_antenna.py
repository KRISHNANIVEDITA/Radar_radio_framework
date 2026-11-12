"""Submit Geant4 antenna-trace combination jobs for a configured event."""

import os
import shutil
import subprocess
from pathlib import Path


def submit_combine_antenna_traces(event, software_home=None):
    """Submit one antenna-combination job for every simulation."""
    if software_home is None:
        software_home = Path(__file__).resolve().parents[2]
    else:
        software_home = Path(software_home).expanduser().resolve()

    module_dir = software_home / "modules" / "GEANT4"
    submit_file = module_dir / "run_combine_antenna_traces.submit"
    run_script = module_dir / "run_combine_antenna_traces.sh"

    condor_submit = shutil.which("condor_submit")

    output_root = Path(event.full_output_geant4_out)
    error_dir = software_home / "output_files" / "GEANT4" / "error_files"
    error_dir.mkdir(parents=True, exist_ok=True)

    environment = os.environ.copy()
    environment["SOFTWARE_HOME"] = str(software_home)

    for simulation_name in event.simulation_names():
        simulation_dir = output_root / simulation_name

        if not simulation_dir.is_dir():
            raise FileNotFoundError(simulation_dir)

        command = [
            condor_submit,
            str(submit_file),
            "RUN_COMBINE_SH={}".format(run_script),
            "ERROR_DIR={}".format(error_dir),
            "INPUT_DIR={}/".format(simulation_dir),
            "OUTPUT_DIR={}/".format(simulation_dir),
            "LOG_NAME={}".format(simulation_name),
        ]

        subprocess.run(command, check=True, env=environment)
        print("Submitted antenna combination: {}".format(simulation_name))
