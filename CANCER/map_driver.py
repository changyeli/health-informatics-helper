# driver function for annotation process
from umlsAnn import umlsAnn
from meddraAnn import meddraAnn
import json
import os
import pickle
class driver(object):
	def __init__(self, location):
		# MetaMap location
		self.location = location
		# get this python script location
		self.path = os.path.dirname(os.path.abspath(__file__))
		# stored MSKCC data
		self.read_file = "cancer_herb_content.jsonl"
		# remove "herb-drug_interactions", "adverse_reactions", "purported_uses" for specific pre-processing
		self.headers = ["contraindications", "last_updated", "common_name", "scientific_name", "warnings", "clinical_summary", "food_sources", "mechanism_of_action"]
	def readFile(self):
		meddra = meddraAnn()
		mm = umlsAnn(self.location)
		mm.start()
		with open(os.path.join(self.path, self.read_file), "r") as f:
			for line in f:
				data = {}
				herb = json.loads(line)
				name = herb["name"]
				data["name"] = name
				print("-----------------")
				print(name)
				# get annotations
				hdi_content = herb["herb-drug_interactions"]
				pu_content = herb["purported_uses"]
				adr_content = herb["adverse_reactions"]
				data["HDI"] = hdi_content
				data["annotated_HDI"] = mm.process(name, hdi_content, "HDI")
				print(data["annotated_HDI"])
				data["PU"] = pu_content
				data["annotated_PU"] = mm.process(name, pu_content, "PU")
				print(data["annotated_PU"])
				data["ADR"] = adr_content
				data["annotated_ADR"] = meddra.main(adr_content)
				# rest components
				for item in self.headers:
					data[item] = herb[item]
				print("-----------------")
				self.write(data)
				
	## write to local file
	def write(self, data):
		with open(os.path.join(self.path, "cancer_ann_data.jsonl"), "a") as output:
			json.dump(data, output)
			output.write("\n")
	def run(self):
		self.readFile()

if __name__ == "__main__":
    x = driver("/Users/Changye/Documents/workspace/public_mm")
    x.run()


