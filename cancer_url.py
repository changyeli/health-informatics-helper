import requests, time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
## extracting url for each 
class cancer_url(object):
	def __init__(self):
		self.urls = {}
		self.domain = "https://www.mskcc.org/cancer-care"
		self.start_page = "https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs/search"
	## load entire page 
	def loadMore(self):
		driver = webdriver.Firefox(executable_path = "/usr/local/bin/geckodriver")
		driver.get(self.start_page)
		#html = driver.page_source.encode("utf-8")
		while driver.find_elements_by_css_selector(".pager__item"):
			driver.find_elements_by_css_selector(".pager__item").click()
			time.sleep(1)
	def start(self):
		page = requests.get(self.start_page)
		soup = bs(page.text, "lxml")
		return soup
	## find url for each herb
	def findHerb(self, soup):
		context = soup.find("msk-view-content")
		herbs = context.findAll("h2")
		for each in herbs:
			herb = each["a"]
			print(herb.text.strip(), herb["href"])
	## main function
	def run(self):
		self.loadMore()
		soup = self.start()
		self.findHerb(soup)







x = cancer_url()
x.run()

