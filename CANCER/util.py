import json, os.path
import pandas as pd
file = "cancer_herb_content.json"
read_file = "cancer_herb_content.json"
## overlap ingredients
overlap_herbs = ["Andrographis", "Blue-Green Algae", "Bromelain", "Butterbur",
				"Calcium", "Cranberry", "Elderberry", "Fenugreek",
				"Flaxseed", "Folic Acid", "Ginkgo", "Grape",
				"Hops", "Indole-3-Carbinol", "Kudzu", "L-Arginine",
				"L-Tryptophan", "Melatonin", "N-Acetyl Cysteine", "Pomegranate",
				"Red Clover", "Reishi Mushroom", "Shiitake Mushroom", "Siberian Ginseng", 
				"Turmeric", "Vitamin B12", "Vitamin E", "Vitamin K",
				"Blue-green Algae", "Folate", "Grape seeds", "Arginine",
				"5-HTP", "N-Acetylcysteine"]
## desired headers
headers = ["name", "last_updated", "common_name", "scientific_name",
			"warnings", "contraindications", "clinical_summary",
			"food_sources", "mechanism_of_action", "purported_uses", 
			"adverse_reactions", "herb-drug_interactions"]
## extract necessary subheaders
def extract():
    try:
        with open(file, "r") as output:
            for line in output:
                data = {}
                herb = json.loads(line)
                name = herb["name"]
                data["name"] = name
                ## extract content for annotation
                if "purported_uses" in herb:
                    pu = herb["purported_uses"]
                    if isinstance(pu, list):
                    	data["purported_uses"] = ",".join(pu)
                    else:
                    	pu = pu.split("\n")
                    	data["purported_uses"] = ",".join(pu)
                else:
                	pass
                write(data, "cancer_pu.json")
    except IOError:
        print("No such file. Please run cancer_context.py first.")
## concatenate list of string into string
def concate(value):
	if isinstance(value, list):
		return ",".join(value)
	else:
		return value
## write to local file
## @value: desired cancer herb content
def write(value, output):
    with open(output, "a") as f:
        json.dump(value, f)
        f.write("\n")
## read json file for adr & hdi
## @json_file: json file to read. i.e cancer_adr.json
## @output_file: output file for preprocessed herb
## return herb
def read(json_file, output_file):
	with open(json_file, "r") as f:
		for lines in f:
			herb = {}
			value = json.loads(lines)
			for k, v in value.items():
				## replace none to empty string
				if v is None or v == "None":
					herb[k] = " "
				else:
					herb[k] = concate(v)
			write(herb, output_file)

## merge into single dataframe
## return merged dataframe
def merge():
	read("cancer_adr.json", "cancer_adr_mergerd.json")
	read("cancer_hdi.json", "cancer_hdi_merged.json")
	adr = pd.read_json("cancer_adr_mergerd.json", lines = True)
	hdi = pd.read_json("cancer_hdi_merged.json", lines = True)
	pu = pd.read_json("cancer_pu.json", lines = True)
	content = adr.merge(hdi, on = "name")
	content_full = content.merge(pu, on = "name")
	return content_full.drop_duplicates()
## add flags to the merged dataframe
## write merged dataframe into local file
## @data: merged dataframe which contains ar, hdi, labels and original content
## @output_file: output file name
## return dataframe that added flags
def addFlag(data, output_file):
	data["ar_flag"] = data["ar_context"].str.contains(":")
	data["hdi_flag"] = data["hdi_context"].str.contains(":")
	if os.path.exists(output_file):
		pass
	else:
		data.to_csv(output_file, sep = "\t")
	return data
## compute basic statistics
def stat(data):
	print("Total %d Cancer herbs" %(data.shape[0]))
	print("Total %d Cancer herbs have structured adverse reactions content." % data.loc[data["ar_flag"] == True].shape[0])
	print("Total %d Cancer herbs have structured herb-drug interactions content." % data.loc[data["hdi_flag"] == True].shape[0])
	print("Total %d Cancer herbs have both structured adverse reactions and herb-drug interactions content." % data.loc[(data["hdi_flag"] == True) & (data["ar_flag"] == True)].shape[0])
	print("Total %d Cancer herbs do not have adverse reactions content" % data.loc[data["ar_context"] == " "].shape[0])
	print("Total %d Cancer herbs do not have herb-drug interactions content" % data.loc[data["hdi_context"] == " "].shape[0])
## extract desired ingredients
def extract_herb():
	try:
		with open(read_file, "r") as f:
			for line in f:
				data = json.loads(line)
				## check if the ingredient is desired
				if data["name"] in overlap_herbs:
					herb = {}
					for each in headers:
						herb[each] = getBefore(data[each])
					write(herb, "MSKCC_overlap.json")
				else:
					pass
	except IOError:
		print("No such file.")
## change data format
def change():
	dt = pd.read_json("MSKCC_overlap.json", lines = True)
	print(dt.shape)
	dt.to_csv("MSKCC_overlap.tsv", sep = "\t", index = False)
## extract words before colon
## @value: 
def getBefore(value):
	if isinstance(value, list):
		values = []
		for each in value:
			values.append(each.split(":")[0])
		return " ".join(values)
	else:
		return value.split(":")[0]
## check structured but not regular ingredient section content
def checkHerb():
	names = []
	try:
		with open(read_file, "r") as f:
			for line in f:
				data = json.loads(line)
				hdi = getBefore(data["herb-drug_interactions"])
				if "Common" in hdi:
					print("===================")
					print(hdi)
					names.append(data["name"])
					print("===================")
		print(len(names))
		print(names)
	except IOError:
		print("No such file.")
## main function
def run():
	#checkHerb()
	
	if os.path.exists("MSKCC_overlap.json"):
		change()
	else:
		extract_herb()
		change()
	'''
	## merge all contents into one file
	if os.path.exists("cancer_pu.json"):
		data = merge()
		data = addFlag(data, "merged_cancer.tsv")
		stat(data)
	else:
		extract()
		data = merge()
		data = addFlag(data, "merged_cancer.tsv")
		stat(data)
	'''

if __name__ == "__main__":
    run()