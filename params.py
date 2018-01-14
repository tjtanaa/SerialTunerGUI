class subParam:
    name = ''
    value = 5
    power = 0
    index = 0

    def __init__(self, name, value, power, index = 0):
        self.name = name
        self.value = value
        self.power = power
        self.index = index

class param:
    name = ''
    subParams = []
    index = 0
    private = False

    def __init__(self, name, index = 0):
        self.name = name
        self.subParams = []
        self.index = index

    def addSubParam(self,subParam):
        self.subParams.append(subParam)
