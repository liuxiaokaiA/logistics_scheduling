import threading


class Car_status(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.at_base = 0
        self.running = 0
        self.arrived_wait_for_command = 0
        self.arrived_wait_for_unload = 0
        self.can_not_use = 0

    def __new__(cls, *args, **kwargs):
        if not hasattr(Car_status, "_instance"):
            with Car_status._instance_lock:
                if not hasattr(Car_status, "_instance"):
                    Car_status._instance = object.__new__(cls)
        return Car_status._instance
