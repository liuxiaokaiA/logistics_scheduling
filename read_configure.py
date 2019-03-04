import logging
import configparser


log = logging.getLogger('default')


def read_fuc(conf_path):
    conf = configparser.ConfigParser()
    try:
        conf.read(conf_path+'default.conf')
    except IOError:
        log.log_mgr.error('file: default.conf can not open')
        return 0
    default_conf = {
        'colony_size': conf.getint('data', 'colony_size'),
        'exchange_min': conf.getint('data', 'exchange_min'),
        'mutation_count': conf.getint('data', 'mutation_count'),
        'try_times': conf.getint('data', 'try_times'),
        'evolution_max_time': conf.getint('data', 'evolution_max_time'),
        'offspring_max': conf.getint('data', 'offspring_max'),
    }
    return default_conf
