"""Submit CORSIKA outputs for Geant4 input-file generation."""

from itertools import product
import os
import shutil
import subprocess
from pathlib import Path


def submit_into_ice(event, software_home=None):
    """Submit one conversion job for every simulation in an EventConfig."""
    if software_home is None:
        software_home = Path(__file__).resolve().parents[2]
    else:
        software_home = Path(software_home).expanduser().resolve()

    module_dir = software_home / "modules" / "CORSIKA"
    submit_file = module_dir / "make_job_files.submit"
    runner = module_dir / "make_job_files.sh"
    corsikaread = software_home / "utilities" / "corsikaread_thin"
    script_dir = software_home / "modules" / "python_scripts"

    required_files = [
        submit_file,
        runner,
        corsikaread,
        script_dir / "make_geant4_input_file_azimuth_rot.py",
        script_dir / "split_on_energy_geant4_input_file.py",
        script_dir / "split_in_job_files_geant4_input_file.py",
    ]

    missing = [path for path in required_files if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing files:\n" + "\n".join(map(str, missing)))

    for executable in (runner, corsikaread):
        if not os.access(executable, os.X_OK):
            raise PermissionError("File is not executable: {}".format(executable))

    condor_submit = shutil.which("condor_submit")
    if condor_submit is None:
        raise FileNotFoundError("condor_submit was not found in PATH")

    error_dir = Path(event.in_ice_output_root) / "error_files"
    error_dir.mkdir(parents=True, exist_ok=True)

    angles = product(event.zenith_angles, event.azimuth_angles)
    simulations = zip(angles, event.simulation_names())

    environment = os.environ.copy()
    environment["SOFTWARE_HOME"] = str(software_home)

    for run_number, ((zenith, azimuth), simulation_name) in enumerate(
        simulations, start=1
    ):
        run_tag = "{:06d}".format(run_number)
        corsika_dir = Path(event.corsika_output_root) / simulation_name
        input_file = corsika_dir / "DAT{}".format(run_tag)
        log_file = corsika_dir / "RUN{}.log".format(run_tag)
        output_dir = Path(event.full_output_geant4_in) / simulation_name

        if not input_file.is_file():
            raise FileNotFoundError("CORSIKA output not found: {}".format(input_file))
        if not log_file.is_file():
            raise FileNotFoundError("CORSIKA log not found: {}".format(log_file))

        output_dir.mkdir(parents=True, exist_ok=True)

        command = [
            condor_submit,
            str(submit_file),
            "MAKE_JOB_FILES_SH={}".format(runner),
            "ERROR_DIR={}".format(error_dir),
            "INPUT_FILE={}".format(input_file),
            "OUTPUT_DIR={}/".format(output_dir),
            "ZENITH={:g}".format(float(zenith)),
            "AZIMUTH={:g}".format(float(azimuth)),
            "CORSIKA_LOG_FILE={}".format(log_file),
            "LOG_NAME={}".format(simulation_name),
        ]

        subprocess.run(command, check=True, env=environment)
        print("Submitted into-ice input generation: {}".format(simulation_name))