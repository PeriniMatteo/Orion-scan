#!/usr/bin/python



import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
import serial
import serial.tools.list_ports
import time
import multiprocessing
import cv2
from pathlib import Path
import re
from PIL import ImageTk, Image
import subprocess
import pickle
import numpy as np
import os



class Ask_Device_Name_Dialog(simpledialog.Dialog):

    def __init__(self, parent,d_dict,sn):

        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.dev_dict=d_dict
        self.title('Choose a name for your new device!')
        self.transient(parent)
        self.parent = parent
    
        tkinter.Label(self, text="SN:").grid(row=0)
        tkinter.Label(self, text="Name:").grid(row=1)
        self.grid_columnconfigure(0,weight=1)
        print('sn === '+sn)
        self.e1_text = tkinter.StringVar()
        self.e1_text.set(str(sn))
        self.e1 = tkinter.Entry(self,textvariable=self.e1_text)
        self.e1.config(state=tkinter.DISABLED)
        self.e2 = tkinter.Entry(self)
    
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e2.bind("<Return>", self.return_pressed)
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
        
        New_Device_Dialog.dev_dict=self.dev_dict
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
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        
        self.combo_txt = tkinter.StringVar()
        self.combo_txt.set('not set!')
        self.combo = tkinter.ttk.Combobox(self, textvariable=self.combo_txt, postcommand = self.get_values)
        self.combo.grid(column=1,row=0, sticky='NSWE')
        #self.combo1_value.set('not set!')
        self.combo.bind("<<ComboboxSelected>>", self.newselection)
        
        self.ok_button = ttk.Button(self, text="Remove", command=self.ok)
        self.ok_button.grid(row=1, column=0,columnspan=2, sticky='NSWE')
        self.quit_button = ttk.Button(self, text="Exit", command=self.qq)
        self.quit_button.grid(row=2, column=0,columnspan=2, sticky='NSWE')
        self.minsize(500,10)
        self.grab_set()
        self.focus_set()
        self.wait_window(self)
        
        
    def write_devices_list(self):
        with open('devices', 'wb') as f:
            pickle.dump(self.dev_dict, f)
        
    def read_devices_list(self):
        try:
            with open('devices', 'rb') as f:
                dev_dict = pickle.loads(f.read())
                return dev_dict
        except:
            return None
        
    def get_values(self):
        self.combo['values'] = [str(nn)+'  '+str(self.dev_dict[nn]) for nn in self.dev_dict]

    def newselection(self,evt):
        val = self.combo.get()
        self.sn = val.split()[0]
        self.name = self.dev_dict[self.sn]
        
    def ok(self):
        self.dev_dict.pop(self.sn)
        self.write_devices_list()
        if self.dev_dict=={}:
            messagebox.showinfo('Warning', "There aren't other devices to remove!")
            self.parent.focus_set()
            self.destroy()
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
        self.minsize(400,300)
        self.wait_window(self)
        
    def remove(self):
        print('remove')
        if self.read_devices_list():
            Remove_Device_Dialog(self)
        else:
            messagebox.showinfo('Warning', "There aren't devices to remove!")

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()
        
    def read_devices_list(self):
        try:
            with open('devices', 'rb') as f:
                dev_dict = pickle.loads(f.read())
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
        with open('devices', 'wb') as f:
            pickle.dump(self.dev_dict, f)
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
                        txt+='ID #'+self.sn+'   Name:'+self.dev_dict[self.sn]+'\n\n'
                    else:
                        new=True
                        txt+='New device found:\n'
                        txt+='ID #'+self.sn+'\n\n'
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
                
    def add(self):
        if self.dev_dict:
            for dev in self.ports:
                if self.check_port_in_dict(dev,self.dev_dict):
                    messagebox.showinfo('', 'Device '+self.sn+' is already in your list.')
                else:
                    if messagebox.askyesno('New device found!', self.sn+'Found!\nDo you want to add this serial device to your system?'):
                        print(self.dev_dict)
                        Ask_Device_Name_Dialog(self,self.dev_dict,self.sn)
                        print(self.dev_dict)
                        self.write_devices_list(self.dev_dict)
        else:
            self.dev_dict={}
            self.get_sn(self.ports[0])
            print(self.dev_dict)
            Ask_Device_Name_Dialog(self,self.dev_dict,self.sn)
            print(self.dev_dict)
            self.write_devices_list(self.dev_dict)
            if len(self.ports)>1:
                self.add()

        
class New_Camera_Dialog(tkinter.Toplevel):

    def __init__(self, parent=None):

        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Select a new camera')
        self.parent = parent
        self.result = None
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        self.detect_button = ttk.Button(self, text="Detect a new camera", command=self.detect, default=tkinter.ACTIVE)
        self.detect_button.grid(row=0, column=0, sticky='NSWE')
        self.add_button = ttk.Button(self, text="Add to know camera", command=self.add, state=tkinter.DISABLED)
        self.add_button.grid(row=1, column=0, sticky='NSWE')
        self.remove_button = ttk.Button(self, text="Remove a camera", command=self.remove)
        self.remove_button.grid(row=2, column=0, sticky='NSWE')
        self.exit_button = ttk.Button(self, text="Exit", command=self.cancel)
        self.exit_button.grid(row=3, column=0, sticky='NSWE')

        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.focus_set()
        self.minsize(400,300)
        self.wait_window(self)
        
        
        
        
        
    def remove(self):
        if self.read_cameras_list() != {}:
            Remove_Camera_dialog(self)
        else:
            messagebox.showinfo('Warning', "There aren't any camera to remove!")


    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()
        
    def read_cameras_list(self):
        try:
            with open('cameras', 'rb') as f:
                cam_dict = pickle.loads(f.read())
                return cam_dict
        except:
            return {}
        
        
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
        
        
    def detect(self):
        print('detect')
        self.cam_dict={}
        self.plugged_in_cameras = self.attached_cameras()
        if self.plugged_in_cameras=={}:
            print('no devices detected')
            if messagebox.askretrycancel("Warning!","Can't recognize any device!\n Connect a valid device and retry."):
                self.detect()
            
        else:
            print('camera(s) detected')
            self.cam_dict=self.read_cameras_list()
            print(self.cam_dict)
            if self.cam_dict != {}:
                new=None
                txt=''
                for k in self.plugged_in_cameras.keys():
                    
                    if k in self.cam_dict.keys():
                        txt+='Camera already in use:\n'
                        txt+='ID #'+self.cam_dict[k]['sn']+'   Name:'+self.cam_dict[k]['name']+'   Desc:'+self.cam_dict[k]['desc']+'\n\n'
                    else:
                        new=True
                        txt+='New camera found:\n'
                        txt+='ID #'+self.plugged_in_cameras[k]['sn']+'   Name:'+self.plugged_in_cameras[k]['name']+'\n\n'
                if new:
                    txt+='\nUse the "Add to know cameras" button to put it in your list.\n'
                    self.add_button.config(state=tkinter.ACTIVE)
                else:
                    txt+='\nNo Unknow device found!'
                messagebox.showinfo('New camera found!', txt)
                        
            else:
                self.add_button.config(state=tkinter.ACTIVE)
                txt='\nAn unknow camera was found!\nUse the "Add to know cameras" button to put it in your list.\n'
                messagebox.showinfo('Unknow camera found!', txt)
                

    def add(self):
        if self.cam_dict != {}:
            for k in self.plugged_in_cameras.keys():
                if k in self.cam_dict.keys():
                    messagebox.showinfo('', 'Camera '+self.cam_dict[k]['sn']+' is already in your list.')
                else:
                    if messagebox.askyesno('New camera found!', self.plugged_in_cameras[k]['sn']+'Found!\nDo you want to add this camera to your system?'):
                        Ask_Camera_Name_Dialog(self, self.cam_dict, self.plugged_in_cameras, k)
                        self.write_cameras_list(self.cam_dict)
        else:
            #self.cam_dict={}
            Ask_Camera_Name_Dialog(self, self.cam_dict, self.plugged_in_cameras)
            self.write_cameras_list(self.cam_dict)
            if len(self.plugged_in_cameras.keys())>1:
                self.add()
    
    def write_cameras_list(self,cam_dict):
        with open('cameras', 'wb') as f:
            pickle.dump(cam_dict, f)
        self.add_button.config(state=tkinter.DISABLED)
        
        
class Ask_Camera_Name_Dialog(simpledialog.Dialog):

    def __init__(self, parent, cam_dict, new_dict, sn=None):

        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.cam_dict = cam_dict
        self.new_dict = new_dict
        self.add_list = [k for k in self.new_dict.keys() if k not in self.cam_dict.keys()]
        self.title('Choose a description for your new Camera!')
        self.transient(parent)
        self.parent = parent
    
        tkinter.Label(self, text="SN:").grid(row=0)
        tkinter.Label(self, text="Desc:").grid(row=1)
        self.grid_columnconfigure(0,weight=1)
        self.e1_text = tkinter.StringVar()
        if sn:
            self.e1_text.set(str(sn))
        else:
            self.e1_text.set(self.add_list[0])
        self.e1 = tkinter.Entry(self,textvariable=self.e1_text)
        self.e1.config(state=tkinter.DISABLED)
        self.e2 = tkinter.Entry(self)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e2.bind("<Return>", self.return_pressed)
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
        print(first)
        second = self.e2.get()
        print(second)
        print('new_dict =\n', self.new_dict)
        print('cam_dict =\n', self.new_dict)
        self.new_dict[str(first)]['desc'] = str(second)
        self.cam_dict[str(first)] = self.new_dict[str(first)]
        
        New_Camera_Dialog.dev_dict=self.cam_dict
        
        self.parent.focus_set()
        self.destroy()
        
class Remove_Camera_dialog(simpledialog.Dialog):

    def __init__(self, parent):

        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.cam_dict = self.read_cameras_list()
        self.title('Remove a camera!')
        self.transient(parent)
        self.parent = parent
    
        tkinter.Label(self, text="Camera:").grid(row=0)
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        
        self.combo_txt = tkinter.StringVar()
        self.combo_txt.set('not set!')
        self.combo = tkinter.ttk.Combobox(self, textvariable=self.combo_txt, postcommand = self.get_values)
        self.combo.grid(column=1,row=0, sticky='NSWE')
        self.combo.bind("<<ComboboxSelected>>", self.newselection)
        
        self.ok_button = ttk.Button(self, text="Remove", command=self.ok)
        self.ok_button.grid(row=1, column=0,columnspan=2, sticky='NSWE')
        self.quit_button = ttk.Button(self, text="Exit", command=self.qq)
        self.quit_button.grid(row=2, column=0,columnspan=2, sticky='NSWE')
        self.minsize(500,10)
        self.grab_set()
        self.focus_set()
        self.wait_window(self)
    
    
    def read_cameras_list(self):
        try:
            with open('cameras', 'rb') as f:
                cam_dict = pickle.loads(f.read())
                return cam_dict
        except:
            return {}
    
    def write_cameras_list(self,cam_dict):
        with open('cameras', 'wb') as f:
            pickle.dump(cam_dict, f)
        
    def get_values(self):
        self.combo['values'] = [str(self.cam_dict[k]['sn']+'  '+self.cam_dict[k]['desc']+'  '+self.cam_dict[k]['name']) for k in self.cam_dict.keys()]
        
    def newselection(self,evt):
        val = self.combo.get()
        self.sn = val.split()[0]
        
    def ok(self):
        self.cam_dict.pop(self.sn)
        self.write_cameras_list(self.cam_dict)
        if self.cam_dict=={}:
            messagebox.showinfo('Warning', "There aren't other devices to remove!")
            self.parent.focus_set()
            self.destroy()
        else:
            self.combo_txt.set('Select a device!')
            self.cam_dict = self.read_cameras_list()
            self.get_values()
        
    def qq(self):
        self.parent.focus_set()
        self.destroy()


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
            self.after(10, self.isAlive)
        elif self:
            messagebox.showinfo(message="3D Scan was sucessful done!", title="Finished")
            self.destroy()


class Retrieve_image():
    def __init__(self, parent, process, camera):
        self.process = process
        self.camera = camera

    def launch(self):
        self.process.start()
        #self.after(20, self.isAlive)
        time.sleep(0.02)
        self.isAlive()
            
    def isAlive(self):
        if self.process.is_alive():
            time.sleep(0.02)
            self.isAlive()
            #self.after(20, self.isAlive)
        else:
            pass
            
class Check_Cameras_Dialog(tkinter.Toplevel):

    def __init__(self, parent, CL, CR):
        self.CL=CL
        self.CR=CR       
        print(self.CL)
        print(self.CR) 
        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Select a new device')
        self.parent = parent
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        img = Image.new("L", [4608,3072], 'white')
        self.img_left = img
        self.img_left = ImageTk.PhotoImage(self.img_left.resize((int(self.img_left.size[0]/10),int(self.img_left.size[1]/10)), Image.ANTIALIAS))
        self.img_right = img
        self.img_right = ImageTk.PhotoImage(self.img_right.resize((int(self.img_right.size[0]/10),int(self.img_right.size[1]/10)), Image.ANTIALIAS))

        #Displaying it
        self.imglabel_left = tkinter.Label(self, image=self.img_left)
        self.imglabel_left.grid(row=2, column=0)        
        self.imglabel_right = tkinter.Label(self, image=self.img_right)
        self.imglabel_right.grid(row=2, column=1) 
        
        self.check_button = ttk.Button(self, text="Check cameras", command=self.check)
        self.check_button.grid(row=3, column=0, columnspan=2, sticky='NSWE')
        
        self.exit_button = ttk.Button(self, text="Exit", command=self.cancel)
        self.exit_button.grid(row=4, column=0, columnspan=2, sticky='NSWE')
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.focus_set()
        self.minsize(400,300)
        self.wait_window(self)
        
    def check(self):
        if self.CL or self.CR:
            try:
                subprocess.Popen(["gphoto2","--port="+self.CL['port'],"--capture-image-and-download",'--filename=left.jpg',"--force-overwrite"])
            except:
                pass
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
        self.parent.focus_set()
        self.destroy()
        
class Check_Pattern_Image_Dialog(tkinter.Toplevel):

    def __init__(self, parent, path, images):

        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)
        r=5
        self.title('Show pattern images')
        self.parent = parent
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        label = {}
        label2 = {}
        
        L=[Image.open(path+'/'+i) for i in images]
        LL=[ImageTk.PhotoImage(i.resize((int(i.size[0]/r),int(i.size[1]/r)), Image.ANTIALIAS)) for i in L]
        for n,i in enumerate(L):
                l=tkinter.Label(self, text=str(images[n]))
                l.grid(row=1, column=n)
                label[str(n)] = l
        
                l=tkinter.Label(self, image= LL[n])
                l.grid(row=2, column=n)
                label2[str(n)] = l
        if len(images)==0:
            l=tkinter.Label(self, text='No valid images in this folder!')
            l.grid(row=1, column=0)
        self.exit_button = ttk.Button(self, text="Exit", command=self.cancel)
        self.exit_button.grid(row=4, column=0, columnspan=1+len(images[:-1]), sticky='NSWE')
        self.exit_button
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.focus_set()
        self.minsize(400,150)
        self.wait_window(self)

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()



class Preferences_Dialog(tkinter.Toplevel):

    def __init__(self, parent, CL = None, CR = None):

        tkinter.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Preferences')
        self.parent = parent
        self.CL = CL
        self.CR = CR
        
        self.inizialize()
        
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.quit_win)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.focus_set()
        self.minsize(700,30)
        self.wait_window(self)
        
        
    def inizialize(self):
        
        self.preL, self.preR, self.extensionL, self.extensionR = self.parent.return_pre_and_ext()
        self.br_list = [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 74880, 115200, 230400, 250000]
        self.pathL, self.pathR = self.parent.return_paths()
        self.br_deg, self.br_shot = self.parent.return_br()
        
        for i in range(6):
            self.grid_columnconfigure(i,weight=1)
        
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self.grid_rowconfigure(2,weight=1)
        
        ################ CAMERAS PARAMETERS ############################
        
        l1 = tkinter.Label(self, text = 'CAMERA LEFT PROPERTY')
        l1.grid(row = 1, column = 0, columnspan = 2)
        
        # left path
        l2 = tkinter.Label(self, text = 'Image dir = ')
        l2.grid(row = 2, column = 0, columnspan = 1, sticky = 'E')
        self.cb2_value = tkinter.StringVar()
        self.cb2_value.set(self.pathL)
        self.cb2 = tkinter.ttk.Combobox(self, textvariable = self.cb2_value, postcommand = lambda : self.get_dirs(self.CL, self.cb2), width=30)
        self.cb2.grid(column = 1,row = 2, sticky = 'WE')
        self.cb2.bind("<<ComboboxSelected>>", self.newselection_cb2)
        
        # left number
        l3 = tkinter.Label(self, text = 'last image number = ')
        l3.grid(row = 3, column = 0, columnspan = 1, sticky = 'E')
        e3txt = tkinter.StringVar()
        e3txt.set(self.get_file_number(self.CL))
        e3 = tkinter.Entry(self,textvariable = e3txt, state = tkinter.DISABLED)
        e3.grid(row = 3, column = 1, columnspan = 1,sticky = 'WE')
        
        # left pre
        l4 = tkinter.Label(self, text = 'pre = ')
        l4.grid(row = 4, column = 0, columnspan = 1, sticky = 'E')
        e4txt = tkinter.StringVar()
        e4txt.set(self.preL)
        e4 = tkinter.Entry(self,textvariable = e4txt)
        e4.grid(row=4, column=1, columnspan=1,sticky='WE')
        e4.bind("<Return>", lambda x: self.set_variable(e4.get(), 1))
        b4 = ttk.Button(self, text="get from camera", command=lambda : self.get_pre_and_ext_from_camera(self.CL, e4txt, 0))
        b4.grid(row=4, column=2, columnspan=1, sticky='NSWE')
        
        # left extension
        l5 = tkinter.Label(self, text='extension = ')
        l5.grid(row=5, column=0, columnspan=1, sticky='E')
        e5txt = tkinter.StringVar()
        e5txt.set(self.extensionL)
        e5 = tkinter.Entry(self,textvariable = e5txt)
        e5.grid(row=5, column=1, columnspan=1,sticky='WE')   
        e5.bind("<Return>", lambda x: self.set_variable(e5.get(), 2))
        b5 = ttk.Button(self, text="get from camera", command=lambda : self.get_pre_and_ext_from_camera(self.CL, e5txt, 1))
        b5.grid(row=5, column=2, columnspan=1, sticky='NSWE')
        
        
        s1 = tkinter.ttk.Separator(self, orient = 'vertical')
        s1.grid(column = 3,row = 0,rowspan = 7,sticky = 'NS')
        
    
        l6=tkinter.Label(self, text='CAMERA RIGHT PROPERTY')
        l6.grid(row=1, column=5, columnspan=2)
        
        # right path
        l7=tkinter.Label(self, text='Images dir = ')
        l7.grid(row=2, column=5, columnspan=1, sticky='E')
        self.cb7_value = tkinter.StringVar()
        self.cb7_value.set(self.pathR)
        self.cb7 = tkinter.ttk.Combobox(self, textvariable=self.cb7_value, postcommand = lambda : self.get_dirs(self.CR, self.cb7), width=30)
        self.cb7.grid(column=6,row=2, sticky='WE')
        self.cb7.bind("<<ComboboxSelected>>", self.newselection_cb7)
        
        # right number
        l8=tkinter.Label(self, text='last image number = ')
        l8.grid(row=3, column=5, columnspan=1, sticky='E')
        e8txt = tkinter.StringVar()
        e8txt.set(self.get_file_number(self.CR))
        e8 = tkinter.Entry(self,textvariable = e8txt, state=tkinter.DISABLED)
        e8.grid(row=3, column=6, columnspan=1,sticky='WE')
        
        # right pre
        l9=tkinter.Label(self, text='pre = ')
        l9.grid(row=4, column=5, columnspan=1, sticky='E')
        e9txt = tkinter.StringVar()
        e9txt.set(self.preR)
        e9 = tkinter.Entry(self,textvariable = e9txt)
        e9.grid(row=4, column=6, columnspan=1,sticky='WE')
        e9.bind("<Return>", lambda x: self.set_variable(e9.get(), 3))
        b9 = ttk.Button(self, text="get from camera", command=lambda : self.get_pre_and_ext_from_camera(self.CR, e9txt, 2))
        b9.grid(row=4, column=7, columnspan=1, sticky='NSWE')

        # right extension
        l10=tkinter.Label(self, text='extension = ')
        l10.grid(row=5, column=5, columnspan=1, sticky='E')
        e10txt = tkinter.StringVar()
        e10txt.set(self.extensionR)
        e10 = tkinter.Entry(self,textvariable = e10txt)
        e10.grid(row=5, column=6, columnspan=1,sticky='WE')        
        e10.bind("<Return>", lambda x: self.set_variable(e10.get(), 4))
        b10 = ttk.Button(self, text="get from camera", command=lambda : self.get_pre_and_ext_from_camera(self.CR, e10txt, 3))
        b10.grid(row=5, column=7, columnspan=1, sticky='NSWE')
        

        self.s2 = tkinter.ttk.Separator(self, orient = 'horizontal')
        self.s2.grid(column = 0,row = 8,columnspan = 10,sticky = 'WE')
        self.s2 = tkinter.ttk.Separator(self, orient = 'horizontal')
        self.s2.grid(column = 0,row = 9,columnspan = 10,sticky = 'WE')
        
        ################ SERIAL PARAMETERS #############################
        
        l11 = tkinter.Label(self, text='TABLE SERIAL PROPERTY')
        l11.grid(row = 10, column = 0, columnspan = 2)
        
        # baud rate table
        l12 = tkinter.Label(self, text='baud rate = ')
        l12.grid(row = 11, column = 0, columnspan = 1, sticky='E')
        self.cb12_value = tkinter.StringVar()
        self.cb12_value.set(self.br_deg)
        self.cb12 = tkinter.ttk.Combobox(self, textvariable = self.cb12_value, postcommand = lambda : self.update_br(self.cb12))
        self.cb12.grid(row = 11, column = 1, sticky = 'WE')
        self.cb12.bind("<<ComboboxSelected>>", self.newselection_cb12)
        
        s3 = tkinter.ttk.Separator(self, orient='vertical')
        s3.grid(column=3,row=10,rowspan=4,sticky='NS')
        
        l15 = tkinter.Label(self, text = 'CAMERA SERIAL PROPERTY')
        l15.grid(row = 10, column = 5, columnspan = 2)
        
        # baud rate camera
        l16 = tkinter.Label(self, text='baud rate = ')
        l16.grid(row = 11, column = 5, columnspan = 1, sticky='E')
        self.cb16_value = tkinter.StringVar()
        self.cb16_value.set(self.br_shot)
        self.cb16 = tkinter.ttk.Combobox(self, textvariable = self.cb16_value, postcommand = lambda : self.update_br(self.cb16))
        self.cb16.grid(row = 11, column = 6, sticky='WE')
        self.cb16.bind("<<ComboboxSelected>>", self.newselection_cb16)
        
        
        self.s3 = tkinter.ttk.Separator(self, orient = 'horizontal')
        self.s3.grid(column = 0,row = 18,columnspan = 10,sticky = 'WE')
        self.s3 = tkinter.ttk.Separator(self, orient = 'horizontal')
        self.s3.grid(column = 0,row = 19,columnspan = 10,sticky = 'WE')
        ################ PROJECTOR? ####################################
        
        
        
        #self.s4 = tkinter.ttk.Separator(self, orient = 'horizontal')
        #self.s4.grid(column = 0,row = 28,columnspan = 10,sticky = 'WE')
        #self.s4 = tkinter.ttk.Separator(self, orient = 'horizontal')
        #self.s4.grid(column = 0,row = 29,columnspan = 10,sticky = 'WE')
        
        ################## TIMING CAMERAS ##############################
        
        
        
        
        #self.s10 = tkinter.ttk.Separator(self, orient = 'horizontal')
        #self.s10.grid(column = 0,row = 48,columnspan = 10,sticky = 'WE')
        #self.s10 = tkinter.ttk.Separator(self, orient = 'horizontal')
        #self.s10.grid(column = 0,row = 49,columnspan = 10,sticky = 'WE')
        
        ################## PATH CONFIGURATION ##########################
        
        
        l50 = tkinter.Label(self, text='PATHS CONFIGURATION')
        l50.grid(row = 50, column = 0, columnspan = 7, sticky='WE')
        
        l51 = tkinter.Label(self, text='Acquired images folder = ')
        l51.grid(row = 51, column = 0, columnspan = 1, sticky='E')
        e51txt = tkinter.StringVar()
        e51txt.set(self.parent.return_default_paths()[0])
        e51 = tkinter.Entry(self,textvariable = e51txt, state=tkinter.DISABLED, width=40)
        e51.grid(row=51, column=1, columnspan=5,sticky='WE')
        b51 = ttk.Button(self, text="change", command=lambda : self.get_new_path(e51txt, 0))
        b51.grid(row=51, column=6, columnspan=2, sticky='NSWE')
        
        l52 = tkinter.Label(self, text='Pattern images folder = ')
        l52.grid(row = 52, column = 0, columnspan = 1, sticky='E')
        e52txt = tkinter.StringVar()
        e52txt.set(self.parent.return_default_paths()[1])
        e52 = tkinter.Entry(self,textvariable = e52txt, state=tkinter.DISABLED)
        e52.grid(row=52, column=1, columnspan=5,sticky='WE')
        b52 = ttk.Button(self, text="change", command=lambda : self.get_new_path(e52txt, 1))
        b52.grid(row=52, column=6, columnspan=2, sticky='NSWE')
        
        ################## OTHER COMMANDS ##############################
        self.update_button = ttk.Button(self, text="Update", command=self.update_var)
        self.update_button.grid(row=79, column=0, columnspan=10, sticky='NSWE')
        self.exit_button = ttk.Button(self, text="Exit", command=self.quit_win)
        self.exit_button.grid(row=80, column=0, columnspan=10, sticky='NSWE')


            
    def get_pre_and_ext_from_camera(self, camera, e, n):
        if camera!=None:
            proc = subprocess.Popen(["gphoto2", "--port="+camera['port'], "--list-files"], stdout=subprocess.PIPE)
                
            sl=[]
            for l in proc.stdout.readlines():
                if l.decode('utf-8')[0]=='#':
                    try:
                        #print(l.decode('utf-8'))
                        nn=str(re.sub('\d{3,5}', ' ',l.decode('utf-8').split()[1]))
                        print(nn)
                        sl.append(nn)
                    except:
                        pass
            
            if sl.count(sl[0]) == len(sl): #check if all the elements in the list are identical
                pre, ext = sl[0].split()
                #print('pre = ',pre)
                #print('ext = ',ext)
                if n == 0:
                    e.set(pre)
                    self.parent.set_preL(pre)
                elif n == 1:
                    e.set(ext)
                    self.parent.set_extL(ext)
                elif n == 2:
                    e.set(pre)
                    self.parent.set_preR(pre)
                elif n == 3:
                    e.set(ext)
                    self.parent.set_extR(ext)
        else:
            tkinter.messagebox.showinfo("No camera found!", "Please check if a camera is connected and if it is selected as used camera in the main window!",icon="warning")
                
                
                
    def get_new_path(self,e, n):
        new_path = filedialog.askdirectory(initialdir=e.get(), title='Please select a directory')
        if  os.path.abspath(new_path) !=  os.path.abspath(e.get()):
            if tkinter.messagebox.askyesno("Changing Folder", "The current folder is:\n"+os.path.abspath(e.get())+"\nAre you sure to change it with:\n"+os.path.abspath(new_path),icon="warning"):
                e.set(new_path)
                if n == 0:
                    self.parent.set_acq_img_dir(os.path.abspath(new_path))
                elif n == 1:
                    self.parent.set_pattern_dir(os.path.abspath(new_path))
    def update_var(self):
        pass1
        
    def update_br(self, cb_br):
        cb_br['values'] = self.br_list
        
    
    def set_variable(self, txt, n):
        if n==1:
            self.preL = txt
            self.parent.set_preL(txt)
            print(txt)
        elif n==2:
            self.extensionL = txt
            self.parent.set_extL(txt)
            print(txt)
        elif n==3:
            self.preR = txt
            self.parent.set_preR(txt)
            print(txt)
        elif n==4:
            self.extensionR = txt
            self.parent.set_extR(txt)
            print(txt)
        elif n==5:
            self.pathL = txt
            self.parent.set_pathL(txt)
        elif n==6:
            self.pathR = txt
            self.parent.set_pathR(txt)
        elif n==7:
            self.br_deg = int(txt)
            self.parent.set_br_deg(txt)
        elif n==8:
            self.br_shot = int(txt)
            self.parent.set_br_shot(txt)

    
    def get_file_number(self, camera):
        if camera == None:
            return "camera not found!"
        else:
            return self.parent.get_last_image_number_and_name(camera)[0]
    def get_dirs(self, camera, combo):
        if camera == None:
            self.update_combo(combo, [])
        else:
            self.update_combo(combo, self.parent.get_camera_dirs(camera))
    
    def update_combo(self, combo, item_list):
        
        combo['values'] = item_list
        
        
    def newselection_cb2(self, evt):
        txt = self.cb2.get()
        self.set_variable(txt, 5)
        
    def newselection_cb7(self, evt):
        txt = self.cb7.get()
        self.set_variable(txt, 6)
        
    def newselection_cb12(self, evt):
        txt = self.cb12.get()
        self.set_variable(txt, 7)

    
    def newselection_cb16(self, evt):
        txt = self.cb16.get()
        self.set_variable(txt, 8)
                
    def quit_win(self, event=None):
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
        self.preL = 'DSC_'
        self.preR = 'DSC_'
        self.extensionL = '.JPG'
        self.extensionR = '.JPG'
        self.pathL = '/store_00010001/DCIM/100D3100'
        self.pathR = '/store_00010001/DCIM/100D3100'
        
        self.acq_img_dir = './acquired_images/'
        self.pattern_dir = '~'
        self.pattern_files=[]
        self.dir_opt = options = {}
        options['initialdir'] = self.pattern_dir
        options['mustexist'] = False

        if self.parent:
            self.parent.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.q)
        self.initialize()
        self.i=0
        
        
    def q(self):
        self.destroy()
        self.parent.update()
        self.parent.deiconify()
    
    def qq(self):
        self.destroy()
        self.parent.update()
        self.parent.deiconify()
        self.parent.destroy()
        
    def read_devices_list(self):
        try:
            with open('devices', 'rb') as f:
                dev_dict = pickle.loads(f.read())
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
        #filemenu.add_command(label="Open", command=self.hello)
        #filemenu.add_command(label="Save", command=self.hello)
        filemenu.add_separator()
        filemenu.add_command(label="Return to main window", command=self.q)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=self.qq)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # create more pulldown menus
        editmenu = tkinter.Menu(menubar, tearoff=0)
        
        editmenu.add_command(label="Check cameras", command=self.camera_utility)
        editmenu.add_command(label="View pattern images", command=self.view_pattern_image)
        editmenu.add_command(label="Add/remove a new camera", command=self.new_camera)
        editmenu.add_command(label="Add/remove a new device", command=self.new_device)
        editmenu.add_command(label="Preferences", command=self.preferences)
        menubar.add_cascade(label="Utility", menu=editmenu)
        
        helpmenu = tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        # display the menu
        self.config(menu=menubar)
        if self.parent:
            self.geometry("+%d+%d" % (self.parent.winfo_rootx()+50,
                                  self.parent.winfo_rooty()+50))
        
        
        
        
        
        for i in range(12):
            self.grid_columnconfigure(i,weight=1)
        
        for i in range(6):
            self.grid_rowconfigure(i,weight=1)
        
        self.combo1_value = tkinter.StringVar()
        self.combo1_value.set('not set!')
        self.combo1 = tkinter.ttk.Combobox(self, textvariable=self.combo1_value, postcommand = self.get_serial_int)
        self.combo1.grid(column=4,row=2, sticky='W')
        self.combo1.bind("<<ComboboxSelected>>", self.newselection_deg)
        
        ##serial
        self.btn_check_serial_deg = tkinter.Button(self,text=u"Test serial!",command=lambda : self.test_serial(self.S_deg,0))
        self.btn_check_serial_deg.grid(column=4,columnspan=1,row=3, sticky='NSWE')
        
        self.combo2_value = tkinter.StringVar()
        self.combo2_value.set('not set!')
        self.combo2 = tkinter.ttk.Combobox(self, textvariable=self.combo2_value, postcommand = self.get_serial_int)
        self.combo2.grid(column=4,row=6, sticky='W')
        self.combo2.bind("<<ComboboxSelected>>", self.newselection_shot)
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
    
    def view_pattern_image(self):
        self.open_win_proj()
        if self.proj.get():
            Check_Pattern_Image_Dialog(self,self.pattern_dir, self.pattern_files)
        #pass
        
    def test_serial(self, s_int,i=None):
        txt=''
        if s_int:
            S=s_int
            time.sleep(0.5)
            try:
                S.flushInput()
                S.flushOutput()
                S.write("$$\n$$\n$$\n".encode('ascii'))
                time.sleep(0.5)
                txt=self.read_serial(S)
                print(txt)
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
    
    
    def preferences(self):
        Preferences_Dialog(self, self.CL, self.CR)
    
    #def hello(self):
    #    print('Hello!!')
    def about(self):
        tkinter.messagebox.showinfo("About", "Orion Scan is a open-source project under GPL licence.\nFor more details please visit:\nhttps://github.com/PeriniMatteo/Orion-scan")
        
    def new_device(self):
        New_Device_Dialog(self)
        
    def new_camera(self):
        New_Camera_Dialog(self)
        
    def camera_utility(self):
        Check_Cameras_Dialog(self, self.CL, self.CR)
        
    def check_pattern_dir(self):
        n=0
        self.pattern_files=[]
        while True:
            filename=str(n)+'.tif'
            m = Path(self.pattern_dir+'/'+filename)
            if m.is_file():
                print(filename+' e un file!')
                self.pattern_files.append(filename)
                n+=1
            else:
                break
        print(self.pattern_files)
            
    def askdirectory(self):
    
        #Returns a selected directoryname
        return filedialog.askdirectory(**self.dir_opt)
        
    def open_win_proj(self):
        if self.proj.get():
            self.check_pattern_dir()
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
        else:
            tkinter.messagebox.showinfo("Warning", 'Enable the projector check button first!')
            
    def get_serial_int(self): 
        devlist=self.read_devices_list()
        self.ser_int = []
        for port in serial.tools.list_ports.comports():
            try:
                sn = self.get_sn(port)
                self.ser_int.append({'port':str(port[0]), 'dev':str(port[1]), 'sn':str(sn),'desc':str(devlist[sn])})
            except:
                self.ser_int.append({'port':str(port[0]), 'dev':str(port[1]), 'sn':str(sn)})
        self.update_combos()
    
    def update_combos(self):
        if self.ser_int == []:
            self.combo1_value.set('not set!')
            self.combo2_value.set('not set!')
            self.combo1['values'] = self.ser_int
            self.combo2['values'] = self.ser_int
            self.S_shot = None
            self.S_deg = None
            
        else:
            self.combo1['values'] = ([item['port']+" - "+item['dev'] if len(item)==3  else item['desc'] for item in self.ser_int])
            self.combo2['values'] = ([item['port']+" - "+item['dev'] if len(item)==3  else item['desc'] for item in self.ser_int])

    
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
        for n,i in enumerate(list(range(int(self.n_deg),360+int(self.n_deg),int(self.n_deg)))):
            if self.camera1.get():
                if self.proj.get():
                    for pattern in self.pattern_files:
                        self.show_image(self.pattern_dir+'/'+pattern)
                        time.sleep(0.2)
                        if self.flash.get():
                            self.S_shot.write(str('xxx 2\n').encode('ascii'))
                            self.check_camera_process()
                            self.destroy_image()
                        else:
                            self.S_shot.write(str('xxx 1\n').encode('ascii'))
                            self.check_camera_process()
                            self.destroy_image()
                else:
                    if self.flash.get():
                        self.S_shot.write(str('xxx 2\n').encode('ascii'))
                        self.check_camera_process()
                    else:
                        self.S_shot.write(str('xxx 1\n').encode('ascii'))
                        self.check_camera_process()
                    
            time.sleep(2)
            if self.table.get():
                if i==360:
                    
                    self.S_deg.write(str('G0 Z'+str(i/10.0)+'\r\n').encode('ascii'))
                    self.S_deg.write("$1=1\r\n".encode('ascii'))
                    self.S_deg.write(str('G0 Z'+str(i/10.0)+'\r\n').encode('ascii'))
                    self.check_stepper_position(i)
                    #if self.CL:
                    #    self.ask_images(self.CL, 0)
                    #if self.CR:
                    #    self.ask_images(self.CR, 1)
                    self.S_deg.write("G92 Z0\r\n".encode('ascii'))
                    time.sleep(0.5)
                else:
                    self.S_deg.write(str('G0 Z'+str(i/10.0)+'\r\n').encode('ascii'))
                    if self.CL:
                        self.ask_images(self.CL, 0, i)
                    if self.CR:
                        self.ask_images(self.CR, 1, i)
                    self.check_stepper_position(i)
                    time.sleep(0.5)

    def ask_images(self, camera, LR, i):
        ask_proc = multiprocessing.Process(target=self.ask_images_and_save(camera, LR, i))
        process_class= Retrieve_image(self, ask_proc, camera, LR, i)
        process_class.launch()
        
    def from_int_to_camera_file(self, LR, n):
        if LR == 0:
            return str(self.preL+str(n).rjust(4,'0')+self.extensionL)
        elif LR == 1:
            return str(self.preR+str(n).rjust(4,'0')+self.extensionR)
        else:
            tkinter.messagebox.showinfo("Warning", 'Camera not found!')
            
    def from_int_to_dest_file(self, LR, n, deg):
        if LR == 0:
            return str(self.preL+str(n).rjust(4,'0')+'_'+deg+'_left'+self.extensionL)
        elif LR == 1:
            return str(self.preR+str(n).rjust(4,'0')+'_'+deg+'_right'+self.extensionR)
        else:
            tkinter.messagebox.showinfo("Warning", 'Camera not found!')
        
    def ask_images_and_save(self,camera, LR, i):
        if LR == 0:
            subprocess.Popen(["gphoto2", "--port="+camera['port'], "--get-file="+self.pathL+'/'+self.from_int_to_camera_file(LR, camera['max_n']), \
                                    "--filename="+self.save_dir+'/'+self.from_int_to_dest_file(LR, camera['max_n'], i)], stdout=subprocess.PIPE)
        else:  
            subprocess.Popen(["gphoto2", "--port="+camera['port'], "--get-file="+self.pathR+'/'+self.from_int_to_camera_file(LR, camera['max_n']), \
                                    "--filename="+self.save_dir+'/'+self.from_int_to_dest_file(LR, camera['max_n'], i)], stdout=subprocess.PIPE)
            
        
        #return True
        #print(camera)
    def return_pre_and_ext(self):
        return self.preL, self.preR, self.extensionL, self.extensionR
    
    def get_last_image_number_and_name(self, camera):
        if camera!=None:
            proc = subprocess.Popen(["gphoto2", "--port="+camera['port'], "--list-files"], stdout=subprocess.PIPE)

            #with open('t.txt','w') as f:
                #f.write(proc.stdout.read().decode('utf-8'))
            k=0
            fns=[]
            #with open('t.txt','r') as f:
                
            for n,l in enumerate(proc.stdout.readlines()):
                #print(l)
                p = re.compile('DSC_\d+\.JPG')
                try:
                    #print(str(p.findall(l)))
                    nn=int(str(p.findall(l.decode('utf-8')))[6:10].lstrip('0'))
                    k+=1
                    #print(nn)
                    fns.append(nn)
                except:
                    pass
            
            afns = np.array(fns)
            #print(afns)
            #print(afns.max())
            #print('DSC_'+str(np.array(fns).max()).rjust(4,'0')+'.JPG')
            return afns.max(), str('DSC_'+str(afns.max()).rjust(4,'0')+'.JPG')
            
    def get_camera_dirs(self, camera):
        if camera!=None:
            proc = subprocess.Popen(["gphoto2", "--port="+camera['port'], "--list-folders"], stdout=subprocess.PIPE)
                #with open('t.txt','w') as f:
                #    f.write(proc.stdout.read().decode('utf-8'))
            
            k=0
            fn=[]

            for l in proc.stdout.readlines():
                #print(l.decode('utf-8'))
                p = re.compile('"/.*"')
                try:
                    path=str(p.findall(l.decode('utf-8')))
                    #print(str(path)[3:-3])
                    fn.append(str(path)[3:-3])
                except:
                    pass
            dir_list = [s for s in fn if s not in ['','/']]
            #print(dir_list)
            return dir_list
            
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
                #print(a)
                if str(a)[:10] == '<Idle,MPos':
                    if abs(float(a.split(',')[6][:5])-float(angle/10.0))<0.02:
                        print(str(float(a.split(',')[6][:5])*10)+' of '+str(float(angle))+' reached   br')
                        time.sleep(0.2)
                        break
                    else:
                        print(str(float(a.split(',')[6][:5])*10)+' of '+str(float(angle))+' reached')
        return True
        
    def check_camera_process(self):
        while True:
            a=''
            time.sleep(0.1)
            if (self.S_shot.inWaiting()>0):
                a=self.read_serial(self.S_shot)
                #print(a)
                a = a.split('\n')[-2]
                
                #print(a)
                if str(a)[:4] == 'gata':
                    break
        return True
        
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
        
        new_int = self.get_tty_name(self.value_of_combo)
        print('new_int = '+new_int)
        if self.S_deg:
            print('dentro')
            
            if self.S_shot:
                if self.S_shot.port != new_int:
                    self.disconnect_serial(self.S_deg)
                    self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
                else:
                    if tkinter.messagebox.askyesno("Serial busy", "This serial interface is already reserved! Do you want to use it anyway?",icon="warning"):
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
            if self.S_shot:
                if self.S_shot.port == new_int:
                    if tkinter.messagebox.askyesno("Serial busy", "This serial interface is already reserved! Do you want to use it anyway?",icon="warning"):
                        self.disconnect_serial(self.S_deg)
                        self.disconnect_serial(self.S_shot)
                        self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
                        self.combo2_value.set('not set!')
                    else:
                        self.combo1_value.set('not set!')
                        pass
                else:
                    self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
            else:
                self.S_deg = self.connect_serial(self.S_deg,new_int,br,0)
            
    def newselection_shot(self,evt):
        br=self.br_shot
        self.value_of_combo = self.combo2.get()
        self.get_serial_int()
        new_int = self.get_tty_name(self.value_of_combo)
        print('new_int = '+new_int)
            
        if self.S_shot:
            if self.S_deg:
                if self.S_deg.port != new_int:
                    self.disconnect_serial(self.S_shot)
                    self.S_shot = self.connect_serial(self.S_shot,new_int,br,0)

                else:
                    if tkinter.messagebox.askyesno("Serial busy", "This serial interface is already reserved! Do you want to use it anyway?",icon="warning"):
                        self.disconnect_serial(self.S_shot)
                        self.disconnect_serial(self.S_deg)
                        self.S_shot = self.connect_serial(self.S_shot,new_int,br,1)
                        self.combo1_value.set('not set!')
            
                    else:
                        self.combo2_value.set('not set!')

            else:
                self.disconnect_serial(self.S_shot)
                self.S_shot = self.connect_serial(self.S_shot,new_int,br,0)
        else:
            if self.S_deg:
                if self.S_deg.port == new_int:
                    if tkinter.messagebox.askyesno("Serial busy", "This serial interface is already reserved! Do you want to use it anyway?",icon="warning"):
                        self.disconnect_serial(self.S_shot)
                        self.disconnect_serial(self.S_deg)
                        self.S_shot = self.connect_serial(self.S_shot,new_int,br,1)
                        self.combo1_value.set('not set!')
                    else:
                        self.combo2_value.set('not set!')
                else:
                    self.S_shot = self.connect_serial(self.S_shot,new_int,br,1)
            else:
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
           return None

    def check_entry_degr(self,string):
        try:
           val = float(string)
           return val
        except ValueError:
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
            with open('cameras', 'rb') as f:
                cam_dict = pickle.loads(f.read())
                return cam_dict
        except:
            return {}
        
    def update_cam_combos(self):
        if self.cam_int == []:
            self.cbl_value.set('not set!')
            self.cbr_value.set('not set!')
            self.cbl['values'] = self.cam_int
            self.cbr['values'] = self.cam_int
            self.CL = None
            self.CR = None
            
        else:
            self.cbl['values'] = ([item['port']+" on "+item['name'] if len(item)==5  else item['desc'] for item in self.cam_int])
            self.cbr['values'] = ([item['port']+" on "+item['name'] if len(item)==5  else item['desc'] for item in self.cam_int])
        
        
    def get_cam_int(self):  
        camlist=self.read_cameras_list()
        self.cam_int = []
        
        for sn in self.attached_cameras().keys():
            if sn in camlist.keys():
                self.cam_int.append(camlist[sn])
            else:
                self.cam_int.append(self.attached_cameras()[sn])
        print('x')
        print(self.cam_int)
        print('x')
        self.update_cam_combos()
        
        
        
    def get_sn_from_combo(self,combo_value):
        cl =  self.attached_cameras()
        cam_list = self.read_cameras_list()
        print(cl)
        
        if combo_value.split()[0][:4]=='usb:':
            for item in cl.keys():
                if combo_value.split()[0][:11]==cl[item]['port']:
                    return item
        else:
            for item in cam_list.keys():
                if combo_value==cam_list[item]['desc']:
                    return item
        
    def newselection_usb_left(self,evt):
        self.value_of_combo = self.cbl.get()
        
        self.get_cam_int()
        new_int = self.get_sn_from_combo(self.value_of_combo)
        print('new_int = '+new_int)
        if self.CL:
            if self.CR:
                if self.CR['sn'] != new_int:
                    self.CL= self.attached_cameras()[new_int]
                else:
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
            if self.CL:
                if self.CL['sn'] != new_int:
                    self.CR= self.attached_cameras()[new_int]
                else:
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
    
    def set_preL(self, txt):
        self.preL = txt
        print('parent ='+txt)
    
    def set_preR(self, txt):
        self.preR = txt
    
    def set_extL(self, txt):
        self.extensionL = txt
    
    def set_extR(self, txt):
        self.extensionR = txt
        
    def return_br(self, n):
        if n==0:
            return self.br_deg
        elif n==1:
            return self.br_shot
    
    def return_paths(self):
        return self.pathL, self.pathR
    
    def set_pathL(self, txt):
        self.pathL = txt
    
    def set_pathR(self, txt):
        self.pathR = txt
    
    def return_br(self):
        return self.br_deg, self.br_shot
    
    def set_br_deg(self, txt):
        self.br_deg = int(txt)
        
    def set_br_shot(self, txt):
        self.br_shot = int(txt)
    
    def return_default_paths(self):
        return self.acq_img_dir, self.pattern_dir
    
    def set_acq_img_dir(self,path):
        self.acq_img_dir = path
        
    def set_pattern_dir(self,path):
        self.pattern_dir = path
        
if __name__ == "__main__":
    app = TakeDialog(None)
    app.title('Take window')
    app.mainloop()
    
