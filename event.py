from dataclasses import dataclass, asdict
from itertools import product
from pathlib import Path
import json
import math


@dataclass
class EventConfig:
    event_id: str
    zenith_angles: list[float]
    azimuth_angles: list[float]
    energy_gev: float
    seed: int

    corsika_output_root: Path
    in_ice_output_root: Path
    radar_output_root: Path

    core_x_north_m: float
    core_y_west_m: float
    antenna_template: Path

    @property
    def energy_exponent_ev(self) -> float:
        return math.log10(self.energy_gev) + 9

    def simulation_names(self) -> list[str]:
        energy_exp = self.energy_exponent_ev

        return [
            (
                f"{self.event_id}"
                f"e{energy_exp:.1f}"
                f"z{zenith:g}"
                f"a{azimuth:g}"
            )
            for zenith, azimuth in product(
                self.zenith_angles,
                self.azimuth_angles,
            )
        ]