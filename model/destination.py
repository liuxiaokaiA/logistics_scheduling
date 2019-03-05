from global_data import distance_around, destination_num
from model.inquiry_info import InquiryInfo
import sys
import logging

"""
@File    :   position_generate.py
@Contact :   liuhaobwjc@163.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019-03-01 14:10   liuhao      1.0         None
"""


class Destination:

    def __init__(self, d_id, inquiry_info):
        self.d_id = d_id
        if not isinstance(inquiry_info, InquiryInfo):
            logging.error("Destination init need right InquiryInfo")
            sys.exit(1)
        self.inquiry_info = inquiry_info
        self.position = inquiry_info.inquiry_destination_position_by_id(d_id)
        self.near_destination_list = []
        for i in range(destination_num):
            if (inquiry_info.inquiry_distance_by_id(d_id_1=d_id, d_id_2=i)) < distance_around and i != d_id:
                self.near_distance_list.append(i)

    def get_position(self):
        return self.position

    def get_distance(self, place):
        return self.inquiry_info.inquiry_distance(self, place)
