# This script converts the Geant4 trace files to the same format CoREAS uses, which means:
# - following the same output format convention
# - using the same unit convention
# - using the same coordinate system convention (Corsika)

import sys
import numpy as np

if(len(sys.argv) != 4):
    sys.exit("This script expects three arguments.\n 1) The G4 trace file to convert.\n 2) The output directorty to store the converted files in.\n 3) The azimuth angle of the shower in degrees.")
else:
    input_fn = sys.argv[1]
    output_dir = sys.argv[2]
    phi = float(sys.argv[3])*np.pi/180. # Converting to radians

tround = 6 # Setting precision to avoid i.e. 1.23e-7 to become 1.230000000001e-7
#print("Precision for time is 1e-%i ns. Adjust the tround parameter in the script if you want to change this.\033[0m" % tround)

# This function does the axis system conversion for the electric field components
def g4_to_CoREAS_Etrans(xG, yG, zG):

    xC = xG*np.cos(phi) + zG*np.sin(phi)
    yC = xG*np.sin(phi) - zG*np.cos(phi)
    zC = yG 

    return xC, yC, zC

# Reading the G4 trace file

G4_traces = []
G4_tunit = ""
G4_Eunit = ""

input_file = open(input_fn, 'r')
line = input_file.readline()

while(line):
    
    # For getting the time and Efield units
    if(line[0] == '#' and "time" in line and "electric field" in line):
        G4_tunit = line.split(" ")[2].split('\t')[0][1:-1]
        G4_Eunit = line.split(" ")[4][1:-2]
        print(G4_Eunit)
    # Checking if we're reading in a new antenna
    elif(line[0] == '#' and " Antenna " in line):
        G4_traces.append([])

    # If we're reading data, add it to the latest antenna array
    elif(line[0] != '#'):
        t = float(line.split(" ")[0])
        Ex = float(line.split(" ")[1].split(",")[0][1:])
        Ey = float(line.split(" ")[1].split(",")[1])
        Ez = float(line.split(" ")[1].split(",")[2][:-2])
        G4_traces[-1].append([t, Ex, Ey, Ez])

    line = input_file.readline()

input_file.close()

# Making the CoREAS format output files
for antnr in range(len(G4_traces)):

    print("Creating file antenna%s.dat" % antnr, end='\r')

    output_file = open("%s/antenna%s.dat" % (output_dir, antnr), 'w')
    trace = G4_traces[antnr]

    for i in range(len(trace)):

        t = trace[i][0]
        Ex_G = trace[i][1]
        Ey_G = trace[i][2]
        Ez_G = trace[i][3]

        # Doing the rotation
        Ex_C, Ey_C, Ez_C = g4_to_CoREAS_Etrans(Ex_G, Ey_G, Ez_G)

        # Switching units

        if(G4_tunit == "ns"):
            tfactor = 1e-9
        else:
            sys.exit("The G4 time unit is %s. The conversion factor is not implemented in this script. Please do so." % G4_tunit)

        if(G4_Eunit == "V/m"):
            Efactor = 1./29979.2458 # 1 statV/cm = 29979.2458 V/m
        else:
            sys.exit("The G4 Efield unit is %s. The conversion factor is not implemented in this script. Please do so." % G4_Eunit)

        t = tfactor*t
        Ex_C = Efactor*Ex_C
        Ey_C = Efactor*Ey_C
        Ez_C = Efactor*Ez_C
            
        t = round(t, 9+tround) # Setting precision to avoid i.e. 1.23e-7 to become 1.230000000001e-7
        output_file.write("%s\t%s\t%s\t%s\n" % (t, Ex_C, Ey_C, Ez_C))

    output_file.close()
