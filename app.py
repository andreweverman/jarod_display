from ctypes.wintypes import RGB
import random
import arrow
from hmac import new
from types import new_class
import urllib3
from samplebase import SampleBase
# from RGBMatrixEmulator import graphics, RGBMatrix
from rpi.bindings.python.rgbmatrix import graphics, RGBMatrix
from random import Random
import time
import math
import json
import numpy as np
import time
import board
import adafruit_tsl2591


i2c = board.I2C()
sensor = adafruit_tsl2591.TSL2591(i2c)

ROBLOX_URL = "https://games.roblox.com/v1/games?universeIds=4674537620"
http = urllib3.PoolManager()

AXE_SHAFT = (139,69,19)
AXE_TIP = (128,128,128)
PLAYER = (211,211,211)

ACTIVE = 'active'
VISITS = 'visits'

REFRESH_SECONDS = 15
ANIMATION_TIME = 3
LIGHT_CAPTURE_TIME = 10

MAX_BRIGHTNESS = 2000000
NIGHT_LIGHT = 20000

MAX_DISPLAY_BRIGHTNESS = 75


class CavernCrawler(SampleBase):

    def smooth_light_data(self):
        l = self.array
        if np.any(l):
            print(l)
            smoothed = l[(l > np.quantile(l, 0.05)) & (l < np.quantile(l, 0.95))].tolist()
            if np.any(smoothed):
                return np.mean(smoothed)
            return np.mean(l)
        return MAX_BRIGHTNESS

    def initialize_light_array(self, size):
        self.array = np.zeros((int(size),))

    def add_light_reading_to_array(self, num):
        self.array[num] = self.get_light_reading()

    def get_brightness(self):
        brightness = self.smooth_light_data()
        if brightness < NIGHT_LIGHT:
            return 10
        else:   
            return min(max(30,brightness / MAX_BRIGHTNESS * MAX_DISPLAY_BRIGHTNESS),MAX_DISPLAY_BRIGHTNESS)


    def get_light_reading(self):
        try:
            if sensor: 
                i = sensor.visible
            else:
                i = MAX_BRIGHTNESS 
#            print('Visible: ' + str(i))
            return i
        except: 
            pass


    def load_config(self):
        with open('config.json') as json_file:
            data = json.load(json_file)
            self.count_type = data.get('count_type')
            if self.count_type not in [ACTIVE, VISITS]:
                self.count_type = ACTIVE
            

    def get_miner_pixels(self,x, y, percent_done):
        if percent_done < .3 or percent_done > .7:
            axe = [
            # hand
            { 'x': x+1, 'y': y+8, 'part': 'player'},
            { 'x': x, 'y': y+8,   'part': 'player'},
            # shaft
            { 'x': x-1, 'y': y+7, 'part': 'shaft'},
            { 'x': x-2, 'y': y+6, 'part': 'shaft'},
            { 'x': x-3, 'y': y+5, 'part': 'shaft'},
            { 'x': x-4, 'y': y+4, 'part': 'shaft'},
            # axe tip
            { 'x': x-2, 'y': y+3, 'part': 'tip'},
            { 'x': x-3, 'y': y+3, 'part': 'tip'},
            { 'x': x-5, 'y': y+5, 'part': 'tip'},
            { 'x': x-5, 'y': y+6, 'part': 'tip'},
            ]
        else:
          axe = [
            # hand
            { 'x': x+1, 'y': y+8, 'part': 'player'},
            { 'x': x, 'y': y+8,   'part': 'player'},
            # shaft
            { 'x': x-1, 'y': y+7, 'part': 'shaft'},
            { 'x': x-1, 'y': y+6, 'part': 'shaft'},
            { 'x': x-2, 'y': y+5, 'part': 'shaft'},
            { 'x': x-2, 'y': y+4, 'part': 'shaft'},
            { 'x': x-3, 'y': y+3, 'part': 'shaft'},
            # axe tip
            { 'x': x-1, 'y': y+2, 'part': 'tip'},
            { 'x': x-2, 'y': y+2, 'part': 'tip'},
            { 'x': x-4, 'y': y+5, 'part': 'tip'},
            { 'x': x-4, 'y': y+4, 'part': 'tip'},
           ]

        miner_pixels = [
        { 'x': x, 'y': y, 'part': 'player' },
        { 'x': x+1, 'y': y, 'part': 'player' },
        { 'x': x+2, 'y': y, 'part': 'player' },
        { 'x': x+3, 'y': y, 'part': 'player' },
        { 'x': x+4, 'y': y, 'part': 'player' },
        { 'x': x, 'y': y+1, 'part': 'player' },
        { 'x': x, 'y': y+2, 'part': 'player' },
        { 'x': x, 'y': y+3, 'part': 'player' },
        { 'x': x, 'y': y+4, 'part': 'player' },
        { 'x': x+1, 'y': y+4, 'part': 'player' },
        { 'x': x+2, 'y': y+4, 'part': 'player' },
        { 'x': x+3, 'y': y+4, 'part': 'player' },
        { 'x': x+4, 'y': y+4, 'part': 'player' },
        { 'x': x+4, 'y': y+3, 'part': 'player' },
        { 'x': x+4, 'y': y+2, 'part': 'player' },
        { 'x': x+4, 'y': y+1, 'part': 'player' },
        { 'x': x+2, 'y': y+5, 'part': 'player' },
        { 'x': x+2, 'y': y+6, 'part': 'player' },
        { 'x': x+2, 'y': y+7, 'part': 'player' },
        { 'x': x+2, 'y': y+8, 'part': 'player' },
        { 'x': x+2, 'y': y+9, 'part': 'player' },
        { 'x': x+2, 'y': y+10, 'part': 'player' },
        { 'x': x+2, 'y': y+11, 'part': 'player' },
        { 'x': x+2, 'y': y+12, 'part': 'player' },
        { 'x': x+2, 'y': y+13, 'part': 'player' },
          ]

        all_pixels = miner_pixels + axe
        for pixel in all_pixels:
            if pixel.get('part') == 'shaft':
                pixel['r'] = AXE_SHAFT[0]
                pixel['g'] = AXE_SHAFT[1]
                pixel['b'] = AXE_SHAFT[2]
            elif pixel.get('part') == 'tip':
                pixel['r'] = AXE_TIP[0]
                pixel['g'] = AXE_TIP[1]
                pixel['b'] = AXE_TIP[2]
            elif pixel.get('part') == 'player':
                pixel['r'] = PLAYER[0]
                pixel['g'] = PLAYER[1]
                pixel['b'] = PLAYER[2]
            else:
                pixel['r'] = 255
                pixel['g'] = 255
                pixel['b'] = 0
        return all_pixels


    def get_active_players(self, response):
        return response.json().get('data')[0].get('playing')

    def get_visits(self, response):
        return response.json().get('data')[0].get('visits')


    def get_count(self):

        self.p_num_players = self.num_players
        response = http.request('GET', ROBLOX_URL)
        num_players = '?'
        try:
            # num_players = self.p_num_players + 1
            if self.count_type == ACTIVE:
                num_players = self.get_active_players(response)
            elif self.count_type == VISITS:
                num_players = self.get_visits(response)
        except Exception:
            pass
        if num_players > self.num_players:
            self.animating = True
        self.num_players = num_players
        return num_players

       

    def __init__(self, *args, **kwargs):
        super(CavernCrawler, self).__init__(*args, **kwargs)
        self.array = self.initialize_light_array(0)
        self.load_config()
        self.p_num_players = 0
        self.num_players = 0
        self.get_count()
        self.animating = True
        self.frame = True

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("./rpi/fonts/6x10.bdf")
        textColor = graphics.Color(255, 255, 0)
        numColor = graphics.Color(0, 128, 0)
        pos = offscreen_canvas.width
        pieces = [
            {'x': 4, 'y': 8, 'text':"Cavern"},
            {'x': 10, 'y': 16, 'text':"Crawlers"},
        ]
        # TODO: reduce brightness at night
        # TODO: put a moon up in the corner at night


        margin = 10
        refresh_interval = .2
        animation_frames_needed = ANIMATION_TIME / refresh_interval
        animation_frame_count = 0
        refresh_count_needed = REFRESH_SECONDS / refresh_interval
        frame_count = 0
        light_count = 0
        light_count_needed = LIGHT_CAPTURE_TIME / refresh_interval
        self.initialize_light_array(light_count_needed)
        brightness = 50
        while True:
            offscreen_canvas.Clear()
            self.matrix.brightness = brightness
            # set brightness to 10
            for piece in pieces:
                graphics.DrawText(offscreen_canvas, font, piece.get('x'), piece.get('y'), textColor, piece.get('text'))

          
            active_str = (format (self.num_players, ',d'))
            if self.animating:
                animation_percent = animation_frame_count/ animation_frames_needed 
                for pixel in self.get_miner_pixels(64-6,17,animation_percent):
                    offscreen_canvas.SetPixel(pixel.get('x'),pixel.get('y'),pixel.get('r', 255),pixel.get('g', 255),pixel.get('b', 0))
                animation_frame_count += 1
                if  animation_frame_count> animation_frames_needed:
                    self.animating = False
                    animation_frame_count = 0
                if animation_percent < .7:
                    active_str = (format (self.p_num_players, ',d'))

            str_offfset = len(active_str) * 6
            x_pos = self.matrix.width - margin - str_offfset
            graphics.DrawText(offscreen_canvas, font, x_pos, 25, numColor,active_str )

            time.sleep(refresh_interval)
            # refreshing the data
            if frame_count> refresh_count_needed:
                frame_count = 0
                self.get_count()
            if light_count > light_count_needed:
                light_count = 0
                brightness = self.get_brightness()
                self.options.brightness = int(brightness)
                self.matrix = RGBMatrix(options = self.options)
                print(brightness)
                self.initialize_light_array(light_count_needed)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            if light_count < light_count_needed:
                self.add_light_reading_to_array(light_count)
            frame_count += 1
            light_count += 1
      


# Main function
if __name__ == "__main__":
    cavern_crawler = CavernCrawler()
    if (not cavern_crawler.process()):
        cavern_crawler.print_help()

