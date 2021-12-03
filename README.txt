Implementation of Twins, BFT Systems made robust in DistAlgo

PLATFORM :

Python: Python 3.7.11
Package manager : Miniconda.
DistAlgo : Cloned from https://github.com/DistAlgo/distalgo.git and ran setup.py
Version : pyDistAlgo==1.1.0b15
Operating system Productname : macOS
OS ProductVersion: 11.5.2
OS BuildVersion: 20G95
Type of Host : Personal Laptop

BUGS and LIMITATIONS :

1. Syncup works well if single validator is lagging behind but is intermittent with multiple validators.
2. Safety violation is recognised in case out of order delivery, haven't completed for checking duplicate commits.


MAIN FILES:

Client source : <path_of_project_folder>/src/client.da
Validator source : <path_of_project_folder>/src/validator.da 
Scenario generator : <path_of_project_folder>src/scenarios_generator.py
Run scenarios using : <path_of_project_folder>src/run_diembft.py

CODE SIZE:

cloc *generator.py
       2 text files.
       2 unique files.
       0 files ignored.

github.com/AlDanial/cloc v 1.90  T=0.01 s (321.5 files/s, 48062.6 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                           2             52             17            230
-------------------------------------------------------------------------------
SUM:                             2             52             17            230
-------------------------------------------------------------------------------

❯ cloc network_playground.da
       1 text file.
       1 unique file.
       0 files ignored.

github.com/AlDanial/cloc v 1.90  T=0.01 s (180.3 files/s, 33352.5 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
DAL                              1             32              0            153
-------------------------------------------------------------------------------

More changes are made to validator.da, ledger.da, run_diembft.da but not complete changes.

LANGUAGE FEATURE USAGE:

(Pertaining to twin's scenario generation and execution, Not including DiemBFT)

Python list comprehension : 7
Python dictionary comprehension : 4
Python set comprehension : 4
DistAlgo quantifications : 2 await(each()) quantifications used in run.da
DistAlgo await statements : 4 await statements
Number of receive handlers : 2 extra receive handlers used for validator's reception of syncup requests and responses


CONTRIBUTIONS:

Vedhachala Tirupattur Shanmugam : Scenario executor, integration with DiemBFT, bugfixes in DiemBFT
Sai Bhargav Varanasi : Scenario generation, bugfix in DiemBFT, testcase testing
Sujay Lakkimsetti : Scenario generation


