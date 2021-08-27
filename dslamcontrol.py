import configparser
from configparser import ConfigParser
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk


class main_program():
    def __init__(self):
        self.window = ThemedTk(theme='arc')
        self.window.title('DSLAMControl')
        self.window.iconbitmap('app.ico')
        self.config()

    def config(self):
        cfg = ConfigParser()
        cfg.read('QDSLAMControl.ini')

        try:
            port = cfg.get('DSLAM', 'port')
        except  configparser.NoSectionError:
            port = '0'
            cfg.add_section('DSLAM')
            cfg.set('DSLAM', 'port', port)
            with open('QDSLAMControl.ini', 'w') as cfgfile:
                cfg.write(cfgfile)
        except configparser.NoOptionError:
            port = '0'
            cfg.set('DSLAM', 'port', port)
            with open('QDSLAMControl.ini', 'w') as cfgfile:
                cfg.write(cfgfile)

        print(port)


program = main_program()

program.window.mainloop()