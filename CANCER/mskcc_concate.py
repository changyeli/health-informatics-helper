## get the overlap ingredients, and get words before ":" for urported_uses
import json, csv
read_file = "cancer_herb_content.json"
output_file = "msckcc_overlap_v101.tsv"
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
## remove "herb-drug_interactions" for specific pre-processing
headers = ["last_updated", "common_name", "scientific_name",
			"warnings", "contraindications", "clinical_summary",
			"food_sources", "mechanism_of_action", "purported_uses",
			"adverse_reactions"]
## check flags for AR and HDI
## @ar: adverse_reactions content for each herb
## @hdi: herb-drug_interactions content for each herb
## @data: extracted herb information in dict form
def checkFlags(ar, hdi, data):
	if ":" in ar:
		data["ar_flag"] = True
	else:
		data["ar_flag"] = False
	if ":" in hdi:
		data["hdi_flag"] = True
	else:
		data["hdi_flag"] = False
## write to local file
## @output_file: file to write
## @data: extracted herb information in dict form
def write(output_file, data):
	with open(output_file, "a") as output:
		w = csv.writer(output, delimiter = "\t")
		w.writerows(data.items())

## concatenate list of string into string
## @value: herb["some-headers"]
def concate(value):
	if isinstance(value, list):
		return " ".join(value)
	else:
		return value
## extract words before colon
## @value: herb["herb-drug_interactions"]
def getBefore(value):
	if isinstance(value, list):
		values = []
		for each in value:
			values.append(each.split(":")[0])
		return " ".join(values)
	else:
		return value.split(":")[0]
## read file
def read(read_file):
	try:
		with open(read_file, "r") as f:
			for line in f:
				herb = json.loads(line)
				## extract overlap 
				if herb["name"] in overlap_herbs:
					data = {}
					data["name"] = herb["name"]
					## add flags for AR and HDI
					checkFlags(herb["adverse_reactions"], herb["herb-drug_interactions"], data)
					## special pre-processing for HDI
					data["herb-drug_interactions"] = getBefore(herb["herb-drug_interactions"])
					## adding remaining headers and associated content
					for each in headers:
						data[each] = concate(herb[each])
					write(output_file, data)
					## for inspection
					'''
					print("==========================")
					print(data["name"])
					print("----------------------")
					print("original AR: " + concate(herb["adverse_reactions"]))
					print("original HDI: " + concate(herb["herb-drug_interactions"]))
					print("----------------------")
					print("pre-processed AR: " + data["adverse_reactions"])
					print("pre-processed HDI: " + data["herb-drug_interactions"])
					print("==========================")
					print("\n")
					'''

	except IOError:
		print("No such file.")

## main function
def run():
	read(read_file)

if __name__ == "__main__":
    run()
