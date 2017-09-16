import numpy

class Image:

    def __init__(self, image_id, image_type):

        self.id = image_id
        self.type = image_type
    
        self.mode = 0
        self.threshold = 0
        self.bias = 0
        self.exposure = 0
        self.filtering = 0
        self.filtered_pixels = 0
        self.original_pixels = 0
        self.min_original = 0
        self.max_original = 0
        self.min_filtered = 0
        self.max_filtered = 0
        self.temperature = 0
        self.temp_limit = 0
        self.pxl_limit = 0
        self.uv1_thr = 0
        self.chunk_id = 0
        self.attitude = [0, 0, 0, 0, 0, 0, 0]
        self.position = [0, 0, 0]
        self.time = 0

        self.data = numpy.zeros(shape=[1, 1])

        self.got_data = 0
        self.got_metadata = 0

        self.favorite = 0
        self.hidden = 0

    def __eq__(self, other):

        if not isinstance(other, Image):
            return 0

        if self.got_metadata != other.got_metadata:
            return 0
        
        if not numpy.array_equal(self.data, other.data):
            return 0

        return 1

    metadata_labels=["Image number:",
                     "Image type:",
                     "Measurement mode:",
                     "Threshold:",
                     "Bias:",
                     "Exposure:",
                     "Filtering:",
                     "Pixel count (Original):",
                     "Pixel count (Filtered):",
                     "Minimal pixel value (Original):",
                     "Maximal pixel value (Original):",
                     "Minimal pixel value (Filtered):",
                     "Maximal pixel value (Filtered):",
                     "Temperature:",
                     "Temperature limit:",
                     "Pixel count threshold (Scanning mode):",
                     "UAV1 threshold (Adrenaline mode):",
                     "Attitude:",
                     "Position:",
                     "Time:",
                     "Chunk ID:",
                     "",
                     # "Mark as hidden:",
                     "Mark as favorite:"
                     ]
