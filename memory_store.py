import time
from threading import Thread, Lock
from logger import logger
import copy

from persistence_manager import persistence_manager

def transaction_safe(func):
    def wrapper(self, *args, **kwargs):
        if self.in_transaction:
            return func(self, *args, **kwargs)
        else:
            with self.lock:
                return func(self, *args, **kwargs)
    return wrapper

def transaction_safe_clean_data(func):
    def wrapper(self, *args, **kwargs):
        if self.in_transaction:
            return func(self, *args, **kwargs)
        else:
            with self.lock:
                # Clean expired keys before executing the function
                self._clean_expired()
                return func(self, *args, **kwargs)
    return wrapper

class inMemoryDB:
    def __init__(self):
        self.data = {}
        self.org_data = {}
        self.lock = Lock()  # To ensure thread safety
        self.in_transaction = False  # Flag to indicate if a transaction is in progress
        self.transaction_commands = []
        self.logger = logger(self.__class__.__name__)
        self.logger.log("Initialized in-memory database")
        # Initialize persistence manager if needed
        self.persistence_manager = None  # Placeholder for persistence manager

        self.key_data_type = str  # Default key type
        self.value_data_type = str  # Default value type

        # Start a background thread to periodically delete expired keys
        self.expiration_thread = Thread(target=self._delete_expired, daemon=True)
        self.expiration_thread.start()

    def execute(self, command):
        return command.execute(self, self.persistence_manager)

        if key in self.data:
            del self.data[key]
            self.logger.log(f"Internally deleted {key}")
        else:
            self.logger.log(f"Attempted to internally delete {key}, but it does not exist")
    def _delete_expired(self):
        while True:
            if not self.in_transaction:
                self._clean_expired()
                time.sleep(1)
    
    def _clean_expired(self):
        current_time = time.time()
        keys_to_delete = []
        for key, value in self.data.items():
            if value.get("expiration_time") is not None and value["expiration_time"] < current_time:
                keys_to_delete.append(key)
        # Delete all expired keys
        for key in keys_to_delete:
            del self.data[key]

    # TODO : Implement save and load methods for persistence
