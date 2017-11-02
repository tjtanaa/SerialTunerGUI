class subParam:
    name = ''
    value = 5
    division = 1
    index = 0

    def __init__(self, name, value, division, index):
        self.name = name
        self.value = value
        self.division = division
        self.index = index

class param:
    name = ''
    subParams = []

    def __init__(self, name):
        self.name = name
        self.subParams = []

    def addSubParam(self,subParam):
        self.subParams.append(subParam)
