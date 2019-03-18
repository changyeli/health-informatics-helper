import json
file = "cancer_herb_content.json"
output = "cancer_sub_content.json"
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
                if "herb-drug_interactions" in herb:
                    hdi = herb["herb-drug_interactions"]
                    data["herb-drug_interactions"] = hdi
                if "adverse_reactions" in herb:
                    ar = herb["adverse_reactions"]
                    data["adverse_reactions"] = ar
                if "purposed_uses" in herb:
                    pu = herb["purposed_uses"]
                    data["purposed_uses"] = pu
                ## if the herb has more than 1 desired element
                if len(data) > 1:
                    write(data)
                else:
                    pass
    except IOError:
        print("No such file. Please run cancer_context.py first.")
## write to local file
## @value: desired cancer herb content
def write(value):
    with open(output, "a") as f:
        json.dump(value, f)
        f.write("\n")
## main function
def run():
    print("start")
    extract()
    print("finish")

if __name__ == "__main__":
    run()