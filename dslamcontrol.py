import configparser
from configparser import ConfigParser
from tkinter import PhotoImage

import threading

# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.style import Bootstyle

import telnetlib

# credential and other private date are stored outside
import secret

class threadDSLAM (threading.Thread):
    def __init__(self, mode, ip , port, event):
        threading.Thread.__init__(self)
        self.mode = mode
        self.ip = ip
        self.port = port
        self.event = event

    def run(self):
        #TODO: error control: Too many connection ...
        t = telnetlib.Telnet(self.ip)
        b = t.read_until(b'>>User name:', 5)
        print(b.decode('utf-8'))
        t.write(bytes(secret.USER, 'utf-8'))
        t.write(b'\r\n')
        b= t.read_until(b'>>User password:', 5)
        print(b.decode('utf-8'))
        t.write(bytes(secret.PASSWORD, 'utf-8'))
        t.write(b'\r\n')
        b = t.read_until(b'MA5603T>', 5)
        print(b.decode('utf-8'))
        t.write(b'enable\r\n')
        b = t.read_until(b'MA5603T#', 5)
        print(b.decode('utf-8'))
        t.write(b'config\r\n')
        b = t.read_until(b'(config)',5)
        print(b.decode('utf-8'))
        t.write(b'interface vdsl 0/0\r\n')
        b = t.read_until(b'(config-if-vdsl-0/0)', 5)
        print(b.decode('utf-8'))

        t.read_very_eager()
        cmd = bytes('deactivate ' + self.port, 'utf-8')
        t.write(cmd)
        t.write(b'\r\n')
        b = t.read_until(b'#', 5)
        print(b.decode('utf-8'))
        
        t.read_very_eager()
        if (self.mode == 'VDSL'):
            cmd = bytes('activate ' + self.port + ' prof-idx ds-rate 3 us-rate 4', 'utf-8')
            t.write(cmd)
            t.write(b' inp-delay 10 noise-margin 13 spectrum 17 upbo 3\r\n')
        else:
            cmd = bytes('activate ' + self.port + ' prof-idx ds-rate 26 us-rate 102', 'utf-8')
            t.write(cmd)
            t.write(b' inp-delay 10 noise-margin 13 spectrum 11 upbo 10\r\n')
        b = t.read_until(b':', 5)
        print(b.decode('utf-8'))
        t.write(b'\r\n')
        b = t.read_until(b'#', 5)
        print(b.decode('utf-8'))

        t.close()
        self.event.set()


class main_program():
    def __init__(self):

        self.window = ttk.Window(resizable=(NO,NO))
        self.window.title('DSLAMControl')
        self.window.iconbitmap('app.ico')
        # self.style = ttk.Style(theme='darkly')

        self.img = PhotoImage(file='.\Icone.PNG')
        
        self.bg = ttk.Canvas(self.window, width=414, height=327)
        self.bg.pack(expand = YES, fill = BOTH)
        self.bg.create_image(0, 0, image = self.img, anchor = 'nw')
        
        self.gauge = ttk.Progressbar(
            bootstyle=SECONDARY,
            mode='indeterminate',
            length=207,
        )
        self.b1_value = ttk.StringVar()
        self.b2_value = ttk.StringVar()

        self.b1 = ttk.Checkbutton(self.bg, text="ADSL", bootstyle=(SUCCESS,TOOLBUTTON), variable=self.b1_value)
        self.b2 = ttk.Checkbutton(self.bg, text="VDSL", bootstyle=(PRIMARY,TOOLBUTTON), variable=self.b2_value)
        self.b1.configure(command=self.buttonADSLClicked, state='disabled')
        self.b2.configure(command=self.buttonVDSLClicked, state='disabled')
        # self.b1.invoke()

        b1_wd = self.bg.create_window( 141, 68, anchor = 'n', window = self.b1)
        b2_wd = self.bg.create_window( 283, 68, anchor = 'n', window = self.b2)
        
        
        
        # gauge_wd = self.bg.create_window( 0, 327, anchor = 'sw', window = self.gauge)
        self.gauge.pack()

        self._config()
        #TODO: check config error

        self.buttonADSLClicked()


    def _config(self):
        cfg = ConfigParser()
        cfg.read('.\QDSLAMControl.ini')

        try:
            self.ip = cfg.get('DSLAM', 'ip')
        except  configparser.NoSectionError:
            self.ip = secret.IP
            cfg.add_section('DSLAM')
            cfg.set('DSLAM', 'ip', self.ip)
            with open('QDSLAMControl.ini', 'w') as cfgfile:
                cfg.write(cfgfile)
        except configparser.NoOptionError:
            self.ip = secret.IP
            cfg.set('DSLAM', 'ip', self.ip)
            with open('QDSLAMControl.ini', 'w') as cfgfile:
                cfg.write(cfgfile)


        try:
            self.port = cfg.get('DSLAM', 'port')
        except  configparser.NoSectionError:
            self.port = secret.PORT
            cfg.add_section('DSLAM')
            cfg.set('DSLAM', 'port', self.port)
            with open('QDSLAMControl.ini', 'w') as cfgfile:
                cfg.write(cfgfile)
        except configparser.NoOptionError:
            self.port = secret.PORT
            cfg.set('DSLAM', 'port', self.port)
            with open('QDSLAMControl.ini', 'w') as cfgfile:
                cfg.write(cfgfile)

    def buttonADSLClicked(self):
        self.gauge.start()

        self.b1.state(['disabled'])
        self.b2.state(['disabled'])
        self.b1.update_idletasks()
        self.b2.update_idletasks()

        event = threading.Event()
        event.clear()
        m = threadDSLAM('ADSL', self.ip, self.port, event)
        m.start()

        while not event.is_set():
            self.window.update()
            event.wait (0.1)

        self.b1_value.set('1')
        self.b2_value.set('0')


        self.b1.state(['!disabled'])
        self.b2.state(['!disabled'])

        self.gauge.stop()

    def buttonVDSLClicked(self):
        self.gauge.start()

        self.b1.state(['disabled'])
        self.b2.state(['disabled'])
        self.b1.update_idletasks()
        self.b2.update_idletasks()

        event = threading.Event()
        event.clear()
        m = threadDSLAM('VDSL', self.ip, self.port, event)
        m.start()

        while not event.is_set():
            self.window.update()
            event.wait (0.1)

        self.b1_value.set('1')
        self.b2_value.set('0')

        self.b1.state(['!disabled'])
        self.b2.state(['!disabled'])

        self.gauge.stop()

if __name__ == '__main__':
    program = main_program()

    program.window.mainloop()