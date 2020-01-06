class Results:

    def __init__(self, optics_segments_list, timepix_segments_list, optics_point_list, timepix_point_list, source_point_list, reflected_rays_segment_list, direct_rays_segment_list, columns):

        self.optics_segments_list = optics_segments_list
        self.timepix_segments_list = timepix_segments_list
        self.optics_point_list = optics_point_list
        self.timepix_point_list = timepix_point_list
        self.source_point_list = source_point_list
        self.reflected_rays_segment_list = reflected_rays_segment_list
        self.direct_rays_segment_list = direct_rays_segment_list
        self.columns = columns
