import pandas as pd

from os.path import join

"""
read related data
"""
data_path = "/Users/Changye/Downloads/idisk_rrf"
chv = pd.read_csv("CHV.tsv", sep="\t")
chv = chv["STR"].tolist()
atom_data = pd.read_csv(join(data_path, "MRCONSO.RRF"), sep="|")
con_data = pd.read_csv(join(data_path, "MRSTY.RRF"), sep="|")
rel_data = pd.read_csv(join(data_path, "MRREL.RRF"), sep="|")

"""
count for seperate data type
"""


def find_concept_output(value_type, atom_data, sub_data):
    """
    find number of CHV found in iDISK database

    :param str value_type: iDISK concept type
    :param DataFrame atom_data: iDISK data
    :param DataFrame sub_data: dataset to find the subset
    """
    sub_data.drop_duplicates()
    con = sub_data[sub_data["STY"].isin([value_type])]
    print("The number of "
          + value_type + " in the dataset: "
          + str(con.shape[0]))
    con = list(set(con["CUI"].tolist()))
    final_con = atom_data[atom_data["CUI"].isin(con)]
    final_con = final_con[final_con["STR"].isin(chv)]
    final_con = set(final_con["CUI"].tolist())
    print("The number of CHV found in iDISK " + value_type
          + " Concept: " + str(len(final_con)))


# for concept

concepts = ["DIS", "SOC", "SS", "TC"]
for each in concepts:
    find_concept_output(each, atom_data, con_data)


# for adr
adr = rel_data[rel_data["REL"].isin(["has_adverse_reaction"])]
adr = adr["CUI2"].tolist()
adr_data = con_data[con_data["CUI"].isin(adr)]
print(len(set(adr_data["CUI"].tolist())))
adr_data = adr_data["CUI"].tolist()
atom = atom_data[atom_data["CUI"].isin(adr_data)]
atom = atom[atom["STR"].isin(chv)]
print(len(set(atom["CUI"].tolist())))


# general stat
print("Total unique concepts: " + str(len(set(con_data["CUI"].tolist()))))
print("Total unique atoms: " + str(len(set(atom_data["AUI"].tolist()))))
print("Total unique relationships: " + str(len(set(rel_data["RUI"].tolist()))))
atr = pd.read_csv(join(data_path, "MRSAT.RRF"), sep="|")
print("Total unique attributes: " + str(len(set(atr["ATUI"].tolist()))))
