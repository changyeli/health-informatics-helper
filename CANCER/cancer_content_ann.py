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
                        "food_sources", "mechanism_of_action", "contraindications"]
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

    # select MM annotated term based on list elements
    # @output: list of MM output, split by "\n"
    # return a list of annotated terms

    def selectChunks(self, output):
        chunk = [each for each in output if not each.startswith("Processing")]
        chunk = [each for each in chunk if not each.startswith("Phrase")]
        chunk = [each for each in chunk if not each.startswith("Meta Mapping")]
        chunk = list(filter(None, chunk))
        chunk = [each.lstrip() for each in chunk]
        chunk = [each for each in chunk if each != " "]
        #chunk = [self.remove(each) for each in chunk]
        return chunk

    # flatten nested list
    # @patterns: nested list, extracted suing re.findall(r'\[(.*?)\]', s)
    # return unique flattened list
    def flatten(self, patterns):
        # check if the list is nested
        if all(isinstance(i, list) for i in patterns):
            patterns = [item for sublist in patterns for item in sublist]
            patterns = list(set(patterns))
            patterns = list(filter(None, patterns))
            return patterns
        else:
            return patterns

    # select term with max score
    # if has the same max score, select the term with more semantic types
    # @terms: a list of output from self.limit() function
    # return qualified terms

    def qualified(self, terms):
        # if current term is empty, i.e. last few lines in MM output
        if not terms:
            return " "
        else:
            scores = [re.findall(r"^\d+", each) for each in terms]
            scores = [each[0] for each in scores]
            max_index = [index for index, value in enumerate(
                                    scores) if value == max(scores)]
            temp_term1 = itemgetter(*max_index)(terms)
            # if has a single max score
            if len(temp_term1) == 1:
                if isinstance(temp_term1, tuple):
                    return list(Counter(temp_term1).keys())
                else:
                    return temp_term1
            else:
                # find term with most number of semantic types
                patterns = [re.findall(r'\[(.*?)\]', each) for each in temp_term1]
                lens = [len(each) for each in patterns]
                # if all terms have same number of semantic types
                if len(set(lens)) == 1:
                    if isinstance(temp_term1, tuple):
                        return list(Counter(temp_term1).keys())
                    else:
                        return temp_term1
                else:
                    max_len = [index for index, value in enumerate(
                                    lens) if value == max(lens)]
                    final_term = itemgetter(*max_len)(temp_term1)
                    return final_term
        
    # get MM chunks that have required semantic types
    # @output: MM output
    # @types: required semantic types, in list format
    # @splitFunction: the function to split MM semantic types

    def limit(self, chunks, types, splitFunction):
        # if there is no such MM output
        if not chunks:
            print("No valid MM output chunk")
            return " "
        else:
            # if there is only one term in the chunk
            if len(chunks) == 1:
                s = chunks[0]
                patterns = re.findall(r'\[(.*?)\]', s)
                patterns = splitFunction(patterns)
                #patterns = self.flatten(patterns)
                # check if the annotated term has required semantic types
                if self.isSubset(patterns, types):
                    return s
                else:
                    print("no terms match required semantic types")
            # if there are multiple terms in the chunk
            else:
                qualified_terms = []
                for each in chunks:
                    patterns = re.findall(r'\[(.*?)\]', each)
                    patterns = splitFunction(patterns)
                    #patterns = self.flatten(patterns)
                    if self.isSubset(patterns, types):
                        qualified_terms.append(each)
                return qualified_terms

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

    # split semantic type into list
    # @patterns: extracted semantic types
    # return split patterns

    def getSplit(self, patterns):
        patterns = list(filter(None, patterns))
        if len(patterns) == 1:
            return patterns
        else:
            new_patterns = []
            for each in patterns:
                if isinstance(each, list):
                    new_patterns.append(each[0])
                else:
                    new_patterns.append(each)
            return new_patterns

    # output selection main function
    # @output: MM output, in string format
    # @splitFun: split function for MM output semantic types
    # return qualified terms

    def outputHelper(self, output, types, splitFun):
        # remove first line
        output = output.split("\n")[1:]
        # find index of line starting with "Meta Mapping ()"
        chunks = self.selectChunks(output)
        terms = self.limit(chunks, types, splitFun)
        if isinstance(terms, str):
            return terms
        elif isinstance(terms, list):
            return self.qualified(terms)
        else:
            return " "

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
                    anno = self.outputHelper(output, hdi_types, self.getSplitHDI)
                    if isinstance(anno, list):
                        anno_terms.extend(anno)
                    else:
                        anno_terms.append(anno)


            else:
                command = mm.getComm(content, additional=" --term_processing")
                output = mm.getAnnNoOutput(command).decode("utf-8")
                anno = self.outputHelper(output, hdi_types, self.getSplitHDI)
                if isinstance(anno, list):
                    anno_terms.extend(anno)
                else:
                    anno_terms.append(anno)
            if not anno_terms:
                data["HDI"] = content
                data["annotated_HDI"] = " "
            else:
                anno_terms = list(filter(None, anno_terms))
                anno_terms = [each for each in anno_terms if each != " "]
                data["HDI"] = content
                data["annotated_HDI"] = self.concate(anno_terms, "\n")
        self.writeContent(output_file, data)

    # AR annotation process
    # get AR content annotated using MEDDRA
    # @name: herb name
    # @ar: AR content
    # @meddra: MEDDRA constructor
    # @output_file: the local file name to write

    def ADRprocess(self, name, ar, meddra, output_file):
        data = {}
        data["name"] = name
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
            print(res)
        #self.writeContent(output_file, data)


    # PU annotation process main function
    # get AR content annotated using MetaMap
    # @name: herb name
    # @pu: PU content
    # @mm: MetaMap constructor
    # @output_file: the local file name to write

    def PUProcess(self, name, pu, mm, output_file):
        data = {}
        data["name"] = name
        content = self.remove(pu)
        pu_types = self.readTypes("PU")
        # if pu is empty
        if not content:
            data["PU"] = " "
            data["annotated_PU"] = " "
        else:
            anno_terms = []
            if isinstance(content, list):
                for each in content:
                    command = mm.getComm(each, additional=" --term_processing")
                    output = mm.getAnnNoOutput(command).decode("utf-8")
                    anno = self.outputHelper(output, pu_types, self.getSplit)
                    if isinstance(anno, list):
                        anno_terms.extend(anno)
                    else:
                        anno_terms.append(anno)
            else:
                command = mm.getComm(content, additional=" --term_processing")
                output = mm.getAnnNoOutput(command).decode("utf-8")
                anno = self.outputHelper(output, pu_types, self.getSplit)
                if isinstance(anno, list):
                    anno_terms.extend(anno)
                else:
                    anno_terms.append(anno)
            if not anno_terms:
                data["HDI"] = content
                data["annotated_HDI"] = " "
            else:
                anno_terms = list(filter(None, anno_terms))
                anno_terms = [each for each in anno_terms if each != " "]
                data["HDI"] = content
                data["annotated_HDI"] = self.concate(anno_terms, "\n")
        self.writeContent(output_file, data)


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
                    print(herb["name"])
                    # HDI
                    
                    print("working on HDI annotation")
                    self.HDIprcess(herb["name"], herb["herb-drug_interactions"], mm,"overlap_hdi.tsv")
                    
                    # ADR
                    print("working on AR annotation")
                    self.ADRprocess(herb["name"], herb["adverse_reactions"], meddra, "overlap_adr.tsv")
                    # PU
                    print("working on PU annotation")
                    self.PUProcess(herb["name"], herb["purported_uses"], mm, "overlap_pu.tsv")
                
                else:
                    pass
    # merge all overlap annotated files

    def mergeAll(self):
        overlap_hdi = pd.read_csv(os.path.join(self.file_location,
                                               "overlap_hdi.tsv"), header=None, sep="\t")
        overlap_hdi.columns = ["name", "HDI", "annotated_HDI"]
        overlap_adr = pd.read_csv(os.path.join(self.file_location,
                                               "overlap_adr.tsv"), header=None, sep="\t")
        overlap_adr.columns = ["name", "ADR", "annotated_ADR"]
        overlap_pu = pd.read_csv(os.path.join(self.file_location,
                                              "overlap_pu.tsv"), header=None, sep="\t")
        overlap_pu.columns = ["name", "PU", "annotated_PU"]
        overlap_hdi["ADR"] = overlap_adr["ADR"].values.tolist()
        overlap_hdi["annotated_ADR"] = overlap_adr["annotated_ADR"].values.tolist()
        overlap_hdi["PU"] = overlap_pu["PU"].values.tolist()
        overlap_hdi["annotated_PU"] = overlap_pu["annotated_PU"].values.tolist()

        overlap_rest = pd.read_csv(os.path.join(self.file_location,
                                                "overlap_rest.tsv"), header=None, sep="\t")
        overlap_rest.columns = ['name', 'last_updated', 'common_name', 'scientific_name',
                                'warnings', 'clinical_summary', 'food_sources', 'mechanism_of_action']
        full = overlap_hdi.merge(overlap_rest, on="name")
        full.to_csv(os.path.join(self.file_location,
                                 "overlap_mskccV152.tsv"), index=False, sep="\t")
        
    # read the rest of headers and content

    def readRest(self):
        with open(os.path.join(self.file_location, self.read_file), "r") as f:
            for line in f:
                herb = json.loads(line)
                data = {}
                if herb["name"] in self.overlap_herbs:
                    data["name"] = herb["name"]
                    for each in self.headers:
                        data[each] = herb[each]
                    with open(os.path.join(self.file_location, "overlap_rest.tsv"), "a") as output:
                        w = csv.writer(output, delimiter="\t")
                        w.writerow([v for v in data.values()])

    # test
    def test(self):
        # Ginkgo
        #mm = umlsAnn()
        #mm.start()
        # get meddra constructor
        meddra = meddraAnn()
        with open(os.path.join(self.file_location, self.read_file), "r") as f:
            for line in f:
                herb = json.loads(line)
                if herb["name"] in self.overlap_herbs:
                    # ADR
                    print("working on AR annotation")
                    self.ADRprocess(herb["name"], herb["adverse_reactions"], meddra, "overlap_adr.tsv")
    # main function

    def run(self):
        #self.readFile()
        #self.readRest()
        #self.mergeAll()
        self.test()

if __name__ == "__main__":
    x = main()
    x.run()
