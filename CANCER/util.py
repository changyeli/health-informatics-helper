import json, os.path
import pandas as pd
file = "cancer_herb_content.json"
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
def run():
	if os.path.exists("cancer_pu.json"):
		data = merge()
		data = addFlag(data, "merged_cancer.csv")
		stat(data)
	else:
		extract()
		data = merge()
		data = addFlag(data, "merged_cancer.csv")
		stat(data)

if __name__ == "__main__":
    run()