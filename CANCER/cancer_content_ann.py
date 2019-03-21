import urllib.request, urllib.error, urllib.parse
import json, config
import time
## get annotation using bioportal
class cancer_ann(object):
    def __init__(self):
        self.file = "cancer_sub_content.json"
        self.meddra = "/annotator?ontologies=http://data.bioontology.org/ontologies/MEDDRA&text=" 
        self.rxnorm = "/annotator?ontologies=http://data.bioontology.org/ontologies/RXNORM&text=" 
        self.REST_URL = "http://data.bioontology.org"
        self.API_KEY = config.api_key
    ## BioPortal login
    def auth(self, url):
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', 'apikey token=' + self.API_KEY)]
        return json.loads(opener.open(url).read())
    ## get prefLabel from annotation
    ## @ annotations: the annotated document from BioPortal
    def getLabel(self, annotations, get_class = True):
        labels = []
        for result in annotations:
            class_details = result["annotatedClass"]
            if get_class:
                try:
                    class_details = self.auth(result["annotatedClass"]["links"]["self"])
                except urllib.error.HTTPError:
                    print(f"Error retrieving {result['annotatedClass']['@id']}")
                    continue
            labels.append(class_details["prefLabel"])
        return labels
    ## concatenate list of string into a single string
    ## @values: i.e. data["adverse_reactions"]
    def concate(self, values):
        if isinstance(values, list):
            return " ".join(values)
        else:
            return values
    ## adverse reactions pre-process
    ## @ar: data["adverse_reactions"]
    def adrProcess(self, ar):
        data = self.concate(ar)
        ## check if exists adverse_reactions section
        if data:
            ar_annotations = self.auth(self.REST_URL + self.meddra + urllib.parse.quote(data))
            labels = self.getLabel(ar_annotations)
            print(labels)
            return labels
        else:
            return None
    ## herb-drug interactions pre-process
    ## @hdi: data["herb-drug_interactions"]
    def hdiProcess(self, hdi):
        data = self.concate(hdi)
        ## if no herb-drug interaction content
        if data:
            hdi_annotations = self.auth(self.REST_URL + self.rxnorm + urllib.parse.quote(data))
            labels = self.getLabel(hdi_annotations)
            print(labels)
            return labels
        else:
            return None
    ## write adverse reactions to local file
    ## @ar_labels: annotated labels from adrProcess function
    ## @name: cancer herb name
    ## @ar: adverse reactions content
    ## @filename: local file name to store annotated adverse reactions
    def writeADR(self, ar_labels, ar):
        data = {}
        ## have content under the section
        if ar_labels is not None:
            data = {}
            data["ar_label"] = ar_labels
            if not ar:
                data["ar_context"] = "None"
            else:
                data["ar_context"] = self.concate(ar)
        else:
            ## no available annotation
            data["ar_label"] = "None"
            if not ar:
                data["ar_context"] = "None"
            else:
                data["ar_context"] = self.concate(ar)
        return data
            
    ## write adverse reactions to local file
    ## @hdi_labels: annotated labels from hdiProcess function
    ## @name: cancer herb name
    ## @ar: adverse reactions content
    ## @filename: local file name to store annotated herb-drug interaction
    def writeHDI(self, hdi_labels, hdi):
        data = {}
        ## check if no such section
        if hdi_labels is not None:
            data["hdi_label"] = hdi_labels
            if not hdi:
                data["hdi_context"] = "None"
            else:
                data["hdi_context"] = self.concate(hdi)
        ## check if there is available annotation
        else:
            ## no available annotation
            data["hdi_label"] = hdi_labels
            if not hdi:
                data["hdi_context"] = "None"
            else:
                data["hdi_context"] = self.concate(hdi)
        return data
    ## write to local file
    ## @data: dict that contains annotated content
    ## @filename: local file to save data
    def write(self, data, filename):
        with open(filename, "a") as output2:
            json.dump(data, output2)
            output2.write("\n")   
    ## check if the content is structure
    ## @content: specific data content, i.e. herb["adverse_reactions"]
    ## returns "yes" if the content has ":", otherwise returns "no"
    def isStructure(self, content):
        content = self.concate(content)
        if ":" in content:
            return "Yes"
        else:
            return "No"
    ## check purposed uses content:
    ## @content: herb["purposed_uses"]
    ## return list of purposed uses
    def checkPU(self, content):
        if isinstance(content, list):
            return content
        else:
            return content.split("\n")
    ## check if purposed uses section is structure
    ## @content: herb["purposed_uses"]
    def isStructurePU(self, content):
        if isinstance(content, list):
            return "Yes"
        else:
            return "No"
    ## merge all dict into one
    ## @ar: herb["adverse_reactions"]
    ## @hdi: herb["herb-drug_interactions"]
    ## @pu: herb["purported_uses"]
    ## @name: herb name
    ## return dict which contains structure flags, hdi & ar annotation, original content, pu content
    def merge(self, ar, hdi, pu, name):
        ## get ar & hdi annotated
        ar_label = self.adrProcess(ar)
        hdi_label = self.hdiProcess(hdi)
        ar_data = self.writeADR(ar_label, ar)
        hdi_data = self.writeHDI(hdi_label, hdi)
        ## merge into one dict
        full = {**ar_data, **hdi_data} 
        full["name"] = name
        ## add ar & hdi flag
        full["ar_flag"] = self.isStructure(ar)
        full["hdi_flag"] = self.isStructure(hdi)
        ## check purposed uses section
        full["pu_context"] = self.checkPU(pu)
        full["pu_flag"] = self.isStructurePU(pu)
        return full

    ## read cancer herb content line by line
    def readJSON(self):
        try:
            with open(self.file, "r") as f:
                for line in f:
                    data = json.loads(line)
                    hdi = data["herb-drug_interactions"]
                    ar = data["adverse_reactions"]
                    pu = data["purported_uses"]
                    print("=========================")
                    name = data["name"]
                    print("processing: " + name)
                    full = self.merge(ar, hdi, pu, name)
                    self.write(full, "cancer_ann.json")
                    print("=========================")
        except IOError:
            print("No such file. Please run cancer_context.py first.")
    ## main function
    def run(self):
        print("start....")
        start = time.time()
        self.readJSON()
        print("finished....")
        endtime = time.time()
        print("time used: " + str(endtime - start) + " second(s).")
if __name__ == "__main__":
    x = cancer_ann()
    x.run()