import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk
from functools import partial
import ast
from tqdm import tqdm

import os
import cv2
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
from tkinter import filedialog as fd
import time

from decord import VideoReader
from decord import cpu, gpu

from src.model import get_frames, Model
from src.view import MyView, View

class Controler :
    def __init__(self,model : Model, view : View) :
        # load the model
        self.model = model
        # load the view
        self.view = view 

    def load_frames(self, idx) :
        """
            Load the video via the model method
            Show the next frame ie the second afterwards
        """
        self.model.load_frames(idx=idx)   
        self.next_frame()

    def restart(self) :
        """
            Restart all the main variable such as the indexes and the pairing
        """
        self.model.current_frame = 0
        self.model.frame1 = 0
        self.model.frame2 = 0
        self.model.pause1 = False
        self.model.pause2 = False
        self.model.pairs = []
        self.view.button_pause1.configure(text="Pause")
        self.view.button_pause2.configure(text="Pause")
        self.next_frame()

    def pause_video(self, idx) :
        """
            For the selected video, change the button and the pausing status to its opposite
        """
        if idx == 0 :
            self.model.pause1 = not self.model.pause1
            if self.model.pause1 : 
                self.view.button_pause1.configure(text="Play")
            else :
                self.view.button_pause1.configure(text="Pause")
        elif idx == 1 :
            self.model.pause2 = not self.model.pause2
            if self.model.pause2 : 
                self.view.button_pause2.configure(text="Play")
            else :
                self.view.button_pause2.configure(text="Pause")

    def next_frame(self, *args) :
        """
            Show the next frame of the video
        """
        self.model.current_frame += 1
        # if not paused
        if not self.model.pause1 :
            self.model.frame1 += 1
        self.model.frame1 = self.model.frame1 % self.model.length
        if self.model.frame1 >= self.model.length1 :
            self.model.frame1 = self.model.length1 - 1
        # if not paused
        if not self.model.pause2 :
            self.model.frame2 += 1
        self.model.frame2 = self.model.frame2 % self.model.length
        if self.model.frame2 >= self.model.length2 :
            self.model.frame2 = self.model.length2 - 1
        # add the frame of each videos or replace if the time has already happened
        if self.model.current_frame <= len(self.model.pairs) :
            # aldready happened
            self.model.pairs[self.model.current_frame-1] = [self.model.frame1-1, self.model.pause1, self.model.frame2-1, self.model.pause2]
        else :
            self.model.pairs.append([self.model.frame1-1, self.model.pause1, self.model.frame2-1, self.model.pause2])
        # show img1 and img2
        try :
            frame1 = self.model.video1[self.model.frame1]
        except :
            frame1 = None
        try :
            frame2 = self.model.video2[self.model.frame2]
        except :
            frame2 = None
        self.view.show_img(frame1, frame2)
        # frame idx
        self.view.frame_count.config(text="{}".format(self.model.current_frame+1))
        self.view.frame_count1.config(text="{}/{}".format(self.model.frame1+1,self.model.length1))
        self.view.frame_count2.config(text="{}/{}".format(self.model.frame2+1,self.model.length2))

    def previous_frame(self, *args) :
        """
            Show the previous frame of the video
        """
        self.model.current_frame -= 1
        self.model.current_frame = max(0, self.model.current_frame)
        # if not paused
        if not self.model.pause1 :
            self.model.frame1 -= 1
        self.model.frame1 = self.model.frame1 % self.model.length1
        # id not paused
        if not self.model.pause2 :
            self.model.frame2 -= 1
        self.model.frame2 = self.model.frame2 % self.model.length2
        # show img1 and img2
        try :
            frame1 = self.model.video1[self.model.frame1]
        except :
            frame1 = None
        try :
            frame2 = self.model.video2[self.model.frame2]
        except :
            frame2 = None
        # add the frame of each videos or replace if the time has already happened
        if self.model.current_frame <= len(self.model.pairs) :
            # aldready happened
            self.model.pairs[self.model.current_frame-1] = [self.model.frame1-1, self.model.pause1, self.model.frame2-1, self.model.pause2]
        else :
            self.model.pairs.append([self.model.frame1-1, self.model.pause1, self.model.frame2-1, self.model.pause2])
        self.view.show_img(frame1, frame2)
        # frame idx
        self.view.frame_count.config(text="{}".format(self.model.current_frame+1))
        self.view.frame_count1.config(text="{}/{}".format(self.model.frame1+1,self.model.length1))
        self.view.frame_count2.config(text="{}/{}".format(self.model.frame2+1,self.model.length2))
        
    def show_frames(self) :
        """
            With cv2, show the video with the current 'model.pairs' status
        """
        self.model.show_frames()

    def create_video(self) :
        """
            With the two videos, create a video similar to the one whown with 'show_frames'
            However, both videos must be loaded
        """    
        video_name = self.view.video_name_entry.get().split(".")[0]
        self.model.create_video(video_name)

    def start(self) :
        """
            Start the program main loop
        """
        # set up the view
        self.view.setUp(self)
        # launch it
        self.view.start_main_loop()
