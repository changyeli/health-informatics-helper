import csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
## extract ulr for each ingredient
class nhpid_url(object):
	def __init__(self):
		self.start_page = "http://webprod.hc-sc.gc.ca/nhpid-bdipsn/monosReq.do?lang=eng&monotype=single"
		self.domain = "http://webprod.hc-sc.gc.ca"
		## list of ingredients' url
		self.urls = {}
	def driverSetup(self):
		options = Options()
		## do not open firefox 
		options.add_argument("--headless")
		driver = webdriver.Firefox(executable_path = "/usr/local/bin/geckodriver", options = options)
		driver.implicitly_wait(1)
		return driver
	## find the final url for each ingredient
	def finishURL(self, url):
		if not url.startswith("/nhpid-bdipsn/"):
			url = self.domain + "/nhpid-bdipsn/" + url
		else:
			url = self.domain + url
		return url
	## 
