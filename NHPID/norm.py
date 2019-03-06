import pickle, re, csv
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
class norm(object):
	def __init__(self):
		self.file = "headers"
		self.header = []
		self.roman = {"i": 1, "ii": 2, "iii": 3, "iiii": 4, "v": 5,
		"vi": 6, "vii": 7, "viii": 8, "viiii": 9, "x": 10}
	## load dumped headers
	def load(self):
		with open(self.file, "rb") as f:
			self.header = pickle.load(f)
	## normalization process
	## step 1
	def step1(self):
		print("start step 1: general pre-process")
		self.header = [each.lower() for each in self.header]
		self.header = [each.strip() for each in self.header]
		## remove parenthesis area
		self.header = [re.sub(r" ?\([^)]+\)", "", item) for item in self.header]
		## remove additional parenthesis
		self.header = [each.replace(")", "") for each in self.header]
		new_header = []
		for each in self.header:
			## remove supplementary section names
			if ":" in each:
				temp = each.split(":")
				each = temp[0]
			## remove table/appendix names
			elif "table" in each or "appendix" in each:
				## table/appendix with number
				try:
					s = re.search("\d", each)
					each = each[:s.start()+1]
					each = re.sub("\s+", " ", each).strip()
				## table/appendix with roman numerals
				except AttributeError:
					values = each.split("\t")[0]
					item = values.split(" ")
					try:
						each = item[0] + " " + str(self.roman[item[1]])
					except KeyError:
						pass
			each = re.sub("\s+", " ", each).strip()
			new_header.append(each)
		print("finish step 1")
		return new_header
	## step 2
	## proper name, common name, source material
	def step2(self, new_header):
		print("start step 2: handle proper name, common name, source material")
		full_header = []
		for each in new_header:
			if "proper" in each:
				temp = each.split(",")
				temp = [item.strip() for item in temp]
				if len(temp) > 1:
					if "and" in temp[1]:
						values = temp[0].split("and")
						values = [item.strip() for item in values]
						full_header.extend(values)
					else:
						full_header.extend(temp)
				else:
					if "and" in temp[0]:
						values = temp[0].split("and")
						values = [item.strip() for item in values]
						full_header.extend(values)
			else:
				full_header.append(each)
		print("finish step 2")
		return full_header
	## step 3
	## plurality
	## @TODO: may need recode this function
	def step3(self, new_header):
		print("start step 3: handle plurality")
		final_header = []
		lemma = WordNetLemmatizer()
		for each in new_header:
			words = word_tokenize(each.strip())
			pos = pos_tag(words)
			clean = []
			for word, tag in pos:
				wntg = tag[0].lower()
				wntg = wntg if wntg == "n" else None
				if not wntg:
					clean.append(word)
				else:
					clean.append(lemma.lemmatize(word, wntg))
			header = " ".join(clean)
			final_header.append(header)
		print("finish step 3")
		return final_header
	## full process
	def process(self):
		new_header = self.step1()
		new_header = self.step2(new_header)
		## @TODO: may need to recode step3
		new_header = self.step3(new_header)
		self.view(new_header)
		self.write(new_header)
	## write to file
	def write(self, new_header):
		try:
			print("writing to file...")
			with open("section_count.csv", "w") as f:
				w = csv.writer(f)
				w = w.writerows(Counter(new_header).items())
			print("finish writing")
		except IOError:
			print("I/O Error")
	def view(self, new_header):
		print("===================================")
		for k, v in Counter(new_header).items():
			print(k, v)
		print("===================================")
	## main function
	def run(self):
		self.load()
		self.process()





if __name__ == "__main__":
	x = norm()
	x.run()