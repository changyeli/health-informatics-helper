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
		meddra = meddraAnn()
		with open(os.path.join(self.path, self.read_file), "r") as f:
			for line in f:
				# start MetaMap server
				mm = umlsAnn(self.location)
				mm.start()
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
				adr_data = meddra.main(adr_content)
				hdi_data = mm.HDIprcess(name, hdi_content)
				pu_data = mm.PUProcess(name, pu_content)
				data["HDI"] = hdi_data["HDI"]
				data["annotated_HDI"] = hdi_data["annotated_HDI"]
				data["PU"] = pu_data["PU"]
				data["annotated_PU"] = pu_data["annotated_PU"]
				data["ADR"] = adr_data["ADR"]
				data["annotated_ADR"] = adr_data["annotated_ADR"]
				'''
				# write to dict
				# read the remaining headers and their contents
				for each in self.headers:
					data[each] = herb[each]
				# write to local file
				self.write(data)
				'''
				print("-----------------")
				
	## write to local file
	def write(self, data):
		with open("cancer_ann_data.jsonl", "a") as output:
			json.dump(data, output)
			output.write("\n")
	def run(self):
		self.readFile()

	# test function
	def test(self):
		meddra = meddraAnn()
		mm = umlsAnn(self.location)
		mm.start()
		with open(os.path.join(self.path, self.read_file), "r") as f:
			for line in f:
				# start MetaMap server
				data = {}
				herb = json.loads(line)
				name = herb["name"]
				data["name"] = name
				print("-----------------")
				print(name)
				# get annotations
				hdi_content = herb["herb-drug_interactions"]
				pu_content = herb["purported_uses"]
				mm.process(name, pu_content, "PU")
				print("-----------------")

if __name__ == "__main__":
    x = driver("/Users/Changye/Documents/workspace/public_mm")
    x.test()


