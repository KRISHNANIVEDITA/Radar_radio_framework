from pathlib import Path
import numpy as np


def create_dag(event):
    """
    Create HTCondor DAG files for GEANT4 jobs.
    One DAG file per simulation.
    """

    software_home = Path(__file__).resolve().parents[2]

    dag_output_dir = software_home / "output_files" / "GEANT4"
    dag_output_dir.mkdir(parents=True, exist_ok=True)

    submit_file = software_home / "modules" / "GEANT4" / "run_new.submit"
    executable = software_home / "modules" / "GEANT4" / "run_new.sh"
    simulations = zip(
        zip(event.zenith_angles, event.azimuth_angles),
        event.simulation_names()
    )

    rng = np.random.default_rng(event.seed)
    dag_files = []

    for (zenith, azimuth), simulation_name in simulations:

        input_dir = Path(event.full_output_geant4_in) / simulation_name
        output_dir = Path(event.full_output_geant4_out) / simulation_name

        output_dir.mkdir(parents=True, exist_ok=True)

        dag_file = dag_output_dir / f"{simulation_name}.dag"

        input_files = sorted(input_dir.glob("geant4*.txt"))

        corsika_dir = Path(event.corsika_output_root) / simulation_name

        reas_file = corsika_dir / f"SIM000001.reas"
        list_file = corsika_dir / f"SIM000001.list"
        atmos_file = software_home / "utilities" / "atm_summer.dat"

        
        error_dir = output_dir / "err"
        error_dir.mkdir(parents=True, exist_ok=True)

        print(f"GEANT4 input directory: {input_dir}")

        with open(dag_file, "w") as dag:

            for i, input_file in enumerate(input_files):

                output_file = input_file.stem
                rand_int = rng.integers(0, 215)

                dag.write(f"JOB job_{i} {submit_file}\n")

                dag.write(
                    f'VARS job_{i} '
                    f'INPUT_FILE="{input_file}" '
                    f'OUTPUT_FILE="{output_dir / output_file}" '
                    f'RAND_INT="{rand_int}" '
                    f'ZENITH_ANGLE="{zenith}" '
                    f'AZIMUTH_ANGLE="{azimuth}" '
                    f'REAS_FILE="{reas_file}" '
                    f'LIST_FILE="{list_file}" '
                    f'ATMOS_FILE="{atmos_file}" '
                    f'ERROR_DIR="{error_dir.resolve()}" '
                    f'RUN_NEW_SH="{executable.resolve()}"\n'
                    
                )

        dag_files.append(dag_file)
        print(f"GEANT4 DAG created: {dag_file}")

    return dag_files