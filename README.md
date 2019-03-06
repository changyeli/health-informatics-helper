# health-informatics-helper
Several Python scripts for various Health Informatics tasks.
## Before Using the Scripts
- You should get scraping permission from [Cancer care herb](https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs/search) administrator
- Install [geckodriver](https://github.com/mozilla/geckodriver/releases) and Firefox first. If you prefer Chrome, you should change the setting (```driverSetup``` function) in the script manually.
- Install python module using ```pip -r requirements.txt```


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


## Misc
- ```generator.py```: generate [brat](http://brat.nlplab.org/)'s annotation file given a keyword list.

## Todo
* [ ] Full information extraction for [Natural Health Products Ingredients Database](http://webprod.hc-sc.gc.ca/nhpid-bdipsn/monosReq.do?lang=eng&monotype=single)'s single ingredient monograph.
* [ ] Rewrite NHPID scripts using ```selenium```.
* [ ] Better normalization tool for section names.
* [x] Extraction tool for [Cancer care herb](https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs/search).


