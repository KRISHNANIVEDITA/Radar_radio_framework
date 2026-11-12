############################################################
# CORSIKA HTCondor submission
#
# This execution wrapper is taken/adapted
# from the FAERIE simulation framework.
#
# Reference:
# S. De Kockere et al.,
# "Simulation of radio signals from cosmic-ray cascades in
# air and ice as observed by in-ice Askaryan radio detectors,"
# Phys. Rev. D 110, 023010 (2024).
# DOI: 10.1103/PhysRevD.110.023010
#
# Modifications:
# Paths are supplied as HTCondor variables for integration
# into the combined-signal simulation workflow.
############################################################
#!/bin/bash

set -e

input_dir="$1"
output_dir="$2"

# Find SOFTWARE_HOME from modules/GEANT4/run_combine_antenna_traces.sh
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOFTWARE_HOME="${SOFTWARE_HOME:-$(cd "$script_dir/../.." && pwd)}"

combine_script="$SOFTWARE_HOME/modules/python_scripts/combine_antenna_traces.py"

mkdir -p "$output_dir"

python3 "$combine_script" "$input_dir" "$output_dir"