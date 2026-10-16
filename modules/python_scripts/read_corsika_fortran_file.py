import sys

# This script provides a function to read a corsika output file.

# Arguments are:
#   - input_file_name, the file name of the fortran file
#   - radius_underlim, the under limit of the radius in which the particles you're interested in 
#     should fall. Unit is cm.
#   - radius_upperlim, the upper limit of the radius in which the particles you're interested in 
#     should fall. Unit is cm.
# Returns:
#   - z_first_interaction, an array holding the z-coords (= wrt sea level) of first interaction in cm 
#
#   z_first_interaction[ev] will give you the z-coord of the first interaction of event ev etc.
#
#   - saved_particle_data, an array holding [part_id, px, py, pz, x, y, t, w] for each particle of interest
#   saved_particle_data[0][part_nr] will give you [part_id, px, py, pz, x, y, t, w] of particle part_nr
#   of the first event encountered
#   saved_particle_data[1][part_nr] will give you [part_id, px, py, pz, x, y, t, w] of particle part_nr
#   of the second event encountered
#   etc.
#   NOTE: Unit of momentum is GeV/c, unit of length is cm, unit of time is ns.
#   NOTE: Only the particles from the first observation level are returned

def read_corsika_fortran_file(input_file_name, radius_underlim, radius_upperlim):

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

                print("Found the RUN HEADER block.")

                line_data = line.split(" ")
                line_data = [float(elt) for elt in line_data if len(elt) > 0]
                print("Using the first observation level defined, which is at %s cm" % line_data[5])

                for skip in range(38):
                    f.readline()

            # If first word of line is 3.33333E+07, this line is the beginning of an event header block
            elif("3.33333E+07" in line):

                print("Found an EVENT HEADER block.")

                # Getting the event number
                # looks like all the values in the fort_*.8 files are separated by two white spaces
                # not sure if the number of whitespaces is fixed though
                # just splitting on a single whitespace and removing all empty entries in the resulting
                # array should work for all number of whitespaces used
                # also allows for string to float casting
                line_data = line.split(" ")
                line_data = [float(elt) for elt in line_data if len(elt) > 0]
                event_number = int(line_data[1])
                print("Reading the data of event %s..." % event_number)
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

                print("Found an EVENT END block.")

                # Resetting the event number
                event_number = -99

                # Skipping the content of the block
                for skip in range(38):
                    f.readline()
            
            # If first word if line is 9.99999E+07, this line is the beginning of a run end block
            # We're not interested in its contents, so we skip it.
            # The block is again 39 lines long.
            elif("9.99999E+07" in line or "1.00000E+08" in line):

                print("Found the RUN END block.")
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

                    # The momenta in the three different directions
                    px = particle_data[1]
                    py = particle_data[2]
                    pz = particle_data[3]
                    
                    # The x and y positions
                    x = particle_data[4]
                    y = particle_data[5]

                    # The time since first interaction
                    t = particle_data[6]

                    # The weight of the particle
                    w = particle_data[7]

                    # Storing the values if particle lies within the specified radius
                    if(x**2 + y**2 >= radius_underlim**2 and x**2 + y**2 < radius_upperlim**2):
                        saved_particle_data[-1].append([part_id, px, py, pz, x, y, t, w])
                                
            # Read the next line
            line = f.readline()

    if(len(z_first_interaction) != len(saved_particle_data)):
        sys.exit("Something went wrong in reading the fort.8 file. The length of z_first_interaction is %s, while the length of saved_particle_data is %s. Both should be the same..." % (len(z_first_interaction), len(saved_particle_data)))

    return z_first_interaction, saved_particle_data
