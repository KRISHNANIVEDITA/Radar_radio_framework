import os
from pathlib import Path

software_home = Path(
    "/user/knivedita/SOFTWARE"
).resolve()

os.environ["SOFTWARE_HOME"] = str(software_home)

from src.CORSIKA.prepare import prepare_corsika
from src.CORSIKA.submit import submit_corsika
print(f"SOFTWARE_HOME={software_home}")
event_id = "O2"
event = EventConfig(
    event_id=event_id,
    zenith_angles=[0],
    azimuth_angles=[0],
    energy_gev=10_000_00,
    seed=100,

    corsika_output_root=(
        software_home
        / "output_files"
        / "CORSIKA"
    ),

    in_ice_output_root=(
        software_home
        / "output_files"
        / "GEANT4"
    ),
    
    radar_output_root=(
        software_home
        / "output_files"
        / "RADAR"
    ),
    full_output_geant4_in = "/pnfs/iihe/radar/store/user/knivedita/RET/in_ice/job_in/",
    full_output_geant4_out = "/pnfs/iihe/radar/store/user/knivedita/RET/in_ice/job_out/",
    core_x_north_m=10,
    core_y_west_m=0,

    antenna_template=(
        software_home
        / "utilities"
        / "local"
        / "example.list"
    ),
    
)

event.save(Path(f"event_data/corsika_{event_id}.json"))

# CORSIKA EVENT RUNNING! CAREFUL CHECK THE CLUSTER IF THE JOB IS RUNNING - ONLY PROCEED AFTER IT FINISH.. :) OR ELSE? 

#prepare_corsika(event)
#submit_corsika(event)

from src.CORSIKA.into_ice import submit_into_ice
#submit_into_ice(event)
from src.GEANT4.create_dagfile import create_dag
create_dag(event)