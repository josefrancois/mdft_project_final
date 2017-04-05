import os
import mdft_parser.gromacsParser as gP
import mdft_parser.parserJson as pJ
import mdft_writer.mdftWriter as mW
import mdft_writer.runAllWriter as rAW
import argparse

arg_parser = argparse.ArgumentParser(prog="mdft_db_process.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

arg_parser.add_argument("--json", help = "JSON file to parse", default = "mobley.json")
arg_parser.add_argument("--topgro", help = "Folder which contains top and gro files to parse", default = "minitopgro")
arg_parser.add_argument("--voxelsize", "-dx", help = "Distance beween two nodes [unit : angstroms]", type=float, default = 0.5)
arg_parser.add_argument("--lenbulk", "-lb", help = "Distance between solute and box sides [unit : angstroms]", type=int, default = 10)
arg_parser.add_argument("--solvent", help = "Solvent to use in MDFT")
arg_parser.add_argument("--mmax", help = "Maximum number of orientations of solvent molecules to consider", type=int, default = 1)
arg_parser.add_argument("--temperature","-T", help = "Temperature to use in MDFT [unit : Celsius degree]", type=float, default = 298.15)
arg_parser.add_argument("--server", "-sv", help = "Server machine in which MDFT calculations would be performed", default = "abalone")
mdft_args = arg_parser.parse_args()

topgro_files = mdft_args.topgro+"/"
json_file = mdft_args.json
input_mdft = "input_mdft/"

if os.path.exists(input_mdft) == False:
    os.mkdir('input_mdft')
    
input_files = os.listdir(topgro_files)

#print json_file

param_mdft = {'lb':mdft_args.lenbulk, 'dx':mdft_args.voxelsize, 'solvent':mdft_args.solvent, 'mmax':mdft_args.mmax, 'temperature':mdft_args.temperature}

run_writer = rAW.runAllWriter() 

for input_file in input_files:    
    input_name = input_file[:-4]
    
    if os.path.exists(input_mdft+input_name):
        #print input_name
        pass
    else:
        os.mkdir(input_mdft+input_name)
        print input_name       
        parser = gP.GromacsParser(topgro_files+input_name + ".gro", topgro_files+input_name + ".top")
        molecule = parser.parse()
                                                    
        fjson = pJ.ParserJson()
        fjson.parseData(json_file, input_name)
        molecule.setData(fjson.getDataSolute() )
        molecule.setName(fjson.getSoluteName() )
        #print molecule.getData
                                                                              
        writer = mW.MdftWriter(molecule, param_mdft)
        writer.write(input_mdft+input_name)
        os.system("cp " + run_writer.getDoFile(mdft_args.server)+ " " + input_mdft+input_name)
        #os.chdir(input_mdft+input_name)
        #os.system("./mdft-dev | tee " + input_name +".log")
        #os.chdir("../..")

 
run_writer.writeRunCmd(mdft_args.server)      
os.system("cp runAll.sh " + input_mdft)        
os.system("tar -czvf ./input_mdft.tar.gz ./input_mdft/")
