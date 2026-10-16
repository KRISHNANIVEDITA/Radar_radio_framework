# This file contains a function creating a dictionary, maping the Corsika particle ID's to their masses.
# Unit of mass is GeV/c^2.

def get_particle_masses():
    particle_masses = {}
    particle_masses[1] = 0.
    particle_masses[2] = .000511
    particle_masses[3] = .000511
    particle_masses[5] = .105658
    particle_masses[6] = .105658
    particle_masses[7] = .134977
    particle_masses[8] = .139570
    particle_masses[9] = .139570
    particle_masses[10] = .49761
    particle_masses[11] = .493677
    particle_masses[12] = .493677
    particle_masses[13] = .939565
    particle_masses[14] = .938272
    particle_masses[15] = .938272
    particle_masses[16] = .49761
    particle_masses[17] = .547862
    particle_masses[18] = 1.11568
    particle_masses[19] = 1.18937
    particle_masses[20] = 1.192642
    particle_masses[21] = 1.197449
    particle_masses[22] = 1.31486
    particle_masses[23] = 1.32171
    particle_masses[24] = 1.67245
    particle_masses[25] = .939565
    particle_masses[26] = 1.115683
    particle_masses[27] = 1.18937
    particle_masses[28] = 1.192642
    particle_masses[29] = 1.197449
    particle_masses[30] = 1.31486
    particle_masses[31] = 1.32171
    particle_masses[32] = 1.67245
    particle_masses[201] = 1.87561 # This is deuteron (ID = 100 x A + Z)
    particle_masses[301] = 2.80892 # This is triton (ID = 100 x A + Z)
    particle_masses[302] = 2.80941 # This is helium-3 nucleus (ID = 100 x A + Z)
    particle_masses[402] = 3.7284 # This is helium nucleus (ID = 100 x A + Z)
    return particle_masses
