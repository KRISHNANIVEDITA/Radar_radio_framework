import ROOT
import glob
import sys

# Reading the arguments
if(len(sys.argv) != 3):
    sys.exit("This script requires two arguments, which are the directory containing all the root files and extra 2D histos root files and the output directory.")
else:
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

# Get the files containing the histos and trees we need to combine
files = glob.glob("%s/geant4_input_*.root" % input_dir)
files = [elt for elt in files if "extra_2D_histos.root" not in elt]
files_extra_2D_histos = glob.glob("%s/geant4_input_*_extra_2D_histos.root" % input_dir)

#########################################################
###################### THE HISTOS  ######################
#########################################################

# Creating an output file
output_file = ROOT.TFile(output_dir + "/histos_combined.root", "RECREATE")

# Combining the 2D slice histos, depth histos, charge histos and radius histos

histo_name_gammas = "EnergyDensityProfile_gammas"
histo_name_electrons = "EnergyDensityProfile_electrons"
histo_name_muons = "EnergyDensityProfile_muons"
histo_name_hadrons = "EnergyDensityProfile_hadrons"

depth_histo_name_gammas = "NumberOfParticlesDepth_gammas"
depth_histo_name_eplus = "NumberOfParticlesDepth_positrons"
depth_histo_name_emins = "NumberOfParticlesDepth_electrons"
depth_histo_name_muplus = "NumberOfParticlesDepth_antimuons"
depth_histo_name_mumins = "NumberOfParticlesDepth_muons"
depth_histo_name_hadrons = "NumberOfParticlesDepth_hadrons"

charge_histo_name_gammas = "ChargeTimeProfile_gammas"
charge_histo_name_electrons = "ChargeTimeProfile_electrons"
charge_histo_name_muons = "ChargeTimeProfile_muons"
charge_histo_name_hadrons = "ChargeTimeProfile_hadrons"

input_file = ROOT.TFile(files[0], "OLD")
output_file.cd()

comb_histo_gammas = input_file.Get(histo_name_gammas).Clone()
comb_histo_electrons = input_file.Get(histo_name_electrons).Clone()
comb_histo_muons = input_file.Get(histo_name_muons).Clone()
comb_histo_hadrons = input_file.Get(histo_name_hadrons).Clone()

comb_depth_histo_gammas = input_file.Get(depth_histo_name_gammas).Clone()
comb_depth_histo_eplus = input_file.Get(depth_histo_name_eplus).Clone()
comb_depth_histo_emins = input_file.Get(depth_histo_name_emins).Clone()
comb_depth_histo_muplus = input_file.Get(depth_histo_name_muplus).Clone()
comb_depth_histo_mumins = input_file.Get(depth_histo_name_mumins).Clone()
comb_depth_histo_hadrons = input_file.Get(depth_histo_name_hadrons).Clone()

comb_charge_histo_gammas = input_file.Get(charge_histo_name_gammas).Clone()
comb_charge_histo_electrons = input_file.Get(charge_histo_name_electrons).Clone()
comb_charge_histo_muons = input_file.Get(charge_histo_name_muons).Clone()
comb_charge_histo_hadrons = input_file.Get(charge_histo_name_hadrons).Clone()

input_file.Close()

for i in range(1, len(files)):
    try:
        input_file = ROOT.TFile(files[i], "OLD")
        print(">>> {0}".format(input_file), file=sys.stderr)
        # Getting the histos
    
        histo_gammas = input_file.Get(histo_name_gammas)
        histo_electrons = input_file.Get(histo_name_electrons)
        histo_muons = input_file.Get(histo_name_muons)
        histo_hadrons = input_file.Get(histo_name_hadrons)
    
        depth_histo_gammas = input_file.Get(depth_histo_name_gammas)
        depth_histo_eplus = input_file.Get(depth_histo_name_eplus)
        depth_histo_emins = input_file.Get(depth_histo_name_emins)
        depth_histo_muplus = input_file.Get(depth_histo_name_muplus)
        depth_histo_mumins = input_file.Get(depth_histo_name_mumins)
        depth_histo_hadrons = input_file.Get(depth_histo_name_hadrons)
    
        charge_histo_gammas = input_file.Get(charge_histo_name_gammas)
        charge_histo_electrons = input_file.Get(charge_histo_name_electrons)
        charge_histo_muons = input_file.Get(charge_histo_name_muons)
        charge_histo_hadrons = input_file.Get(charge_histo_name_hadrons)
    
        # Adding the histo to the combined histo
        
        comb_histo_gammas.Add(histo_gammas)
        comb_histo_electrons.Add(histo_electrons)
        comb_histo_muons.Add(histo_muons)
        comb_histo_hadrons.Add(histo_hadrons)
    
        comb_depth_histo_gammas.Add(depth_histo_gammas)
        comb_depth_histo_eplus.Add(depth_histo_eplus)
        comb_depth_histo_emins.Add(depth_histo_emins)
        comb_depth_histo_muplus.Add(depth_histo_muplus)
        comb_depth_histo_mumins.Add(depth_histo_mumins)
        comb_depth_histo_hadrons.Add(depth_histo_hadrons)
    
        comb_charge_histo_gammas.Add(charge_histo_gammas)
        comb_charge_histo_electrons.Add(charge_histo_electrons)
        comb_charge_histo_muons.Add(charge_histo_muons)
        comb_charge_histo_hadrons.Add(charge_histo_hadrons)
    
        # Getting rid of the histo we read as we do not want to save it again
    
        del histo_gammas
        del histo_electrons
        del histo_muons
        del histo_hadrons
    
        del depth_histo_gammas
        del depth_histo_eplus
        del depth_histo_emins
        del depth_histo_muplus
        del depth_histo_mumins
        del depth_histo_hadrons
    
        del charge_histo_gammas
        del charge_histo_electrons
        del charge_histo_muons
        del charge_histo_hadrons
        input_file.Close()
        
    except:
        print(">>> didnt open XXXX {0}".format(input_file), file=sys.stderr)
        continue
# Combining the 2D radial histos

histo_name_gammas = "RadialEnergyProfile_gammas"
histo_name_electrons = "RadialEnergyProfile_electrons"
histo_name_muons = "RadialEnergyProfile_muons"
histo_name_hadrons = "RadialEnergyProfile_hadrons"

input_file = ROOT.TFile(files_extra_2D_histos[0], "OLD")
output_file.cd()
comb_rad_histo_gammas = input_file.Get(histo_name_gammas).Clone()
comb_rad_histo_electrons = input_file.Get(histo_name_electrons).Clone()
comb_rad_histo_muons = input_file.Get(histo_name_muons).Clone()
comb_rad_histo_hadrons = input_file.Get(histo_name_hadrons).Clone()
input_file.Close()

for i in range(1, len(files_extra_2D_histos)):

    # Reading the file containing the histo
    input_file = ROOT.TFile(files_extra_2D_histos[i], "OLD")
    
    # Getting the histos
    histo_gammas = input_file.Get(histo_name_gammas)
    histo_electrons = input_file.Get(histo_name_electrons)
    histo_muons = input_file.Get(histo_name_muons)
    histo_hadrons = input_file.Get(histo_name_hadrons)

    # Adding the histo to the combined histo
    comb_rad_histo_gammas.Add(histo_gammas)
    comb_rad_histo_electrons.Add(histo_electrons)
    comb_rad_histo_muons.Add(histo_muons)
    comb_rad_histo_hadrons.Add(histo_hadrons)

    # Getting rid of the histo we read as we do not want to save it again
    del histo_gammas
    del histo_electrons
    del histo_muons
    del histo_hadrons

# Saving the combined histogram
output_file.Write()
output_file.Close()

print("Finished combining the histograms")

#########################################################
###################### THE TTREES  ######################
#########################################################

# Getting the names of the trees

input_file = ROOT.TFile(files[0], "OLD")
input_file.cd("")
object_names = [key.GetName() for key in ROOT.gDirectory.GetListOfKeys()]
input_file.Close()

object_names = [elt for elt in object_names if "SnapshotNtuple" in elt] 

if(len(object_names) > 0):

    for object_name in object_names:

        chain = ROOT.TChain(object_name)

        for path in files:
            chain.Add(path)

        chain.Merge(output_dir + "/" + object_name + "_combined.root")

print("Finished combining the trees.")