import argparse
import os
import subprocess
import json


def parse_args():
    """
    Set up arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--content_file", type=str,
                        required=True,
                        help="the full path of MSKCC content file.")
    parser.add_argument("--mm_location", type=str,
                        required=True,
                        help="MetaMap location")
    args = parser.parse_args()
    return args


"""
This script is used for MetaMap tutorial
This tutorial is designed for:
    - MetaMap 2016
    - macOS platform
    - MetaMap 2018AB additional dataset
"""


class mm(object):
    """
    MetaMap wrapper
    """
    def __init__(self, infile, mm_location):
        """
        mm constructor
        """
        # file location to read in
        self.infile = infile
        # MetaMap location
        self.mm_location = mm_location

    def start_mm_server(self):
        """
        Start MetaMap server
        """
        os.chdir(self.mm_location)
        output = subprocess.check_output(["./bin/skrmedpostctl", "start"])
        print(output.decode("utf-8"))

    def get_mm_command(self, use_strict_model, use_relax_model,
                       ignore_word_order, term_processing, show_cui,
                       value, knowledge_source="2018AB",
                       data_version="Base", no_header=True):
        """
        generate MetaMap command

        Currently supported options:
            knowledge source: -Z
            data version: -V
            hide header output: --slient
            use strict model: -A
            use relax model: -C
            ignore word order: -i
            use term processing: -z
            show cui for each term: -I

        :param bool use_strict_model: use MetaMap strict model
        :param bool use_relax_model: use MetaMap relax model
        :param bool ignore_word_order: ignore input word order
        :param bool term_processing: process input content in short fragment
        :param bool show_cui: show CUI for each term
        :param str value: the content is to be annotated
        :param str knowledge_source: sets the version of the UMLS to use,
                                 default to 2018AB
        :param str data_version: sets MetaMap’s data version,
                             default to Base
        :param bool no_header: suppress the display of header information,
                               default to True
        :return: the full commends for MetaMap
        :rtype: str
        """
        if use_strict_model and use_relax_model:
            raise ValueError("You cannot use two models at the same time.")
        if value is None:
            raise ValueError("You must define the content to be annotated.")
        if data_version not in ["Base", "USAbase", "NLM"]:
            raise ValueError("You must choose among Base, USAbase, NLM")
        comm = "echo " + value + " | " + "./bin/metamap16"
        comm += " -Z 2018AB"
        comm += " -V Base"
        if use_strict_model:
            comm += " -A"
        if use_relax_model:
            comm += " -C"
        if ignore_word_order:
            comm += " -i"
        if term_processing:
            comm += " -z"
        if show_cui:
            comm += " -I"
        if no_header:
            comm += " --silent"
        return comm

    def annotate_list_content(self, value):
        """
        use MetaMap to annotate each item in a list
        print out the annotated result

        :param list value: the list content to be annotated
        """
        for each in value:
            comm = self.get_mm_command(
                use_relax_model=True,
                ignore_word_order=True,
                term_processing=True,
                show_cui=True,
                use_strict_model=False,
                value=each,
                no_header=True)
            output = subprocess.Popen(
                comm,
                shell=True,
                stdout=subprocess.PIPE).stdout.read()
            print(output.decode("utf-8"))

    def annotate_str_content(self, value):
        """
        use MetaMap to annotate the string content
        print out the annotated result

        :param str value: the string content to be annotated
        """
        # check if the string has multiple content split by \n
        value = value.split("\n")
        # if the content is actually a list
        if len(value) > 1:
            self.annotate_list_content(value)
        # if the content is only a string
        else:
            value = value[0]
            comm = self.get_mm_command(
                use_strict_model=False,
                use_relax_model=True,
                show_cui=True,
                no_header=True,
                term_processing=True,
                ignore_word_order=True,
                value=value
            )
            output = subprocess.Popen(
                comm,
                shell=True,
                stdout=subprocess.PIPE).stdout.read()
            print(output.decode("utf-8"))

    def process_content_file(self):
        """
        process content file to get annotation
        """
        self.start_mm_server()
        with open(self.infile, "r") as f:
            for line in f:
                herb = json.loads(line)
                pu = herb["purported_uses"]
                if isinstance(pu, list):
                    pass
                    self.annotate_list_content(pu)
                else:
                    self.annotate_str_content(pu)
                break


if __name__ == "__main__":
    args = parse_args()
    x = mm(args.content_file, args.mm_location)
    x.process_content_file()
