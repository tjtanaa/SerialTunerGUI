import struct as st
import serial as sp
import params as p

class serialPort:
    #private
    _ser = []
    _connected = False
    _changed = False

    _rxBuffer = []

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
        self._ser = sp.Serial(self.portName, 115200, timeout=1)
        print 'Connected to '+self._ser.name
        self._connected = True
        self._changed = True

    def disconnect(self):
        self._ser.close()
        del self._ser
        self._connected = False
        self._changed = True

    def sendCommand(self, value, index):
        byte = st.pack('f',value)
        print 'p '+str(index)+' '+str(value)+'\n'
        self._ser.write('p'+chr(index))
        self._ser.write(byte)

    def getParam(self, params):
        print 'p get\n'
        #TODO:getParameters
        #while condition
            #print 'p NOTok\n'
        print 'p ok\n'

    def clearRxBuffer(self):
        del self._rxBuffer[:]
        self._rxBuffer = []
