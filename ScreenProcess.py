from PIL import Image, ImageGrab
import cv2 as cv
import numpy as np
import os
import time
import mss
from vpkeys import *


def get_monitor_size():
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize


class ScreenProcess:
    def __init__(self) -> None:
        width, height = get_monitor_size()
        self.region = (0, 0, width, height)
    
    def _click(self, x, y):
        if(x == None or y == None):
            return
        click((x,y))
    
    def is_found(self, region, picturePath):
        picture = cv.imread(picturePath)
        img = ImageGrab.grab(bbox=region)
        img_cv = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
        result = cv.matchTemplate(img_cv, picture, cv.TM_CCOEFF_NORMED)
        return (result >= 0.8).any()
    
    def find(self, region, picturePath):
        picture = cv.imread(picturePath)
        img = ImageGrab.grab(bbox=region)
        img_cv = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
        result = cv.matchTemplate(img_cv, picture, cv.TM_CCOEFF_NORMED)
        loc = np.where(result >= 0.8)
        if(loc[0].size == 0):
            return None
        return list(zip(*loc[::-1]))[0]


    def match_all(image, template, threshold=0.8, debug=False, color=(0, 0, 255)):
        picture1 = cv.imread("aries.png")
        picture1.imshow()
        img_cv1 = cv.cvtColor(np.array(picture1), cv.COLOR_RGB2BGR)

        picture = cv.imread("taskbar.png")
        img_cv = cv.cvtColor(np.array(picture), cv.COLOR_RGB2BGR)

        """ Match all template occurrences which have a higher likelihood than the threshold """
        width, height = picture1.shape[:2]
        match_probability = cv.matchTemplate(img_cv, img_cv1, cv.TM_CCOEFF_NORMED)
        
        match_locations = np.where(match_probability >= threshold)

        # Add the match rectangle to the screen
        locations = []
        for x, y in zip(*match_locations[::-1]):
            locations.append(((x, x + width), (y, y + height)))

            if debug:
                cv.rectangle(image, (x, y), (x + width, y + height), color, 1)
        return locations

    def screenshot(self, delay=1):
        monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
        try:
            return np.array(mss.mss().grab(monitor))
        except mss.exception.ScreenShotError:
            print(f'\n[!] Error while taking screenshot, retrying in {delay} second'
                  + ('s' if delay != 1 else ''))
            time.sleep(delay)