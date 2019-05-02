# driver function for annotation process
from umlsAnn import umlsAnn
from meddraAnn import meddraAnn
import json
import os
class driver(object):
	def __init__(self, location):
		# MetaMap location
		self.location = location
		# get this python script location
		self.path = os.path.dirname(os.path.abspath(__file__))
		# stored MSKCC data
		self.read_file = "cancer_herb_content.json"
	def readFile(self):
		with open(os.path.join(self.path, self.read_file), "r") as f:
			for line in f:
				herb = json.loads(line)
				name = herb["name"]
				hdi = herb["herb-drug_interactions"]
				pu = herb["purported_uses"]
				mm = umlsAnn(self.location)
				data = mm.HDIprcess(name, hdi)
				temp_data = mm.PUProcess(name, pu)
				print("===============")
				print(data)
				print(temp_data)
				print("===============")
	def run(self):
		self.readFile()

if __name__ == "__main__":
    x = driver("/Users/Changye/Documents/workspace/public_mm")
    x.run()


