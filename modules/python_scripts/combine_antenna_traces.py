# This script combines the separate txt traces files created by the different cluster jobs into one txt traces file.
# This version is made to work with the different antenna trace output files (direct, indirect, and SA radiation. 
# It will make a combined file for each type of radiation, as well as a combined file combining the direct and indirect emission.

import sys
import glob
import numpy as np

if len(sys.argv) != 3:
    sys.exit("This script expects two arguments: the input directory with the txt trace files and the output directory to store the combined traces.")
else:
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
print(">>> Python job started successfully", file=sys.stderr)
# Getting the input files
input_files_dir = glob.glob(f"{input_dir}/geant4*_dir.txt")
input_files_indir = glob.glob(f"{input_dir}/geant4*_indir.txt")
#input_files_SA = glob.glob(f"{input_dir}/geant4*_SA.txt")
input_files_tot = input_files_dir + input_files_indir

# Read first comment lines from one file (excluding # Antenna lines)
first_lines = []
input_fn = input_files_tot[0]
with open(input_fn, 'r') as f:
    for line in f:
        if line.startswith("#") and "# Antenna" not in line:
            first_lines.append(line)
        else:
            break

# Get antenna header lines
antenna_lines = []
with open(input_fn, 'r') as f:
    for line in f:
        if "# Antenna " in line:
            antenna_lines.append(line)

# Function to combine electric field traces across files
def combine_input_files(input_files):
    antennas = [{} for _ in range(len(antenna_lines))]
    for input_file_name in input_files:
        #print(">>> {0}".format(input_file_name), file=sys.stderr)
        try:
            with open(input_file_name, 'r') as f:
                print(f)
                antenna_number = -1
                for line in f:
                    if "# Antenna " in line:
                        antenna_number = int(line.split(" ")[2])
                    elif not line.startswith("#"):
                        time_val, vec = line.strip().split(" ")
                        time_val = float(time_val)
                        Ex, Ey, Ez = vec.strip("()").split(",")
                        E = np.array([float(Ex), float(Ey), float(Ez)])
                        if time_val not in antennas[antenna_number]:
                            antennas[antenna_number][time_val] = E
                        else:
                            antennas[antenna_number][time_val] += E
        except:
            print(">>> skipping file {0}".format(input_file_name), file=sys.stderr)
            continue
    return antennas

# Combine files by type

antennas_dir = combine_input_files(input_files_dir) if input_files_dir else None
antennas_indir = combine_input_files(input_files_indir) if input_files_indir else None
#antennas_SA = combine_input_files(input_files_SA) if input_files_SA else None
antennas_tot = combine_input_files(input_files_tot)

# Function to write combined traces to file
def write_traces(antennas, output_file_name):
    with open(output_file_name, 'w') as out:
        for line in first_lines:
            out.write(line)

        for antenna_number in range(len(antenna_lines)):
            out.write(antenna_lines[antenna_number])
            antenna_time_vals = sorted(antennas[antenna_number].keys())
            for t in antenna_time_vals:
                E = antennas[antenna_number][t]
                out.write(f"{t} ({E[0]},{E[1]},{E[2]})\n")

    print(f"Finished writing to {output_file_name}")

# Write output files
if antennas_dir:
    write_traces(antennas_dir, f"{output_dir}/antenna_traces_comb_dir.txt")
if antennas_indir:
    write_traces(antennas_indir, f"{output_dir}/antenna_traces_comb_indir.txt")
#if antennas_SA:
#    write_traces(antennas_SA, f"{output_dir}/antenna_traces_comb_SA.txt")
write_traces(antennas_tot, f"{output_dir}/antenna_traces_comb.txt")
