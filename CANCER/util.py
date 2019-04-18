import json
file = "cancer_herb_content.json"
## script for multiple inspections
def test():
	with open(file, "r") as f:
		for line in f:
			data = json.loads(line)
			if data["name"] ==  "Vitamin E":
				print(data["herb-drug_interactions"])

if __name__ == "__main__":
    test()