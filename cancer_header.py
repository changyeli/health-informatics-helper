import csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from collections import Counter
class cancer_header(object):
	def __init__(self):
		self.herb = "cancer_herb_url.csv"
		## headers for patients & caregivers
		self.con = []
		## headers for professionals
		self.pro = []
	def driverSetup(self):
		options = Options()
		## do not open firefox 
		options.add_argument("--headless")
		driver = webdriver.Firefox(executable_path = "/usr/local/bin/geckodriver", options = options)
		return driver
	## extract all headers for patients & caregivers
	def conSection(self, driver):
		print("Extracting patients & caregivers")
		element = driver.find_element_by_id("msk_consumer")
		headers = element.find_elements_by_xpath('.//span[@class = "accordion__headline"]')
		print(headers)
		for each in headers:
			name = each.get_attribute("data-listname")
			print(name)
			#self.con.append(name.strip())
	## extract all headers for professionals
	def proSection(self, driver):
		print("Extracting professionals")
		element = driver.find_element_by_id("msk_professional")
		headers = element.find_elements_by_xpath('.//span[@class = "accordion__headline"]')
		print(headers)
		for each in headers:
			name = each.get_attribute("data-listname")
			print(name)
			#self.pro.append(name.strip())
	## write to files
	def write(self):
		print("Writing to files....")
		with open("cancer_consumer.csv", "w") as f:
			w = csv.writer(f)
			w.writerows(Counter(self.con).items())
		with open("cancer_professional.csv", "w") as f:
			w = csv.writer(f)
			w.writerows(Counter(self.pro).items())
		print("Finish writing")
	def process(self):
		driver = self.driverSetup()
		driver.implicitly_wait(1)
		with open("cancer_herb_url.csv", "r") as f:
			readCSV = csv.reader(f, delimiter = ",")
			for row in readCSV:
				print("Extracting " + row[0] + " headers")
				driver.get(row[1])
				self.conSection(driver)
				self.proSection(driver)
				print("=====================================")
				break
		#self.write()
	## main function
	def run(self):
		self.process()

x = cancer_header()
x.run()
