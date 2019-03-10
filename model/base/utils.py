# coding: utf-8
"""
一些基本的工具函数
"""
import time

from global_data import distance_around, mode_start_time


def get_time_torday():
    pass


def is_near(position1, position2, distance):
    if position1.get_position_distance(position2) < distance:
        return True
    else:
        return False


def timestamp_to_date_time(timestamp):
    timeTuple = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeTuple)[:-3]


def data_time_to_timestamp(datetime):
    st = time.strptime(datetime, '%Y-%m-%d %H:%M:%S')
    return time.mktime(st)


def model_time_to_date_time(day, hour):
    timestamp = mode_start_time + day*24*3600+hour*3600
    return timestamp_to_date_time(timestamp)


if __name__ == '__main__':
    time_now = '2019-03-10 16:00:00'
    b = 1552204800.0 - 3 * 60 + 24 * 60 * 60
    print data_time_to_timestamp(time_now)
    print timestamp_to_date_time(b)
