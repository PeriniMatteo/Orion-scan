
#!/usr/bin/python


import tkinter
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time
from take4 import TakeDialog


class simpleapp_tk(tkinter.Tk):
    def __init__(self,parent):
        tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
        
    def initialize(self):
        self.grid()

        self.btnTake = tkinter.Button(self,text=u"Take Images",command=self.OnButtonTakeClick)
        self.btnTake.grid(column=0,row=0,sticky='NSEW')
        
        self.btnPP = tkinter.Button(self,text=u"PostPrcessing",command=self.OnButtonPPClick)
        self.btnPP.grid(column=0,row=1,sticky='NSEW')
        
        self.btnExit = tkinter.Button(self,text=u"Exit",command=self.OnButtonExitClick)
        self.btnExit.grid(column=0,row=2,sticky='NSEW')

        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        #self.resizable(True,False)
        self.update()
        self.minsize(720,480)
    
        
        
        
    def OnButtonTakeClick(self):
        #self.new_win()
        TakeDialog(self)
        
    def OnButtonPPClick(self):
        print('PP')
        #self.new_win()
        
    def OnButtonExitClick(self):
        app.quit()


if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('My serial monitor')
    app.mainloop()
