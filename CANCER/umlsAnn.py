import os
import subprocess
from operator import itemgetter
import pandas as pd
import re
# get UMLS annotation for HDI, contradictions and purposed uses


class umlsAnn(object):
    def __init__(self, location):
        # MetaMap location
        #self.location = "/Users/Changye/Documents/workspace/public_mm"
        self.location = location
        # get this python script location
        self.path = os.path.dirname(os.path.abspath(__file__))
    # start MM server

    def start(self):
        os.chdir(self.location)
        output = subprocess.check_output(["./bin/skrmedpostctl", "start"])
        print(output)
    # get MM command
    # @value: content to be annotated
    # @additional: additional command to be added
    # @relax: true if use relax model for term processing
    # return MM commands
    # TODO: add more supported commands

    def getComm(self, value, additional="", relax=True):
        if relax:
            command = "echo " + value + " | " + "./bin/metamap16" + " -I " + "-Z 2018AB -V Base --relaxed_model " + \
                "--silent " + "--ignore_word_order" + additional  # +  "--term_processing "
            return command
        else:
            command = "echo " + value + " | " + "./bin/metamap16" + " -I " + "-Z 2018AB -V Base " + \
                "--silent " + "--ignore_word_order" + additional  # +  "--term_processing "
            return command

    # get annotated terms using UMLS without output format
    # @command: full command from @getComm function
    # return MM output, split by "\n"

    def getAnnNoOutput(self, command):
        # echo lung cancer | ./bin/metamap16 -I
        # check if value is valid
        output = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE).stdout.read()
        return output

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

    # split HDI content with "/" or ","
    # @content: herb["herb-drug_interacitons"]
    # return separate HDI content as list

    def SplitContent(self, content):
        if isinstance(content, list):
            split_content = []
            for each in content:
                if "/" in each:
                    items = each.split("/")
                    split_content.extend(items)
                elif "," in each:
                    items = each.split(",")
                    split_content.extend(items)
                else:
                    split_content.append(each)
            return split_content
        else:
            return content


    # get MM chunks that have required semantic types
    # @output: MM output
    # @types: required semantic types, in list format
    # @splitFunction: the function to split MM semantic types
    # return all qualified MM output

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
                    return temp_term1[0]
                else:
                    return temp_term1
            else:
                # find term with most number of semantic types
                patterns = [re.findall(r'\[(.*?)\]', each) for each in temp_term1]
                lens = [len(each) for each in patterns]
                # if all terms have same number of semantic types
                if len(set(lens)) == 1:
                    if isinstance(temp_term1, tuple):
                        return temp_term1[0]
                    else:
                        return temp_term1
                else:
                    max_len = [index for index, value in enumerate(
                                    lens) if value == max(lens)]
                    final_term = itemgetter(*max_len)(temp_term1)
                    return final_term

    # remove item if the item has same name for both herb name and mapping word
    # for HDI only
    # @name: herb name, annotated by MetaMap
    # @anno_terms: final annotated terms returned by self.outputHelper()

    def duplicateHDI(self, name, anno_terms):
        final_term = []
        # find the mapping word 
        for each in anno_terms:
            res = re.sub(r" ?\([^)]+\)", "", each)
            res = re.sub(r" \[(.*?)\]", "", res)
            res = res.split(":")[1]
            if name.lower() != res.lower():
                final_term.append(each)
            else:
                pass
        return final_term

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

    # read MM type file
    # @fun: annotation section names, i.e. PU, HDI
    # each section will return a list of MM types

    def readTypes(self, fun):
        full_types = pd.read_csv(os.path.join(self.path, "mmtypes.txt"),
                                 sep="|", header=None, index_col=False)
        full_types.columns = ["abbrev", "name", "tui", "types"]
        if fun.upper() not in ["HDI", "PU", "CON"]:
            raise ValueError("Currently only supports HDI, PU and Con.")
        else:
            # hdi mm types
            if fun.upper() == "HDI":
                hdi_types = pd.read_csv(
                    os.path.join(self.path, "hdi_types.txt"),
                    sep="|", header=None, index_col=False)
                hdi_types.columns = ["group", "group_name", "tui", "types"]
                hdi_types = hdi_types["tui"].values.tolist()
                hdi = full_types.loc[full_types["tui"].isin(hdi_types)]
                return hdi["types"].values.tolist()
            # pu mm types
            if fun.upper() == "PU":
                pu_types = pd.read_csv(
                    os.path.join(self.path, "pu_types.txt"),
                    sep="|", header=None, index_col=False)
                pu_types.columns = ["group", "group_name", "tui", "types"]
                pu_types = pu_types["tui"].values.tolist()
                pu = full_types.loc[full_types["tui"].isin(pu_types)]
                return pu["types"].values.tolist()
            # con mm types
            if fun.upper() == "CON":
                con_types = pd.read_csv(
                    os.path.join(self.path, "con_types.txt"),
                    sep="|", header=None, index_col=False)
                con_types.columns = ["group", "group_name", "tui", "types"]
                con_types = con_types["tui"].values.tolist()
                con = full_types.loc[full_types["tui"].isin(con_types)]
                return con["types"].values.tolist()

    # HDI annotation process
    # @name: herb name
    # @content: section content for the herb, i.e. herb["drug_herb-interactions"]
    # get HDI content annotated using MM

    def HDIprcess(self, name, content):
        data = {}
        data["name"] = name
        content = self.remove(self.getBefore(content))
        content = self.SplitContent(content)
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
                    command = self.getComm(each, additional=" --term_processing")
                    output = self.getAnnNoOutput(command).decode("utf-8")
                    anno = self.outputHelper(output, hdi_types, self.getSplitHDI)

                    if isinstance(anno, list):
                        anno_terms.extend(anno)
                    else:
                        anno_terms.append(anno)
            else:
                command = self.getComm(content, additional=" --term_processing")
                output = self.getAnnNoOutput(command).decode("utf-8")
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
                anno_terms = self.duplicateHDI(name, anno_terms)
                data["annotated_HDI"] = self.concate(anno_terms, "\n")
        return data
    # PU annotation process main function
    # @name: herb name
    # @content: section content for the herb, i.e. herb["purposed_uses"]
    # get AR content annotated using MetaMap

    def PUProcess(self, name, content):
        data = {}
        data["name"] = name
        content = self.remove(content)
        pu_types = self.readTypes("PU")
        # if pu is empty
        if not content:
            data["PU"] = " "
            data["annotated_PU"] = " "
        else:
            anno_terms = []
            if isinstance(content, list):
                for each in content:
                    command = self.getComm(each, additional=" --term_processing")
                    output = self.getAnnNoOutput(command).decode("utf-8")
                    anno = self.outputHelper(output, pu_types, self.getSplit)
                    if isinstance(anno, list):
                        anno_terms.extend(anno)
                    else:
                        anno_terms.append(anno)
            else:
                command = self.getComm(content, additional=" --term_processing")
                output = self.getAnnNoOutput(command).decode("utf-8")
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
        return data