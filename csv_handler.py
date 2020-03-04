import csv

class CSVHandler():
    """
    Seconds, Closed, Pending, Connected, Service Available
    0,0,1,0,400
    1,0,2,160,400
    3,0,43,280,400
    4,0,21,379,400
    ...
    """
    def __init__(self, file, mode):
        self.file = file
        if mode in ["r","w"]:
            self.mode = mode
        else:
            raise(EnvironmentError)
        self.f = open(self.file, self.mode)

    def parseCSV(self, line):
        return

    def writeCSV(self, data):
        return