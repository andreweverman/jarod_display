from cgitb import text
from ctypes.wintypes import RGB
from hmac import new
from types import new_class
import urllib3
from samplebase import SampleBase
# from RGBMatrixEmulator import graphics
from font import Font
from rpi.bindings.python.rgbmatrix import graphics
import time
import json
import numpy as np
import time
import board
import adafruit_tsl2591
import logging
from pixel import AnimationPixel, Point

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


i2c = None
sensor = None

try:
    i2c = board.I2C()
    sensor = adafruit_tsl2591.TSL2591(i2c)
except Exception as e:
    logger.error(e)

ROBLOX_URL = "https://games.roblox.com/v1/games?universeIds="
http = urllib3.PoolManager()

AXE_SHAFT = (139, 69, 19)
AXE_TIP = (128, 128, 128)
PLAYER = (211, 211, 211)
# gray rgb
GUN = (128, 128, 128)
NIGHT_COLOR = graphics.Color(0, 0, 139)
DAY_COLOR = graphics.Color(0, 0, 139)

ACTIVE = 'active'
VISITS = 'visits'

REFRESH_SECONDS = 5
ANIMATION_TIME = 3
LIGHT_CAPTURE_TIME = 10

MAX_SENSOR_BRIGHTNESS = 2000000
NIGHT_LIGHT = 20000

MAX_DISPLAY_BRIGHTNESS = 70
MIN_DISPLAY_BRIGHTNESS = 2


CAVERNCRAWLERS = {
    'name': 'Cavern Crawlers',
    'id': 4674537620,
}
BATTLEBLOX = {
    'name': 'BattleBlox',
    'id': 5224035285
}


class ScoreboardGame(SampleBase):

    def __init__(self, count_type, game, *args, **kwargs):
        super(ScoreboardGame, self).__init__(*args, **kwargs)
        self.array = self.initialize_light_array(0)
        self.count_type = count_type
        self.roblox_url = ROBLOX_URL + str(game.get('id'))
        self.p_num_players = 0
        self.num_players = 0
        self.get_count()
        self.animating = True
        self.frame = True
        self.moon = False
        self.font = graphics.Font()
        self.font.LoadFont("./rpi/fonts/6x10.bdf")

    def smooth_light_data(self):
        l = self.array
        if np.any(l):
            smoothed = l[(l > np.quantile(l, 0.05)) & (
                l < np.quantile(l, 0.95))].tolist()
            if np.any(smoothed):
                return np.mean(smoothed)
            return np.mean(l)
        return MAX_SENSOR_BRIGHTNESS

    def initialize_light_array(self, size):
        self.array = np.zeros((int(size),))

    def add_light_reading_to_array(self, num):
        self.array[num] = self.get_light_reading()

    def get_brightness(self):
        brightness = self.smooth_light_data()
        calculated_brightness = brightness / \
            MAX_SENSOR_BRIGHTNESS * MAX_DISPLAY_BRIGHTNESS
        logger.debug("Brightness: " + str(brightness))
        logger.debug("Brightness Percent: " + str(calculated_brightness))
        if brightness < NIGHT_LIGHT:
            self.moon = True
            return MIN_DISPLAY_BRIGHTNESS
        else:
            self.moon = False
            return min(max(MIN_DISPLAY_BRIGHTNESS, calculated_brightness), MAX_DISPLAY_BRIGHTNESS)

    def get_light_reading(self):
        i = MAX_SENSOR_BRIGHTNESS
        try:
            if sensor:
                i = sensor.visible
        except Exception as e:
            print(e)

        return i

    def get_moon_pixels(self, x, y):
        moon = [
            {'x': x, 'y': y, 'part': 'bg'},
            {'x': x, 'y': y+1, 'part': 'bg'},
            {'x': x, 'y': y+2, 'part': 'bg'},
            {'x': x, 'y': y+3, 'part': 'fg'},
            {'x': x, 'y': y+4, 'part': 'bg'},
            {'x': x, 'y': y+5, 'part': 'bg'},
            {'x': x-1, 'y': y, 'part': 'bg'},
            {'x': x-1, 'y': y+1, 'part': 'bg'},
            {'x': x-1, 'y': y+2, 'part': 'bg'},
            {'x': x-1, 'y': y+3, 'part': 'bg'},
            {'x': x-1, 'y': y+4, 'part': 'bg'},
            {'x': x-2, 'y': y, 'part': 'bg'},
            {'x': x-2, 'y': y+1, 'part': 'fg'},
            {'x': x-2, 'y': y+2, 'part': 'bg'},
            {'x': x-2, 'y': y+3, 'part': 'bg'},
            {'x': x-2, 'y': y+4, 'part': 'bg'},
            {'x': x-3, 'y': y, 'part': 'bg'},
            {'x': x-3, 'y': y+1, 'part': 'bg'},
            {'x': x-3, 'y': y+2, 'part': 'bg'},
            {'x': x-3, 'y': y+3, 'part': 'bg'},
            {'x': x-4, 'y': y, 'part': 'bg'},
            {'x': x-4, 'y': y+1, 'part': 'bg'},
            {'x': x-4, 'y': y+2, 'part': 'bg'},
            {'x': x-5, 'y': y, 'part': 'bg'},
            {'x': x-5, 'y': y+1, 'part': 'bg'},
        ]

        for pixel in moon:
            if pixel.get('part') == 'bg':
                pixel['r'] = 119
                pixel['g'] = 146
                pixel['b'] = 153
            elif pixel.get('part') == 'fg':
                pixel['r'] = 32
                pixel['g'] = 32
                pixel['b'] = 32

        return moon

    def get_active_players(self, response):
        return response.json().get('data')[0].get('playing')

    def get_visits(self, response):
        return response.json().get('data')[0].get('visits')

    def get_count(self):

        self.p_num_players = self.num_players
        num_players = '?'
        try:
            response = http.request('GET', self.roblox_url)
            if self.count_type == ACTIVE:
                num_players = self.get_active_players(response)
            elif self.count_type == VISITS:
                num_players = self.get_visits(response)
        except Exception:
            return num_players
        if isinstance(num_players, str) or isinstance(num_players, int) and num_players > self.num_players:
            self.animating = True
        self.num_players = num_players
        return num_players

    def get_text_color(self):
        return NIGHT_COLOR if self.moon else DAY_COLOR


class CavernCrawler(ScoreboardGame):

    def get_miner_pixels(self, x, y, percent_done):
        if percent_done < .3 or percent_done > .7:
            axe = [
                # hand
                {'x': x+1, 'y': y+8, 'part': 'player'},
                {'x': x, 'y': y+8,   'part': 'player'},
                # shaft
                {'x': x-1, 'y': y+7, 'part': 'shaft'},
                {'x': x-2, 'y': y+6, 'part': 'shaft'},
                {'x': x-3, 'y': y+5, 'part': 'shaft'},
                {'x': x-4, 'y': y+4, 'part': 'shaft'},
                # axe tip
                {'x': x-2, 'y': y+3, 'part': 'tip'},
                {'x': x-3, 'y': y+3, 'part': 'tip'},
                {'x': x-5, 'y': y+5, 'part': 'tip'},
                {'x': x-5, 'y': y+6, 'part': 'tip'},
            ]
        else:
            axe = [
                # hand
                {'x': x+1, 'y': y+8, 'part': 'player'},
                {'x': x, 'y': y+8,   'part': 'player'},
                # shaft
                {'x': x-1, 'y': y+7, 'part': 'shaft'},
                {'x': x-1, 'y': y+6, 'part': 'shaft'},
                {'x': x-2, 'y': y+5, 'part': 'shaft'},
                {'x': x-2, 'y': y+4, 'part': 'shaft'},
                {'x': x-3, 'y': y+3, 'part': 'shaft'},
                # axe tip
                {'x': x-1, 'y': y+2, 'part': 'tip'},
                {'x': x-2, 'y': y+2, 'part': 'tip'},
                {'x': x-4, 'y': y+5, 'part': 'tip'},
                {'x': x-4, 'y': y+4, 'part': 'tip'},
            ]

        miner_pixels = [
            {'x': x, 'y': y, 'part': 'player'},
            {'x': x+1, 'y': y, 'part': 'player'},
            {'x': x+2, 'y': y, 'part': 'player'},
            {'x': x+3, 'y': y, 'part': 'player'},
            {'x': x+4, 'y': y, 'part': 'player'},
            {'x': x, 'y': y+1, 'part': 'player'},
            {'x': x, 'y': y+2, 'part': 'player'},
            {'x': x, 'y': y+3, 'part': 'player'},
            {'x': x, 'y': y+4, 'part': 'player'},
            {'x': x+1, 'y': y+4, 'part': 'player'},
            {'x': x+2, 'y': y+4, 'part': 'player'},
            {'x': x+3, 'y': y+4, 'part': 'player'},
            {'x': x+4, 'y': y+4, 'part': 'player'},
            {'x': x+4, 'y': y+3, 'part': 'player'},
            {'x': x+4, 'y': y+2, 'part': 'player'},
            {'x': x+4, 'y': y+1, 'part': 'player'},
            {'x': x+2, 'y': y+5, 'part': 'player'},
            {'x': x+2, 'y': y+6, 'part': 'player'},
            {'x': x+2, 'y': y+7, 'part': 'player'},
            {'x': x+2, 'y': y+8, 'part': 'player'},
            {'x': x+2, 'y': y+9, 'part': 'player'},
            {'x': x+2, 'y': y+10, 'part': 'player'},
            {'x': x+2, 'y': y+11, 'part': 'player'},
            {'x': x+2, 'y': y+12, 'part': 'player'},
            {'x': x+2, 'y': y+13, 'part': 'player'},
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

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        num_color = graphics.Color(0, 128, 0)
        pieces = [
            {'x': 4, 'y': 8, 'text': "Cavern"},
            {'x': 10, 'y': 16, 'text': "Crawlers"},
        ]

        margin = 10
        refresh_interval = 1
        animation_frames_needed = ANIMATION_TIME / refresh_interval
        animation_frame_count = 0
        refresh_count_needed = REFRESH_SECONDS / refresh_interval
        frame_count = 0
        light_count = 0
        light_count_needed = LIGHT_CAPTURE_TIME / refresh_interval
        self.initialize_light_array(light_count_needed)
        brightness = MAX_DISPLAY_BRIGHTNESS
        while True:
            offscreen_canvas.Clear()
            self.matrix.brightness = brightness
            # set brightness to 10
            for piece in pieces:
                graphics.DrawText(offscreen_canvas, self.font, piece.get(
                    'x'), piece.get('y'), self.get_text_color(), piece.get('text'))

            active_str = (format(self.num_players, ',d'))
            if self.moon:
                for pixel in self.get_moon_pixels(63, 0):
                    offscreen_canvas.SetPixel(pixel.get('x'), pixel.get('y'), pixel.get(
                        'r', 255), pixel.get('g', 255), pixel.get('b', 0))
            if self.animating:
                animation_percent = animation_frame_count / animation_frames_needed
                for pixel in self.get_miner_pixels(64-6, 17, animation_percent):
                    offscreen_canvas.SetPixel(pixel.get('x'), pixel.get('y'), pixel.get(
                        'r', 255), pixel.get('g', 255), pixel.get('b', 0))
                animation_frame_count += 1
                if animation_frame_count > animation_frames_needed:
                    self.animating = False
                    animation_frame_count = 0
                if animation_percent < .7:
                    active_str = (format(self.p_num_players, ',d'))

            str_offfset = len(active_str) * 6
            x_pos = self.matrix.width - margin - str_offfset
            graphics.DrawText(offscreen_canvas, self.font,
                              x_pos, 25, num_color, active_str)

            time.sleep(refresh_interval)
            # refreshing the data
            if frame_count > refresh_count_needed:
                frame_count = 0
                self.get_count()
            if light_count > light_count_needed:
                light_count = 0
                brightness = self.get_brightness()
                self.initialize_light_array(light_count_needed)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            if light_count < light_count_needed:
                self.add_light_reading_to_array(light_count)
            frame_count += 1
            light_count += 1


class BattleBlox(ScoreboardGame):

    def get_miner_pixels(self, x, y):

        gun = [
            # hand
            {'x': x+1, 'y': y+8, 'part': 'player'},
            {'x': x, 'y': y+8,   'part': 'player'},
            # shaft
            {'x': x-1, 'y': y+7, 'part': 'gun'},
            {'x': x-1, 'y': y+6, 'part': 'gun'},
            {'x': x-2, 'y': y+6, 'part': 'gun'},
            {'x': x-3, 'y': y+6, 'part': 'gun'},
        ]

        shooter_pixels = [
            {'x': x, 'y': y, 'part': 'player'},
            {'x': x+1, 'y': y, 'part': 'player'},
            {'x': x+2, 'y': y, 'part': 'player'},
            {'x': x+3, 'y': y, 'part': 'player'},
            {'x': x+4, 'y': y, 'part': 'player'},
            {'x': x, 'y': y+1, 'part': 'player'},
            {'x': x, 'y': y+2, 'part': 'player'},
            {'x': x, 'y': y+3, 'part': 'player'},
            {'x': x, 'y': y+4, 'part': 'player'},
            {'x': x+1, 'y': y+4, 'part': 'player'},
            {'x': x+2, 'y': y+4, 'part': 'player'},
            {'x': x+3, 'y': y+4, 'part': 'player'},
            {'x': x+4, 'y': y+4, 'part': 'player'},
            {'x': x+4, 'y': y+3, 'part': 'player'},
            {'x': x+4, 'y': y+2, 'part': 'player'},
            {'x': x+4, 'y': y+1, 'part': 'player'},
            {'x': x+2, 'y': y+5, 'part': 'player'},
            {'x': x+2, 'y': y+6, 'part': 'player'},
            {'x': x+2, 'y': y+7, 'part': 'player'},
            {'x': x+2, 'y': y+8, 'part': 'player'},
            {'x': x+2, 'y': y+9, 'part': 'player'},
            {'x': x+2, 'y': y+10, 'part': 'player'},
            {'x': x+2, 'y': y+11, 'part': 'player'},
            {'x': x+2, 'y': y+12, 'part': 'player'},
            {'x': x+2, 'y': y+13, 'part': 'player'},
        ]

        all_pixels = shooter_pixels + gun
        for pixel in all_pixels:
            if pixel.get('part') == 'gun':
                pixel['r'] = GUN[0]
                pixel['g'] = GUN[1]
                pixel['b'] = GUN[2]
            elif pixel.get('part') == 'player':
                pixel['r'] = PLAYER[0]
                pixel['g'] = PLAYER[1]
                pixel['b'] = PLAYER[2]
            else:
                pixel['r'] = 255
                pixel['g'] = 255
                pixel['b'] = 0
        return all_pixels

    def manhattan_distance(self, tup1, tup2):
        val =  abs(tup1[0] - tup2[0]) + abs(tup1[1] - tup2[1])
        if val == 1:
            return 1
        # check for diagonals
        return val
    
    def separete(self,data):
        """ Separates a list of coordinates into a list of list of coordinates by adjacency """

        # create a dict filled with Nones to make loooking up easier
        record = dict()
        sorted_data = sorted(data)
        for x, y in sorted_data:
            if x in record.keys():
                record[x][y] = None
            else:
                record[x] = dict()
                record[x][y] = None

        def in_record(x, y):
            """ returns true if x, y is in record """
            return x in record.keys() and y in record[x].keys()

        def find_adjacents(x, y):
            """ find adjacent cells (8 directions) """
            check = [((x - 1, y - 1), in_record(x - 1, y - 1)),
                    ((x + 1, y + 1), in_record(x + 1, y + 1)),
                    ((x - 1, y + 1), in_record(x - 1, y + 1)),
                    ((x + 1, y - 1), in_record(x + 1, y - 1)),
                    ((x - 1, y), in_record(x - 1, y)),
                    ((x + 1, y), in_record(x + 1, y)),
                    ((x, y - 1), in_record(x, y - 1)),
                    ((x, y - 1), in_record(x, y - 1))]

            result = []
            for coord, found in check:
                if found:
                    result.append(coord)
            return result

        def get_group(cells):
            """ Returns group id number of first of cells, or None """
            for x, y in cells:
                if record[x][y] is not None:
                    return record[x][y]
            return None


        # loop over each, assigning a group id
        group_id = 0
        for x, y in sorted_data:
            cells = find_adjacents(x, y)
            if len(cells) == 0:
                # no neighbors found, make a new group
                record[x][y] = group_id
                group_id += 1
            else:
                # found cells
                found_group = get_group(cells)
                if found_group is None:
                    # no neighbors have a group
                    # give this cell and all neighbors a new group
                    record[x][y] = group_id
                    for f_x, f_y in cells:
                        record[f_x][f_y] = group_id
                    group_id += 1
                else:
                    # found a neighbor in a group
                    # apply that group to this and all other neighbors
                    record[x][y] = found_group
                    for f_x, f_y in cells:
                        record[f_x][f_y] = found_group

        result = []
        for i in range(0, group_id):
            result.append([])
            for x, y_dict in record.items():
                for y, group in y_dict.items():
                    if group == i:
                        result[i].append( (x, y) )
        result = [r for r in result if len(r) != 0]
        return result
            
    def get_bitmap_of_text(self, text, x_offset, y_offset, dest: 'Point', reverse=False):
        linelimit = len(text) * (self.font.headers['fbbx'] + 1)
        self.text_map = self.bitmap_font.bdf_font.draw(
            text, linelimit, missing=self.bitmap_font.default_character).todata(2)
        # create new text map that accounts for x and y offset and is the total size of the matrix
        self.full_text_map = np.zeros((self.matrix.height, self.matrix.width))
        for y, row in enumerate(self.text_map):
            for x, value in enumerate(row):
                self.full_text_map[y_offset + y, x_offset + x] = value

        if reverse:
            '''
            dfs to find groups of pixels
            '''

            count_pixels = []
            for y, row in enumerate(self.full_text_map):
                for x, value in enumerate(row):
                    if value == 1:
                        if reverse:
                            count_pixels.append((x, y))
            # taking count_pixels and going to rearrange them by clumping using manhattan distance to group

            res = self.separete(count_pixels)

            # turn res into a list of AnimationPixels
            self.count_pixels = []
            for group in res:
                for x, y in group:
                    self.count_pixels.append(
                        AnimationPixel(dest._x, dest._y, Point(x, y)))
            pass

        else:
            self.count_pixels = []
            for y, row in enumerate(self.full_text_map):
                for x, value in enumerate(row):
                    if value == 1:
                        if not reverse:
                            self.count_pixels.append(
                                AnimationPixel(x, y, dest))

    def run(self):
        self.bitmap_font = Font()
        self.bitmap_font.LoadFont("./rpi/fonts/6x10.bdf")
        self.display_bm = None
        self.real_bm = None
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        num_color = graphics.Color(0, 128, 0)
        pieces = [
            {'x': 3, 'y': 8, 'text': "BattleBlox"},
        ]

        margin = 10
        self.refresh_interval = 1
        self.animation_phase = 'suck'
        animation_frames_needed = ANIMATION_TIME / self.refresh_interval
        animation_frame_count = 0
        refresh_count_needed = REFRESH_SECONDS / self.refresh_interval
        frame_count = 0
        light_count = 0
        light_count_needed = LIGHT_CAPTURE_TIME / self.refresh_interval
        self.initialize_light_array(light_count_needed)
        brightness = MAX_DISPLAY_BRIGHTNESS
        destination = Point(54, 23)
        while True:
            offscreen_canvas.Clear()
            self.matrix.brightness = brightness
            # set brightness to 10
            for piece in pieces:
                graphics.DrawText(offscreen_canvas, self.font, piece.get(
                    'x'), piece.get('y'), self.get_text_color(), piece.get('text'))

            active_str = (format(self.num_players, ',d'))
            if self.moon:
                for pixel in self.get_moon_pixels(63, 0):
                    offscreen_canvas.SetPixel(pixel.get('x'), pixel.get('y'), pixel.get(
                        'r', 255), pixel.get('g', 255), pixel.get('b', 0))

            str_offset = len(active_str) * 6
            x_pos = self.matrix.width - margin - str_offset

            if self.animating:
                font_y_offset = - \
                    (self.bitmap_font.headers['fbby'] +
                     self.bitmap_font.headers['fbbyoff'])

                for pixel in self.get_miner_pixels(64-6, 17):
                    offscreen_canvas.SetPixel(pixel.get('x'), pixel.get('y'), pixel.get(
                        'r', 255), pixel.get('g', 255), pixel.get('b', 0))

                if animation_frame_count == 0 and self.animation_phase == 'suck':
                    self.refresh_interval = .15
                    prev_count = format(self.p_num_players, ',d')
                    self.get_bitmap_of_text(
                        prev_count, x_pos, 25 + font_y_offset, destination)
                if self.animation_phase == 'suck':
                    if all(pixel.at_destination() for pixel in self.count_pixels):
                        self.animation_phase = 'shoot'
                        animation_frame_count = -1
                    else:
                        for pixel in self.count_pixels:
                            if not pixel.at_destination():
                                next_pixel = pixel.get_next_position()
                                offscreen_canvas.SetPixel(
                                    next_pixel._x, next_pixel._y, num_color.red, num_color.green, num_color.blue)
                elif self.animation_phase == 'shoot':

                    if animation_frame_count == 0:
                        self.refresh_interval = .01
                        self.get_bitmap_of_text(
                            active_str, x_pos, 25 + font_y_offset, destination, reverse=True)

                    if all(pixel.at_destination() for pixel in self.count_pixels):
                        self.animation_phase = 'done'
                    for pixel in self.count_pixels:
                        if not pixel.at_destination():
                            next_pixel = pixel.get_next_position()
                            offscreen_canvas.SetPixel(
                                next_pixel._x, next_pixel._y, num_color.red, num_color.green, num_color.blue)
                            break
                        else:
                            offscreen_canvas.SetPixel(
                                pixel.current_position._x, pixel.current_position._y, num_color.red, num_color.green, num_color.blue)

                animation_frame_count += 1
            else:
                graphics.DrawText(offscreen_canvas, self.font,
                                  x_pos, 25, num_color, active_str)

            time.sleep(self.refresh_interval)

            if self.animation_phase == 'done':
                self.refresh_interval = 1
                self.animating = False
                animation_frame_count = 0
                self.animation_phase = 'suck'
            # refreshing the data
            if frame_count > refresh_count_needed:
                frame_count = 0
                self.get_count()
            if light_count > light_count_needed:
                light_count = 0
                brightness = self.get_brightness()
                self.initialize_light_array(light_count_needed)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            if light_count < light_count_needed:
                self.add_light_reading_to_array(light_count)

            if not self.animating:
                frame_count += 1
                light_count += 1


def load_config():
    with open('config.json') as json_file:
        data = json.load(json_file)
        count_type = data.get('count_type')
        game = data.get('game', '')
        if count_type not in [ACTIVE, VISITS]:
            count_type = ACTIVE
        if game == CAVERNCRAWLERS['name']:
            game_nst = CavernCrawler(count_type, CAVERNCRAWLERS)
        else:
            game_nst = BattleBlox(count_type, BATTLEBLOX)
        return game_nst


# Main function
if __name__ == "__main__":
    game = load_config()
    if (not game.process()):
        game.print_help()
