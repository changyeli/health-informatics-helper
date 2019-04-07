import re, csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
## get specific header and its information for each NHPID ingredient
class nhpid_header(object):
	def __init__(self):
		self.url = "urls.csv"
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
	## remove parenthesis area
	## @header: the header content extracted from website
	def remove(self, header):
		header = header.lower()
		return re.sub(r" ?\([^)]+\)", "", header)
	def driverSetup(self):
		options = Options()
		## do not open firefox 
		options.add_argument("--headless")
		driver = webdriver.Firefox(executable_path = "/usr/local/bin/geckodriver", options = options)
		driver.implicitly_wait(1)
		return driver
	## read csv file to process each ingredient
	def read(self):
		driver = self.driverSetup()
		with open(self.url, "r") as f:
			## ignore first 3 lines in the file
			for _ in range(3):
				next(f)
			csvReader = csv.reader(f, delimiter = ",")
			for line in csvReader:
				print("===========================")
				print(line[0])
				driver.get(line[1])
				headers = self.getHeader(driver)
				for each in headers:
					if each in 
				print("===========================")
			#for line in csvReader:
	## extract desired headers from website
	## @driver: selenium driver
	## @level: 
	def getHeader(self, driver, level):
		headers = driver.find_elements_by_tag_name("h2")
		values = [self.remove(each.text) for each in headers]
		return values

	## main function
	def run(self):
		self.read()

x = nhpid_header()
x.run()
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