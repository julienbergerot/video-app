import cv2
import numpy as np
import os
from decord import VideoReader
from decord import cpu, gpu

from tkinter import filedialog as fd
from tqdm import tqdm

def get_frames(video_path, end=True) :
    """
        Return a list of the frames (as NDArray from Mxnet)
        Decord is very fast comapred to cv2
    """
    # get fps
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)

    # base fps is 30
    vr = VideoReader(video_path, ctx=cpu(0))
    frames = []
    for i in tqdm(range(0, len(vr), int((fps+1)//30))) :
        image = vr[i].asnumpy()
        if end :
            image = cv2.resize(image, (min(int(400*image.shape[1] / image.shape[0]),540), 400))
        frames.append(image)

    return frames

class Model :
    def __init__(self) :
        # current idx of the final video
        self.current_frame = 0
        # actually useless
        self.length = 1
        # frames of video 1
        self.video1 = []
        # frames of video 2
        self.video2 = []
        # length of first video
        self.length1 = 1
        #length of second video
        self.length2 = 1
        # current idx of the video 1
        self.frame1 = 0
        # current idx of the video 2
        self.frame2 = 0
        # is video 1 paused ?
        self.pause1 = False
        # is video 2 paused ?
        self.pause2 = False
        # pairs of idx for the final video
        self.pairs = []
    
    def show_frames(self) :
        # loop throught all the pairs
        for frame1, pause1, frame2, pause2 in self.pairs :
            # Load the image
            ori_size = (1920,1080)
            # we put a try in case there is only video 1 or video 2
            try :
                image1 = self.video1[frame1]
                if pause1 :
                    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            except :
                image1 = np.zeros((10,10,3))
                image1 = cv2.resize(image1, (min(int(400*ori_size[1] / ori_size[0]),540), 400))
            try :
                image2 = self.video2[frame2]
                if pause2 :
                    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            except :
                image2 = np.zeros((10,10,3))
                image2 = cv2.resize(image2, (min(int(400*ori_size[1] / ori_size[0]),540), 400))
            
            # concat horiz
            image_total = np.ones((image1.shape[0]+20, image1.shape[1]*2+30,3)) * 255
            # try except : color vs gray
            try :
                image_total[10:-10, 10:image1.shape[1]+10] = image1
            except :
                image_total[10:-10, 10:image1.shape[1]+10, 0] = image1
                image_total[10:-10, 10:image1.shape[1]+10, 1] = image1
                image_total[10:-10, 10:image1.shape[1]+10, 2] = image1
            try :
                image_total[10:-10, image1.shape[1]+20:-10] = image2
            except :
                image_total[10:-10, image1.shape[1]+20:-10, 0] = image2
                image_total[10:-10, image1.shape[1]+20:-10, 1] = image2
                image_total[10:-10, image1.shape[1]+20:-10, 2] = image2

            # uint8 for display
            image_total = image_total.astype(np.uint8)
            # RGB
            image_total = cv2.cvtColor(image_total, cv2.COLOR_BGR2RGB)
            # show
            cv2.imshow("video test", image_total)
            # you can interrupt it with the key 'q'
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    def create_video(self, video_name) :
        # load the videos again (not to have the resize factor)
        try :
            frames1 = get_frames(self.video_path1, end=False)
            frames2 = get_frames(self.video_path2, end=False)
        except :
            print("Error, couldn't process")
            return
        # final size to resize (in case they are not the same)
        all_frames = []
        image_size = (frames1[0].shape[0], frames1[0].shape[1])
        for frame1, pause1, frame2, pause2 in tqdm(self.pairs) :
            # load the images
            frame1 = frames1[frame1]
            frame2 = frames2[frame2]
            # resize
            frame1 = cv2.resize(frame1, image_size[::-1], interpolation=cv2.INTER_CUBIC)
            frame2 = cv2.resize(frame2, image_size[::-1], interpolation=cv2.INTER_CUBIC)
            # gray if paused
            if pause1 :
                frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                frame1 = cv2.merge((frame1,frame1,frame1))
            if pause2 :
                frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                frame2 = cv2.merge((frame2,frame2,frame2))
            # total image
            image_total = np.ones((frame1.shape[0]+20, frame1.shape[1]*2+30,3)) * 255
            # image 1 in the left
            image_total[10:-10, 10:frame1.shape[1]+10] = frame1
            # image 2 in the right
            image_total[10:-10, frame1.shape[1]+20:-10] = frame2
            # npuint8
            image_total = image_total.astype(np.uint8)
            # RGB
            image_total = cv2.cvtColor(image_total, cv2.COLOR_BGR2RGB)
            # resize, so we can then still have the phone format (16/9)
            image_total = cv2.resize(image_total, (1080, 1000), interpolation=cv2.INTER_CUBIC)
            # phone format for this image
            image_final = np.ones((1920,1080,3), dtype=np.uint8)*255
            # put it in the middle
            image_final[460:460+1000,:,:] = image_total            
            all_frames.append(image_final)
        
        # with open cv, write the video : format mov or mp4!
        final_size = image_final.shape[:2][::-1]
        if not os.path.exists("videos") :
            os.mkdir("videos")
        # the name if set as a global variable
        out = cv2.VideoWriter(os.path.join("videos", video_name+".mov"),cv2.VideoWriter_fourcc(*'MP4V'), 30, final_size)
        for frame in tqdm(all_frames) :
            out.write(frame)
        out.release()

    def load_frames(self, idx=0) :
        """
            Load the frames of the current video
            Result of when someone opens a file
        """
        # accept all : If there are errors, it's on you
        filetypes = (
            ('All files', '*.*'),
        )
        # for the file visual
        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)
        # retrieve the frames
        frames = get_frames(filename)
        # restart the idx
        self.current_frame = 0
        self.frame1 = 0
        self.frame2 = 0
        # video 1
        if idx == 0 :
            self.video_path1 = filename
            self.video1 = frames
            self.length1 = len(self.video1)
        # video 2
        else : 
            self.video_path2 = filename
            self.video2 = frames
            self.length2 = len(self.video2)
        # restart the pairing
        self.pairs = []
        # useless
        self.length = max(len(self.video1), len(self.video2))
        
  