import json
class cancer_section(object):
	def __init__(self):
		self.data = "cancer_herb_content.json"
	def load(self):
		try:
			print("Start to process file")
			with open(self.data, "r") as f:
				for line in f:
					output = {}
					line = json.loads(line)
					if line["herb-drug_interactions"] == "" or line["purported_uses"] == "":
						pass
					else:
						name = line["name"]
						hdi_subheaders = self.extract(line["herb-drug_interactions"])
						pu_subheaders = self.extract(line["purported_uses"])
						output[name] = {}
						output[name]["herb-drug_interactions"] = hdi_subheaders
						output[name]["purported_uses"] = pu_subheaders
						self.write(output)
			print("Finished")
		except IOError:
			print("No such file. Please run cancer_context.py first to get the file.")
	## remove special character, like •
	def remove(self, sentence):
		sentence = sentence.replace("\u2022", "")
		return sentence.strip()
	## check if ":" is in the element
	def check(self, element):
		if ":" in element:
			return True
		else:
			return False
	## write to local file
	def write(self, output):
		with open("cancer_subheaders.json", "a") as f:
			json.dump(output, f, indent = 4)
	## list process for herb["herb-drug_interactions"]
	## @values: list of strings from herb["herb-drug_interactions"] or herb["purported_uses"]
	def listProcess(self, values):
		subheaders = []
		for item in values:
			if self.check(item):
				item = self.remove(item)
				subheaders.append(item.split(": ")[0])
			else:
				item = self.remove(item)
				subheaders.extend(item.split("\n"))
		return subheaders
	## extracting HDI subheader
	## @context: herb["herb-drug_interactions"] for each herb
	def extract(self, context):
		total_subheaders = []
		## if context is in list format
		if isinstance(context, list):
			total_subheaders.extend(self.listProcess(context))
		else:
			values = context.split("\n")
			total_subheaders.extend(self.listProcess(values))
		return total_subheaders
	## main function
	def run(self):
		self.load()




x = cancer_section()
x.load()