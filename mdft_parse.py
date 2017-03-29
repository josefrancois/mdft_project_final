import os
import mdft_parser.parserJson as pJ
import mdft_parser.parserLog as pL
import mdft_writer.jsonWriter as jW

json_file = "mobley.json"
folder_to_parse = "./mini_input_mdft/"
pJson = pJ.ParserJson()
pLog = pL.ParserLog()

mdft_database = {}

for subfolder in os.listdir(folder_to_parse):
	for mdft_file in os.listdir(folder_to_parse+subfolder):
		if mdft_file[-4:] == ".log":
			path_to_logfile = folder_to_parse+subfolder+'/'+mdft_file
			pJson.parseData(json_file, subfolder)
			pLog.parse(path_to_logfile)
			data_solute = pJson.getDataSolute()
			data_solute['mdft_energy (kJ/mol)'] = float(pLog.getMdftEnergy())
			data_solute['functional_at_min (kJ/mol)'] = float(pLog.getFunctionalAtMin())
			data_solute['mdft_energy_pc (kJ/mol)'] = float(pLog.getMdftEnergyPc())
			data_solute['mdft_energy_pc+ (kJ/mol)'] = float(pLog.getMdftEnergyPcPlus())
			data_solute['mdft_energy_pmv (kJ/mol)'] = float(pLog.getMdftEnergyPmv())
			data_solute['mdft_energy_pid (kJ/mol)'] = float(pLog.getMdftEnergyPid())
			print subfolder
			mdft_database[subfolder] = data_solute

newJson = jW.JsonWriter(mdft_database)
newJson.write('mdft.json')






























