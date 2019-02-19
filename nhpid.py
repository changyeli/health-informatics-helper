import requests
from bs4 import BeautifulSoup as bs

class nhpid(object):
	def __init__(self):
		self.start_page = "http://webprod.hc-sc.gc.ca/nhpid-bdipsn/monosReq.do?lang=eng&monotype=single"
		self.domain = "http://webprod.hc-sc.gc.ca"
		## list of ingredients' url
		self.urls = {}
	def start(self):
		page = requests.get(self.start_page)
		soup = bs(page.text, "lxml")
		return soup
	## find the final url for each ingredient
	def finishURL(self, url):
		if not url.startswith("/nhpid-bdipsn/"):
			url = self.domain + "/nhpid-bdipsn/" + url
		else:
			url = self.domain + url
		return url
	## write to dict
	def write(self, name, url):
		self.urls[name] = url
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
	## testing
	def test(self):
		for k,v in self.urls.items():
			print(k, v)
				
			

if __name__ == "__main__":
	x = nhpid()
	soup = x.start()
	x.iterate(soup)
	x.test()