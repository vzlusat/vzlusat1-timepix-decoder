import numpy as np
from src.Segment import *

def plotSegment(segment_buffer, segment, color, width):

    new_segment = SegmentForPrint(segment, color, width)

    segment_buffer.append(new_segment)
