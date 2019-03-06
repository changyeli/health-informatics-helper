import requests, re
from bs4 import BeautifulSoup as bs
## get specific header and its information for each NHPID ingredient
class nhpid_header(object):
	def __init(self):
		self.url = "nhpid_urls.csv"
		self.common_header = ["source material",
							"use or purpose", # == "all use or purpose"
							"risk information",
							"caution and warning",
							"contraindication",
							"known adverse reaction",
							"nhpid name",
							"date",
							"date modified"]
		self.addtional_header = ["proper name",
								"common name",
								"synonym"]
	## use beautifulsoup to process website
	def readPage(self, url):
		page = requests.get(url)
		soup = bs(page.text, "lxml")
		return soup
	## get
	def getHeaders(self, soup):
		context = soup.find(class_ = "center")

	def run(self):
		url = "http://webprod.hc-sc.gc.ca/nhpid-bdipsn/atReq.do?atid=cayenne.oral.orale&lang=eng"
		



'''
def getSection(self):
		headers = []
		with open("urls.csv", "r") as f:
			data = csv.reader(f)
			## ignore first 3 rows
			for _ in range(3):
				next(data)
			for line in data:
				website = line[1]
				page = requests.get(website)
				soup = bs(page.text, "lxml")
				context = soup.find(class_ = "center")
				## all headers
				temp = context.find_all(re.compile('^h[2-6]$'))
				## only h2
				#temp = context.find_all("h2")
				for each in temp:
headers.append(each.text.strip())
'''