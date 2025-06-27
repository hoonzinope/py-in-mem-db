import threading
import time
import os

class logger:
    def __init__(self, name):
        self.name = name
        self.time_format = "%Y-%m-%d %H:%M:%S"
        # for logging command usage
        self.command_log = []
        self.usage_log_file_path = "./meta-data/command_usage.log"
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.usage_log_file_path), exist_ok=True)

        self.lock = threading.Lock()
        self.batch_size = 100  # Number of commands to log before flushing
        self.running = True
        self.thread = threading.Thread(target=self._flush, daemon=True)
        self.thread.start()

    def log(self, message):
        timestamp = time.strftime(self.time_format, time.localtime())
        print(f"[{timestamp}]\t[{self.name}]\tlog:{message}")

    def append_usage_log(self, command):
        with self.lock:
            timestamp = time.strftime(self.time_format, time.localtime())
            log_entry = f"[{timestamp}]\t[{self.name}]\tcommand:{command}\n"
            self.command_log.append(log_entry)
            if len(self.command_log) >= self.batch_size:
                self._flush_log()

    def _flush_log(self):
        if self.command_log:
            with open(self.usage_log_file_path, "a") as f:
                f.writelines(self.command_log)
            self.command_log.clear()

    def _flush(self):
        while self.running:
            time.sleep(1)
            try:
                with self.lock:
                    self._flush_log()
            except Exception as e:
                pass

    def close(self):
        self.running = False
        self.thread.join()
        with self.lock:
            self._flush_log()