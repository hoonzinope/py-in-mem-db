import time

class logger:
    def __init__(self, name):
        self.name = name
        self.time_format = "%Y-%m-%d %H:%M:%S"

    def log(self, message):
        timestamp = time.strftime(self.time_format, time.localtime())
        print(f"[{timestamp}]\t[{self.name}]\tlog:{message}")