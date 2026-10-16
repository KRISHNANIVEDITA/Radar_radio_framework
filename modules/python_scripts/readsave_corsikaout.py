import numpy as np
import sys
import importlib
mass_file = importlib.import_module("particle_masses")

# The particle ids and masses in GeV/c^2 of the particles. 
particle_masses = mass_file.get_particle_masses()

def read_corsika_fortran_file_energy(input_file_name, radius_underlim, radius_upperlim):

    z_first_interaction = []
    saved_particle_data = []

    # Reading the fort_*.8 file
    with open(input_file_name) as f:

        # Keeps track of the event number
        event_number = -99

        # Read the first line
        line = f.readline()

        while(len(line) != 0):

            # If first word of line is 1.11111E+07, this line is the beginning of a run header block
            # We're not interested in its content, so we skip the block.
            # The block is 39 lines long.
            if("1.11111E+07" in line):

                print( "Found the RUN HEADER block.")

                line_data = line.split(" ")
                line_data = [float(elt) for elt in line_data if len(elt) > 0]
                print( "Using the first observation level defined, which is at %s cm" % line_data[5])

                for skip in range(38):
                    f.readline()

            # If first word of line is 3.33333E+07, this line is the beginning of an event header block
            elif("3.33333E+07" in line):

                print( "Found an EVENT HEADER block.")

                # Getting the event number
                # looks like all the values in the fort_*.8 files are separated by two white spaces
                # not sure if the number of whitespaces is fixed though
                # just splitting on a single whitespace and removing all empty entries in the resulting
                # array should work for all number of whitespaces used
                # also allows for string to float casting
                line_data = line.split(" ")
                line_data = [float(elt) for elt in line_data if len(elt) > 0]
                event_number = int(line_data[1])
                print( "Reading the data of event %s..." % event_number)
                saved_particle_data.append([])

                # Getting the z coordinate of the first interaction
                z_first_interaction.append(float(line_data[6]))

                # Skipping the rest of the event header block, moving on to the data blocks
                # The header block is also 39 lines long.
                for skip in range(38):
                    f.readline()
                
            # If first word of line is 5.55555E+07, this line is the beginning of a longtitudinal block
            # I do not use the option which generates these blocks, so I don't care about them.
            elif("5.55555E+07" in line or "5.55556E+07" in line):

                sys.exit("LONGITUDINAL block encountered. This code is not made for that kind of filth.")

            # If first word of line is 7.77777E+07, this line is the beginning of an event end block
            # This means we have read the data of one full air shower event.
            # We're not interested in the contents of the block so we skip it.
            # The block is again 39 lines long.
            elif("7.77777E+07" in line or "7.77778E+07" in line):

                print( "Found an EVENT END block.")

                # Resetting the event number
                event_number = -99

                # Skipping the content of the block
                for skip in range(38):
                    f.readline()
            
            # If first word if line is 9.99999E+07, this line is the beginning of a run end block
            # We're not interested in its contents, so we skip it.
            # The block is again 39 lines long.
            elif("9.99999E+07" in line or "1.00000E+08" in line):

                print( "Found the RUN END block.")
                for skip in range(38):
                    f.readline()

            # No special word in the beginning means we're reading a line from a data block of an event.
            # We read the data in the line and store it in the array.
            else:

                # looks like all the values in the fort_*.8 files are separated by two white spaces
                # not sure if the number of whitespaces is fixed though
                # just splitting on a single whitespace and removing all empty entries in the resulting
                # array should work for all number of whitespaces used
                # also allows for string to float casting
                particle_data = line.split(" ")
                particle_data = [float(elt) for elt in particle_data if len(elt) > 0]

                # Checking the particle id.
                part_id = int(particle_data[0]/1000.)
                
                # Checking the observation level number, which is the final digit of particle_data[0]
                obs_level_nr = particle_data[0] - int(particle_data[0]/10.)*10
                obs_level_nr = int(obs_level_nr)

                # part_id of 75 and 76 is additional info for resp. mu+ and mu-
                if(obs_level_nr == 1 and part_id != 0 and part_id != 75 and part_id != 76):
                    
                    # The final data block of an event often contains multiple lines 
                    # filled with zeroes to fill it up to get a complete block. 
                    # If we're reading such a line the id is 0.
                    # Corsika does not asign ID = 0 to any particle.

                    # The momenta in the three different directions [GeV/c]
                    px = float(particle_data[1]) * float(energy_unit)
                    py = float(particle_data[2]) * float(energy_unit)
                    pz = float(particle_data[3]) * float(energy_unit)
                    
                    # The x and y positions
                    x = float(particle_data[4]) * float(length_unit)
                    y = float(particle_data[5]) * float(length_unit)

                    # The time since first interaction (incorrect, currently not implemented)
                    t = particle_data[6]

                    # The weight of the particle
                    w = float(particle_data[7])

                    ##### faerie end of read_corsika_fortran_file.py 
                    # z = (depth_active_volume*1./2.)/float(length_unit)     (from later in makegeant4inputfile)

                    # Rotating such that azimuth = 0
                    # This means we rotate the x- and y-axis over an angle = azimuth
                    xrot = x*np.cos(azimuth) + y*np.sin(azimuth)
                    yrot = y*np.cos(azimuth) - x*np.sin(azimuth)
                    x, y = xrot , yrot

                    pxrot = px*np.cos(azimuth) + py*np.sin(azimuth)
                    pyrot = py*np.cos(azimuth) - px*np.sin(azimuth)
                    px, py = pxrot , pyrot

                    # The total momentum in GeV/c
                    p = np.sqrt(px*px + py*py + pz*pz)

                    # The particle mass in GeV/c^2
                    m = float(particle_masses[part_id])*float(energy_unit) # GeV/c^2

                    #Calculate energy [GeV] and radius [cm] of each particle 
                    E_ = np.sqrt(p*p + m*m)
                    r_ = np.sqrt(x**2 + y**2)

                    # Storing the values if particle lies within the specified radius (of circle containing elipse)
                    if(x**2 + y**2 >= radius_underlim**2 and x**2 + y**2 < radius_upperlim**2):

                        # Check if particle in ellipse 
                        if(not in_ellipse(x, y, a_under, b_under) and in_ellipse(x, y, a_upper, b_upper)):

                            saved_particle_data[-1].append([part_id, px, py, pz, x, y, t, w, E_, r_])
                                
            # Read the next line
            line = f.readline()

    if(len(z_first_interaction) != len(saved_particle_data)):
        sys.exit("Something went wrong in reading the fort.8 file. The length of z_first_interaction is %s, while the length of saved_particle_data is %s. Both should be the same..." % (len(z_first_interaction), len(saved_particle_data)))

    return z_first_interaction, saved_particle_data

# This function checks if a given x,y pair lies within an ellipse with width 2a and height 2b:
def in_ellipse(x, y, a, b):
    if(a == 0 or b == 0): # No ellipse...
        return False
    elif(x**2/a**2 + y**2/b**2 < 1):
        return True
    else:
        return False
    
########################################################################
########################################################################
length_unit = 1. # The unit of length in cm
length_unit_str = "cm" # The unit of length in string format
energy_unit = 1. # The unit of energy in GeV. Unit of momentum is (unit of energy)/c.
energy_unit_str = "GeV" # The unit of energy in string format. Unit of momentum is (unit of energy)/c.
time_unit = 1. # The unit of time in ns
time_unit_str = "ns" # The unit of time in string format

depth_active_volume = 2000. # The depth of the active volume in cm
########################################################################
########################################################################

########
# Reading the filename
if(len(sys.argv) != 7):
    sys.exit("This script expects 6 arguments, the first argument is the full path to the corsika output file, the second argument is the full path to the directory write the output file to, the third argument is the radius under limit in cm, the fourth argument is the radius upper limit in cm, the fifth argument is the zenith angle of the shower in degrees, the sixth argument is the azimuth angle of the shower in degrees.")
else:
    input_file_name= sys.argv[1]
    output_file_dir = sys.argv[2]
    radius_underlim = float(sys.argv[3])
    radius_upperlim = float(sys.argv[4])
    zenith = float(sys.argv[5])*np.pi/180.
    azimuth = float(sys.argv[6])*np.pi/180.

######## First check for particle radii, if in circle containing the ellipse (based on zenith angle)
a_upper, a_under = radius_upperlim/np.cos(zenith) , radius_underlim/np.cos(zenith)
b_upper, b_under = radius_upperlim , radius_underlim

########  Reading the fortran output file
z_first_interaction, saved_particle_data = read_corsika_fortran_file_energy(input_file_name, b_under, a_upper)

# sanity check, for depth of first interaction
for i in range(len(z_first_interaction)):
    if(z_first_interaction[i] >= 0):
        sys.exit("The z coordinate of first interaction point of event %s is not negative, which indicates TSTART = false. Aborting..." % i)

print( "Read the Corsika fortran output file. Now saving particle data.")

######## Saving fortran output file data in np array 
spd   =  np.array(saved_particle_data)[0,:,:]       #moves data to np array and flattens
np.savetxt(f"{'spd.txt'}",spd)                      #save data as .txt file (for now)


