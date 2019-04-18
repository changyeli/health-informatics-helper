import os
import subprocess
# get UMLS annotation for HDI, contradictions and purposed uses


class umlsAnn(object):
    def __init__(self):
        # MetaMap location
        self.location = "/Users/Changye/Documents/workspace/public_mm"
        # get this python script location
        self.path = os.path.dirname(os.path.abspath(__file__))
    # start MM server

    def start(self):
        os.chdir(self.location)
        output = subprocess.check_output(["./bin/skrmedpostctl", "start"])
        print(output)
    # get MM command
    # @value: content to be annotated
    # @additional: additional command to be added
    # @relax: true if use relax model for term processing
    # return MM commands
    # TODO: add more supported commands

    def getComm(self, value, additional="", relax=True):
        if relax:
            command = "echo " + value + " | " + "./bin/metamap16" + " -I " + "-Z 2018AB -V Base --relaxed_model " + \
                "--silent " + "--ignore_word_order" + additional  # +  "--term_processing "
            return command
        else:
            command = "echo " + value + " | " + "./bin/metamap16" + " -I " + "-Z 2018AB -V Base " + \
                "--silent " + "--ignore_word_order" + additional  # +  "--term_processing "
            return command
    # get annotated terms using UMLS
    # @output: the desired format for the annotated terms. Select choices: JSON, XML
    # return MM output

    def getAnn(self, command, output):
        if output not in ["JSON", "XML"]:
            raise ValueError("Only JSON and XML formats supported")
        else:
            if output.upper() == "JSON":
                command += " --JSONn"
            else:
                command += " --XMLf1"
        output = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE).stdout.read()
        return output
    # get annotated terms using UMLS without output format
    # @command: full command from @getComm function
    # return MM output

    def getAnnNoOutput(self, command):
        # echo lung cancer | ./bin/metamap16 -I
        # check if value is valid
        output = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE).stdout.read()
        return output
