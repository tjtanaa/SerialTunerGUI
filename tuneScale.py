class tuneScale:

    sPPow = 0
    sPDiv = 1
    sPVar = 5
    sPMin = 0
    sPMax = 10
    sPInt = 2
    sPRes = 0.01

    scaleChanged = False
    valueChanged = False

    def __init__(self, sPVar = 5, sPPow = 0):
        self.scaleChanged = False
        self.valueChanged = False
        self.sPVar = sPVar
        self.sPPow = sPPow

        self.sPDiv = pow(10,self.sPPow)

        self.sPInt = self.sPDiv*5
        self.sPRes = self.sPDiv/100

        self.sPMin = sPVar - self.sPInt
        self.sPMax = sPVar + self.sPInt

    def set(self, sPVar = 5, sPPow = 0):
        self.sPVar = sPVar
        self.sPPow = sPPow

        self.sPDiv = pow(10,self.sPPow)

        self.sPInt = self.sPDiv*5
        self.sPRes = self.sPDiv/100

        self.sPMin = sPVar - self.sPInt
        self.sPMax = sPVar + self.sPInt

    def magnify(self):
        if self.sPDiv > 1e+30:
            return

        self.sPPow = self.sPPow + 1
        self.sPDiv = self.sPDiv * 10.0
        self.sPInt = self.sPDiv*5
        self.sPRes = self.sPDiv/100
        self.sPMin = self.sPVar - self.sPInt
        self.sPMax = self.sPVar + self.sPInt
        self.scaleChanged = True

    def shrink(self):
        if self.sPDiv < 1e-12:
            return

        self.sPPow = self.sPPow - 1
        self.sPDiv = self.sPDiv / 10.0
        self.sPInt = self.sPDiv*5
        self.sPRes = self.sPDiv/100
        self.sPMin = self.sPVar - self.sPInt
        self.sPMax = self.sPVar + self.sPInt
        self.scaleChanged = True

    def tune(self,var):
        self.valueChanged = True
        self.sPVar = float(var)
