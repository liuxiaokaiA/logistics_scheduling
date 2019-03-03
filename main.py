# coding: utf-8
from log import MyLogging
from read_configure import read_fuc
from algorithm.ga import update_global
from model.trunk import trunk_init
from model.base_station import base_init


def update(day):
    pass


def comput(day):
    pass


def output(day):
    pass


def init():
    base_init()
    trunk_init()


if __name__ == "main":
    MyLogging()
    default_conf = read_fuc('conf/default.conf')
    update_global(default_conf)

    init()
    days = 100
    for day in range(days):
        update(day)
        comput(day)
        output(day)
