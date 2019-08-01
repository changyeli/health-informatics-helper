import argparse
import json

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

"""
This script is designed for scrapying MSKCC website data
Please make sure you have the scrapying permission before running this script
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


"""
Extracting MSKCC data by alphabetic listing,
then load each page and extract all herbs from [A-Z]
"""


class MSKCC_URL(object):
    """
    Get MSKCC ingredients URLs by alphabetic listing.
    Save the alphabetic listing file to self.pages
    From each URL in self.pages, load the entire page and extract all herbs.
    Save each herb's URL into self.herbs
    Return self.herbs
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
Extract section data for each herb
"""


class MSKCC_Content(object):
    """
    Extract section contents for each ingredient
    This is a following-up class for MSKCC_URL.py
    """

    def __init__(self, driver):
        """
        MSKCC_Content constructor

        :param WebDriver driver: selenium driver, setup in ExtractDriver class
        """
        # headers to skip
        self.skip_header = ["scientific_name", "references"]
        # selenium driver, setup in ExtractDriver class
        self.driver = driver

    def get_content_from_healthcare_professionals(self):
        """
        Get section contents under For Healthcare Professionals
        Store the required secitons to a dict, pro_sections
        Return sections

        :return: a dict that contains all pre-defined sections and contents
        :rtype: dict
        """
        content = self.driver.find_elements_by_css_selector("div.mskcc__article:nth-child(4)")  # noqa
        # dict to save required sections
        sections = {}
        # iterate all sections
        for each in content:
            # find section name: accordion__headline
            section_name = each.find_element_by_class_name("accordion__headline")  # noqa
            section_name = section_name.get_attribute("data-listname").strip()
            section_name = section_name.lower().split(" ")
            section_name = "_".join(section_name)
            # find section content
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

    def get_conent_from_patient_caregivers(self):
        """
        Get section contents under For Patient & Caregivers
        Store the required secitons to a dict, con_sections
        Return sections

        :return: a dict that contains all sections and contents
        :rtype: dict
        """

    def get_last_updated_date(self):
        """
        Find the date the the herb is last updated
        Return date

        :return: latest update date
        :rtype: str
        """
        section = self.driver.find_element_by_xpath('//*[@id="field-shared-last-updated"]')  # noqa
        date = section.find_element_by_class_name("datetime")
        date = date.get_attribute("datetime")
        return date

    def get_content_from_url(self, herb_name, url, scrapy_fun):
        """
        For every line in herb_file, do:
        1. Use selenium driver to open the herb's URL
        2. Save each extracted info to a dict
        3. Return the dict

        :param str herb_name: ingredient name
        :param str url: ingredient url
        :param fun scrapy_fun: the function to get sepefic sections
        :return: the dict that contains required content
        :rtype: dict
        """
        data = {}
        data["herb_name"] = herb_name
        data["url"] = url
        print("---------------------")
        print("Currently processing herb: " + herb_name)
        self.driver.get(url)
        sections = scrapy_fun
        if sections is not None:
            data.update(sections)
        data["last_updated_date"] = self.get_last_updated_date()
        print("---------------------")
        return data


"""
Driver class for MSKCC data extraction
"""


class extract_driver(object):
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
        # options.add_argument("--headless")
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
        url_getter = MSKCC_URL(driver)
        content_getter = MSKCC_Content(driver)
        line_seen = []
        # extract herb url
        name2url = url_getter.get_herb_url()
        # iterate name2url tp get content
        for herb_name, url in name2url.items():
            # consumer sections
            content = content_getter.get_content_from_url(
                      herb_name, url,
                      content_getter.get_conent_from_patient_caregivers()
            )
            with open(self.con_file, "a") as con_f:
                if content not in line_seen:
                    json.dump(content, con_f)
                    con_f.write("\n")
            # professional sections
            content = content_getter.get_content_from_url(
                      herb_name, url,
                      content_getter.get_content_from_healthcare_professionals()  # noqa
            )
            with open(self.pro_file, "a") as con_f:
                if content not in line_seen:
                    json.dump(content, con_f)
                    con_f.write("\n")
        driver.close()


if __name__ == "__main__":
    args = parse_args()
    x = extract_driver(args.pro_file, args.con_file)
    x.extract_process()
