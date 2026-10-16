#!/bin/bash

# The path to the corsikaread_thin (or corsikaread, in case of no thinning) executable
corsikaread_thin=/user/knivedita/airtoice/python_scripts/corsikaread_thin

# The maximum radius of the footprint for which the particles will be read out, in cm
# This is defined in the plane perpendicular to the shower axis frame,
# i.e. the footprint will be an ellipse of
# width upper_radius/cos(zenith) and an height of upper_radius, aligned with the
# azimuth angle
upper_radius=100

ROOTSYS="/cvmfs/icecube.opensciencegrid.org/py2-v2/RHEL_7_x86_64/i3ports/root-v5.34.18"
eval `/cvmfs/icecube.opensciencegrid.org/py2-v2/setup.sh`

input_file=${1}
output_dir=${2}
zenith=${3}
azimuth=${4}

# Copying the file
cp ${input_file} ${TMPDIR}/corsika_file

# Using corsikaread to read the file
echo "${TMPDIR}/corsika_file                                                                  	" > ${TMPDIR}/corsikaread_input
cd ${TMPDIR}/
${corsikaread_thin} < ${TMPDIR}/corsikaread_input > ${TMPDIR}/corsikaread_output
rm ${TMPDIR}/corsika_file
rm ${TMPDIR}/corsikaread_input
rm ${TMPDIR}/corsikaread_output

# read fort.8 file and save particle data 
python /user/knivedita/airtoice/python_scripts/readsave_corsikaout.py ${TMPDIR}/fort.8 ${TMPDIR} 0 ${upper_radius} ${zenith} ${azimuth}

rm ${TMPDIR}/fort.8

cp -f ${TMPDIR}/*.txt ${output_dir}
