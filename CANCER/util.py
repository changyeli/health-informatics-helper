import re
import os
import json
import pandas as pd
from operator import itemgetter
from umlsAnn import umlsAnn


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

    # check if a list is a subset of another list
    # @list1: shorter list
    # @list2: longer list
    # return true if list1 is a subset of list2, otherwise false

    def isSubset(self, list1, list2):
        return all(elem in list2 for elem in list1)

    # select MM annotated term based on list elements
    # @output: list of MM output, split by "\n"
    # return a list of annotated terms

    def selectChunks(self, output):
        mm_index = [index for index, value in enumerate(
            output) if value.startswith("Meta Mapping")]
        # if no MM output
        if not mm_index:
            pass
        else:
            # find every two index as chunk
            # only has one annotated term
            if len(mm_index) == 1:
                annotated_terms = output[mm_index[0] + 1:]
                # remove empty string from the list
                annotated_terms = list(filter(None, annotated_terms))
                annotated_terms = [each.lstrip() for each in annotated_terms]
                print(annotated_terms)
                return(annotated_terms)
            else:
                chunk = []
                for v, w in zip(mm_index[:-1], mm_index[1:]):
                    chunk.append([v, w])
                # if only has one pair
                if len(chunk) == 1:
                    chunk = chunk[0]
                    annotated_terms = []
                    terms = output[chunk[0] + 1:chunk[1]]
                    annotated_terms.extend(terms)
                    terms = output[chunk[1] + 1:]
                    annotated_terms.extend(terms)
                    annotated_terms = list(filter(None, annotated_terms))
                    annotated_terms = [each.lstrip()
                                       for each in annotated_terms]
                    print(annotated_terms)
                    return annotated_terms
                else:
                    annotated_terms = []
                    for each in chunk:
                        try:
                            terms = output[each[0] + 1:each[1]]
                            terms = list(filter(None, terms))
                            terms = [each.lstrip() for each in terms]
                            annotated_terms.extend(terms)
                        except IndexError:
                            terms = output[each[0] + 1:]
                            terms = list(filter(None, terms))
                            terms = [each.lstrip() for each in terms]
                            annotated_terms.extend(terms)
                    print(annotated_terms)
                    return(annotated_terms)

    # output selection main function
    # @output: MM output, in string format
    # return qualified terms

    def HDIoutputHelper(self, output, types):
        # remove first line
        output = output.split("\n")[1:]
        # find index of line starting with "Meta Mapping ()"
        terms = self.selectChunks(output)

    # split semantic types string into list
    # specifically for HDI content
    # @patterns: extracted semantic types strings

    def getSplitHDI(self, patterns):
        new_patterns = []
        for each in patterns:
            if isinstance(each, list):
                new_patterns.extend(each)
            if isinstance(each, str):
                new_patterns.append(each)
        new_patterns = list(set(new_patterns))
        res = []
        for each in new_patterns:
            if "Amino Acid, Peptide, or Protein" in each:
                each = each.replace("Amino Acid, Peptide, or Protein", "")
                res.append("Amino Acid, Peptide, or Protein")
                res.append(each.split(",")[-1])
            elif "Element, Ion, or Isotope" in each:
                each = each.replace("Element, Ion, or Isotope", "")
                res.append("Element, Ion, or Isotope")
                res.append(each.split(",")[-1])
            elif "Indicator, Reagent, or Diagnostic Aid" in each:
                each = each.replace(
                    "Indicator, Reagent, or Diagnostic Aid", "")
                res.append("Indicator, Reagent, or Diagnostic Aid")
                res.append(each.split(",")[-1])
            elif "Nucleic Acid, Nucleoside, or Nucleotide" in each:
                each = each.replace(
                    "Nucleic Acid, Nucleoside, or Nucleotide", "")
                res.append("Nucleic Acid, Nucleoside, or Nucleotide")
                res.append(each.split(",")[-1])
            else:
                res.extend(each.split(","))
        return res

    # find qualified terms
    # select term in
    # select term with max score
    # if has the same max score, select the term with more semantic types
    # @terms: MM output chunk
    # @types: semantic types
    # return single qualified string

    def findHDIQualified(self, terms, types):
        # if there is no such term
        if terms is None:
            return " "
        else:
            # if there is only one term in the chunk
            if len(terms) == 1:
                s = terms[0]
                patterns = re.findall(r'\[(.*?)\]', s)
                patterns = self.getSplitHDI(patterns)
                # check if the annotated term has required semantic types
                if self.isSubset(patterns, types):
                    return s
            # if there are multiple terms in the chunk
            else:
                patterns = [re.findall(r'\[(.*?)\]', s) for s in terms]
                if not patterns:
                    return " "
                else:
                    patterns = self.getSplitHDI(patterns)
                    flags = [self.isSubset(each, types) for each in patterns]
                    flags_index = [index for index,
                                   value in enumerate(flags) if value]
                    # if none of the terms have required semantic types
                    if not flags_index:
                        print("no valid annotated terms")
                        return " "
                    else:
                        # if only one valid term
                        if len(flags_index) == 1:
                            terms_temp1 = terms[flags_index[0]]
                            return terms_temp1
                        else:
                            terms_temp1 = list(itemgetter(*flags_index)(terms))
                            scores = [re.findall(r"^\d+", each)
                                      for each in terms_temp1]
                            # remove empty scores
                            scores = list(filter(None, scores))
                            scores = [each[0] for each in scores]
                            max_index = [index for index, value in enumerate(
                                scores) if value == max(scores)]
                            terms_temp2 = itemgetter(*max_index)(terms_temp1)
                            return terms_temp2

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
        # HDI semantic types
        hdi_types = self.readTypes("HDI")
        # if hdi is empty
        if not content:
            data["HDI"] = " "
            data["annotated_HDI"] = " "
        # hdi is not empty
        else:
            anno_terms = []
            if isinstance(content, list):
                for each in content:
                    command = mm.getComm(each, additional=" --term_processing")
                    output = mm.getAnnNoOutput(command).decode("utf-8")
                    print(output)
                    anno = self.HDIoutputHelper(output, hdi_types)
                    anno_terms.append(anno)

            else:
                command = mm.getComm(content, additional=" --term_processing")
                output = mm.getAnnNoOutput(command).decode("utf-8")
                print(output)
                anno = self.HDIoutputHelper(output, hdi_types)
                anno_terms.append(anno)
            anno_terms = list(filter(None, anno_terms))
            data["HDI"] = content
            data["annotated_HDI"] = anno_terms

    # read the herb file

    def readFile(self):
        # start mm server
        mm = umlsAnn()
        mm.start()
        with open(os.path.join(self.file_location, self.read_file), "r") as f:
            for line in f:
                herb = json.loads(line)
                if herb["name"] in self.overlap_herbs:
                    print(herb["name"])
                    # HDI
                    self.HDIprcess(
                        herb["name"], herb["herb-drug_interactions"], mm,
                        "overlap_hdi.tsv")
                    break
                else:
                    pass

    # read MM type file
    # @fun: annotation section names, i.e. PU, HDI
    # each section will return a list of MM types

    def readTypes(self, fun):
        full_types = pd.read_csv(os.path.join(self.file_location, "mmtypes.txt"),
                                 sep="|", header=None, index_col=False)
        full_types.columns = ["abbrev", "name", "tui", "types"]
        if fun.upper() not in ["HDI", "PU", "CON"]:
            raise ValueError("Currently only supports HDI, PU and Con.")
        else:
            # hdi mm types
            if fun.upper() == "HDI":
                hdi_types = pd.read_csv(
                    os.path.join(self.file_location, "hdi_types.txt"),
                    sep="|", header=None, index_col=False)
                hdi_types.columns = ["group", "group_name", "tui", "types"]
                hdi_types = hdi_types["tui"].values.tolist()
                hdi = full_types.loc[full_types["tui"].isin(hdi_types)]
                return hdi["types"].values.tolist()
            # pu mm types
            if fun.upper() == "PU":
                pu_types = pd.read_csv(
                    os.path.join(self.file_location, "pu_types.txt"),
                    sep="|", header=None, index_col=False)
                pu_types.columns = ["group", "group_name", "tui", "types"]
                pu_types = pu_types["tui"].values.tolist()
                pu = full_types.loc[full_types["tui"].isin(pu_types)]
                return pu["types"].values.tolist()
            # con mm types
            if fun.upper() == "CON":
                con_types = pd.read_csv(
                    os.path.join(self.file_location, "con_types.txt"),
                    sep="|", header=None, index_col=False)
                con_types.columns = ["group", "group_name", "tui", "types"]
                con_types = con_types["tui"].values.tolist()
                con = full_types.loc[full_types["tui"].isin(con_types)]
                return con["types"].values.tolist()
    # main function

    def run(self):
        # self.readTypes()
        self.readFile()

        # self.test()
        # self.mergeAll()
        # self.readRest()
if __name__ == "__main__":
    x = main()
    x.run()
