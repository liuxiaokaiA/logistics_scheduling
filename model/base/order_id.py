import threading
order_id = 0
order_group_id = 0


class OrderId(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        global order_id
        order_id += 1
        self.id = order_id

    def __new__(cls, *args, **kwargs):
        if not hasattr(OrderId, "_instance"):
            with OrderId._instance_lock:
                if not hasattr(OrderId, "_instance"):
                    OrderId._instance = object.__new__(cls)
        return OrderId._instance


class OrderGroupId(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        global order_group_id
        order_group_id += 1
        self.id = order_group_id

    def __new__(cls, *args, **kwargs):
        if not hasattr(OrderGroupId, "_instance"):
            with OrderGroupId._instance_lock:
                if not hasattr(OrderGroupId, "_instance"):
                    OrderGroupId._instance = object.__new__(cls)
        return OrderGroupId._instance


if __name__ == '__main__':
    print OrderId().id
    print OrderId().id
    print OrderId().id
    print OrderId().id
    print OrderId().id

    print OrderGroupId().id
    print OrderGroupId().id
    print OrderGroupId().id
    print OrderGroupId().id
    print OrderGroupId().id
