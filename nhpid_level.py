import requests, csv, re
from bs4 import BeautifulSoup as bs
from nhpid_url import nhpid_url
## extract NHPID headers with level
class nhpid_level(object):
	def __init__(self):
		self.url = "nhpid_urls.csv"
	def readFile(self):
		## if exists
		try:
			with open(self.url, "r") as f:
				data = csv.reader(f)
				for _ in range(3):
					next(data)
		## if not exists
		except IOError:
			print("Unable to open urls.csv")
			print("Running nhpid_url.py to get the file...")
			runner = nhpid_url()
			runner.run()
			with open(self.url, "r") as f:
				data = csv.reader(f)
				for _ in range(3):
					next(data)
	## use beautifulsoup to process 
	## test
	## only use one ingredient
	def test(self):
		url = "http://webprod.hc-sc.gc.ca/nhpid-bdipsn/monoReq.do?id=514&lang=eng"
		page = requests.get(url)
		soup = bs(page.text, "lxml")
		context = soup.find(class_ = "center")
		headers = context.find_all("h2")
		for each in headers:
			print(each.text)
			self.findHeader(each)
	## find all possible headers
	## @headers: processed bs object
	def findHeader(self, headers):
		level = 3
		while level <= 6:
			next_header = "h" + str(level)
			## if it has multiple sub-sections
			try:
				print("multiple sub-sections")
				new_header = headers.findAll(next_header)
				for item in new_header:
					print(item.text)
			## if it only has one sub-section
			except AttributeError:
				try:
					print("only one sub-section")
					new_header = headers.find("next_header")
					for item in new_header:
						print(item.text)
				except AttributeError:
					print("no sub-section")
					continue
			level += 1
			self.findHeader(next_header)
	## main function
	def run(self):
		self.test()



x = nhpid_level()
x.run()

