import urllib.request, urllib.error, urllib.parse
import json, config, os, subprocess, re, csv, pickle
class meddraAnn(object):
    def __init__(self):
        self.meddra = "/annotator?ontologies=http://data.bioontology.org/ontologies/MEDDRA&text=" 
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
    ## adverse reactions pre-process
    ## @ar: data["adverse_reactions"]
    ## return annotated terms
    def adrProcess(self, ar):
        ## check if exists adverse_reactions section
        if ar:
            ar_annotations = self.auth(self.REST_URL + self.meddra + urllib.parse.quote(ar))
            labels = self.getLabel(ar_annotations)
            return labels
        else:
            return " "