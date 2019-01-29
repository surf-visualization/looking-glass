import json
from math import cos, atan

class Calibration:
    
    def __init__(self, jsonfile):

        config = json.loads(open(jsonfile, 'rt').read())

        self.screenW = int(config['screenW']['value'])
        self.screenH = int(config['screenH']['value'])
        self.DPI = int(config['DPI']['value'])
        self.pitch = config['pitch']['value']
        self.slope = config['slope']['value']
        self.center = config['center']['value']

        # Physical image width
        self.screenInches = self.screenW / self.DPI

        self.pitch = self.pitch * self.screenInches * cos(atan(1.0/self.slope))
        self.tilt = self.screenH/(self.screenW * self.slope)
        self.subp = 1.0 / (3*self.screenW) * self.pitch