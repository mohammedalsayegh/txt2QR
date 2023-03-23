#! /usr/bin/python
# python -m PyInstaller -w --onefile .\qu.py
# python -m nuitka --onefile --standalone .\qu.py
# python -m PyInstaller --clean -w --onefile .\qu.py

from pathlib import Path
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk

import multiprocessing

#This part for the QR
import qrcode
from qrcode.image.styledpil import StyledPilImage

from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer
from qrcode.image.styles.moduledrawers.pil import GappedSquareModuleDrawer
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.moduledrawers.pil import VerticalBarsDrawer
from qrcode.image.styles.moduledrawers.pil import HorizontalBarsDrawer

from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.colormasks import SquareGradiantColorMask
from qrcode.image.styles.colormasks import HorizontalGradiantColorMask
from qrcode.image.styles.colormasks import VerticalGradiantColorMask
from qrcode.image.styles.colormasks import ImageColorMask

from easygui import *
from PIL import Image, ImageDraw
import os
import pathlib
import shutil

#OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = os.getcwd() + "\\assets\\frame0"
TEMP_PATH = os.getcwd() + "\\assets\\temp"
MAIN_PATH = os.getcwd()

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def relative_to_temp(path: str) -> Path:
    return TEMP_PATH / Path(path)

def main_to_temp(path: str) -> Path:
    return MAIN_PATH / Path(path)

class App:
    def __init__(self, master=tk.Tk()):
        self.master = master
        master.resizable(False, False)

        screen_width = master.winfo_screenwidth()  # Width of the screen
        screen_height = master.winfo_screenheight() # Height of the screen

        self.qr_size=300
 
        # Calculate Starting X and Y coordinates for Window
        width = 720
        height = 450
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
 
        master.geometry('%dx%d+%d+%d' % (width, height, x, y))
        master.iconbitmap(relative_to_assets('icon.ico'))
        #master.geometry("720x512")
        #master.configure(bg = "#FFFFFF")
        master.configure(bg = "#B2B99F")
        
        # create a menubar
        menubar = tk.Menu(master)
        master.config(menu=menubar)

        # create the file_menu
        file_menu = tk.Menu(menubar, tearoff=0 )
        # add menu items to the File menu
        file_menu.add_command(label='New')
        file_menu.add_command(label='Open...',accelerator="Ctrl+O", command=lambda:self.open_txt_file())
        file_menu.add_command(label='Open TXT List to QR',accelerator="Ctrl+L", command=lambda:self.textlist2qr())
        file_menu.add_command(label='Close')
        file_menu.add_command(label='Save Location', accelerator="Ctrl+Shift+S", command=lambda:self.save_location_fun())
        file_menu.add_separator()

        # add a submenu
        sub_menu = tk.Menu(file_menu, tearoff=0)
        sub_menu.add_command(label='Keyboard Shortcuts')
        sub_menu.add_command(label='Color Themes')

        # add the File menu to the menubar
        file_menu.add_cascade(label="Preferences", menu=sub_menu)

        # add Exit menu item
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=master.destroy)
        menubar.add_cascade(label="File", menu=file_menu, underline=0)

        # Hotkey for file menu
        master.bind("<Control-Shift-S>", lambda x: self.save_location_fun())
        master.bind("<Control-o>", lambda x: self.open_txt_file())
        master.bind("<Control-l>", lambda x: self.textlist2qr())

        # create the preferences menu
        preferences_menu = tk.Menu(menubar, tearoff=0 )
        preferences_menu.add_command(label='Color Mask List', accelerator="Ctrl+P",command=lambda: self.color_mask_update())
        preferences_menu.add_command(label='Fill Color', accelerator="Ctrl+O",command=lambda:(self.fill_colorchooser_fun(),self.color_chooser_call()))
        preferences_menu.add_command(label='Background Color', accelerator="Ctrl+I",command=lambda: self.back_colorchooser_fun())
        preferences_menu.add_separator()
        preferences_menu.add_command(label='Refresh', accelerator="F5",command=lambda: self.string_chnaged())
        menubar.add_cascade(label="Preferences", menu=preferences_menu, underline=0 )

        # Hotkey for preferences menu
        master.bind("<Control-p>", lambda x: self.color_mask_update())
        master.bind("<Control-u>", lambda x: self.fill_colorchooser_fun())
        master.bind("<Control-i>", lambda x: self.back_colorchooser_fun())
        master.bind("<F5>", lambda x: self.string_chnaged())

        # create the Help menu
        help_menu = tk.Menu(menubar, tearoff=0 )
        help_menu.add_command(label='Welcome')
        help_menu.add_command(label='About...')

        # add the Help menu to the menubar
        menubar.add_cascade(label="Help", menu=help_menu, underline=0 )

        self.hi="Hi from __init__!"
        self.save_location=main_to_temp("out.png")
        self.back_color_array=(255,255,255)
        self.fill_color_array=('black')
        print(self.save_location)
        self.reply2='SolidFillColorMask()'

        self.name_var=tk.StringVar()
        
        #self.name_var.trace('w', lambda *args: print('hi'))
        #self.aWriteTracerID = self.name_var.trace('w', lambda *args: self.sring_chnaged())

        self.frame = tk.Frame(master)
        self.canvas = tk.Canvas(self.frame,bg = "#FFFFFF",height = height,width = width,bd = 0,highlightthickness = 0,relief = "ridge")
        self.canvas.place(x = 0, y = 0)

        #self.img0 = tk.PhotoImage(file=relative_to_assets("entry_1.png"))
        #entry_bg_1 = self.canvas.create_image(281.5, 48.0, image=self.img0)

        self.txtframe = tk.Frame(master)
        self.txtframe.place(x=83.0, y=24.0, width=554.0, height=24.0)
        self.textbox = tk.Text(self.txtframe,bd=0,bg="#D9D9D9",fg="#000716",highlightthickness=0)
        self.textbox.place(x=83.0, y=24.0, width=554.0, height=24.0)
        #self.scroll = tk.Scrollbar(self.textbox)
        #self.textbox.configure(yscrollcommand=self.scroll.set)
        self.textbox.pack(side=tk.RIGHT)
          
        #self.scroll.config(command=self.textbox.yview)
        #self.scroll.pack(side=tk.LEFT, fill=tk.Y)

        self.textbox.config(fg='grey')
        self.textbox.insert(1.0, "QR2txt")
        self.init_placeholder(self.textbox, "QR2txt")
        #self.textbox.bind("<Return>", lambda x: self.string_chnaged())

        y_bottom=244.0
        self.img1 = tk.PhotoImage(file=relative_to_assets("button_1.png"))
        self.button_1 = tk.Button(image=self.img1,borderwidth=0,highlightthickness=0,command=lambda: shutil.copyfile(relative_to_temp("qr_file1.png"), self.save_location),relief="flat") 
        self.button_1.bind('<Button-3>', lambda x: self.show_cliked_qr("qr_file1.png"))
        self.button_1.place(x=520.0, y=y_bottom, width=150.0, height=150.0)

        self.img2 = tk.PhotoImage(file=relative_to_assets("button_2.png"))
        self.button_2 = tk.Button(image=self.img2,borderwidth=0,highlightthickness=0,command=lambda: shutil.copyfile(relative_to_temp("qr_file2.png"), self.save_location),relief="flat")
        self.button_2.bind('<Button-3>', lambda x: self.show_cliked_qr("qr_file2.png"))
        self.button_2.place(x=285.0, y=y_bottom, width=150.0, height=150.0)

        self.img3 = tk.PhotoImage(file=relative_to_assets("button_3.png"))
        self.button_3 = tk.Button(image=self.img3,borderwidth=0,highlightthickness=0,command=lambda: shutil.copyfile(relative_to_temp("qr_file3.png"), self.save_location),relief="flat")
        self.button_3.bind('<Button-3>', lambda x: self.show_cliked_qr("qr_file3.png"))
        self.button_3.place(x=50.0, y=y_bottom, width=150.0, height=150.0)

        y_top=71.0
        self.img4 = tk.PhotoImage(file=relative_to_assets("button_4.png"))
        self.button_4 = tk.Button(image=self.img4,borderwidth=0,highlightthickness=0,command=lambda: shutil.copyfile(relative_to_temp("qr_file4.png"), self.save_location),relief="flat")
        self.button_4.bind('<Button-3>', lambda x: self.show_cliked_qr("qr_file4.png"))
        self.button_4.place(x=520.0, y=y_top, width=150.0, height=150.0)

        self.img5 = tk.PhotoImage(file=relative_to_assets("button_5.png"))
        self.button_5 = tk.Button(image=self.img5,borderwidth=0,highlightthickness=0,command=lambda: shutil.copyfile(relative_to_temp("qr_file5.png"), self.save_location),relief="flat")
        self.button_5.bind('<Button-3>', lambda x: self.show_cliked_qr("qr_file5.png"))
        self.button_5.place(x=285.0, y=y_top, width=150.0, height=150.0)

        self.img6 = tk.PhotoImage(file=relative_to_assets("button_6.png"))
        self.button_6 = tk.Button(image=self.img6,borderwidth=0,highlightthickness=0,command=lambda: shutil.copyfile(relative_to_temp("qr_file6.png"), self.save_location),relief="flat")
        self.button_6.bind('<Button-3>', lambda x: self.show_cliked_qr("qr_file6.png"))
        self.button_6.place(x=50.0, y=y_top, width=150.0, height=150.0)
        
        self.frame.bind("q", self.close)
        self.frame.bind("<Escape>", self.close)
        self.frame.pack()
        self.frame.focus_set()

        self.string_chnaged()

        self.is_active = True

    def textlist2qr(self):
        self.color_mask_update()

        s=['SquareModuleDrawer()','GappedSquareModuleDrawer()','CircleModuleDrawer()','RoundedModuleDrawer()','VerticalBarsDrawer()','HorizontalBarsDrawer()']
        s=choicebox("Select color_mask preferance:", choices = s)
        functions_drawer = {
            'SquareModuleDrawer()': "qr_file1.png",
            'GappedSquareModuleDrawer()': "qr_file2.png",
            'CircleModuleDrawer()': "qr_file3.png",
            'RoundedModuleDrawer()':"qr_file4.png",
            'VerticalBarsDrawer()':"qr_file5.png",
            'HorizontalBarsDrawer()':"qr_file6.png"
        }
        #with open('Book8.csv') as fp:

        self.txtfile = tk.filedialog.askopenfilename()
        #fob=open(self.txtfile ,'r', encoding="utf8")
        c = 0
        with open(self.txtfile ,'r', encoding="utf8") as fob:
            for line in fob:
                c = c + 1
                #print line[1]
                self.textbox.delete(1.0, "end")
                self.textbox.insert(1.0, line)

                #update name save
                save_location_list=str(self.save_location)[:-4]+"_"+str(c)+".png"

                #print out the QRs
                self.string_chnaged()

                #copy qr to the new 
                shutil.copyfile(relative_to_temp(functions_drawer[s]), save_location_list)
        print("textlist2qr done!")

    def show_cliked_qr(self,imgfilename):
        print("Here I am!")
        img = Image.open(relative_to_temp(imgfilename))
        img.show() 

    def color_chooser_call(self):
        self.reply2 = 'Color Chooser'
    
    def open_txt_file(self):
        #self.txtfile = tk.filedialog.askopenfile(mode='r',filetypes=(("txt files","*.txt"),))

        self.txtfile = tk.filedialog.askopenfilename()
        fob=open(self.txtfile ,'r', encoding="utf8")
        print(fob.read())

        self.textbox.config(fg='black')
        self.textbox.delete(1.0, "end")
        #self.textbox.insert(1.0, self.txtfile.read())
        fob.seek(0)
        self.textbox.insert(1.0, fob.read())

    def string_chnaged(self):
        self.txt2qr()

        self.img1 = tk.PhotoImage(file=relative_to_temp("qr_file1.png"))
        self.img1 = self.resizeImage(self.img1, 150, 150)  # resized to 150px x 150px
        self.button_1.config(image=self.img1)
        
        self.img2 = tk.PhotoImage(file=relative_to_temp("qr_file2.png"))
        self.img2 = self.resizeImage(self.img2, 150, 150)  # resized to 150px x 150px
        self.button_2.config(image=self.img2)
        
        self.img3 = tk.PhotoImage(file=relative_to_temp("qr_file3.png"))
        self.img3 = self.resizeImage(self.img3, 150, 150)  # resized to 150px x 150px
        self.button_3.config(image=self.img3)
        
        self.img4 = tk.PhotoImage(file=relative_to_temp("qr_file4.png"))
        self.img4 = self.resizeImage(self.img4, 150, 150)  # resized to 150px x 150px
        self.button_4.config(image=self.img4)
        
        self.img5 = tk.PhotoImage(file=relative_to_temp("qr_file5.png"))
        self.img5 = self.resizeImage(self.img5, 150, 150)  # resized to 150px x 150px
        self.button_5.config(image=self.img5)
        
        self.img6 = tk.PhotoImage(file=relative_to_temp("qr_file6.png"))
        self.img6 = self.resizeImage(self.img6, 150, 150)  # resized to 150px x 150px
        self.button_6.config(image=self.img6)

    def color_mask_update(self):
        s=('SolidFillColorMask()','RadialGradiantColorMask()','SquareGradiantColorMask()','HorizontalGradiantColorMask()','VerticalGradiantColorMask()', 'ImageColorMask()','Color Chooser')
        self.reply2=choicebox("Select color_mask preferance:", choices = s)

        
        #if self.reply2=='SolidFillColorMask()':
            #self.aWriteTracerID = self.name_var.trace('w', lambda *args: self.sring_chnaged())
        #else:
            #print("Im here")
            #print(self.aWriteTracerID)
            #self.name_var.trace_remove("w", self.aWriteTracerID)

        if self.reply2=="ImageColorMask()":
            self.logo = fileopenbox()
            self.logo = Image.open(self.logo)
            print(self.logo)
        if self.reply2=="Color Chooser":
            self.fill_colorchooser_fun()
        #self.sring_chnaged()

    def resizeImage(self, img, newWidth, newHeight):
        oldWidth = img.width()
        oldHeight = img.height()
        newPhotoImage = tk.PhotoImage(width=newWidth, height=newHeight)
        for x in range(newWidth):
            for y in range(newHeight):
                xOld = int(x*oldWidth/newWidth)
                yOld = int(y*oldHeight/newHeight)
                rgb = '#%02x%02x%02x' % img.get(xOld, yOld)
                newPhotoImage.put(rgb, (x, y))
        return newPhotoImage

    def init_placeholder(self, widget, placeholder_text):
        widget.placeholder = placeholder_text
        if widget.get(1.0, "end") == "":
            widget.insert("end", placeholder_text)

        # set up a binding to remove placeholder text
        widget.bind("<FocusIn>", self.remove_placeholder)
        widget.bind("<FocusOut>", self.add_placeholder)

    def remove_placeholder(self,event):
        """Remove placeholder text, if present"""
        placeholder_text = getattr(event.widget, "placeholder", "")
        if placeholder_text and event.widget.get("1.0",'end-1c') == placeholder_text:
            print("FocusIn")
            event.widget.delete(1.0, "end")
            event.widget.config(fg='black')

    def add_placeholder(self,event):
        """Add placeholder text if the widget is empty"""
        placeholder_text = getattr(event.widget, "placeholder", "")
        if placeholder_text and event.widget.get(1.0, "end-1c") == "":
            print("FocusOut")
            event.widget.insert(1.0, placeholder_text)
            event.widget.config(fg='grey')

    def back_colorchooser_fun(self):
        self.back_color_array = colorchooser.askcolor(title ="Choose Background Color")
        self.back_color_array = (self.back_color_array[0][0], self.back_color_array[0][1], self.back_color_array[0][2])
    
    def fill_colorchooser_fun(self):
        self.fill_color_array = colorchooser.askcolor(title ="Choose Fill Color")
        self.fill_color_array = (self.fill_color_array[0][0], self.fill_color_array[0][1], self.fill_color_array[0][2])
        fill_color_mask = Image.new('RGB', (self.qr_size, self.qr_size), self.fill_color_array)
        fill_color_mask.save("./assets/temp/fill_color_mask.png")
        self.fill_color_img=Image.open(relative_to_temp("fill_color_mask.png"))
        print(self.fill_color_img)
         
    def save_location_fun(self):
            self.save_location = filesavebox(msg=None, title="Save At", default="out", ﬁletypes="*.png")
            if self.save_location:
                print("update save location:")
                self.save_location = self.save_location+".png"
            else:
                self.save_location=main_to_temp("out.png")
            #print(self.save_location)
            print("done")

    def txt2qr(self):
        functions_drawer = {
            'SquareModuleDrawer()': SquareModuleDrawer,
            'GappedSquareModuleDrawer()': GappedSquareModuleDrawer,
            'CircleModuleDrawer()': CircleModuleDrawer,
            'RoundedModuleDrawer()':RoundedModuleDrawer,
            'VerticalBarsDrawer()':VerticalBarsDrawer,
            'HorizontalBarsDrawer()':HorizontalBarsDrawer
        }

        functions_color_mask = {
            'SolidFillColorMask()': SolidFillColorMask,
            'RadialGradiantColorMask()': RadialGradiantColorMask,
            'SquareGradiantColorMask()': SquareGradiantColorMask,
            'HorizontalGradiantColorMask()':HorizontalGradiantColorMask,
            'VerticalGradiantColorMask()':VerticalGradiantColorMask,
            'ImageColorMask()':ImageColorMask
        }
        
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
        
        qr.add_data(self.textbox.get("1.0","end"))
        #qr.add_data(self.name_var.get())

        #qr.add_data(self.txtfile.read())

        reply1=['SquareModuleDrawer()','GappedSquareModuleDrawer()','CircleModuleDrawer()','RoundedModuleDrawer()','VerticalBarsDrawer()','HorizontalBarsDrawer()']

        if self.reply2=="ImageColorMask()":
 
            # variable to store hexadecimal code of color
            #back_color_array = colorchooser.askcolor(title ="Choose color")
            #back_color_array = (back_color_array[0][0], back_color_array[0][1], back_color_array[0][2])
            #print(color_code)

            #back_color_array=(255,255,255)
            #self.back_color_array=(125,125,125)

            reply=reply1[0]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.logo), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file1.png")

            reply=reply1[1]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.logo), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file2.png")

            reply=reply1[2]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.logo), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file3.png")

            reply=reply1[3]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.logo), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file4.png")

            reply=reply1[4]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.logo), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file5.png")

            reply=reply1[5]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.logo), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file6.png")
        
        elif self.reply2=="Color Chooser":
            reply=reply1[0]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.fill_color_img), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file1.png")

            reply=reply1[1]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.fill_color_img), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file2.png")

            reply=reply1[2]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.fill_color_img), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file3.png")

            reply=reply1[3]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.fill_color_img), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file4.png")

            reply=reply1[4]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.fill_color_img), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file5.png")

            reply=reply1[5]
            img = qr.make_image(image_factory=StyledPilImage, color_mask=ImageColorMask(back_color=self.back_color_array, color_mask_image=self.fill_color_img), module_drawer=functions_drawer[reply]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file6.png")
        else:
            print("IM HERE")
            reply=reply1[0]
            img = qr.make_image(image_factory=StyledPilImage, module_drawer=functions_drawer[reply](), color_mask=functions_color_mask[self.reply2]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file1.png")

            reply=reply1[1]
            img = qr.make_image(image_factory=StyledPilImage, module_drawer=functions_drawer[reply](), color_mask=functions_color_mask[self.reply2]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file2.png")
            
            reply=reply1[2]
            img = qr.make_image(image_factory=StyledPilImage, module_drawer=functions_drawer[reply](), color_mask=functions_color_mask[self.reply2]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file3.png")

            reply=reply1[3]
            img = qr.make_image(image_factory=StyledPilImage, module_drawer=functions_drawer[reply](), color_mask=functions_color_mask[self.reply2]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file4.png")

            reply=reply1[4]
            img = qr.make_image(image_factory=StyledPilImage, module_drawer=functions_drawer[reply](), color_mask=functions_color_mask[self.reply2]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file5.png")

            reply=reply1[5]
            img = qr.make_image(image_factory=StyledPilImage, module_drawer=functions_drawer[reply](), color_mask=functions_color_mask[self.reply2]())
            img=img.resize((self.qr_size, self.qr_size))
            img.save("./assets/temp/qr_file6.png")

    def my_function(self):
        print("Hello from a function")
        print("button_1 clicked")

        self.img = tk.PhotoImage(file=relative_to_assets("123.png"))
        self.button_1.config(image=self.img)
        #self.update()
        print(self.hi)

    def load_image(self, filename):
        self.fig_image = ImageTk.PhotoImage(Image.open(filename).resize(self.fig_size, Image.BILINEAR))

    #def update(self, *args):
        #self.load_image('sample2.png')
        #self.image_label.config(image=self.fig_image)

    def close(self, *args):
        print('GUI closed...')
        self.master.quit()
        self.is_active = False

    def is_closed(self):
        return not self.is_active

    def mainloop(self):
        self.master.mainloop()
        print('mainloop closed...')

if __name__ == '__main__':
    import time
    app = App()
    app.mainloop()