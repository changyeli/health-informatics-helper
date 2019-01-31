import re, os, glob
import pandas as pd
## a generator to generate Brat .ann file
class generator(object):
	## constructor
	def __init__(self):
		## keyword list path
		self.keyword = "ingredient_list.csv"
		## current folder path
		self.path = os.path.dirname(os.path.realpath(__file__))
		## dataframe for the keyword list
		self.df_kw = pd.DataFrame()
	## return a list of keywords to search for
	def readKeywords(self):
		self.df_kw = pd.read_csv(self.keyword)
		keywords = self.df_kw["STR"].values
		keywords = [x.lower() for x in keywords]
		return keywords
	## get all abstracts' filename
	def getFileName(self):
		abstracts = []
		os.chdir(self.path)
		for file in glob.glob("*.txt"):
			abstracts.append(file)
		return abstracts
	## iterate all abstract files
	def iterateFiles(self):
		abstracts = self.getFileName()
		for doc in abstracts:
			ann = doc[:-4]
			with open(doc, "r") as f:
				data = f.read()
				self.findKeywords(data, ann)
	## finding keywords appeared in abstracts
	## write to filename.ann 
	def findKeywords(self, doc, ann):
		keywords = self.readKeywords()
		new_doc = doc.lower()
		output = ann + ".ann"
		for i, each in enumerate(keywords):
			each_lower = each.lower()
			if each_lower in new_doc:
				index = re.search(r'\b({})\b'.format(each_lower), new_doc)
				if index != None:
					#print(("%s\t%s %d %d\t%s" % ("T1", self.df_kw.iloc[i, 0], index.start(), index.end(), each)))
					with open(output, "a") as f:
						f.write("%s\t%s %d %d\t%s\n" % ("T1", self.df_kw.iloc[i, 0], index.start(), index.end(), each))
	## main function
	def run(self):
		self.iterateFiles()
		## finished tests
		#files = self.getFileName()
		#print(files)
		#keywords = self.readKeywords()
		#print(keywords)


## test run
test = generator()
test.run()

