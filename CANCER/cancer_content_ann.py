import urllib.request, urllib.error, urllib.parse
import json, config, os
## get annotation using bioportal for adverse reaction section
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
    ## concatenate list of string into a single string
    ## @values: i.e. data["adverse_reactions"]
    def concate(self, values):
        if isinstance(values, list):
            return " ".join(values)
        else:
            return values
    ## adverse reactions pre-process
    ## @ar: data["adverse_reactions"]
    ## return annotated terms
    def adrProcess(self, ar):
        data = self.concate(ar)
        ## check if exists adverse_reactions section
        if data:
            ar_annotations = self.auth(self.REST_URL + self.meddra + urllib.parse.quote(data))
            labels = self.getLabel(ar_annotations)
            return labels
        else:
            return None
## get UMLS annotation for HDI, contradictions and purposed uses
class umlsAnn(object):
    def __init__(self, location):
        ## MetaMap location
        self.location = location
        ## get this python script location
        self.path = os.path.dirname(os.path.abspath(__file__))
        ## .py file name
        self.pyName = "cancer_content_ann.py"
        ## MM version
        self.version = 2016
    ## start MM server 
    def start(self):
        os.chdir(self.location)
        subprocess.run(["./bin/skrmedpostctl", "start"])
    ## generate a list MM commands
    ## inspired by: https://github.com/AnthonyMRios/pymetamap/blob/master/pymetamap/SubprocessBackend.py
    def getComm(self, hide = True, FormatXML, UnformatXML, FormatJSON, UnformatJSON, MMversion, ):
    ## get annotated terms using UMLS
    ## @value: content to be annotated
    ## @command: a list of MM commands
    def getAnn(self, value, command):
        ## echo lung cancer | ./bin/metamap16 -I
        ## output = subprocess.check_output(["./bin/skrmedpostctl", "start"])


