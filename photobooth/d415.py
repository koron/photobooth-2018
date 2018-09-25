import pyrealsense2 as rs
import numpy as np

from .capture import Capture 

class D415:

    def __init__(self, csize=(1920, 1080), dsize=(1280, 720)):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, csize[0], csize[1], rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, dsize[0], dsize[1], rs.format.z16, 30)
        self.profile = self.pipeline.start(config)
        self.depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_scale = self.depth_sensor.get_depth_scale()
        self.align = rs.align(rs.stream.color)
        self.colorizer = None

    def enable_colorize(self, enable):
        if enable:
            c = rs.colorizer()
            c.set_option(rs.option.color_scheme, 2)
            self.colorizer = c
        else:
            self.colorizer = None

    def close(self):
        self.pipeline.stop()

    def capture(self):
        frames = self.align.process(self.pipeline.wait_for_frames())
        cframe = frames.get_color_frame()
        dframe = frames.get_depth_frame()
        if not cframe or not dframe:
            return None
        color = np.asanyarray(cframe.get_data())
        depth = np.asanyarray(dframe.get_data())
        colorDepth = None
        if self.colorizer is not None:
            cdframe = self.colorizer.colorize(dframe)
            colorDepth = np.asanyarray(cdframe.get_data())
        return Capture(color, depth, self.depth_scale, colorDepth)
