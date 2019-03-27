import subprocess, os
## MetaMap wrapper for annotation 
## use MetaMap 2016 as default version
class mmwrap(object):
	## constructor
	## @location: MetaMap location in full path
	def __init__(self, location):
		## MetaMap location
		self.location = location
		## get this python script location
		self.path = os.path.dirname(os.path.abspath(__file__))
		## this script name
		self.name = "mmwrap.py"
	## start MetaMap server
	def start(self):
		## move to MetaMap location
		os.chdir(self.location)
		print(self.path)
		output = subprocess.check_output(["./bin/skrmedpostctl", "start"])
		print(output)
	## set command for MetaMap annotation
	def getAnn(self, sententce = None):
		## echo Cancer prevention | metamap
		command = ["echo"]
	## main function
	def run(self):
		self.start()

location = "/Users/Changye/Documents/workspace/public_mm/"
x = mmwrap(location)
x.run()
