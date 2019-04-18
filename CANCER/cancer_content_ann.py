import json
import re
import csv
import os
from umlsAnn import umlsAnn
from meddraAnn import meddraAnn
from collections import Counter
from operator import itemgetter 
import pandas as pd
# main class for getting annotation


class main(object):
    def __init__(self):
        # get annotation using bioportal for adverse reaction section
        self.read_file = "cancer_herb_content.json"
        # this file location
        self.file_location = os.path.dirname(os.path.realpath(__file__))
        # overlap ingredients
        self.overlap_herbs = ["Andrographis", "Blue-Green Algae", "Bromelain", "Butterbur",
                              "Calcium", "Cranberry", "Elderberry", "Fenugreek",
                              "Flaxseed", "Folic Acid", "Ginkgo", "Grape",
                              "Hops", "Indole-3-Carbinol", "Kudzu", "L-Arginine",
                              "L-Tryptophan", "Melatonin", "N-Acetyl Cysteine", "Pomegranate",
                              "Red Clover", "Reishi Mushroom", "Shiitake Mushroom", "Siberian Ginseng",
                              "Turmeric", "Vitamin B12", "Vitamin E", "Vitamin K",
                              "Blue-green Algae", "Folate", "Grape seeds", "Arginine",
                              "5-HTP", "N-Acetylcysteine"]
        # remove "herb-drug_interactions", "adverse_reactions", "purported_uses", "contraindications" for specific pre-processing
        self.headers = ["last_updated", "common_name", "scientific_name",
                        "warnings", "clinical_summary",
                        "food_sources", "mechanism_of_action"]
    # concate list of string into single string
    # @value: content to be concated
    # @sep: separator, i.e. "\t", "\n", " "

    def concate(self, value, sep):
        if isinstance(value, list):
            return (sep.join(value))
        else:
            return value
    # remove all non-ASCII characters in the content
    # remove contents inside of ()
    # @value: the content needs to be cleaned

    def remove(self, value):
        if isinstance(value, list):
            value = [re.sub(r'[^\x00-\x7F]+', " ", each) for each in value]
            value = [re.sub(r" ?\([^)]+\)", "", each) for each in value]
            return value
        else:
            value = re.sub(r'[^\x00-\x7F]+', " ", value)
            value = re.sub(r" ?\([^)]+\)", "", value)
            return value
    # get content before ":"
    # @content: content need to be split
    # return a list of contents that are before ":"

    def getBefore(self, content):
        if isinstance(content, list):
            value = [each.split(":")[0] for each in content]
            return value
        else:
            value = content.split("\n")
            value = [each.split(":")[0] for each in value]
            return value
    # write to local .tsv file if the content exists
    # @output_file: file to write
    # @data: extracted herb information in dict form

    def writeContent(self, output_file, data):
        with open(os.path.join(self.file_location, output_file), "a") as output:
            w = csv.writer(output, delimiter="\t")
            w.writerow([v for v in data.values()])

    # check if a list is a subset of another list
    # @list1: shorter list
    # @list2: longer list
    # return true if list1 is a subset of list2, otherwise false
    def isSubset(self, list1, list2):
        return all(elem in list2 for elem in list1)

    # process MM JSON output
    # @output: MM output, string type
    # @types: list of semantic types
    # return the max scored item
    # if it has more than one max scored item, return the item with more MM types
    # TODO: need to rewrite this part to avoid nested loop

    def selectOutput(self, output, types):
        mm_types = self.readTypes(types)
        mm_output = json.loads(output)
        docs = mm_output["AllDocuments"]  # must be []
        for doc in docs:
            document = doc["Document"]
            utterances = document["Utterances"]  # must be []
            for each in utterances:
                phrases = each["Phrases"]  # must be []
                for phrase in phrases:
                    mappings = phrase["Mappings"]  # must be []
                    for item in mappings:
                        candidates = item["MappingCandidates"]  # must be []
                        # get scores
                        scores = [int(can["CandidateScore"])
                                  for can in candidates]
                        # find max-scored index
                        max_index = [index for index, val in enumerate(
                            scores) if val == max(scores)]
                        # find item with max_index
                        max_candidate = [itemgetter(*max_index)(candidates)]
                        # if a term has multiple records, keep the one with more types
                        print(max_candidate)
                        print("\n")

    # HDI annotation process
    # get HDI content annotated using MM
    # @name: herb name that in the overlap
    # @hdi: HDI content for the herb
    # @mm: MetaMap constructor
    # @output_file: the local file name to write

    def HDIprcess(self, name, hdi, mm, output_file):
        data = {}
        data["name"] = name
        content = self.remove(self.getBefore(hdi))
        # if hdi is empty
        if not content:
            data["HDI"] = " "
            data["annotated_HDI"] = " "
        # hdi is not empty
        else:
            if isinstance(content, list):
                for each in content:
                    command = mm.getComm(each, additional=" --term_processing")
                    output = mm.getAnn(command, "JSON").decode("utf-8")
                    # remove output first line
                    output = "\n".join(output.split("\n")[1:])
                    self.selectOutput(output, "HDI")
            else:
                command = mm.getComm(content, additional=" --term_processing")
                output = mm.getAnn(command, "JSON").decode("utf-8")
                output = "\n".join(output.split("\n")[1:])
                self.selectOutput(output, "HDI")
        #self.writeContent(output_file, data)
    # AR annotation process
    # get AR content annotated using MEDDRA
    # @name: herb name
    # @ar: AR content
    # @meddra: MEDDRA constructor
    # @output_file: the local file name to write

    def ADRprocess(self, name, ar, meddra, output_file):
        data = {}
        data["name"] = name
        print(name)
        ar = self.remove(self.concate(ar, " "))
        # if ar is empty
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
    # purposed uses annotation process
    # get purposed uses content annotated using MM
    # @name: herb name that in the overlap
    # @pu: contraindications content for the herb
    # @mm: MetaMap constructor
    # @output_file: the local file name to write

    def PUprpcess(self, name, pu, mm, output_file):
        data = {}
        data["name"] = name
        pu = self.remove(self.concate(pu))
        # if pu is empty
        if not pu:
            data["PU"] = " "
            data["annotated_PU"] = " "
        # hdi is not empty
        else:
            command = mm.getComm(pu, additional="--term_processing")
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
    # read MM type file
    # @fun: annotation section names, i.e. PU, HDI
    # each section will return a list of MM types

    def readTypes(self, fun):
        full_types = pd.read_csv(os.path.join(self.file_location, "mmmap.txt"), sep="|",
                                 header=None, index_col=False)
        full_types.columns = ["abbrev", "tui", "types"]
        if fun.upper() not in ["HDI", "PU", "CON"]:
            raise ValueError("Currently only supports HDI, PU and Con.")
        else:
            # hdi mm types
            if fun.upper() == "HDI":
                hdi_types = pd.read_csv(
                    os.path.join(self.file_location, "hdi_types.txt"), sep="|", header=None, index_col=False)
                hdi_types.columns = ["group", "group_name", "tui", "types"]
                hdi_types = hdi_types["tui"].values
                hdi = full_types.loc[full_types["tui"].isin(hdi_types)]
                return hdi["abbrev"].values
            # pu mm types
            if fun.upper() == "PU":
                pu_types = pd.read_csv(
                    os.path.join(self.file_location, "pu_types.txt"), sep="|", header=None, index_col=False)
                pu_types.columns = ["group", "group_name", "tui", "types"]
                pu_types = pu_types["tui"].values
                pu = full_types.loc[full_types["tui"].isin(pu_types)]
                return pu["abbrev"].values
            # con mm types
            if fun.upper() == "CON":
                con_types = pd.read_csv(
                    os.path.join(self.file_location, "con_types.txt"), sep="|", header=None, index_col=False)
                con_types.columns = ["group", "group_name", "tui", "types"]
                con_types = con_types["tui"].values
                con = full_types.loc[full_types["tui"].isin(pu_types)]
                return con["abbrev"].values
    # read the herb file

    def readFile(self):
        # start mm server
        mm = umlsAnn()
        mm.start()
        # get meddra constructor
        meddra = meddraAnn()
        with open(os.path.join(self.file_location, self.read_file), "r") as f:
            for line in f:
                herb = json.loads(line)
                if herb["name"] in self.overlap_herbs:
                    # pass
                    # HDI
                    self.HDIprcess(
                        herb["name"], herb["herb-drug_interactions"], mm, "overlap_hdi.tsv")
                    break
                    #self.writeContent("overlap_hdi.tsv", data)
                    # ADR
                    #self.ADRprocess(herb["name"], herb["adverse_reactions"], meddra, "overlap_adr.tsv")

                    ##self.PUprpcess(herb["name"], herb["purported_uses"], mm, "overlap_con.tsv")
                else:
                    pass
    # main function

    def run(self):
        # self.readTypes()
        self.readFile()


if __name__ == "__main__":
    x = main()
    x.run()
