from rgbxy import Converter
from phue import Bridge
import json, math
import numpy as np

converter = Converter()

class Utils:
    # Writing to json file
    def write_json(self, file, data):
        with open(file, "w") as f:
            json.dump(data, f)
            return

    # Convert text to include color for terminal output
    def color_back(self, text, red, green, blue):
        RESET = '\033[0m'
        ATTR = { 'bold' : '\033[1m', 'underline' : '\033[4m', 'strike' : '\033[9m'}
        background = '\033[48;2;{r};{g};{b}m'.format(r=red, g=green, b=blue)
        text = background + text + RESET
        return text

    # Convert RGB to XY
    def rgb_to_xy(self, r, g, b):
        return converter.rgb_to_xy(r, g, b)

    # Update lights using HUE API
    def update_light(self, light, colors):
        try:
            # By default chose the most dominant color
            display_color = colors[0]
            print_color = self.color_back(f"CURRENT COLOR 0", display_color[0], display_color[1], display_color[2])
            print(print_color)
            # Convert RGB color code to XY
            xy = self.rgb_to_xy(display_color[0], display_color[1], display_color[2])
            # Update color of lights  if light is on
            if light.on == True:
                light.brightness = 254
                light.xy = xy
            return
        except Exception as e:
            print(f"Error updating light: {e}")
