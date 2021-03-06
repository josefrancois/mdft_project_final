import os
import mdft_parser.gromacsParser as gP
import mdft_parser.jsondbParser as jdP
import mdft_writer.mdftWriter as mW
import mdft_writer.runAllWriter as rAW
import dbCloner as dbC
import json
import argparse
import sys


# Options to get the name of the database and parametrize MDFT calculations
arg_parser = argparse.ArgumentParser(prog="mdft_db_process.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
arg_parser.add_argument("--database", "-db", help = "Used key in database_definition.json to indicate the database", default = None)
arg_parser.add_argument("--voxelsize", "-dx", help = "Distance between two nodes [unit : angstroms]", type=float, default = 0.5)
arg_parser.add_argument("--lenbulk", "-lb", help = "Distance between solute and box sides [unit : angstroms]", type=int, default = 10)
arg_parser.add_argument("--solvent", help = "Solvent to use in MDFT")
arg_parser.add_argument("--mmax", help = "Maximum number of orientations of solvent molecules to consider", type=int, default = 1)
arg_parser.add_argument("--temperature","-T", help = "Temperature to use in MDFT [unit : Kelvin]", type=float, default = 298.15)
arg_parser.add_argument("--server", "-sv", help = "Server machine in which MDFT calculations would be performed", default = "pc")
arg_parser.add_argument("--mdftcommit", help = "Commit hash of mdft-dev that should be used", default = None)
arg_parser.add_argument("--mdftpath", help = "Path of mdft-dev if already compiled", default = None)
arg_parser.add_argument("--bridge", "-bg", help = "Bridge Functional to use in MDFT calculations", default = "none")
arg_parser.add_argument("--solute_charges_scale_factor", "-scsf", help = "Solute charges factor which indicates how much we consider the influence of the partial charges", default = None)
arg_parser.add_argument("--direct_solute_sigmak", "-dss", help = "Guillaume Jeanmairet's implementation", default = None)
mdft_args = arg_parser.parse_args()


# If used, add bridge name to the database name 
if mdft_args.database == None:
    sys.exit("Please indicate an input database !")

if mdft_args.bridge == 'none' :
    input_mdft = mdft_args.database+'/'
else:
    input_mdft = mdft_args.database+ "_"+ mdft_args.bridge +'/'
    

# Creation of a directory whose name is database's
if os.path.exists(input_mdft) == False:
    os.mkdir(input_mdft)
    
    
# Retrieving of all values of the command options
param_mdft = {'lb':mdft_args.lenbulk, 'dx':mdft_args.voxelsize, 'solvent':mdft_args.solvent, \
              'mmax':mdft_args.mmax, 'temperature':mdft_args.temperature, 'bridge':mdft_args.bridge, \
              'solute_charges_scale_factor':mdft_args.solute_charges_scale_factor,\
              'direct_solute_sigmak': mdft_args.direct_solute_sigmak}
              

# Retrieveing informations from database_definition.json about the database and choice of the adequate parser
with open('database_definition.json', 'r') as json_file:
    db_def = json.load(json_file)
input_name = db_def[mdft_args.database]
db_format = input_name["format"] 
parser = None
input_db_name = None
if db_format == 'gromacs':
    if "github" in input_name:
        cloner = dbC.DBCloner(input_name["github"], input_name["mol_db"])
        if "commit" in input_name:
            cloner.setCommitHash(input_name["commit"])
        if "ref_values" in input_name :
            cloner.setRefFile(input_name["ref_values"])
        input_db_name = cloner.write()
        cloner.execute()
    else:
        input_db_name = input_name["mol_db"]
    if "ref_values" in input_name:
        os.system("cp " + input_name["ref_values"] + " " + input_mdft) #Copy the database of reference values if provided in input_mdft  
    parser = gP.GromacsParser(input_db_name)    
    input_db = [f[:-4] for f in os.listdir(input_db_name) if ".gro" in f]
elif db_format == 'json':
    with open(input_name["mol_db"], 'r') as fjson:
        input_db = json.load(fjson)
    parser = jdP.JsonDBParser(input_db)
    

# Creation of one subfolder for each molecule of the database with its dft.in, solute.in and .do file, and writing of runAll.sh into the created folder (input_mdft)   
run_writer = rAW.runAllWriter()

for mol in input_db:
    print mol
    molecule = parser.parse(mol)
    molecule.setName(mol)
    os.mkdir(input_mdft+molecule.getName())
    writer = mW.MdftWriter(molecule, param_mdft)
    writer.write(input_mdft+molecule.getName())
    os.system("cp ./references/do_files/" + run_writer.getDoFile(mdft_args.server)+ " " + input_mdft+molecule.getName())

run_writer.write(mdft_args.server, mdft_args.mdftcommit, input_mdft)    

  
# Copying of all the necessary files into the created folder
os.system("cp mdft_parse.py " + input_mdft)
os.system("cp database_definition.json " + input_mdft)
os.system("cp -r mdft_parser "  + input_mdft)
os.system("cp -r mdft_writer "  + input_mdft)
os.system("cp -r references " + input_mdft)


# If MDFTPATH option was used, transferring of MDFT code from the submitted path to the output folder
if mdft_args.mdftpath is not None :
    os.system("cp -r " + mdft_args.mdftpath + " " + input_mdft)
    
    
# Creation of an archive    
os.system("tar -czvf " + input_mdft[:-1] + ".tar.gz " +input_mdft)
