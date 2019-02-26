import requests, csv, re, pickle
from bs4 import BeautifulSoup as bs
from pathlib import Path
from collections import Counter

class nhpid(object):
	def __init__(self):
		self.start_page = "http://webprod.hc-sc.gc.ca/nhpid-bdipsn/monosReq.do?lang=eng&monotype=single"
		self.domain = "http://webprod.hc-sc.gc.ca"
		## list of ingredients' url
		self.urls = {}
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
		with open ("urls.csv", "a") as f:
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
	## get all section names for each ingredient
	## testing: only use one ingredient
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
		## dump all headers to a binary file for normalization
		print("Dump all headers into a local file")
		with open("headers", "wb") as f:
			pickle.dump(headers, f)
		print("Finish dumping")
			
	## main function
	def run(self):
		## check if it's the first time run
		ulrs_file = Path("urls.csv")
		if ulrs_file.is_file():
			print("Second time run.")
			self.getSection()
		else:
			soup = self.start(self.start_page)
			self.iterate(soup)
			self.getSection()



			

if __name__ == "__main__":
	x = nhpid()
	x.run()