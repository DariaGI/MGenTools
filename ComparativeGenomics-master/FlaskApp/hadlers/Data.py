import polars as pl

class Data():

    def __init__(self):
        self.rastCls = pl.DataFrame()
        self.kwCls = pl.DataFrame(data=[], schema=[
            ('Category', pl.Utf8),
            ('System', pl.Utf8),
            ('Subsystem', pl.Utf8),
            ('Function', pl.Utf8)
        ])
        self.classified = {}
        self.count = pl.DataFrame()
        self.hierarchy = {}
        self.userCls = pl.DataFrame()
        self.plots = {}
        self.breakdown = pl.DataFrame()
        self.distance_matrix = {}
        self.statistics_results = {}

    def reset(self):
        self.kwCls = pl.DataFrame(data=[], schema=[
            ('Category', pl.Utf8),
            ('System', pl.Utf8),
            ('Subsystem', pl.Utf8),
            ('Function', pl.Utf8)
        ])
        self.classified = {}
        self.count = pl.DataFrame()
        self.userCls = pl.DataFrame()
        self.plots = {}
        self.breakdown = pl.DataFrame()
        self.distance_matrix = {}
        self.statistics_results = {}

    def setRastCls(self, file):
        self.rastCls = file

    def setKwCls(self, file):
        self.kwCls = file

    def getRastCls(self):
        return self.rastCls

    def getKwCls(self):
        return self.kwCls

    def setClassified(self, files):
        self.classified = files

    def getClassified(self):
        return self.classified

    def setCount(self, file):
        self.count = file

    def getCount(self):
        return self.count

    def setResCount(self):
        self.count = pl.DataFrame()

    def setHierarchy(self, file):
        self.hierarchy = file

    def getHierarchy(self):
        return self.hierarchy

    def setUserCls(self, file):
        self.userCls = file

    def getUserCls(self):
        return self.userCls

    def setPlots(self, file):
        self.plots = file

    def getPlots(self):
        return self.plots

    def resPlots(self):
        self.plots = {}



    def setBreakdown(self, file):
        self.breakdown = file

    def getBreakdown(self):
        return self.breakdown

    def setComputedMatrix(self, file):
        self.distance_matrix = file

    def getComputedMatrix(self):
        return self.distance_matrix

    def resComputedMatrix(self):
        self.distance_matrix = {}


    def setStatResults(self, file):
        self.statistics_results= file

    def getStatResults(self):
        return self.statistics_results



