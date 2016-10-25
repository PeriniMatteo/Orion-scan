#!/usr/bin/python



import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
import serial
import serial.tools.list_ports
#import threading
import time
import multiprocessing
import cv2
#from proj import ProjectorDialog
from pathlib import Path
import re
from PIL import ImageTk, Image
import subprocess
import pickle



class Ask_Device_Name_Dialog(simpledialog.Dialog):

    def __init__(self, parent,d_dict,sn):

        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.dev_dict=d_dict
        #self.sn=sn
        self.title('Choose a name for your new device!')
        self.transient(parent)
        self.parent = parent
    
        tkinter.Label(self, text="SN:").grid(row=0)
        tkinter.Label(self, text="Name:").grid(row=1)
        self.grid_columnconfigure(0,weight=1)
        print('sn === '+sn)
        self.e1_text = tkinter.StringVar()
        self.e1_text.set(str(sn))
        #self.e1 = tkinter.Entry(self,textvariable=str(sn), state=tkinter.DISABLED)
        self.e1 = tkinter.Entry(self,textvariable=self.e1_text)
        self.e1.config(state=tkinter.DISABLED)
        #self.e1
        self.e2 = tkinter.Entry(self)
    
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e2.bind("<Return>", self.return_pressed)
        #return self.e1 # initial focus
        self.ok_button = ttk.Button(self, text="OK", command=self.ok)
        self.ok_button.grid(row=2, column=0,columnspan=2, sticky='NSWE')
        self.minsize(300,10)
        self.grab_set()
        self.focus_set()
        self.wait_window(self)
    
    def return_pressed(self,event):
        self.ok()
        
    def ok(self):
        first = self.e1.get()
        second = self.e2.get()
        self.dev_dict[str(first)]=str(second)
        
        #print first, second
        print('self.dev_dict in Ask_Device_Name_Dialog')
        print(self.dev_dict)
        New_Device_Dialog.dev_dict=self.dev_dict
        print('self.dev_dict in New_Device_Dialog')
        print(New_Device_Dialog.dev_dict)
        self.parent.focus_set()
        self.destroy()
        
class Remove_Device_Dialog(simpledialog.Dialog):

    def __init__(self, parent):

        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.dev_dict = self.read_devices_list()
        #self.sn=sn
        self.title('Remove a device!')
        self.transient(parent)
        self.parent = parent
    
        tkinter.Label(self, text="Device:").grid(row=0)
        #tkinter.Label(self, text="Name:").grid(row=1)
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        
        self.combo_txt = tkinter.StringVar()
        self.combo_txt.set('not set!')
        self.combo = tkinter.ttk.Combobox(self, textvariable=self.combo_txt, postcommand = self.get_values)
        self.combo.grid(column=1,row=0, sticky='NSWE')
        #self.combo1_value.set('not set!')
        self.combo.bind("<<ComboboxSelected>>", self.newselection)
        
        #self.names_combo_txt = tkinter.StringVar()
        #self.names_combo_txt.set('not set!')
        #self.names_combo = tkinter.ttk.Combobox(self, textvariable=self.names_combo_txt, postcommand = self.get_values)
        #self.names_combo.grid(column=1,row=0, sticky='W')
        #self.combo1_value.set('not set!')
        #self.names_combo.bind("<<ComboboxSelected>>", self.newselection_names)
        
        self.ok_button = ttk.Button(self, text="Remove", command=self.ok)
        self.ok_button.grid(row=1, column=0,columnspan=2, sticky='NSWE')
        self.quit_button = ttk.Button(self, text="Exit", command=self.qq)
        self.quit_button.grid(row=2, column=0,columnspan=2, sticky='NSWE')
        self.minsize(500,10)
        self.grab_set()
        self.focus_set()
        self.wait_window(self)
        
        
    def write_devices_list(self):
        f=open('devices.txt','w')
        for d in self.dev_dict.keys():
            f.write(str(d)+' '+str(self.dev_dict[d])+'\n')
        f.close()
        
    def read_devices_list(self):
        try:
            f=open('devices.txt','r')
            dev_dict={item.split()[0] : ' '.join(item.split()[1:]) for item in f.readlines()}
            f.close()
            return dev_dict
        except:
            return None
        
    def get_values(self):
        self.combo['values'] = [str(nn)+'  '+str(self.dev_dict[nn]) for nn in self.dev_dict]
        #pass
    def newselection(self,evt):
        val = self.combo.get()
        self.sn = val.split()[0]
        self.name = self.dev_dict[self.sn]
        
        
    #def return_pressed(self,event):
    #    self.ok()
        
    def ok(self):
        self.dev_dict.pop(self.sn)
        self.write_devices_list()
        if self.dev_dict=={}:
            messagebox.showinfo('Warning', "There aren't other devices to remove!")
            self.parent.focus_set()
            self.destroy()
            #New_Device_Dialog()
        else:
            self.combo_txt.set('Select a device!')
            self.dev_dict = self.read_devices_list()
            self.get_values()
        
        
    def qq(self):
        self.parent.focus_set()
        self.destroy()
        
class New_Device_Dialog(tkinter.Toplevel):

    def __init__(self, parent=None):

        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Select a new device')
        #self.sn=''
        self.parent = parent
        self.fff=0
        self.result = None
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        self.detect_button = ttk.Button(self, text="Detect a new device", command=self.detect, default=tkinter.ACTIVE)
        self.detect_button.grid(row=0, column=0, sticky='NSWE')
        self.add_button = ttk.Button(self, text="Add to know devices", command=self.add, state=tkinter.DISABLED)
        self.add_button.grid(row=1, column=0, sticky='NSWE')
        self.remove_button = ttk.Button(self, text="Remove a device", command=self.remove)
        self.remove_button.grid(row=2, column=0, sticky='NSWE')
        self.exit_button = ttk.Button(self, text="Exit", command=self.cancel)
        self.exit_button.grid(row=3, column=0, sticky='NSWE')


        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.focus_set()
        self.wait_window(self)
        
        
        
        
        
    def remove(self):
        #if not self.fff:
        #    self.fff=0
        print('remove')
        if self.read_devices_list():
            Remove_Device_Dialog(self)
        else:
            messagebox.showinfo('Warning', "There aren't devices to remove!")
            
        #self.fff+=1
        #print(self.fff)
        #self.add_button.config(state=tkinter.ACTIVE)
        pass

    def cancel(self, event=None):
        # put focus back to the parent window
        #print(self.fff)
        self.parent.focus_set()
        self.destroy()
    def read_devices_list(self):
        try:
            f=open('devices.txt','r')
            dev_dict={item.split()[0] : ' '.join(item.split()[1:]) for item in f.readlines()}
            f.close()
            return dev_dict
        except:
            return None
    def get_sn(self,port):
        self.port=port
        p = re.compile('S..=\w+')
        self.sn=p.findall(self.port[2])[0][4:]
        print('sn = '+self.sn)
        return self.sn
        
    def check_port_in_dict(self,port,dev_dict):
        self.port=port
        self.dev_dict=dev_dict
        self.get_sn(self.port)
        if self.sn in self.dev_dict:
            return True
        else:
            return False
        
    def write_devices_list(self,dev_dict):
        self.dev_dict=dev_dict
        f=open('devices.txt','w')
        for d in dev_dict.keys():
            f.write(str(d)+' '+str(dev_dict[d])+'\n')
        f.close()
        self.add_button.config(state=tkinter.DISABLED)
            
    def detect(self):
        print('detect')
        self.dev_dict=None
        self.ports = list(serial.tools.list_ports.comports())
        if self.ports==[]:
            print('no devices detected')
            if messagebox.askretrycancel("Warning!","Can't recognize any device!\n Connect a valid device and retry."):
                self.detect()
            
        else:
            print('new device detected')
            self.dev_dict=self.read_devices_list()
            print(self.dev_dict)
            if self.dev_dict:
                new=None
                txt=''
                for dev in self.ports:
                    
                    if self.check_port_in_dict(dev,self.dev_dict):
                        txt+='Device already in use:\n'
                        #print('esiste')
                        #messagebox.showinfo('Device #'+self.sn, 'Device:'+self.dev_dict[self.sn]+' is already in your list')
                        #pass
                        txt+='ID #'+self.sn+'   Name:'+self.dev_dict[self.sn]+'\n\n'
                    else:
                        new=True
                        txt+='New device found:\n'
                        txt+='ID #'+self.sn+'\n\n'
                        #print('aggiungiamo?')
                        #self.add_button.config(state=tkinter.ACTIVE)
                if new:
                    txt+='\nUse the "Add to know devices" button to put it in your list.\n'
                    self.add_button.config(state=tkinter.ACTIVE)
                else:
                    txt+='\nNo Unknow device found!'
                messagebox.showinfo('New device found!', txt)
                        
            else:
                print('aggiungiamo nuovo?')
                self.add_button.config(state=tkinter.ACTIVE)
                txt='\nUse the "Add to know devices" button to put it in your list.\n'
                messagebox.showinfo('Unknow device found!', txt)
                #messagebox.showinfo('New device found!', 'Use the "Add to know devices" button to put it in your list.')
                #Ask_Device_Name_Dialog(self.dev_dict,sn)
                

    def add(self):
        print('add')
        #print(self.dev_dict)
        #p = re.compile('S..=\w+')
        if self.dev_dict:
            for dev in self.ports:
                if self.check_port_in_dict(dev,self.dev_dict):
                    messagebox.showinfo('', 'Device '+self.sn+' is already in your list.')
                else:
                    if messagebox.askyesno('New device found!', self.sn+'Found!\nDo you want to add this serial device to your system?'):
                        print(self.dev_dict)
                        Ask_Device_Name_Dialog(self,self.dev_dict,self.sn)
                        print(self.dev_dict)
                        print('siiiiiiiiiiiiiiiiiii')
                        self.write_devices_list(self.dev_dict)
        else:
            #self.ports
            self.dev_dict={}
            self.get_sn(self.ports[0])
            print('a')
            print(self.dev_dict)
            Ask_Device_Name_Dialog(self,self.dev_dict,self.sn)
            print('b')
            print(self.dev_dict)
            print('soooooooooooooooo')
            self.write_devices_list(self.dev_dict)
            if len(self.ports)>1:
                self.add()
            
                
        #else:
            #p = re.compile('S..=\w+')
            #self.dev_dict={}
            #for dev in ports:
                #sn=p.findall(dev[2])[0][4:]
                #if messagebox.askyesno('New device found!', 'Do you want to add this device to your system?'):
                    #Ask_Device_Name_Dialog(self.dev_dict,sn)
class New_Camera_Dialog(tkinter.Toplevel):
    pass
        

class ProcessWindow(tkinter.Toplevel):
    def __init__(self, parent, process, serial):
        tkinter.Toplevel.__init__(self, parent)
        self.parent = parent
        self.process = process
        self.serial = serial
        self.minsize(200,100)
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)

        terminate_button = ttk.Button(self, text="Stop Scan", command=self.cancel)
        terminate_button.grid(row=0, column=0, sticky='NSWE')

        self.grab_set() # so you can't push submit multiple times
        
        

    def cancel(self):
        self.process.terminate()
        self.destroy()
        messagebox.showinfo(title="3D Scan Cancelled", message='Process was terminated from user')
        if messagebox.askyesno("Restore position?", "Come back to the 0 position?"):
            self.serial.write("$1=1\r\n".encode('ascii'))
            self.serial.write("G0 Z0\r\n".encode('ascii'))

    def launch(self):
        self.process.start()
        self.after(10, self.isAlive)

    def isAlive(self):
        if self.process.is_alive():
            self.after(100, self.isAlive)
        elif self:
            # Process finished
            messagebox.showinfo(message="3D Scan was sucessful done!", title="Finished")
            self.destroy()
            
class Check_Cameras_Dialog(tkinter.Toplevel):

    def __init__(self, parent, CL, CR):
        self.CL=CL
        self.CR=CR       
        print(self.CL)
        print(self.CR) 
        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Select a new device')
        #self.sn=''
        self.parent = parent
        #self.fff=0
        #self.result = None
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        img = Image.new("L", [4608,3072], 'white')
        #img_left = Image.open("left.jpg")
        self.img_left = img
        self.img_left = ImageTk.PhotoImage(self.img_left.resize((int(self.img_left.size[0]/10),int(self.img_left.size[1]/10)), Image.ANTIALIAS))
        #img_right = Image.open("left.jpg")
        self.img_right = img
        self.img_right = ImageTk.PhotoImage(self.img_right.resize((int(self.img_right.size[0]/10),int(self.img_right.size[1]/10)), Image.ANTIALIAS))
        #img_left = img_left

        #Displaying it
        self.imglabel_left = tkinter.Label(self, image=self.img_left)
        self.imglabel_left.grid(row=2, column=0)        
        self.imglabel_right = tkinter.Label(self, image=self.img_right)
        self.imglabel_right.grid(row=2, column=1) 
        
        
        #self.detect_button = ttk.Button(self, text="Detect a new device", command=self.detect, default=tkinter.ACTIVE)
        #self.detect_button.grid(row=0, column=0, sticky='NSWE')
        #self.add_button = ttk.Button(self, text="Add to know devices", command=self.add, state=tkinter.DISABLED)
        #self.add_button.grid(row=1, column=0, sticky='NSWE')
        #self.remove_button = ttk.Button(self, text="Remove a device", command=self.remove)
        #self.remove_button.grid(row=2, column=0, sticky='NSWE')
        
        self.exit_button = ttk.Button(self, text="Check cameras", command=self.check)
        self.exit_button.grid(row=3, column=0, columnspan=2, sticky='NSWE')
        
        self.exit_button = ttk.Button(self, text="Exit", command=self.cancel)
        self.exit_button.grid(row=4, column=0, columnspan=2, sticky='NSWE')
        self.exit_button
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.focus_set()
        self.wait_window(self)
        
    def check(self):
        if self.CL or self.CR:
            try:
                subprocess.Popen(["gphoto2","--port="+self.CL['port'],"--capture-image-and-download",'--filename=left.jpg',"--force-overwrite"])
            except:
                pass
            #time.sleep(1)
            try:
                subprocess.Popen(["gphoto2","--port="+self.CR['port'],"--capture-image-and-download",'--filename=right.jpg',"--force-overwrite"])
            except:
                pass
            time.sleep(5)
            if self.CL:
                with Image.open("left.jpg") as img_left:
                    self.img_left = ImageTk.PhotoImage(img_left.resize((int(img_left.size[0]/10),int(img_left.size[1]/10)), Image.ANTIALIAS))
                    self.imglabel_left.configure(image = self.img_left)
            if self.CR:
                with Image.open("right.jpg") as img_right:
                    self.img_right = ImageTk.PhotoImage(img_right.resize((int(img_right.size[0]/10),int(img_right.size[1]/10)), Image.ANTIALIAS))
                    self.imglabel_right.configure(image = self.img_right)
                
        

    def cancel(self, event=None):
        # put focus back to the parent window
        #print(self.fff)
        self.parent.focus_set()
        self.destroy()

class TakeDialog(tkinter.Toplevel):
    def __init__(self,parent):
        tkinter.Toplevel.__init__(self)
        self.parent = parent
        self.ser_int = []
        self.n_shots = 0
        self.n_deg = 0
        self.S_shot = None
        self.S_deg = None
        self.br_deg = 115200
        self.br_shot = 9600
        self.CL = None
        self.CR = None

        self.pattern_dir='~'
        self.pattern_files=[]
        self.dir_opt = options = {}
        options['initialdir'] = self.pattern_dir
        options['mustexist'] = False

        self.parent.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.q)
        self.initialize()
        self.i=0
        
        
    def q(self):
        print('quit')
        self.destroy()
        self.parent.update()
        self.parent.deiconify()
        
    def read_devices_list(self):
        try:
            f=open('devices.txt','r')
            dev_dict={item.split()[0] : ' '.join(item.split()[1:]) for item in f.readlines()}
            f.close()
            return dev_dict
        except:
            return None
    def get_sn(self,port):
        p = re.compile('S..=\w+')
        sn=p.findall(port[2])[0][4:]
        return sn
        
    def check_port_in_dict(self,port,dev_dict):
        sn=self.get_sn(port)
        if sn in dev_dict:
            return True
        else:
            return False
        
    def initialize(self):
        self.grid()
        
        
        self.l1 = tkinter.Label(self, text="N° Scatti")
        self.l1.grid(column=2,row=1,sticky='WE')
        self.l3 = tkinter.Label(self, text="Serial Interface")
        self.l3.grid(column=4,row=1,sticky='WE')
        self.l2 = tkinter.Label(self, text="N° Gradi")
        self.l2.grid(column=2,row=3,sticky='WE')
        self.l4 = tkinter.Label(self, text="Serial Interface")
        self.l4.grid(column=4,row=5,sticky='WE')

        self.s1 = tkinter.ttk.Separator(self, orient='horizontal')
        self.s1.grid(column=0,row=4,columnspan=7,sticky='WE')
        self.s2 = tkinter.ttk.Separator(self, orient='horizontal')
        self.s2.grid(column=0,row=8,columnspan=7,sticky='WE')

        self.entryShotsVariable = tkinter.StringVar()
        self.entryShots = tkinter.Entry(self,textvariable=self.entryShotsVariable)
        self.entryShots.grid(column=3,row=1,columnspan=1,sticky='WE')
        self.entryShots.bind("<Return>", self.Validate_Entry_Shots)
        self.entryShots.bind("<FocusOut>", self.Validate_Entry_Shots)
        
        self.entryDegrVariable = tkinter.StringVar()
        self.entryDegr = tkinter.Entry(self,textvariable=self.entryDegrVariable)
        self.entryDegr.grid(column=3,row=3,columnspan=1,sticky='WE')
        self.entryDegr.bind("<Return>", self.Validate_Entry_Degr)
        self.entryDegr.bind("<FocusOut>", self.Validate_Entry_Degr)
        
        self.btn_take = tkinter.Button(self,text=u"Take Pictures!",command=self.Take)
        self.btn_take.grid(column=0,columnspan=6,row=11, sticky='NSWE')
        
        self.table=tkinter.IntVar()
        self.cb_rolling = tkinter.Checkbutton(self,text=u"Enable Turning Table",variable=self.table)
        self.cb_rolling.grid(column=0,row=2,columnspan=2,sticky='W')
        self.camera1=tkinter.IntVar()
        self.cb_camera1 = tkinter.Checkbutton(self,text=u"Enable Camera1",variable=self.camera1)
        self.cb_camera1.grid(column=0,row=5,columnspan=2,sticky='W')
        self.camera2=tkinter.IntVar()
        self.cb_camera2 = tkinter.Checkbutton(self,text=u"Enable Camera2",variable=self.camera2)
        self.cb_camera2.grid(column=0,row=6,columnspan=2,sticky='W')
        self.flash=tkinter.IntVar()
        self.cb_flash = tkinter.Checkbutton(self,text=u"Enable External Flash",variable=self.flash)
        self.cb_flash.grid(column=0,row=9,columnspan=2,sticky='W')
        self.proj=tkinter.IntVar()
        self.cb_proj = tkinter.Checkbutton(self,text=u"Enable Projector",variable=self.proj,command=self.open_win_proj)
        self.cb_proj.grid(column=0,row=10,columnspan=2,sticky='W')

        menubar = tkinter.Menu(self)
    
        # create a pulldown menu, and add it to the menu bar
        filemenu = tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.hello)
        filemenu.add_command(label="Save", command=self.hello)
        filemenu.add_separator()
        filemenu.add_command(label="Return to main window", command=self.q)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # create more pulldown menus
        editmenu = tkinter.Menu(menubar, tearoff=0)
        
        editmenu.add_command(label="Check cameras", command=self.camera_utility)
        editmenu.add_command(label="Add a new camera", command=self.new_camera)
        editmenu.add_command(label="Add a new device", command=self.new_device)
        menubar.add_cascade(label="Utility", menu=editmenu)
        
        helpmenu = tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        # display the menu
        self.config(menu=menubar)
        self.geometry("+%d+%d" % (self.parent.winfo_rootx()+50,
                                  self.parent.winfo_rooty()+50))
        
        
        
        
        
        for i in range(12):
            self.grid_columnconfigure(i,weight=1)
        
        ##self.grid_columnconfigure(3,weight=1)
        for i in range(6):
            self.grid_rowconfigure(i,weight=1)
        
        ##self.grid_rowconfigure(2,weight=1)
        ##self.resizable(True,False)
        #self.update()
        #self.geometry(self.geometry())
        #self.entry.focus_set()
        #self.entry.selection_range(0, tkinter.END)
        ##self.minsize(720,480)
        
        self.combo1_value = tkinter.StringVar()
        self.combo1_value.set('not set!')
        self.combo1 = tkinter.ttk.Combobox(self, textvariable=self.combo1_value, postcommand = self.get_serial_int)
        self.combo1.grid(column=4,row=2, sticky='W')
        #self.combo1_value.set('not set!')
        self.combo1.bind("<<ComboboxSelected>>", self.newselection_deg)
        #elf.combo1.bind("<<postcommand>>", self.get_serial_int)
        ##serial
        self.btn_check_serial_deg = tkinter.Button(self,text=u"Test serial!",command=lambda : self.test_serial(self.S_deg,0))
        self.btn_check_serial_deg.grid(column=4,columnspan=1,row=3, sticky='NSWE')
        
        self.combo2_value = tkinter.StringVar()
        self.combo2_value.set('not set!')
        self.combo2 = tkinter.ttk.Combobox(self, textvariable=self.combo2_value, postcommand = self.get_serial_int)
        self.combo2.grid(column=4,row=6, sticky='W')
        #self.combo2_value.set('not set!')
        self.combo2.bind("<<ComboboxSelected>>", self.newselection_shot)
        #self.combo2.bind("<<postcommand>>", self.get_serial_int)
        self.btn_check_serial_shot = tkinter.Button(self,text=u"Test serial!",command=lambda : self.test_serial(self.S_shot,1))
        self.btn_check_serial_shot.grid(column=4,columnspan=1,row=7, sticky='NSWE')
        
        
        #### Cameras
        #label carera left
        self.lcl = tkinter.Label(self, text="left camera")
        self.lcl.grid(column=2,row=5,sticky='WE')
        #label camera right
        self.lcr = tkinter.Label(self, text="right camera")
        self.lcr.grid(column=3,row=5,sticky='WE')
        #combo camera left
        self.cbl_value = tkinter.StringVar()
        self.cbl_value.set('not set!')
        self.cbl = tkinter.ttk.Combobox(self, textvariable=self.cbl_value, postcommand = self.get_cam_int)
        self.cbl.grid(column=2,row=6, sticky='NSWE')
        self.cbl.bind("<<ComboboxSelected>>", self.newselection_usb_left)
        #combo camera right
        self.cbr_value = tkinter.StringVar()
        self.cbr_value.set('not set!')
        self.cbr = tkinter.ttk.Combobox(self, textvariable=self.cbr_value, postcommand = self.get_cam_int)
        self.cbr.grid(column=3,row=6, sticky='NSWE')
        self.cbr.bind("<<ComboboxSelected>>", self.newselection_usb_right)
        
        self.btn_check_cameras = tkinter.Button(self,text=u"Test cameras!",command=self.camera_utility)
        self.btn_check_cameras.grid(column=2,columnspan=2,row=7, sticky='NSWE')
        
        #### End cameras
        
        ##serial
        self.option_add("*Dialog.msg.wrapLength", "10i") #### to enlarge the tkMessageBox dialog windows  
        
        ##Update window
        self.update()
    
    
    def test_serial(self, s_int,i=None):
        txt=''
        if s_int:
            S=s_int
            time.sleep(0.5)
            try:
                #self.read_serial(S)
                S.flushInput()
                S.flushOutput()
                #time.sleep(0.5)
                #S.write("$$\n".encode('ascii'))
                S.write("$$\n$$\n$$\n".encode('ascii'))
                time.sleep(0.5)
                txt=self.read_serial(S)
                #print(txt)
                #time.sleep(0.5)
                #txt+=self.read_serial(S)
                print(txt)
                #print(txt)
            except:
                tkinter.messagebox.showinfo("Except!", "This connection seems inactive or not properly set!",icon="warning")
                pass
            p = re.compile('\$101=\d{3}\..*')
            if p.findall(txt)!=[]:
                print('grbl')
                if i==0:
                    tkinter.messagebox.showinfo("Connection is fine!", "This connection seems to be perfect!")
                else:
                    tkinter.messagebox.showinfo("Connection is working!", "This device would be connected to the 'turning table' combobox!",icon="warning")
            p = re.compile('\d+xak\d+')
            if p.findall(txt)!=[]:
                if i==1:
                    tkinter.messagebox.showinfo("Connection is fine!", "This connection seems to be perfect!")
                else:
                    tkinter.messagebox.showinfo("Connection is working!", "This device would be connected to the 'turning table' combobox!",icon="warning")
            if txt=='':
                tkinter.messagebox.showinfo("Problem detected!", "This connection seems inactive or not properly set!",icon="warning")
        else:
            tkinter.messagebox.showinfo("Problem detected!", "This connection seems inactive or not properly set!",icon="warning")
            
    def hello(self):
        print('Hello!!')
    def about(self):
        tkinter.messagebox.showinfo("About", "Orion Scan is a open-source project under GPL licence.\nFor more details please visit:\nhttps://github.com/PeriniMatteo/Orion-scan")
        
    def new_device(self):
        New_Device_Dialog(self)
        
    def new_camera(self):
        New_Camera_Dialog(self)
        
    def camera_utility(self):
        Check_Cameras_Dialog(self,self.CL,self.CR)
        
    def check_pattern_dir(self):
        print('check_pattern_dir')
        #self.pattern_dir='~'
        n=0
        self.pattern_files=[]
        while True:
            filename=str(n)+'.tif'
            #print(self.pattern_dir+'/'+filename)
            m = Path(self.pattern_dir+'/'+filename)
            if m.is_file():
                print(filename+' e un file!')
                self.pattern_files.append(filename)
                n+=1
            else:
                break
        print(self.pattern_files)
            
    def askdirectory(self):
    
        """Returns a selected directoryname."""
        return filedialog.askdirectory(**self.dir_opt)
        
    def open_win_proj(self):
        if self.proj.get():
            print('open_win_proj')
            self.check_pattern_dir()
            print('continue')
            if tkinter.messagebox.askyesno("Select Pattern Folder", "The current folder is "+self.pattern_dir+"! Do you want to change it?",icon="warning"):
                self.pattern_dir = self.askdirectory()
                self.check_pattern_dir()
                if len(self.pattern_files)==0:
                    if tkinter.messagebox.askyesno("Select Pattern Folder", "There aren't valid pictures in this folder! Do you want to select another one?",icon="warning"):
                        self.pattern_dir = self.askdirectory()
                        self.check_pattern_dir()
                else:
                    tkinter.messagebox.showinfo("Using files", ''.join([str(a)+'\n' for a in self.pattern_files]))
            else:
                tkinter.messagebox.showinfo("Using files", ''.join([str(a)+'\n' for a in self.pattern_files]))
            
        #P=ProjectorDialog(self)
        #print(self.pattern_dir)
    def get_serial_int(self):
        print('get')
        #print("get_ser_int")   
        devlist=self.read_devices_list()
        self.ser_int = []
        for port in serial.tools.list_ports.comports():
            try:
                sn = self.get_sn(port)
                self.ser_int.append({'port':str(port[0]), 'dev':str(port[1]), 'sn':str(sn),'desc':str(devlist[sn])})
            except:
                self.ser_int.append({'port':str(port[0]), 'dev':str(port[1]), 'sn':str(sn)})
        self.update_combos()
        #return self.ser_int
    
    def update_combos(self):
        if self.ser_int == []:
            self.combo1_value.set('not set!')
            self.combo2_value.set('not set!')
        else:
            #devlist=self.read_devices_list()
             
            #self.combo1['values'] = ([port[0]+" - "+port[1] for port in serial.tools.list_ports.comports() if not New_Device_Dialog.check_port_in_dict(port,devlist) else devlist[New_Device_Dialog.get_sn(port)]])
            #self.combo1['values'] = ([port[0]+" - "+port[1] if not self.check_port_in_dict(port,devlist)  else devlist[self.get_sn(port)] for port in serial.tools.list_ports.comports()])
            #self.combo2['values'] = ([port[0]+" - "+port[1] if not self.check_port_in_dict(port,devlist)  else devlist[self.get_sn(port)] for port in serial.tools.list_ports.comports()])
            self.combo1['values'] = ([item['port']+" - "+item['dev'] if len(item)==3  else item['desc'] for item in self.ser_int])
            self.combo2['values'] = ([item['port']+" - "+item['dev'] if len(item)==3  else item['desc'] for item in self.ser_int])
            #self.combo2['values'] = ([port[0]+" - "+port[1] for port in serial.tools.list_ports.comports()])
    
    def show_image(self, image):
        img = cv2.imread(image)
        cv2.startWindowThread()
        cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)          
        #cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
        cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('image', img)
        time.sleep(1)
        #cv2.destroyAllWindows()
    def destroy_image(self):
        cv2.destroyAllWindows()
    def Take(self):
        
        proc = multiprocessing.Process(target=self.DoTake)
        process_window = ProcessWindow(self, proc, self.S_deg)
        process_window.launch()
        
    def DoTake(self):
        if self.table.get():
            self.S_deg.write("\r\n\r\n".encode('ascii'))
            self.S_deg.write("G17 G20 G90 G94 G54 G21\r\n".encode('ascii'))
            self.S_deg.write("$102=222.22\r\n".encode('ascii'))
            self.S_deg.write("$1=255\r\n".encode('ascii'))
            self.S_deg.write("G92 Z0\r\n".encode('ascii'))
            #self.S_deg.write("g10 p1 l20 x0 y0 z0\r\n".encode('ascii'))
        for n,i in enumerate(list(range(int(self.n_deg),360+int(self.n_deg),int(self.n_deg)))):
            if self.camera1.get():
                if self.proj.get():
                    print('with proj')
                    for pattern in self.pattern_files:
                        self.show_image(self.pattern_dir+'/'+pattern)
                        time.sleep(0.2)
                        if self.flash.get():
                            self.S_shot.write(str('xxx 2\n').encode('ascii'))
                            #time.sleep(10)
                            self.check_camera_process()
                            self.destroy_image()
                        else:
                            self.S_shot.write(str('xxx 1\n').encode('ascii'))
                            #time.sleep(10)
                            self.check_camera_process()
                            self.destroy_image()
                    
                    
                    
                    
                    
                    
                    
                    
                    
                else:
                    print('without proj')
                    #print("I'm taking picture(s) at "+str(i)+" deg!   Just "+str(self.n_shots-n)+" steps left")
                    if self.flash.get():
                        self.S_shot.write(str('xxx 2\n').encode('ascii'))
                        #time.sleep(10)
                        self.check_camera_process()
                    else:
                        self.S_shot.write(str('xxx 1\n').encode('ascii'))
                        #time.sleep(10)
                        self.check_camera_process()
                    
                    
                    
                    
                    
            time.sleep(2)
            if self.table.get():
                if i==360:
                    
                    self.S_deg.write(str('G0 Z'+str(i/10.0)+'\r\n').encode('ascii'))
                    self.S_deg.write("$1=1\r\n".encode('ascii'))
                    self.S_deg.write(str('G0 Z'+str(i/10.0)+'\r\n').encode('ascii'))
                    self.check_stepper_position(i)
                    self.S_deg.write("G92 Z0\r\n".encode('ascii'))
                    time.sleep(0.5)
                else:
                    self.S_deg.write(str('G0 Z'+str(i/10.0)+'\r\n').encode('ascii'))
                    self.check_stepper_position(i)
                    time.sleep(0.5)
        #if self.table.get():
        #    self.S_deg.write("$1=1\r\n".encode('ascii'))
    #def show_image(self,image):
        #img = cv2.imread(image)
        #cv2.startWindowThread()
        #cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)          
        ##cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
        #cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        #cv2.imshow('image', img)
        ##time.sleep(1)
            
    def read_serial(self,serial_int):
        data_str=''
        self.S=serial_int
        while (self.S.inWaiting()>0):
            data_str = data_str + self.S.read(self.S.inWaiting()).decode('ascii')
            time.sleep(0.01)
        return data_str

        
                
    def check_stepper_position(self, angle):
        while True:
            a=''
            self.S_deg.write(str('?\n').encode('ascii'))
            time.sleep(0.1)
            if (self.S_deg.inWaiting()>0):
                a=self.read_serial(self.S_deg)
                print(a)
                if str(a)[:10] == '<Idle,MPos':
                    if abs(float(a.split(',')[6][:5])-float(angle/10.0))<0.02:
                        print(str(float(a.split(',')[6][:5])*10)+' of '+str(float(angle))+' reached   br')
                        time.sleep(0.2)
                        break
                    else:
                        print(str(float(a.split(',')[6][:5])*10)+' of '+str(float(angle))+' reached')
                        #time.sleep(0.1)
        return True
        
    def check_camera_process(self):
        while True:
            a=''
            time.sleep(0.1)
            print('check camera process')
            if (self.S_shot.inWaiting()>0):
                a=self.read_serial(self.S_shot)
                print(a)
                a = a.split('\n')[-2]
                
                print(a)
                if str(a)[:4] == 'gata':
                    break
            
        return True
        
        
        ##thread = threading.Thread(target=read_from_port(), args=(self.S))
        ##thread.start()
    
    ##def new_win(self):
        ##t = tkinter.Toplevel(self)
        ##t.wm_title("Window 2")
        ##l = tk.Label(t, text="This is window 2")
        ##l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
    #def get_serial_int_from_combo(self, combo_value):
        #if combo_value[:8]=='/dev/tty':
            #return combo_value.split()[0]
        #else:
            #devlist=self.read_devices_list()
            #for k in devlist.keys:
                #if devlist(k)==
        #pass
    def get_tty_name(self,combo_value):
        if combo_value.split()[0][:8]=='/dev/tty':
            return str(combo_value.split()[0])
        else:
            for i in self.ser_int:
                if len(i)>3:
                    if self.value_of_combo==i['desc']:
                        return i['port']
                
    def newselection_deg(self,evt):
        print('newselection_deg')
        br=self.br_deg
        self.value_of_combo = self.combo1.get()
        
        self.get_serial_int()
        ################
        new_int = self.get_tty_name(self.value_of_combo)
        #print('###############################################')
        print('new_int = '+new_int)
        #print('###############################################')

        #self.combo1['values'] = ([port[0]+" - "+port[1] for port in serial.tools.list_ports.comports()])
        #self.ser_int = [{'port':str(port[0]), 'desc':str(port[1])} for port in serial.tools.list_ports.comports()]
        if self.S_deg:
            print('dentro')
            
            if self.S_shot:
                if self.S_shot.port != new_int:
                    print('porta libera')
                    self.disconnect_serial(self.S_deg)
                    self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
                else:
                    print('porta occupata')
                    if tkinter.messagebox.askyesno("Serial busy", "This serial interface is already reserved! Do you want to use it anyway?",icon="warning"):
                        #print('cambio')
                        self.disconnect_serial(self.S_shot)
                        self.disconnect_serial(self.S_deg)
                        self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
                        self.combo2_value.set('not set!')
                    else:
                        self.combo1_value.set('not set!')
                        pass
            else:
                self.disconnect_serial(self.S_deg)
                self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
        else:
            print('fuori')
            if self.S_shot:
                if self.S_shot.port == new_int:
                    print('porta occupata')
                    #print(self.S_shot.port)
                    #print(str(self.value_of_combo.split()[0]))
                    if tkinter.messagebox.askyesno("Serial busy", "This serial interface is already reserved! Do you want to use it anyway?",icon="warning"):
                        #print('cambio')
                        self.disconnect_serial(self.S_deg)
                        self.disconnect_serial(self.S_shot)
                        self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
                        self.combo2_value.set('not set!')
                    else:
                        #self.S_deg = self.connect_serial(self.S_deg,str(self.value_of_combo.split()[0]),br)
                        self.combo1_value.set('not set!')
                        pass
                else:
                    #print('S_deg in teoria')
                    self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
            else:
                #print('S_deg in teoria')
                self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
            
    def newselection_shot(self,evt):
        print('newselection_shot')
        br=self.br_shot
        self.value_of_combo = self.combo2.get()
        self.get_serial_int()
        ################
        new_int = self.get_tty_name(self.value_of_combo)
        #print('###############################################')
        print('new_int = '+new_int)
        #print('###############################################')
        #self.combo2['values'] = ([port[0]+" - "+port[1] for port in serial.tools.list_ports.comports()])
        #self.ser_int = [{'port':str(port[0]), 'desc':str(port[1])} for port in serial.tools.list_ports.comports()]
            
        if self.S_shot:
            print('dentro')
            
            if self.S_deg:
                if self.S_deg.port != new_int:
                    print('porta libera')
                    self.disconnect_serial(self.S_shot)
                    self.S_shot = self.connect_serial(self.S_shot,new_int,br,0)
                    #print('Now serial '+self.S_deg.port+' will be used to turn the table')
                else:
                    print('porta occupata')
                    if tkinter.messagebox.askyesno("Serial busy", "This serial interface is already reserved! Do you want to use it anyway?",icon="warning"):
                        #print('cambio')
                        self.disconnect_serial(self.S_shot)
                        self.disconnect_serial(self.S_deg)
                        self.S_shot = self.connect_serial(self.S_shot,new_int,br,1)
                        self.combo1_value.set('not set!')
            
                    else:
                        self.combo2_value.set('not set!')
                        #pass
            else:
                self.disconnect_serial(self.S_shot)
                self.S_shot = self.connect_serial(self.S_shot,new_int,br,0)
        else:
            print('fuori')
            if self.S_deg:
                print('S_deg exist')
                if self.S_deg.port == new_int:
                    print('porta occupata')
                    #print(self.S_shot.port)
                    #print(str(self.value_of_combo.split()[0]))
                    if tkinter.messagebox.askyesno("Serial busy", "This serial interface is already reserved! Do you want to use it anyway?",icon="warning"):
                        #print('cambio')
                        self.disconnect_serial(self.S_shot)
                        self.disconnect_serial(self.S_deg)
                        self.S_shot = self.connect_serial(self.S_shot,new_int,br,1)
                        self.combo1_value.set('not set!')
                    else:
                        #self.S_shot = self.connect_serial(self.S_shot,str(self.value_of_combo.split()[0]),br)
                        self.combo2_value.set('not set!')
                        #pass
                else:
                    #print('S_shot in teoria')
                    self.S_shot = self.connect_serial(self.S_shot,new_int,br,1)
            else:
                #print('S_shot in teoria')
                self.S_shot = self.connect_serial(self.S_shot,new_int,br,1)
        
    def disconnect_serial(self, serial_name):
        try:
            serial_name.close()
        except:
            pass
        
    def connect_serial(self, serial_name,s_int,br,i=None): #SERIAL INTERFACE , BAUDRATE
        
        s = serial.Serial(s_int,br,timeout=0)
        s.close()
        s.open()
        s.flushInput()
        s.write('\r\n\r\n'.encode('ascii'))
        s.flushInput()
        #print(serial_name)
        #print(self.S_deg)
        if i==0:
            print('Now serial '+s_int+'@'+str(br)+' will be used to turn the table')
        elif i==1:
            print('Now serial '+s_int+'@'+str(br)+' will be used to manage cameras')
        return s
        


    def Validate_Entry_Shots(self,event):
        e = self.entryShots.get()
        print(e)
        if not self.check_entry_shots(e):
            self.entryShots.delete(0, tkinter.END)
            self.entryShots.insert(0,"Error! I need an int!")
        else:
            self.n_shots = self.check_entry_shots(e)
            self.n_deg = 360.0/float(self.check_entry_shots(e))
            self.entryDegr.delete(0, tkinter.END)
            self.entryDegr.insert(0,str(self.n_deg))
            
        
    def Validate_Entry_Degr(self,event):
        e = self.entryDegr.get()
        print(e)
        if not self.check_entry_degr(e):
            self.entryDegr.delete(0, tkinter.END)
            self.entryDegr.insert(0,"Error! I need a number!")
        else:
            self.n_deg = self.check_entry_degr(e)
            self.n_shots = 360.0/self.check_entry_degr(e)
            #round(self.n_shots)
            if self.n_shots%1 == 0.0:
                self.entryShots.delete(0, tkinter.END)
                self.entryShots.insert(0,str(int(self.n_shots)))
            else:
                self.entryDegr.delete(0, tkinter.END)
                self.entryDegr.insert(0,'Error! I need a 360 divisor, retry!')
                self.entryShots.delete(0, tkinter.END)
                self.entryShots.insert(0,"Error! I need an int!")
                self.n_shots = None
                self.n_deg = None
                

    def check_entry_shots(self,string):
        try:
           val = int(string)
           return val
        except ValueError:
           #print("I need an int!")
           return None

    def check_entry_degr(self,string):
        try:
           val = float(string)
           return val
        except ValueError:
           #print("I need an int!")
           return None

    def attached_cameras(self):
        cl={}
        g=subprocess.Popen(["gphoto2","--auto-detect"], stdout=subprocess.PIPE)
        for l in g.stdout.readlines():
            p = re.compile('\susb:\d')
            a = p.findall(l.decode('ascii'))
            if a != []:
                p = re.compile('^.*\s+usb:')
                a = p.findall(l.decode('ascii'))
                name= '"'+(a[0][:-4]).rstrip()+'"'
                p = re.compile('usb:\d+,\d+')
                a = p.findall(l.decode('ascii'))
                usbid=a[0][4:7]
                dev=a[0][8:11]
                g=subprocess.Popen(["lsusb","-s "+str(usbid)+":"+str(dev),"-v"], stdout=subprocess.PIPE)
                for l in g.stdout.readlines():
                    p = re.compile('iSerial')
                    a = p.findall(l.decode('ascii'))
                    if a != []:
                        p = re.compile('00*\d*$')
                        serial = p.findall(l.decode('ascii'))[0]
                
                cl[serial]={'name':name,'port':str('usb:'+str(usbid)+','+str(dev)),'usb_id':usbid,'usb_n':dev,'sn':serial}
        #print(cl)
        return cl
    
    def read_cameras_list(self):
        try:
            with open('cameras.txt', 'rb') as f:
                cam_dict = pickle.loads(f.read())
            print(cam_dict)
            return cam_dict
        except:
            return {}
        
    def update_cam_combos(self):
        if self.cam_int == []:
            self.cbl_value.set('not set!')
            self.cbr_value.set('not set!')
        else:
            self.cbl['values'] = ([item['port']+" on "+item['name'] if len(item)==5  else item['name'] for item in self.cam_int])
            self.cbr['values'] = ([item['port']+" on "+item['name'] if len(item)==5  else item['name'] for item in self.cam_int])
        
        
    def get_cam_int(self):
        #print('get')
        #print("get_ser_int")   
        camlist=self.read_cameras_list()
        self.cam_int = []
        
        
        for sn in self.attached_cameras().keys():
            if sn in camlist.keys():
                #self.cam_int.append({'port':str(port[0]), 'dev':str(port[1]), 'sn':str(sn),'desc':str(devlist[sn])})
                self.cam_int.append(camlist[sn])
            else:
                self.cam_int.append(self.attached_cameras()[sn])
        self.update_cam_combos()
        
        
        
    def get_sn_from_combo(self,combo_value):
        cl =  self.attached_cameras()
        if combo_value.split()[0][:4]=='usb:':
            for item in cl.keys():
                if combo_value.split()[0][:11]==cl[item]['port']:
                    return item
        else:
            for item in cl.keys():
                if combo_value==cl[item]['desc']:
                    return item
        
    def newselection_usb_left(self,evt):
        #br=self.br_deg    ####bitrate
        self.value_of_combo = self.cbl.get()
        
        self.get_cam_int()
        new_int = self.get_sn_from_combo(self.value_of_combo)
        print('new_int = '+new_int)
        if self.CL:
            #print('dentro')
            
            if self.CR:
                if self.CR['sn'] != new_int:
                    self.CL= self.attached_cameras()[new_int]
                else:
                    #print('porta occupata')
                    if tkinter.messagebox.askyesno("Camera busy", "This camera is already in use! Do you want to use it anyway?",icon="warning"):
                        self.CR=None
                        self.CL= self.attached_cameras()[new_int]
                        self.cbr_value.set('not set!')
                    else:
                        self.cbl_value.set('not set!')
            else:
                
                self.CL= self.attached_cameras()[new_int]
        else:
            if self.CR:
                if self.CR['sn'] == new_int:
                    #print('porta occupata')
                    if tkinter.messagebox.askyesno("Camera busy", "This camera is already in use! Do you want to use it anyway?",icon="warning"):
                        
                        self.CR=None
                        self.CL= self.attached_cameras()[new_int]
                        self.cbr_value.set('not set!')
                    else:
                        self.cbl_value.set('not set!')
                        pass
                else:
                    self.CL= self.attached_cameras()[new_int]
            else:
                self.CL= self.attached_cameras()[new_int]
    
    def newselection_usb_right(self,evt):
        
        self.value_of_combo = self.cbr.get()
        
        self.get_cam_int()
        new_int = self.get_sn_from_combo(self.value_of_combo)
        print('new_int = '+new_int)
        if self.CR:
            #print('dentro')
            
            if self.CL:
                if self.CL['sn'] != new_int:
                    self.CR= self.attached_cameras()[new_int]
                else:
                    #print('porta occupata')
                    if tkinter.messagebox.askyesno("Camera busy", "This camera is already in use! Do you want to use it anyway?",icon="warning"):
                        self.CL=None
                        self.CR= self.attached_cameras()[new_int]
                        self.cbl_value.set('not set!')
                    else:
                        self.cbr_value.set('not set!')
            else:
                
                self.CR= self.attached_cameras()[new_int]
        else:
            if self.CL:
                if self.CL['sn'] == new_int:
                    #print('porta occupata')
                    if tkinter.messagebox.askyesno("Camera busy", "This camera is already in use! Do you want to use it anyway?",icon="warning"):
                        
                        self.CL=None
                        self.CR= self.attached_cameras()[new_int]
                        self.cbl_value.set('not set!')
                    else:
                        self.cbr_value.set('not set!')
                        pass
                else:
                    self.CR= self.attached_cameras()[new_int]
            else:
                self.CR= self.attached_cameras()[new_int]

if __name__ == "__main__":
    app = TakeDialog(None)
    app.title('Take window')
    app.mainloop()
    
