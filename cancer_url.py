from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import csv
## extracting url for each 
class cancer_url(object):
	def __init__(self):
		self.urls = {}
		self.domain = "https://www.mskcc.org/cancer-care"
		self.start_page = "https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs/search"
		## pages that are split by herb leading character
		self.pages = {}
	## setup selenium webdriver
	def driverSetup(self):
		options = Options()
		## do not open firefox 
		options.add_argument("--headless")
		driver = webdriver.Firefox(executable_path = "/usr/local/bin/geckodriver", options = options)
		return driver
	## iterate by leading character
	def loadKeyword(self, driver):
		driver.get(self.start_page)
		driver.implicitly_wait(10)
		element =  driver.find_elements_by_class_name("form-keyboard-letter")
		for each in element:
			url = each.get_attribute("href")
			if url.startswith("https://www.mskcc.org/cancer-care"):
				self.pages[each.text] = url
			else:
				url = self.domain + url
				self.pages[each.text] = url
		self.write()
		driver.close()
	## write urls to file
	def write(self):
		print("start writing leading character specific website into file")
		with open("cancer_url.csv", "w") as f:
			w = csv.writer(f)
			w.writerows(self.pages.items())
		print("Finished!")
	## load entire page 
	def loadMore(self):
		driver = webdriver.Firefox(executable_path = "/usr/local/bin/geckodriver")
		driver.get(self.start_page)
		#html = driver.page_source.encode("utf-8")
		while driver.find_element_by_link_text("Load More"):
			driver.find_element_by_link_text("Load More").click()
		print("Finish clicking")

x = cancer_url()
driver = x.driverSetup()
x.loadKeyword(driver)





x = cancer_url()

