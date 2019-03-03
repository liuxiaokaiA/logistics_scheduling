# coding: utf-8
from model.trunk import Trunk


def update(day):
    pass


def comput(day):
    pass


def output(day):
    pass


if __name__ == "main":
    days = 100
    from model.base_station import BaseStation
    from model.destination import Destination
    from model.inquiry_info import InquiryInfo

    inquriry_info = InquiryInfo()
    list_base = []
    list_destination = []
    list_trunk = []
    baseNum = 40
    destination_num = 2000
    trunk_num = 2400
    for base_index in range(baseNum):
        temp_base = BaseStation(base_index, inquriry_info)
        list_base.append(temp_base)

    for destination_index in range(destination_num):
        temp_destination = Destination(destination_index, inquriry_info)
        list_destination.append(temp_destination)

    for trunk_index in range(trunk_num):
        temp_trunk = Trunk(trunk_index, inquriry_info)

    for day in range(days):
        update(day)
        comput(day)
        output(day)
