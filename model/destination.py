from model.inquiry_info import InquiryInfo
import sys
import logging


class Destination:

    def __init__(self, d_id, inquiry_info):
        self.d_id = d_id
        if not isinstance(inquiry_info, InquiryInfo):
            logging.error("Destination init need right InquiryInfo")
            sys.exit(1)
        self.inquiry_info = inquiry_info
        self.position = inquiry_info.inquiry_destination_position_by_id(d_id)

    def get_position(self):
        return self.position

    def get_distance(self, place):
        return self.inquiry_info.inquiry_distance(self, place)
