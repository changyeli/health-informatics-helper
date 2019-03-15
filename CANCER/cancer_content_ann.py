import urllib.request, urllib.error, urllib.parse
import json, config
import time
class cancer_ann(object):
    def __init__(self):
        self.file = "cancer_herb_content.json"
        self.meddra = "/annotator?ontologies=http://data.bioontology.org/ontologies/MEDDRA&text=" 
        self.rxnorm = "/annotator?ontologies=http://data.bioontology.org/ontologies/RXNORM&text=" 
        self.REST_URL = "http://data.bioontology.org"
        self.API_KEY = config.api_key
    ## BioPortal login
    def auth(self, url):
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', 'apikey token=' + self.API_KEY)]
        return json.loads(opener.open(url).read())
    ## adverse reaction annotation
    ## use meddra
    ## @ar: adverse reaction content
    def adr(self, ar):
        annotations = self.auth(self.REST_URL + self.meddra + urllib.parse.quote(ar))
        return annotations
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
        if not data:
            pass
        else:
            ar_annotations = self.auth(self.REST_URL + self.meddra + urllib.parse.quote(data))
            labels = self.getLabel(ar_annotations)
            return labels
    ## herb-drug interactions pre-process
    ## @hdi: data["herb-drug_interactions"]
    def hdiProcess(self, hdi):
        data = self.concate(hdi)
        if not data:
            pass
        else:
            hdi_annotations = self.auth(self.REST_URL + self.rxnorm + urllib.parse.quote(data))
            labels = self.getLabel(hdi_annotations)
            return labels
    ## write adverse reactions to local file
    ## @ar_labels: annotated labels from adrProcess function
    ## @name: cancer herb name
    ## @ar: adverse reactions content
    ## @filename: local file name to store annotated adverse reactions
    def writeADR(self, ar_labels, name, ar, filename):
        ## check if no such section
        if ar_labels is None:
            ## ignore this cancer herb
            pass
        ## check if there is available annotation
        if not ar_labels:
            ## no available annotation
            data = {}
            data["name"] = name
            data["ar_label"] = "None"
            data["ar_context"] = ar
            with open(filename, "a") as output1:
                json.dump(data, output1)
                output1.write("\n")
        else:
            ## available annotation exists
            data = {}
            data["name"] = name
            data["ar_label"] = ar_labels
            data["ar_context"] = ar
            with open(filename, "a") as output2:
                json.dump(data, output2)
                output2.write("\n")
    ## write adverse reactions to local file
    ## @hdi_labels: annotated labels from hdiProcess function
    ## @name: cancer herb name
    ## @ar: adverse reactions content
    ## @filename: local file name to store annotated herb-drug interaction
    def writeHDI(self, hdi_labels, name, hdi, filename):
        ## check if no such section
        if hdi_labels is None:
            ## ignore this cancer herb
            pass
        ## check if there is available annotation
        if not hdi_labels:
            ## no available annotation
            data = {}
            data["name"] = name
            data["hdi_label"] = "None"
            data["hdi_context"] = hdi
            with open(filename, "a") as output1:
                json.dump(data, output1)
                output1.write("\n")
        else:
            ## available annotation exists
            data = {}
            data["name"] = name
            data["hdi_label"] = hdi_labels
            data["hdi_context"] = hdi
            with open(filename, "a") as output2:
                json.dump(data, output2)
                output2.write("\n")
    ## read cancer herb content line by line
    def readJSON(self):
        try:
            with open(self.file, "r") as f:
                for line in f:
                    data = json.loads(line)
                    hdi = data["herb-drug_interactions"]
                    ar = data["adverse_reactions"]
                    name = data["name"]
                    ar_labels = self.adrProcess(ar)
                    hdi_labels = self.hdiProcess(hdi)
                    self.writeADR(ar_labels, name, ar, "cancer_adr.json")
                    self.writeHDI(hdi_labels, name, hdi, "cancer_hdi.json")
        except IOError:
            print("No such file. Please run cancer_context.py first.")
    ## main function
    def run(self):
        print("start....")
        start = time.time()
        self.readJSON()
        print("finished....")
        endtime = time.time()
        print("time used: " + str(endtime - start))

x = cancer_ann()
x.run()