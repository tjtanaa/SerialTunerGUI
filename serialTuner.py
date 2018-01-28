import Tkinter as tk
import time

import tuneScale as ts
import serial_connect as sc
import params as p
import datetime as dt

window = tk.Tk()
window.title('SerialTuner')
window.geometry('900x500')
version = '1.2.02'

logo = tk.PhotoImage(file="logo.gif")

w1 = tk.Label(window, image=logo).place(x=35,y=360)
tk.Label(window,text= version,font=('Arial,2')).place(x=35,y=465)

#====================Serial Connection====================
sp = sc.serialPort()
tk.Label(window,text='Enter Serial Port Name:',font=('Arial,8')).place(x=10,y=10)
eserialName = tk.Entry(window, width = 15, borderwidth = 2,font=('Arial,8'))
eserialName.place(x=210,y=8)

connectStatusString = tk.StringVar()
connectStatusString.set('Status: Not connected')
lconnectStatus = \
    tk.Label(window,textvariable = connectStatusString,font=('Arial,7')).place(x=490,y=10)

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

paramList = []

def list_show(paramList):
    global clb
    for item in paramList:
        if item.private == False:
            clb.insert('end',item.name)
        else:
            clb.insert('end','')

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
        tScale = ts.tuneScale(subp.value, subp.power);
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
#==================On-board flash update==================
bflash = tk.Button(window,text = 'Update',command = sp.sendUpdateCommand,
        width = 8, height = 1,font=('Arial,6'))
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
                sp.sendParam(tScale.sPVar, paramList[param_index].index, \
                paramList[param_index].subParams[index].index)
            tScale.valueChanged = False
        index = index + 1

    index = 0
    scaleChanged = False
    for tScale in tScaleList:
        if tScale.scaleChanged == True:
            changeScale(paramList[param_index].subParams[index],index)
            paramList[param_index].subParams[index].power = tScale.sPPow
            sp.sendScale(paramList[param_index].index, \
                paramList[param_index].subParams[index].index, \
                tScale.sPPow)
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
            if paramList[param_index].private == False:
                setScale(paramList[param_index])
                scaleChanged = True
            else:
                param_index = 1000000

def param_update(sp):
    global paramList
    param_val_index = 9*(sp.param_count)
    for i in range(0, sp.param_count):
        parameter = p.param(sp.paramName[i], sp.rxBuffer[9*i + 8])
        parameter.private = sp._private_flag[parameter.index]
        for j in range(0, sp.rxBuffer[9*i]):
            parameter.addSubParam(p.subParam(sp.subParamName[i][j],\
                sp.rxBuffer[param_val_index],sp.rxBuffer[9*i + j + 1],j))
            param_val_index = param_val_index + 1
        paramList.append(parameter)
    sp.clearRxBuffer()

def serialPort_update(sp):
    global eserialName
    global paramList
    global bflash
    if sp.checkConnectionChange():
        if sp.checkConnection() == False:
            tconnectButton.set('Connect')
            connectStatusString.set('Status: Not connected')
            bflash.destroy()
            list_clear()
            clearScale()
            del paramList[:]
        else:
            if sp.getParam(paramList) == False:
                sp.disconnect();
                connectStatusString.set('Status: Not connected')
                return;
            bflash = tk.Button(window,text = 'Update',command = sp.sendUpdateCommand,
                    width = 8, height = 1,font=('Arial,6'))
            bflash.place(x=785,y=5)
            param_update(sp)
            tconnectButton.set('Disconnect')
            connectStatusString.set('Status: Connected to '+sp.portName)
            list_show(paramList)

#=====================TODO: Save log======================
tk.Label(window,text='Enter Target File Name:',font=('Arial,8')).place(x=175,y=460)
eFileName = tk.Entry(window, width = 25, borderwidth = 2,font=('Arial,8'))
eFileName.place(x=372,y=458)
popWindow1 = 0
popWindow2 = 0
fileName = 0

#TODO: Save parameters to Log
def saveToFile(f):
    if len(paramList) > 0:
        f.write('--RMTunerEnterprize--' + dt.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '--\n')
        for item in paramList:
            f.write(item.name +'\n '+ str(item.index) + ' ' + str(item.private) + ' '+str(len(item.subParams))+'\r\n')
            for subitem in item.subParams:
                f.write('\t'+str(subitem.value)+' '+subitem.name +' ' +str(subitem.power)+' '+str(subitem.index)+'\r\n')
        print 'File saved'
    else:
        print 'No parameters to save'

def inputYes1():
    f = open(fileName,'w')
    saveToFile(f)
    f.close()
    popWindow1.destroy()

def inputNo1():
    popWindow1.destroy()

def paramSave():
    global popWindow1
    global fileName
    fileName = eFileName.get()
    if fileName == '' or len(fileName) < 4 or fileName[len(fileName)-4:len(fileName)] != '.txt':
        print 'please input the target file name'
        return

    try:
        f = open(fileName,'r')
    except IOError:
        fn = open(fileName,'w')
        saveToFile(fn)
        fn.close()
        return

    line1 = f.readline()
    if line1[0:21] != '--RMTunerEnterprize--':
        print 'Invalid file name 2'
        f.close()
        return

    popWindow1 = tk.Toplevel()
    popWindow1.title('Warning')
    popWindow1.geometry('400x150')
    tk.Label(popWindow1,text='Are you sure to overwrite this file?',font=('Arial,8')).place(x=50,y=25)
    bY = tk.Button(popWindow1,text = 'Yes',command = inputYes1,
        width = 10, height = 1,font=('Arial,6'))
    bY.place(x=60,y=100)
    bN = tk.Button(popWindow1,text = 'No',command = inputNo1,
        width = 10, height = 1,font=('Arial,6'))
    bN.place(x=210,y=100)

def LoadToDevice(f,paramList):
    global sp
    global scaleList

    nameList = []
    subNameList = []
    tempParamList = []

    while True:
        name = f.readline()
        if name == '':
            f.close()
            break
        name = name[0:len(name)-1]

        info = f.readline()
        infolist = info.split(' ')[1:4]
        param = p.param(name,int(infolist[0]))
        param.private = (infolist[1] == 'True')

        subName = []
        for i in range(0,int(infolist[2])):
            subline = f.readline()
            sublist = subline.split(' ')
            param.addSubParam(p.subParam(sublist[1],float(sublist[0]),int(sublist[2]),i))
            subName.append(sublist[1])
        tempParamList.append(param)
        nameList.append(name)
        subNameList.append(subName)

    for param in paramList:
        try:
            index = nameList.index(param.name)
            for subParam in param.subParams:
                try:
                    subIndex = subNameList[index].index(subParam.name)
                    if subParam.value != tempParamList[index].subParams[subIndex].value:
                        subParam.value = tempParamList[index].subParams[subIndex].value
                        sp.sendParam(subParam.value, param.index, subParam.index)
                        print 'Updated \"'+subParam.name+'\" of \"'+param.name+"\" to be "+str(subParam.value)
                    if subParam.power != tempParamList[index].subParams[subIndex].power:
                        subParam.power = tempParamList[index].subParams[subIndex].power
                        sp.sendScale(param.index, subParam.index, subParam.power)
                except ValueError:
                    print 'W: Parameter \"'+param.name+'\" (Num:'+str(tempParamList[index].index)+') missing sub-param in file'
        except ValueError:
            print 'W: Parameter \"'+param.name+'\" (Num:'+str(tempParamList[index].index)+') not found in file'
        clearScale()

def inputYes2():
    global paramList
    fileName = eFileName.get()
    if fileName == '' or len(fileName) < 4 or fileName[len(fileName)-4:len(fileName)] != '.txt':
        print 'please input the target file name'
        return

    try:
        f = open(fileName,'r')
        line1 = f.readline()
        if line1[0:21] != '--RMTunerEnterprize--':
            print 'Invalid file name'
            f.close()
            return

        LoadToDevice(f,paramList)
        f.close()

    except IOError:
        print 'Invalid file name'
    popWindow2.destroy()

def inputNo2():
    popWindow2.destroy()

def paramLoad():
    global popWindow2

    popWindow2 = tk.Toplevel()
    popWindow2.title('Warning')
    popWindow2.geometry('400x150')
    tk.Label(popWindow2,text='Loading parameter file might be dangerous',font=('Arial,8')).place(x=35,y=50)
    tk.Label(popWindow2,text='Please make sure the device is protected',font=('Arial,8')).place(x=35,y=25)
    bY = tk.Button(popWindow2,text = 'Yes',command = inputYes2,
        width = 10, height = 1,font=('Arial,6'))
    bY.place(x=60,y=100)
    bN = tk.Button(popWindow2,text = 'No',command = inputNo2,
        width = 10, height = 1,font=('Arial,6'))
    bN.place(x=210,y=100)

bsave = tk.Button(window,text = 'Save to file',command = paramSave,
    width = 10, height = 1,font=('Arial,6'))
bsave.place(x=632,y=455)

bload = tk.Button(window,text = 'Load to device',command = paramLoad,
    width = 10, height = 1,font=('Arial,6'))
bload.place(x=765,y=455)
#========================Main loop=========================
while True:
    scale_update()
    serialPort_update(sp)
    window.update_idletasks()
    window.update()
    time.sleep(0.075)
