# -*- coding: UTF-8 -*-
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk
from functools import partial
import ast

import cv2
import numpy as np
from PIL import Image, ImageTk

class View(ABC) :
    @abstractmethod
    def setUp(self,controler):
        """
            Set up the tkinter view
        """
        pass

    @abstractmethod
    def start_main_loop() :
        pass

class MyView(View) :
    def setUp(self,controller):
        """
        Set up the view
        """
        # global features
        self.root = tk.Tk()
        self.root.geometry("850x500")
        self.root.title("Video Annotations")

        # Image loader
        self.image_frame = tk.LabelFrame(self.root,text="Image",width=550,height=500)
        self.image_frame.grid_propagate(False) 
        self.image_frame.grid(row=0,column=0)  
        # Preivous : click on it or left arrow
        self.previous = tk.Button(self.image_frame,text="<-",command=controller.previous_frame)
        self.previous.place(x=250, y=450)
        self.root.bind("<Left>",controller.previous_frame)
        # Next : click on it or right arrow
        self.next = tk.Button(self.image_frame,text="->",command=controller.next_frame)
        self.next.place(x=277, y=450)
        self.root.bind("<Right>",controller.next_frame)
        # show the current frame we're at globally
        self.frame_count = tk.Label(self.image_frame)
        self.frame_count.place(x=260, y=430)
        # same for video 1
        self.frame_count1 = tk.Label(self.image_frame)
        self.frame_count1.place(x=150, y=430)
        # and video 2
        self.frame_count2 = tk.Label(self.image_frame)
        self.frame_count2.place(x=380, y=430)
        # if we have already displayed a frame
        self.already = False
        # button to pause the first video
        pause_video1 = partial(controller.pause_video, 0)
        self.button_pause1 = tk.Button(self.image_frame, text="Pause", command=pause_video1)
        self.button_pause1.place(x=150, y=450)
        # to pause the second video
        pause_video2 = partial(controller.pause_video, 1)
        self.button_pause2 = tk.Button(self.image_frame, text="Pause", command=pause_video2)
        self.button_pause2.place(x=380,y=450)

        # Config
        self.text_frame = tk.LabelFrame(self.root,text="Config",width=300,height=500)
        self.text_frame.grid_propagate(False) 
        self.text_frame.grid(row=0,column=1) 
        # Open the first video
        load_vid1 = partial(controller.load_frames, 0)
        self.open_button1 = ttk.Button(
            self.text_frame,
            text='Open video 1',
            command=load_vid1
        )
        self.open_button1.place(x=70, y=30)
        # open the second video
        load_vid2 = partial(controller.load_frames, 1)
        self.open_button2 = ttk.Button(
            self.text_frame,
            text='Open video 2',
            command=load_vid2
        )
        self.open_button2.place(x=170, y=30)
        # restart the count of all idx at 0
        self.button_restart = tk.Button(self.text_frame, text="Restart", command=controller.restart)
        self.button_restart.place(x=130, y=60)
        # display the results of 'pairs' via cv2
        self.button_display = tk.Button(self.text_frame, text="Look at video!", command=controller.show_frames)
        self.button_display.place(x=111, y=100)
        # create and save the video!
        self.button_save = tk.Button(self.text_frame, text="Save video!", command=controller.create_video)
        self.button_save.place(x=121, y=130)
        # name of the video
        self.video_name_entry = tk.Entry(self.text_frame, bd =5)
        self.video_name_entry.place(x=95, y=160)
        
    def show_img(self, image1, image2) :
        """
            Show the image of the loaded video
        """
        # Load the image
        ori_size = (1920,1080)
        try :
            _ = image1.shape
        except :
            # if it's not an image, we replace it with zeros
            image1 = np.zeros((10,10,3))
            image1 = cv2.resize(image1, (min(int(400*ori_size[1] / ori_size[0]),540), 400))
        try :
            _ = image2.shape
        except :
            image2 = np.zeros((10,10,3))
            image2 = cv2.resize(image2, (min(int(400*ori_size[1] / ori_size[0]),540), 400))
        
        # concat horiz
        image_total = np.ones((image1.shape[0]+20, image1.shape[1]*2+30,3)) * 255
        image_total[10:-10, 10:image1.shape[1]+10] = image1
        image_total[10:-10, image1.shape[1]+20:-10] = image2
        # to Image
        image_total = Image.fromarray(image_total.astype(np.uint8))
        # Display
        resize_image = image_total
        img = ImageTk.PhotoImage(resize_image)

        if not self.already :
            # create the label to store the image only the first time as the mainloop must be restarted
            self.image_label = tk.Label(self.image_frame,image=img)
            self.image_label.place(x=30,y=5)
            self.already = True
            self.root.mainloop()
        else :
            # update the image label
            self.image_label.configure(image=img)
            self.image_label.image = img
    
    def start_main_loop(self) :
        """
        Main loop for the view
        """
        self.root.mainloop()
