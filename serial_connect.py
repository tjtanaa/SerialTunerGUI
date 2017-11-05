import struct as st
import serial as sp
import params as p

class serialPort:
    #private
    _ser = []
    _connected = False
    _changed = False

    rxBuffer = ()

    param_count = 0
    _subparam_count = 0

    #public
    portName = ''

    def __init__(self):
        self._connected = False
        self._changed = False

    def checkConnection(self):
        self._changed = False
        return self._connected

    def checkConnectionChange(self):
        return self._changed

    def connect(self):
        self._ser = sp.Serial(self.portName, 115200, timeout=0.5)
        print 'Connected to '+self._ser.name
        self._connected = True
        self._changed = True

    def disconnect(self):
        self._ser.close()
        del self._ser
        self._connected = False
        self._changed = True

    def sendParam(self, value, index, sub_index):
        byte = st.pack('f',value)
        self._ser.write('p'+chr(index)+chr(sub_index))
        self._ser.write(byte)
        print 'p '+str(index)+' '+str(sub_index)+' '+str(value)

    def sendScale(self, index, sub_index, power):
        byte = st.pack('i',power)
        self._ser.write('s'+chr(index)+chr(sub_index))
        self._ser.write(byte)
        print 's '+str(index)+' '+str(sub_index)+' '+str(power)

    def sendConfirmation(self):
        byte1 = st.pack('i',self.param_count)
        byte2 = st.pack('i',self._subparam_count)
        self._ser.write('ccc')
        self._ser.write(byte1)
        self._ser.write(byte2)
        print 'c '+str(self.param_count)+' '+str(self._subparam_count)

    def sendUpdateCommand(self):
        self._ser.write('update ')
        print 'parameters saved'

    def getParam(self, params):
        #TODO:getParameters
        self._ser.flush()
        self._ser.write('getPIDs')

        byte1 =  self._ser.read(1)
        byte2 =  self._ser.read(1)

        if len(byte1) == 0:
            print 'Unable to retrieve parameters from board!'
            return False;

        self.param_count = (st.unpack('B',byte1))[0]
        self._subparam_count = (st.unpack('B',byte2))[0]

        print 'Retrieved '+str(self.param_count)+' parameters and ' +\
            str(self._subparam_count)+' sub-parameters'

        byteSubparams =  self._ser.read(self.param_count * 8)
        for byte in byteSubparams:
            self.rxBuffer = self.rxBuffer + st.unpack('b',byte)
        param_count = 0

        for i in range(0, self.param_count):
            print 'Param '+ str(i)+' has '+ str(self.rxBuffer[8*i])+ ' subparams'
            for j in range(0, self.rxBuffer[8*i]):
                byteparams = self._ser.read(4)
                self.rxBuffer = self.rxBuffer + st.unpack('f',byteparams)
            param_count = param_count + self.rxBuffer[8*i]

        self._ser.flush()
        if len(byteSubparams) != self.param_count*8 or param_count != self._subparam_count:
            print 'GODDAMNIT!!Fucking incorrect parameters on board!'
            return False;

        return True
