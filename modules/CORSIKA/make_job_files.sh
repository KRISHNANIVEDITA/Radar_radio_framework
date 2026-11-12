#!/bin/bash

set -e

# Arguments from make_job_files.submit
input_file="$1"
output_dir="$2"
zenith="$3"
azimuth="$4"
corsika_log_file="$5"
log_name="$6"

# Find the main SOFTWARE directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOFTWARE_HOME="${SOFTWARE_HOME:-$(cd "$script_dir/../.." && pwd)}"

# Condor temporary directory
tmp_dir="${_CONDOR_SCRATCH_DIR:-$TMPDIR}"

echo "Event: $log_name"
echo "Temporary directory: $tmp_dir"

# Required programs
corsikaread_thin="$SOFTWARE_HOME/utilities/corsikaread_thin"

python_scripts="$SOFTWARE_HOME/modules/python_scripts"

make_geant4_script="$python_scripts/make_geant4_input_file_azimuth_rot.py"
split_energy_script="$python_scripts/split_on_energy_geant4_input_file.py"
split_jobs_script="$python_scripts/split_in_job_files_geant4_input_file.py"

# Maximum footprint radius in cm
upper_radius=100

source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh \
    LCG_104 \
    x86_64-el9-gcc13-opt

mkdir -p "$output_dir"

# Copy the CORSIKA particle file
cp "$input_file" "$tmp_dir/corsika_file"

# Run corsikaread_thin
printf "%-80s\n" "$tmp_dir/corsika_file" \
    > "$tmp_dir/corsikaread_input"

cd "$tmp_dir"

"$corsikaread_thin" \
    < "$tmp_dir/corsikaread_input" \
    > "$tmp_dir/corsikaread_output"

rm -f "$tmp_dir/corsika_file"
rm -f "$tmp_dir/corsikaread_input"
rm -f "$tmp_dir/corsikaread_output"

# Create the Geant4 input file
python3 "$make_geant4_script" \
    "$tmp_dir/fort.8" \
    "$tmp_dir" \
    0 \
    "$upper_radius" \
    "$zenith" \
    "$azimuth" \
    "$corsika_log_file"

rm -f "$tmp_dir/fort.8"

# Split by energy
mkdir -p "$tmp_dir/energy_splitted/"

python3 "$split_energy_script" \
    "$tmp_dir/geant4_input_file.txt" \
    "$tmp_dir/energy_splitted/"

rm -f "$tmp_dir/geant4_input_file.txt"

# Create the individual Geant4 job-input files
mkdir -p "$tmp_dir/jobs_input/"

python3 "$split_jobs_script" \
    "$tmp_dir/energy_splitted/" \
    "$tmp_dir/jobs_input/"

rm -rf "$tmp_dir/energy_splitted/"

# Copy results
cp -f "$tmp_dir/jobs_input/"* "$output_dir/"

rm -rf "$tmp_dir/jobs_input/"

echo "Geant4 job-input files created successfully."
echo "Output directory: $output_dir"