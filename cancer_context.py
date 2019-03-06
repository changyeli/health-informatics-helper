import csv, json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
class cancer_context(object):
	def __init__(self):
		self.urls = "cancer_herb_url.csv"
	def driverSetup(self):
		options = Options()
		## do not open firefox 
		options.add_argument("--headless")
		driver = webdriver.Firefox(executable_path = "/usr/local/bin/geckodriver", options = options)
		driver.implicitly_wait(1)
		return driver
	## get content under common names
	def getCommon(self, driver):
		print("extracting common names")
		context = driver.find_element_by_id("block-mskcc-content")
		## if the herb has common names
		try:
			value = context.find_element_by_class_name("list-bullets")
			items = value.find_elements_by_tag_name("li")
			names = []
			for each in items:
				names.append(each.text.strip())
			return names
		except NoSuchElementException:
			return ""
	## check if it's under correct section
	def correctSection(self, context):
		for each in context:
			try:
				forPro = each.find_elements_by_xpath('//*[@id="msk_professional"]')
				print("under For Healthcare Professionals")
				## find all sections under For Healthcare Professionals
				headers = each.find_elements_by_class_name("accordion ")
				return self.getContent(headers)
			except NoSuchElementException:
				print("ignore For Patients & Caregivers")
				pass
	## get content for each accordion__headeline
	def getContent(self, headers):
		print("extracting sections and contents")
		## dict to save every section information
		sections = {}
		## iterate each section
		for each in headers:
			## find section name: accordion__headline
			section_name = each.find_element_by_class_name("accordion__headline").get_attribute("data-listname").strip()
			## ignore not-wanted sections
			if section_name == "Herb Lab Interactions" or section_name == "Brand Name" or section_name == "References" or section_name == "Dosage (OneMSK Only)" or section_name == "Brand Name":
				pass
			else:
			## find section context: field-item
				section_content = each.find_element_by_class_name("field-item")
				## if current section has bullet-list
				try:
					value = section_content.find_element_by_class_name("bullet-list")
					items = value.find_elements_by_tag_name("li")
					bullets = []
					for each in items:
						bullets.append(each.text.strip())
					sections[section_name] = bullets
				except NoSuchElementException:
					sections[section_name] = section_content.text.strip()
		return sections
	## get content under For Healthcare Professional
	def getPro(self, driver):
		## For Healthcare Professionals main context
		## mskcc__article mskcc__article--sub-article navigate-section
		context = driver.find_elements_by_xpath("/html/body/div[2]/div/div/div[1]/main/div/div[2]/div[2]/div[4]/div/div/article/div[1]/div[4]")
		return(self.correctSection(context))
	## get last updated information
	def getUpdate(self, driver):
		print("extracting last updated information")
		section = driver.find_element_by_xpath('//*[@id="field-shared-last-updated"]')
		time = section.find_element_by_xpath("/html/body/div[2]/div/div/div[1]/main/div/div[2]/div[2]/div[4]/div/div/article/div[1]/div[6]/div/div/time").get_attribute("datetime")
		return time
	## main function
	def run(self):
		driver = self.driverSetup()
		try:
			with open(self.urls, "r") as f:
				readCSV = csv.reader(f, delimiter = ",")
				for row in readCSV:
					## save each website's extraction in to dict, then save it to json
					data = {}
					driver.get(row[1])
					print("=========================")
					print("processing " + row[0])
					data["Name"] = row[0]
					names = self.getCommon(driver)
					data["Common Names"] = names
					sections = self.getPro(driver)
					for k, v in sections.items():
						data[k] = v
					data["Last Updated"] = self.getUpdate(driver)
					print("=========================")
					with open("cancer_herb_content.json", "a") as output:
						json.dump(data, output, indent = 4)
		except IOError:
			print("No such file, please run cancer_header.py first.")
		driver.close()
	## test with single url
	def test(self):
		driver = self.driverSetup()
		driver.get("https://www.mskcc.org/cancer-care/integrative-medicine/herbs/chrysanthemum")
		print("==========================")
		print("--------------------------")
		print("Common Names")
		self.getCommon(driver)
		print("--------------------------")
		self.getPro(driver)
		print("--------------------------")
		print("Last Updated")
		self.getUpdate(driver)
		print("--------------------------")
		print("==========================")
x = cancer_context()
x.run()