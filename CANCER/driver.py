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
		self.read_file = "cancer_herb_content.json"
		# remove "herb-drug_interactions", "adverse_reactions", "purported_uses" for specific pre-processing
		self.headers = ["contraindications", "last_updated", "common_name", "scientific_name", "warnings", "clinical_summary", "food_sources", "mechanism_of_action"]
	def readFile(self):
		mm = umlsAnn(self.location)
		meddra = meddraAnn()
		with open(os.path.join(self.path, self.read_file), "r") as f:
			for line in f:
				data = {}
				herb = json.loads(line)
				name = herb["name"]
				# get annotations
				hdi_content = herb["herb-drug_interactions"]
				pu_content = herb["purported_uses"]
				adr_content = herb["adverse_reactions"]
				adr_data = meddra.ADRprocess(name, adr_content)
				hdi_data = mm.HDIprcess(name, hdi_content)
				pu_data = mm.PUProcess(name, pu_content)
				# write to dict
				data["name"] = name
				data.update(hdi_data)
				data.update(pu_data)
				data.update(adr_data)
				# read the remaining headers and their contents
				for each in self.headers:
					data[each] = herb[each]
				# write to local file
				self.write(data)
	## write to local file
	def write(self, data):
		with open("cancer_ann_data.jsonl", "a") as output:
			json.dump(data, output)
			output.write("\n")
	def run(self):
		self.readFile()

if __name__ == "__main__":
    x = driver("/Users/Changye/Documents/workspace/public_mm")
    x.run()


