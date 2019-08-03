import argparse
import csv
import pickle


from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


"""
This is an alternative script for scrapying MSKCC website data
Please make sure you have the scrapying premission before running this script
"""


def parse_args():
    """
    set up arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--pro_file", type=str,
                        required=True,
                        help="""Full path of the file to store
                                professional section data""")
    parser.add_argument("--con_file", type=str,
                        required=True,
                        help="""Full path of the file to store
                                consumer section data""")
    args = parser.parse_args()
    return args


class mskcc_url(object):
    """
    Get MSKCC ingredients URLs by alphabetic listing.
    Save the alphabetic listing file to self.pages
    From each URL in self.pages, load the entire page and extract all herbs.
    Save each herb's URL into self.herbs
    Return self.herbs

    Current problem: stale exception
    """

    def __init__(self, driver):
        """
        MSKCC_URL class constructor

        :param WebDriver driver: selenium driver, setup in ExtractDriver class
        """
        self.domain = "https://www.mskcc.org/cancer-care"  # noqa
        self.start_page = "https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs/search"  # noqa
        # pages that are split by herb leading character
        self.pages = {}
        # url for each herb
        self.herbs = {}
        # selenium webdriver
        self.driver = driver

    def create_keyword_file(self):
        """
        For alphabetic listing
        Load herb URL in alphabetic listing
        """

        self.driver.get(self.start_page)
        element = self.driver.find_elements_by_class_name(
            "form-keyboard-letter")
        for each in element:
            url = each.get_attribute("href")
            if url.startswith("https://www.mskcc.org/cancer-care"):
                self.pages[each.text] = url
            else:
                url = self.domain + url
                self.pages[each.text] = url

    def complete_url(self, link):
        """
        For individual herb
        Complete the extracted herb URL if the URL is not full
        Return the full URL

        :param str link: the extracted herb's URL, from self.extract_url
        :return: full herb URL
        :rtype: str
        """
        if link.startswith("https://www.mskcc.org/cancer-care"):
            return link
        else:
            link = self.domain + link
            return link

    def extract_url(self):
        """
        For individual herb
        Extract herb URL
        """
        element = self.driver.find_elements_by_class_name(
            "baseball-card__link")
        for each in element:
            link = each.get_attribute("href")
            link = self.complete_url(link)
            name = each.text.strip()
            if name not in self.herbs:
                self.herbs[name] = link

    def load_entire_page(self):
        """
        For alphabetic listing
        Load entire page for a specific character
        I.e., load entire page under leading character "A"
        """
        print("Start to extract")
        for char, url in self.pages.items():
            print("Currently processing leading char: " + char)
            self.driver.get(url)
            # load all page
            try:
                while self.driver.find_element_by_link_text("Load More"):  # noqa
                    self.driver.find_element_by_link_text(
                                        "Load More").click()
                    self.driver.implicitly_wait(2)
            except StaleElementReferenceException:
                self.extract_url()
            except NoSuchElementException:
                self.extract_url()
        print("Finish extracting.")

    def get_herb_url(self):
        """
        Main function for MSKCC_URL class
        Return self.herbs that follows the below format
        self.herbs["herb_a"] = "herb_a's url"

        :return: dict that contains each herb's URL
        :rtype: dict
        """
        # find alphabetic listing url
        self.create_keyword_file()
        # find all ingredient urls
        self.load_entire_page()
        return self.herbs


"""
Extract content for each ingredient
"""


class mskcc_content(object):
    """
    Extract section contents for each ingredient
    This is a following-up class for mskcc_url class
    """

    def __init__(self, driver):
        """
        MSKCC_Content constructor

        :param WebDriver driver: selenium driver, setup in driver class
        """
        # headers to skip
        self.skip_header = ["Scientific Name", "References",
                            "Dosage (OneMSK Only)"]
        # selenium driver, setup in ExtractDriver class
        self.driver = driver

    def get_content_from_healthcare_professionals(self):
        """
        Get section contents under For Healthcare Professionals
        Store the required secitons to a dict, sections
        Return sections

        :return: a dict that contains all pre-defined sections and contents
        :rtype: dict
        """
        sections = {}
        content = self.driver.find_element_by_css_selector("div.mskcc__article:nth-child(5)")  # noqa
        headers = content.find_elements_by_class_name("accordion ")
        for each in headers:
            section_name = each.find_element_by_class_name("accordion__headline")  # noqa
            section_name = section_name.get_attribute("data-listname").strip()
            if section_name not in self.skip_header:
                print("section name: " + section_name)
                section_content = each.find_element_by_class_name("field-item")
                # check if the section has bullet points
                try:
                    value = section_content.find_element_by_class_name("bullet-list")  # noqa
                    items = value.find_elements_by_tag_name("li")
                    bullets = []
                    for item in items:
                        bullets.append(item.text.strip())
                    sections[section_name] = bullets
                except NoSuchElementException:
                    sections[section_name] = section_content.text.strip()
        return sections

    def get_content_from_patients_and_caregiverss(self):
        """
        Get section contents under For Patients & Caregivers
        Store all sections into a dict, sections

        :return: a dict that contains all sections and contents
        :rtype: dict
        """
        sections = {}
        content = self.driver.find_element_by_css_selector("div.mskcc__article:nth-child(4)")  # noqa
        headers = content.find_elements_by_class_name("accordion ")
        for each in headers:
            section_name = each.find_element_by_class_name("accordion__headline")  # noqa
            section_name = section_name.get_attribute("data-listname").strip()
            print("section name: " + section_name)
            section_content = each.find_element_by_class_name("field-item")
            # check if the section has bullet points
            try:
                value = section_content.find_element_by_class_name("bullet-list")  # noqa
                items = value.find_elements_by_tag_name("li")
                bullets = []
                for item in items:
                    bullets.append(item.text.strip())
                sections[section_name] = bullets
            except NoSuchElementException:
                sections[section_name] = section_content.text.strip()
        return sections

    def get_content_from_url(self, herb_name, url,
                             section_type, output):
        """
        For every line in herb_file, do:
        1. Use selenium driver to open the herb's URL
        2. Save each extracted info to a dict, based on the section_type
        3. Write the contents to dict
        4. Write the dict to local file, con_output or pro_output

        :param str herb_name: ingredient name
        :param str url: ingredient url
        :param str section_type:
                    con: For Patients & Caregivers
                    pro: For Healthcare Professionals
        :param str output: path to save section contents
        :
        """
        self.driver.get(url)
        if section_type.lower() == "con":
            data = {}
            data["name"] = herb_name
            data["url"] = url
            sections = self.get_content_from_patients_and_caregiverss()
            data.update(sections)
            with open(output, "a") as f:
                w = csv.writer(f)
                w.writerows(data.items())
        elif section_type.lower() == "pro":
            data = {}
            data["name"] = herb_name
            data["url"] = url
            sections = self.get_content_from_healthcare_professionals()
            data.update(sections)
            with open(output, "a") as f:
                w = csv.writer(f)
                w.writerows(data.items())
        else:
            raise ValueError("Only two types of section supported.")
        print("---------------------")


"""
Driver function for the script
"""


class driver(object):
    def __init__(self, pro_file, con_file):
        """
        Extraction driver constructor
        """
        # file to store professional sections
        self.pro_file = pro_file
        # file to store consumer sections
        self.con_file = con_file

    def set_driver(self):
        """
        Set up selenium driver
        """
        options = Options()
        # do not open firefox
        options.add_argument("--headless")
        options.set_preference("dom.webnotifications.enabled", False)
        driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver",  # noqa
                                   options=options)
        driver.implicitly_wait(1)
        return driver

    def extract_process(self):
        """
        Main function for extraction process
        """
        driver = self.set_driver()
        content_getter = mskcc_content(driver)
        '''
        url_getter = mskcc_url(driver)
        name2url = url_getter.get_herb_url()
        pickle.dump(name2url, open("url.p", "wb"))
        '''
        name2url = pickle.load(open("url.p", "rb"))
        for name, url in name2url.items():
            print("---------------------")
            print("Currently processing herb: " + name)
            # consumer
            print("Currently processing For Patients & Caregivers")
            content_getter.get_content_from_url(name, url,
                                                "con", self.con_file)
            # professional
            print("Currently processing For Healthcare Professionals")
            content_getter.get_content_from_url(name, url,
                                                "pro", self.pro_file)
            print("---------------------")


if __name__ == "__main__":
    args = parse_args()
    x = driver(args.pro_file, args.con_file)
    x.extract_process()
