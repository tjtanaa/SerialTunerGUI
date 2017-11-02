import Tkinter as tk
import time

import tuneScale as ts
import serial_connect as sc
import params as p

window = tk.Tk()
window.title('SerialTuner')
window.geometry('800x500')

#====================Serial Connection====================
sp = sc.serialPort()
tk.Label(window,text='Enter Serial Port Name:',font=('Arial,8')).place(x=10,y=10)
eserialName = tk.Entry(window, width = 15, borderwidth = 2,font=('Arial,8'))
eserialName.place(x=210,y=8)

connectStatusString = tk.StringVar()
connectStatusString.set('Status: Not connected')
lconnectStatus = \
    tk.Label(window,textvariable = connectStatusString,font=('Arial,8')).place(x=495,y=10)

tconnectButton = tk.StringVar()
tconnectButton.set('Connect')
#Connect button action
def serialConnect():
    global sp
    global eserialName
    if sp.checkConnection() == False:
        sp.portName = eserialName.get()
        if sp.portName == '':
            return
        sp.connect()
    else:
        sp.disconnect()

bconnect = tk.Button(window,textvariable = tconnectButton,command = serialConnect,
    width = 8, height = 1,font=('Arial,6'))
bconnect.place(x=375,y=5)

#=====================Listbox==============================
clb = tk.Listbox(window,font=('Arial,5'),width=15,height = 15)
clb.place(x=10,y=45)

#TODO: This is just for testing , should be retrieved from STM32
paramList = []

for i in range(0,4):
    parameter = p.param('Controller '+str(i))
    parameter.addSubParam(p.subParam('Kp',5,1,0+2*i))
    parameter.addSubParam(p.subParam('Ki',1,0.01,1+2*i))
    paramList.append(parameter)

paramList[3].addSubParam(p.subParam('Kd',10000,10,8))
#end of test variables

def list_show(paramList):
    global clb
    for item in paramList:
        clb.insert('end',item.name)

def list_clear():
    global clb
    clb.delete(0, len(paramList))

#========================Scales============================
param_index = 1000000
scaleList = []
tScaleList = []
bmagnifyList = []
bshrinkList = []

def clearScale():
    global scaleList
    global bmagnifyList
    global bshrinkList
    global tScaleList

    for scale in scaleList:
        scale.destroy()
    for button in bmagnifyList:
        button.destroy()
    for button in bshrinkList:
        button.destroy()

    del tScaleList[:]
    del scaleList[:]
    del bmagnifyList[:]
    del bshrinkList[:]

scaleX = 180
scaleY = [40,115,190,255,340,405,490]

def setScale(p):
    global scaleList
    global tScaleList
    global bmagnifyList
    global bshrinkList

    global scaleX
    global scaleY

    clearScale()

    for subp in p.subParams:
        tScale = ts.tuneScale(subp.value, subp.division);
        tScaleList.append(tScale)
        scale = tk.Scale(window, label = subp.name,from_ = tScale.sPMin, to=tScale.sPMax,
            orient = tk.HORIZONTAL, length = 500, showvalue = True, tickinterval = tScale.sPInt,
            resolution = tScale.sPRes, command = tScale.tune)
        scale.set(tScale.sPVar)
        scaleList.append(scale)

        bmagnify = tk.Button(window,text = '+',command = tScale.shrink)
        bmagnifyList.append(bmagnify)

        bshrink = tk.Button(window,text = '-',command = tScale.magnify)
        bshrinkList.append(bshrink)

    for i in range(0,len(scaleList)):
        scaleList[i].place(x=scaleX,y=scaleY[i])
        bmagnifyList[i].place(x=scaleX+520,y=scaleY[i] + 30)
        bshrinkList[i].place(x=scaleX+560,y=scaleY[i] + 30)

def changeScale(subp, index):
    global scaleList
    global tScaleList

    global scaleX
    global scaleY

    scaleList[index].destroy()
    scaleList[index] = tk.Scale(window, label = subp.name,from_ = tScaleList[index].sPMin, to=tScaleList[index].sPMax,
        orient = tk.HORIZONTAL, length = 500, showvalue = True, tickinterval = tScaleList[index].sPInt,
        resolution = tScaleList[index].sPRes, command = tScaleList[index].tune)
    scaleList[index].set(tScaleList[index].sPVar)
    scaleList[index].place(x=scaleX,y=scaleY[index])

#========================Update=========================
scaleChanged = False
def scale_update():
    global sp
    global clb
    global param_index
    global paramList
    global scaleList
    global tScaleList

    global scaleChanged

    index = 0
    for tScale in tScaleList:
        if tScale.valueChanged == True:
            paramList[param_index].subParams[index].value = tScale.sPVar
            if scaleChanged == False:
                sp.sendCommand(tScale.sPVar, paramList[param_index].subParams[index].index)
            tScale.valueChanged = False

    scaleChanged = False
    for tScale in tScaleList:
        if tScale.scaleChanged == True:
            changeScale(paramList[param_index].subParams[index],index)
            paramList[param_index].subParams[index].division = tScale.sPDiv
            tScale.scaleChanged = False
            scaleChanged = True
        index = index + 1

    if len(clb.curselection()):
        index = clb.curselection()[0]
    else:
        index = 1000000
    if index != param_index:
        param_index = index
        if param_index != 1000000:
            setScale(paramList[param_index])
            scaleChanged = True

def serialPort_update(sp):
    global eserialName
    global paramList
    if sp.checkConnectionChange():
        if sp.checkConnection() == False:
            tconnectButton.set('Connect')
            connectStatusString.set('Status: Not connected')
            list_clear()
            clearScale()
        else:
            tconnectButton.set('Disconnect')
            connectStatusString.set('Status: Connected to '+sp.portName)
            sp.getParam(paramList)
            list_show(paramList)
            sp.clearRxBuffer()

#=====================TODO: Save log======================
#tk.Label(window,text='Enter Target File Name:',font=('Arial,8')).place(x=10,y=50)
eFileName = tk.Entry(window, width = 15, borderwidth = 2,font=('Arial,8'))
#eFileName.place(x=210,y=48)

def paramSave():
    pass

def paramLoad():
    pass

bsave = tk.Button(window,text = 'Save',command = paramSave,
    width = 8, height = 1,font=('Arial,6'))
#bsave.place(x=475,y=48)

bload = tk.Button(window,text = 'Load',command = paramLoad,
    width = 8, height = 1,font=('Arial,6'))
#bload.place(x=475,y=88)
#========================Main loop=========================
while True:
    scale_update()
    serialPort_update(sp)
    window.update_idletasks()
    window.update()
    time.sleep(0.075)
