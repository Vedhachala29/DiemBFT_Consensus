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


MAIN FILES:

Client source : <path_of_project_folder>/src/client.da
Validator source : <path_of_project_folder>/src/validator.da 
Scenario generator : <path_of_project_folder>src/scenarios_generator.py
Run scenarios using : <path_of_project_folder>src/run_diembft.py

CODE SIZE:



LANGUAGE FEATURE USAGE:

(Pertaining to twin's scenario generation and execution, Not including DiemBFT)

Python list comprehension : 5 
Python dictionary comprehension : 4
Python set comprehension : 4
DistAlgo quantifications : 2 await(each()) quantifications used in run.da
DistAlgo await statements : 4 await statements
Number of receive handlers : 2 extra receive handlers used for validator's reception of syncup requests and responses

