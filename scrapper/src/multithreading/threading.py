import threading
import config


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def dynamic_function(target, args, result):
    result['result'] = None
    result['result'] = target(*args)


class MultiThreading(metaclass=Singleton):
    def __init__(self):
        self.pool = []
        self.active = set()
        thread = threading.Thread(target=self.activator)
        thread.start()

    def add_thread(self, target, args=(), result=None):
        if result is None:
            result = {}
        if type(args) is not tuple:
            args = (args, )
        thread = threading.Thread(target=dynamic_function, args=(target, args, result))
        self.pool.append(thread)

    def pool_is_full(self):
        done = []
        for thread in self.active:
            if not thread.is_alive():
                done.append(thread)
        for thread in done:
            self.active.remove(thread)
        return len(self.active) == config.threading.MAX_THREADS

    def join_all(self):
        while len(self.pool) > 0 or len(self.active) > 0:
            pass

    def activator(self):
        while True:
            if not self.pool_is_full() and len(self.pool) > 0:
                thread = self.pool.pop()
                thread.start()
                self.active.add(thread)
