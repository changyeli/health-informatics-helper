import json, re, csv, os
from umlsAnn import umlsAnn
from meddraAnn import meddraAnn
from collections import Counter
import pandas as pd
## main class for getting annotation
class main(object):
    def __init__(self):
        ## get annotation using bioportal for adverse reaction section
        self.read_file = "cancer_herb_content.json"
        ## this file location
        self.file_location = os.path.dirname(os.path.realpath(__file__))
        ## overlap ingredients
        self.overlap_herbs = ["Andrographis", "Blue-Green Algae", "Bromelain", "Butterbur",
                        "Calcium", "Cranberry", "Elderberry", "Fenugreek",
                        "Flaxseed", "Folic Acid", "Ginkgo", "Grape",
                        "Hops", "Indole-3-Carbinol", "Kudzu", "L-Arginine",
                        "L-Tryptophan", "Melatonin", "N-Acetyl Cysteine", "Pomegranate",
                        "Red Clover", "Reishi Mushroom", "Shiitake Mushroom", "Siberian Ginseng", 
                        "Turmeric", "Vitamin B12", "Vitamin E", "Vitamin K",
                        "Blue-green Algae", "Folate", "Grape seeds", "Arginine",
                        "5-HTP", "N-Acetylcysteine"]
        ## remove "herb-drug_interactions", "adverse_reactions", "purported_uses", "contraindications" for specific pre-processing
        self.headers = ["last_updated", "common_name", "scientific_name",
                    "warnings",  "clinical_summary",
                "food_sources", "mechanism_of_action"]
    ## concate list of string into single string
    ## @value: content to be concated
    ## @sep: separator, i.e. "\t", "\n", " "
    def concate(self, value, sep):
        if isinstance(value, list):
            return (sep.join(value))
        else:
            return value
    ## remove all non-ASCII characters in the content
    ## remove contents inside of ()
    ## @value: the content needs to be cleaned
    def remove(self, value):
        if isinstance(value, list):
            value = [re.sub(r'[^\x00-\x7F]+', " ", each) for each in value]
            value = [re.sub(r" ?\([^)]+\)", "", each) for each in value]
            return value
        else:
            value = re.sub(r'[^\x00-\x7F]+', " ", value)
            value = re.sub(r" ?\([^)]+\)", "", value)
            return value
    ## get content before ":"
    ## @content: content need to be split 
    def getBefore(self, content):
        if isinstance(content, list):
            value = [each.split(":")[0] for each in content]
            return value
        else:
            return content.split(":")[0]
    ## write to local .tsv file if the content exists
    ## @output_file: file to write
    ## @data: extracted herb information in dict form
    def writeContent(self, output_file, data):
        with open(os.path.join(self.file_location, output_file), "a") as output:
            w = csv.writer(output, delimiter = "\t")
            w.writerow([v for v in data.values()])
    ## HDI annotation process
    ## get HDI content annotated using MM
    ## @name: herb name that in the overlap
    ## @hdi: HDI content for the herb
    ## @mm: MetaMap constructor
    ## @output_file: the local file name to write
    def HDIprcess(self, name, hdi, mm, output_file):
        data = {}
        data["name"] = name
        print(os.getcwd())
        hdi = self.remove(self.getBefore(hdi))
        ## if hdi is empty
        if not hdi:
            data["HDI"] = " "
            data["annotated_HDI"] = " "
        ## hdi is not empty
        else:
            if isinstance(hdi, list):
                for each in hdi:
                    command = mm.getComm(each, additional = " --term_processing")
                    print(command)
                    output = mm.getAnnNoOutput(each).decode("utf-8")
                    print(output)
            else:
                command = mm.getComm(hdi, additional = " --term_processing")
                output = mm.getAnnNoOutput(each).decode("utf-8")
                print(output)
        #self.writeContent(output_file, data)
    ## AR annotation process
    ## get AR content annotated using MEDDRA
    ## @name: herb name
    ## @ar: AR content
    ## @meddra: MEDDRA constructor
    ## @output_file: the local file name to write
    def ADRprocess(self, name, ar, meddra, output_file):
        data = {}
        data["name"] = name
        print(name)
        ar = self.remove(self.concate(ar, " "))
        ## if ar is empty
        if not ar:
            data["ADR"] = " "
            data["annotated_ADR"] = " "
        else:
            res = meddra.adrProcess(ar)
            res = [x.lower() for x in res]
            res = self.concate(list(Counter(res).keys()), "\n")
            data["ADR"] = ar
            data["annotated_ADR"] = res
        self.writeContent(output_file, data)
    ## purposed uses annotation process
    ## get purposed uses content annotated using MM
    ## @name: herb name that in the overlap
    ## @pu: contraindications content for the herb
    ## @mm: MetaMap constructor
    ## @output_file: the local file name to write
    def PUprpcess(self, name, pu, mm, output_file):
        data = {}
        data["name"] = name
        pu = self.remove(self.concate(pu))
        ## if pu is empty
        if not pu:
            data["PU"] = " "
            data["annotated_PU"] = " "
        ## hdi is not empty
        else:
            command = mm.getComm(pu, additional = "--term_processing")
            output = mm.getAnnNoOutput(command).decode("utf-8")
            print("=======================================")
            print(name)
            print(pu)
            print("---------------------------------------")
            print(output)
            print("---------------------------------------")
            res = output.split("\b")
            res = list(set(res))
            res = "\n".join(res)
            print(res)
            data["annotated_PU"] = res
            data["PU"] = pu
            print("=======================================")
    ## read MM type file
    ## @fun: annotation section names, i.e. PU, HDI
    ## each section will return a list of MM types
    def readTypes(self, fun):
        full_types = pd.read_csv("mmtypes.txt", sep = "|", header = None, index_col = False)
        full_types.columns = ["group", "name", "tui", "types"]
        if fun not in ["PU, HDI, CON"]:
            raise ValueError("Currently only supports PU, HDI and CON")
        else:
            if fun.upper() == "PU":
                pu_types = full_types.loc[full_types["group"].isin(["DISO", "PHYS", "PROC"])]
                return pu_types["types"].values()
            if fun.upper() == "HDI":
                hdi_types = full_types.loc[full_types["group"] == "CHEM"]
                return hdi_types["types"].values()
            if fun.upper() == "CON":
                con_types = full_types.loc[full_types["group"].isin(["DISO", "PHYS", "PROC"])]
                return con_types["types"].values()
    ## read the herb file
    def readFile(self):
        ## start mm server
        mm = umlsAnn()
        mm.start()
        ## get meddra constructor
        meddra = meddraAnn()
        with open(os.path.join(self.file_location, self.read_file), "r") as f:
            for line in f:
                herb = json.loads(line)
                if herb["name"] in self.overlap_herbs:
                    pass
                    ## HDI
                    #self.HDIprcess(herb["name"], herb["herb-drug_interactions"], mm, "overlap_hdi.tsv")
                    #self.writeContent("overlap_hdi.tsv", data)
                    ## ADR
                    #self.ADRprocess(herb["name"], herb["adverse_reactions"], meddra, "overlap_adr.tsv")
            
                    ##self.PUprpcess(herb["name"], herb["purported_uses"], mm, "overlap_con.tsv")
                else:
                    pass
    ## main function
    def run(self):
        self.readTypes()
if __name__ == "__main__":
    x = main()
    x.run()