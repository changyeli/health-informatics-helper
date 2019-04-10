import urllib.request, urllib.error, urllib.parse
import json, config, os, subprocess, re, csv
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
## get UMLS annotation for HDI, contradictions and purposed uses
class umlsAnn(object):
    def __init__(self, location):
        ## MetaMap location
        self.location = location
        ## get this python script location
        self.path = os.path.dirname(os.path.abspath(__file__))
    ## start MM server 
    def start(self):
        os.chdir(self.location)
        output = subprocess.check_output(["./bin/skrmedpostctl", "start"])
        print(output)
    ## get annotated terms using UMLS
    ## @value: content to be annotated
    ## @output: the desired format for the annotated terms. Select choices: JSON, XML
    def getAnn(self, value, output):
        ## echo lung cancer | ./bin/metamap16 -I
        ## check if value is valid
        if value is None:
            return " "
        else:
            command = "echo " + "'" + value + "'"  + " | " + "./bin/metamap16" + " -I " + "--silent " + "--term_processing " + "--ignore_word_order "
            if output not in ["JSON", "XML"]:
                raise ValueError("Only JSON and XML formats supported")
            else:
                if output.upper() == "JSON":
                    command += "--JSONf 0"
                else:
                    command += "--XMLf1"
            output = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE).stdout.read()
            return output
    ## get annotated terms using UMLS without output format
    def getAnnNoOutput(self, value):
        ## echo lung cancer | ./bin/metamap16 -I
        ## check if value is valid
        if value is None:
            return " "
        else:
            command = "echo " + "'" + value + "'"  + " | " + "./bin/metamap16" + " -I " + "--silent " + "--term_processing " + "--ignore_word_order "
            output = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE).stdout.read()
            return output
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
        ## MM location
        self.location = "/Users/Changye/Documents/workspace/public_mm"
    ## remove all non-ASCII characters in the content
    ## @value: the content needs to be cleaned
    def remove(self, value):
        return re.sub(r'[^\x00-\x7F]+', " ", value)
    ## get content before ":"
    ## @content: content need to be split 
    def getBefore(self, content):
        if isinstance(content, list):
            value = [each.split(":")[0] for each in content]
            return " ".join(value)
        else:
            return content.split(":")[0]
    ## concate list into single string
    def concate(self, value):
        if isinstance(value, list):
            return " ".join(value)
        else:
            return value
    ## write to local .tsv file
    ## @output_file: file to write
    ## @data: extracted herb information in dict form
    def write(self, output_file, data):
        with open(os.path.join(self.file_location, output_file), "a") as output:
            w = csv.writer(output, delimiter = "\t")
            w.writerows(data.items())
    ## annotation process
    ## @herb: json object for a herb
    ## @mm: MetaMap constructor
    ## @meddra: MMEDRA constructor
    def annProcess(self, herb, mm, meddra):
        data = {}
        print("=============================")
        print(herb["name"])
        data["name"] = herb["name"]
        ## check if annotated content is valid
        try:
            print("\tProcessing HDI")
            hdi = self.remove(self.getBefore(herb["herb-drug_interactions"]))
            data["HDI"] = hdi
            output = mm.getAnnNoOutput(hdi)
            data["annotated_HDI"] = output
        except KeyError:
            print("\tNo such content in HDI")
            data["HDI"] = " "
            data["annotated_HDI"] = " "
        try:
            print("\tProcessing contradictions")
            con = self.remove(self.concate(herb["contradictions"]))
            data["contradictions"] = con
            output = mm.getAnnNoOutput(con)
            data["annotated_contradictions"] = output
        except KeyError:
            print("\tNo such content in contradictions")
            data["contradictions"] = " "
            data["annotated_contradictions"] = " "
        try:
            print("\tProcessing PU")
            pu = self.remove(self.concate(herb["purported_uses"]))
            data["purported_uses"] = pu
            output = mm.getAnnNoOutput(pu)
            data["annotated_PU"] = output
        except KeyError:
            print("\tNo such content in purported_uses")
            data["purported_uses"] = " "
            data["annotated_PU"] = " "
        try:
            print("\tProcessing AR")
            ar = self.remove(self.concate(herb["adverse_reactions"]))
            data["adverse_reactions"] = ar
            output = self.concate(meddra.adrProcess(ar))
            data["annotated_AR"] = output
        except KeyError:
            print("\tNo such content in adverse_reactions")
            data["adverse_reactions"] = " "
            data["annotated_AR"] = " "
        for each in self.headers:
            data[each] = self.concate(herb[each])
        self.write("MSKCC_overlap_v110.tsv", data)
        print("=============================")
    ## read the file
    def readFile(self):
        ## start mm server
        mm = umlsAnn(self.location)
        mm.start()
        ## get meddra constructor
        meddra = meddraAnn()
        with open(os.path.join(self.file_location, self.read_file), "r") as f:
            for line in f:
                herb = json.loads(line)
                if herb["name"] in self.overlap_herbs:
                    self.annProcess(herb, mm, meddra)
                else:
                    pass
    ## main function
    def run(self):
        self.readFile()
if __name__ == "__main__":
    x = main()
    x.run()

