# health-informatics-helper
Several Python scripts for various Health Informatics tasks.
## Before Using the Scripts
- You should get scraping permission from [Cancer care herb](https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs/search) administrator
- Install [geckodriver](https://github.com/mozilla/geckodriver/releases) and Firefox first. If you prefer Chrome, you should change the setting (```driverSetup``` function) in the script manually.
- Install [MetaMap](https://metamap.nlm.nih.gov/), and make sure you have all [2018 additional dataset](https://metamap.nlm.nih.gov/DataSetDownload.shtml) installed in the MetaMap folder.
- Install required python modules using ```pip -r requirements.txt```
- Register [NCBO BioPortal](https://bioportal.bioontology.org/#) and get your API key for BioPortal, then set up ```config.py``` with your API key under ```CANCER``` folder.


## Folders
### NHPID
Scripts that extract necessary section & content from [Natural Health Products Ingredients Database](http://webprod.hc-sc.gc.ca/nhpid-bdipsn/monosReq.do?lang=eng&monotype=single)'s single ingredient monograph information.
#### Scripts
- ```nhpid_url.py```: extract url for each ingredient in NHPID website and write urls into ```nhpid_urls.csv```.
- ```nhpid_header.py```: extract specific header and its information for each NHPID ingredient.
- ```norm.py```: NHPID header normalization tool.
- ```nhpid_level.py```: extract each ingredient's headers with hierarchical level.

### CANCER
Scripts that extract necessary section & content from [Cancer care herb](https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs/search).
#### Scripts
- ```cancer_url.py```: 
	- extracting url as alphabetic listing, i.e. herbs starting with ```A```, herbs starting with ```B```. Write the output to ```cancer_url.csv```
	- extracting each herb's website in each alphabetic listing  page.
- ```cancer_header.py```: extracting headers in each page that appeared the alphabetic listing webpage. Write the output to ```cancer_herb_header.csv```. This script is aimed at finding wanted section and content to scrape.
- ```cancer_context.py```: extracting wanted section and content from each herb's website. If you want to scrape different sections and their content, please modified ```getContent``` function in this script. Write the output to ```cancer_herb_content.jsonl```.
- ```umlsAnn.py```: MetaMap constructor, returns MetaMap output with fixed, built-in commands.
- ```meddraAnn.py```: BioPortal constructor, using ```MEDDRA``` module to annotate the input content.
- ```cancer_content_ann.py```: an example script for generating annotations for ```adverse reaction``` with ```MEDDRA```, ```herb-drug interaction``` with ```MetaMap```, and ```purposed uses``` with ```MetaMap```. This script will only generate annotations on a limited list of ingredient.
- ```util.py```: a script for testing.

#### Other files
- ```mmmap.txt```: MetaMap [semantic types mappings](https://metamap.nlm.nih.gov/Docs/SemanticTypes_2018AB.txt).  The format of the file is *Abbreviation|Type Unique Identifier (TUI)|Full Semantic Type Name*.
- ```mmtypes.txt```: MetaMap [semantic groups and their mappings to the semantic types](https://metamap.nlm.nih.gov/Docs/SemGroups_2018.txt). The format of the file is *Semantic Group Abbrev|Semantic Group Name|TUI|Full Semantic Type Name*.
- ```con_types.txt```: contraindication semantic types, following the format as ```mmtypes.txt```.
- ```hdi_types.txt```: herb-drug interaction semantic types, following the format as ```mmtypes.txt```.
- ```pu_types.txt```: purposed uses semantic types, following the format as ```mmtypes.txt```


## Misc
- ```generator.py```: generate [brat](http://brat.nlplab.org/)'s annotation file given a keyword list.

## Todo
* [ ] support all MetaMap commands for generating annotation output
* [ ] add CUI information to BioPortal annotation output
* [ ] remove all hard-coded snippets, i.e. MetaMap location
* [ ] write a wrapper script for all cancer site data


