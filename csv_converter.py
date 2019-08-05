import pandas as pd
import json
import argparse

from collections import OrderedDict


def parse_args():
    """
    set up arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--con_infile", type=str,
                        required=True,
                        help="""Full path of the file to store
                                consumer section data""")
    parser.add_argument("--pro_infile", type=str,
                        required=True,
                        help="""Full path of the file to store
                                professional section data""")
    parser.add_argument("--con_outfile", type=str,
                        required=True,
                        help="""Full path of the file to the 
                                converted consumer file""")
    parser.add_argument("--pro_outfile", type=str,
                        required=True,
                        help="""Full path of the file to the 
                                converted professional file""")
    args = parser.parse_args()
    return args


"""
Convert .json files into pandas DataFrame, then to .csv
"""


class converter(object):

    def __init__(self, con_infile, pro_infile,
                 con_outfile, pro_outfile):
        """
        converter constructor

        :param str con_infile: the full path to consumer .json file
        :param str pro_infile: the full path to professional .json file
        :param str con_outfile: the full path to the consumer .tsv file
        :param str pro_outfile: the full path to the pro .tsv file
        """
        self.con_file = con_infile
        self.pro_file = pro_infile
        self.con_outfile = con_outfile
        self.pro_outfile = pro_outfile

    def read_json_file(self, read_type):
        """
        Read .json file with read_type

        :param str read_type: .json file indicator
                              con -> consumer file
                              pro -> professional file
        """
        if read_type.lower() == "con":
            con_df = self.process_json_file(self.con_file)
            con_df.to_csv(self.con_outfile, sep="\t",
                          index=False)
        elif read_type.lower() == "pro":
            pro_df = self.process_json_file(self.pro_file)
            pro_df.to_csv(self.pro_outfile, sep="\t",
                          index=False)
        else:
            raise ValueError("Only con and pro supported.")

    def process_json_file(self, file_par):
        """
        Read consumer file
        Process the file into DataFrame

        :param str file_par: file name parameter
                             self.con_file -> consumer file
                             self.pro_file -> professional file
        :return: the dataframe with full headers and contents
        :rtype: pd.DataFrame
        """
        # find universal dataframe headers
        con_data = []
        with open(file_par, "r") as f:
            for line in f:
                herb_data = json.loads(line)
                con_data.append(herb_data)
        con_columns = [list(data.keys()) for data in con_data]
        con_columns = [val for sublist in con_columns for val in sublist]
        con_columns = sorted(list(set(con_columns)))
        con_df = pd.DataFrame(columns=con_columns)
        # fill the data with same headers
        with open(file_par, "r") as f:
            for line in f:
                herb_data = json.loads(line)
                od_herb_data = self.fill_dict_to_same_length(
                               headers=con_columns,
                               dict_to_fill=herb_data)
                # drop the accidientcal "key"
                od_herb_data.pop("key", None)
                # fill the dataframe
                con_df = con_df.append(od_herb_data, ignore_index=True)
            print(con_df.shape)
        # move the last two columns in the front
        cols = con_df.columns.tolist()
        cols.insert(0, cols.pop(cols.index("url")))
        cols.insert(0, cols.pop(cols.index("name")))
        con_df = con_df.reindex(columns=cols)
        return con_df

    def fill_dict_to_same_length(self, headers, dict_to_fill):
        """
        Fill the data if a universal key not appears in it

        :param list headers: the list of universal headers
        :param dict: dict_to_fill: the dict to be checked and fill

        :return: a dict with full universal headers,
                 if the header does not appear in the original dict,
                 fill it with empty string, ""
        :rtype: dict
        """
        for each in headers:
            if each not in dict_to_fill.keys():
                dict_to_fill[each] = ""
        od = OrderedDict(sorted(dict_to_fill.items()),
                         key=lambda t: t[0])
        return od

    def start_process(self):
        self.read_json_file("con")
        self.read_json_file("pro")


if __name__ == "__main__":
    args = parse_args()
    x = converter(args.con_infile, args.pro_infile,
                  args.con_outfile, args.pro_outfile)
    x.start_process()
