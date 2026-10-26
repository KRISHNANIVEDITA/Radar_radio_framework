Radar–Radio Simulation Framework
Work in progress: This repository is currently in progress. The full source code and documentation will be made publicly available soon.

This project provides a common workflow for simulating radio and radar signals from a high-energy cosmic-ray event. It is designed to connect the different stages of the simulation.

The framework brings together:
- CORSIKA/CoREAS for air-shower development and in-air radio emission;
- FAERIE/Geant4-based tools for propagating the shower into ice and simulating the in-ice component; and
- MARES for radar-echo simulations.
The external simulation packages are not bundled with this repository and must be installed separately. 
Development status
The current development focuses on:
- generating CORSIKA input files from event parameters;
- assigning consistent event and simulation identifiers;
- transforming antenna coordinates relative to a selected shower core;
- preparing and submitting CORSIKA jobs through HTCondor;
- converting CORSIKA particle output into Geant4 job-input files; and
- organising outputs so that the same event can be followed through the complete simulation chain.
The MARES integration and final combined-signal workflow are being prepared for a future update.
Intended workflow
1. Define the event properties, including energy, zenith, azimuth, random seed, shower-core position, and antenna geometry.
2. Generate the CORSIKA/CoREAS input files.
3. Run CORSIKA separately and inspect its output.
4. Convert the CORSIKA particle output into Geant4 input files.
5. Run the in-ice simulation separately.
6. Run MARES separately for the same event geometry.
7. Combine and analyse the radio, Askaryan, and radar signals.
The framework coordinates the files and metadata between these stages; it does not automatically run the complete chain as a single command.
Repository structure
Radar_radio_framework/
├── setup.sh
├── src/
│   └── CORSIKA/
│       ├── prepare.py
│       ├── submit.py
│       └── into_ice.py
├── modules/
│   ├── CORSIKA/
│   │   ├── run_corsika.sh
│   │   ├── run_corsika.submit
│   │   ├── make_job_files.sh
│   │   └── make_job_files.submit
│   └── python_scripts/
├── utilities/
│   └── local/
└── output_files/
The structure may change while the software is under development.
Basic setup
Clone the repository and enter its main directory:
git clone https://github.com/KRISHNANIVEDITA/Radar_radio_framework.git
cd Radar_radio_framework
Set the project root for the current terminal:
source setup.sh
This defines SOFTWARE_HOME, which is used by the submission and execution scripts to locate the modules and utilities belonging to the repository.
Running the stages
The main commands will follow this structure:
The exact versions and installation instructions will be documented soon. The workflow currently expects access to:
- Python 3;
- CORSIKA 7 with CoREAS;
- Geant4;
- MARES;
- ROOT;
- HTCondor; and
- the required FAERIE components or adapted scripts.
Large simulation outputs should be stored outside the Git repository.

Attribution
Parts of the CORSIKA-to-Geant4 workflow and execution scripts are taken from or adapted from the FAERIE simulation framework. Relevant adapted files retain attribution to the original authors.
If you use the FAERIE-related components, please cite:
S. De Kockere et al., “Simulation of radio signals from cosmic-ray cascades in air and ice as observed by in-ice Askaryan radio detectors,” Physical Review D 110, 023010 (2024). https://doi.org/10.1103/PhysRevD.110.023010
Users should also cite CORSIKA, CoREAS, Geant4, MARES, and other external packages.
License
License information for the original code in this repository will be added before the full release. External and adapted components remain subject to their respective licenses and usage conditions.
Author
Developed by Krishna Nivedita Gopinath as part of research on combined radio and radar signatures from high-energy particle cascades.
