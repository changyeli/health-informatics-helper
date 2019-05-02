# driver function for annotation process
from umlsAnn import umlsAnn
from meddraAnn import meddraAnn
import json
class driver(object, location):
	def __init__(self):
		# MetaMap location
		self.location = location
		# stored MSKCC data
		self.read_file = "cancer_herb_content.json"
		# remove "herb-drug_interactions", "adverse_reactions", "purported_uses" for specific pre-processing
        self.headers = ["contraindications", "last_updated", "common_name", "scientific_name", "warnings", "clinical_summary","food_sources", "mechanism_of_action"]

