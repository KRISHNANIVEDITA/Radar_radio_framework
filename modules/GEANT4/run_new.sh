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

ice_shelf_exe=/user/knivedita/software/Iceshelf/build/ice_shelf

# Sourcing the geant4.sh script of the geant4 installation here
#eval 'source /software/geant4/geant4.10.05.p01-install/bin/geant4.sh'

source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_104 x86_64-el9-gcc13-opt

# This script launches the ice_shelf project, using the CoREAS reas and list file to initialize the antenna positions. It needs eight arguments. The first argument is the input file, the second argument is the output file (no extension), the third argument is a random number used for the seed of the random engine (NOTE: The index of seedtable will be this number modulo 215, so using 0 or 215 e.g. will result in same engine seed). The fourth argument is the zenith angle of the shower (in degrees). The fifth argument is the azimuth angle of the shower (in degrees). The sixth argument is the reas file. The seventh argument is the list file. The eight argument is the amtosphere data file.

inputfile=${TMPDIR}/input_file.txt
cp ${1} ${inputfile}

outputfile=${TMPDIR}/output_file

rand_number=${3}
zenith=${4}
azimuth=${5}

reas_file=${TMPDIR}/CoREAS.reas
cp ${6} ${reas_file}
list_file=${TMPDIR}/CoREAS.list
cp ${7} ${list_file}
atmos_file=${TMPDIR}/Atmosphere.dat
cp ${8} ${atmos_file}

${ice_shelf_exe} ${inputfile} ${outputfile} ${rand_number} ${zenith} ${azimuth} ${reas_file} ${list_file} ${atmos_file}

# Copying the output files
cp -f ${outputfile}.root ${2}.root
cp -f ${outputfile}_extra_2D_histos.root ${2}_extra_2D_histos.root
cp -f ${outputfile}_dir.txt ${2}_dir.txt
cp -f ${outputfile}_indir.txt ${2}_indir.txt
cp -f ${outputfile}_SA.txt ${2}_SA.txt
# Cleaning up
rm ${inputfile}
rm ${outputfile}*
rm ${reas_file}
rm ${list_file}
rm ${atmos_file}
