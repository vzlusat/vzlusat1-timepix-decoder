from src.Line import *

class SegmentForPrint:

    def __init__(self, segment, color, width):

        self.segment = segment
        self.color = color
        self.width = width

class Segment:

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.line = Line(x, y)
