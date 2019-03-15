import urllib.request, urllib.error, urllib.parse
import json, os, config
from pprint import pprint
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
            pass

    ## read cancer herb content line by line
    def readJSON(self):
        try:
            with open(self.file, "r") as f:
                for line in f:
                    data = json.loads(line)
                    hdi = data["herb-drug_interactions"]
                    ar = data["adverse_reactions"]
                    print(data["name"])
                    ar_labels = self.adrProcess(ar)
                    hdi_labels = self.hdiProcess(hdi)
                    ## herb-drug interactions
        except IOError:
            print("No such file. Please run cancer_context.py first.")
    ## main function
    def run(self):
        self.readJSON()

x = cancer_ann()
x.run()