import requests, csv
from bs4 import BeautifulSoup as bs
from pathlib import Path
## extract ulr for each ingredient
class nhpid_url(object):
	def __init__(self):
		self.start_page = "http://webprod.hc-sc.gc.ca/nhpid-bdipsn/monosReq.do?lang=eng&monotype=single"
		self.domain = "http://webprod.hc-sc.gc.ca"
		## list of ingredients' url
		self.urls = {}
	## initial step, use beautifulsoup to process website
	def start(self, start_page):
		page = requests.get(start_page)
		soup = bs(page.text, "lxml")
		return soup
	## find the final url for each ingredient
	def finishURL(self, url):
		if not url.startswith("/nhpid-bdipsn/"):
			url = self.domain + "/nhpid-bdipsn/" + url
		else:
			url = self.domain + url
		return url
	## write the dict to csv file
	def write(self):
		with open ("urls.csv", "w") as f:
			w = csv.writer(f)
			w.writerows(self.urls.items())
	## get ingredients' names and urls
	def iterate(self, soup):
		context = soup.find(class_ = "center")
		items = context.findAll("ul")
		for each in items:
			## if there is only a single item under the tag
			try:
				for stuff in each.findAll("li"):
					item = stuff.find("a")
					final_url = self.finishURL(item["href"])
					self.urls[item.text.strip()] = final_url
			except AttributeError:
				context = each.find("li")
				item = context.find("a")
				final_url = self.finishURL(item["href"])
				self.urls[item.text.strip()] = final_url
		self.write()
	## main function
	def run(self):
		## check if it's the first time run
		ulrs_file = Path("nhpid_urls.csv")
		if ulrs_file.is_file():
			print("File already existed.")
		else:
			print("Start to extract url for each ingredient...")
			soup = self.start(self.start_page)
			self.iterate(soup)
			print("Finish extracting")