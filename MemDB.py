import time
from threading import Thread, Lock
from SysLog import logger
class inMemoryDB:
    def __init__(self):
        self.data = {}
        self.lock = Lock()  # To ensure thread safety
        # Start a background thread to periodically delete expired keys
        self.expiration_thread = Thread(target=self._delete_expired, daemon=True)
        self.expiration_thread.start()

        self.logger = logger(self.__class__.__name__)
        self.logger.log("Initialized in-memory database")

    # Store a value with a key and an optional expiration time in days
    # If expiration_time is None, it defaults to 7 seconds
    def put(self, key, value, expiration_time):
        with self.lock:  # Ensure thread safety when modifying the data
            if expiration_time is not None:
                # Convert expiration_time to a timestamp if it's not already
                if isinstance(expiration_time, int):
                    expiration_time = time.time() + expiration_time
                else:
                    self.logger.log(f"Invalid expiration time type: {type(expiration_time)}. Must be an integer.")
                    return
            else:# Default expiration time of 7 seconds
                expiration_time = time.time() + 7
            self.data[key] = { "value" : value, "expiration_time": expiration_time }
            self.logger.log(f"Stored {key}: {value} with expiration time of {expiration_time - time.time()} seconds")

    # lazy expiration
    # If the key has an expiration time, check if it has expired before returning the value
    def get(self, key):
        with self.lock:  # Ensure thread safety when accessing the data
            result = None
            log_msg = f"Retrieving {key}"

            if key not in self.data:
                log_msg += " - Key not found"
            elif self.data[key].get("expiration_time") is not None:
                if self.data[key]["expiration_time"] < time.time():
                    del self.data[key]
                    log_msg += " - Key has expired"
                else:
                    result = self.data[key]["value"]
            else:
                result = self.data[key]["value"]

            self.logger.log(log_msg)
            return result
    def delete(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                self.logger.log(f"Deleted {key}")
            else:
                self.logger.log(f"Attempted to delete {key}, but it does not exist")

    def _delete_expired(self):
        while True:
            with self.lock:
                current_time = time.time()
                keys_to_delete = []
                for key, value in self.data.items():
                    if value.get("expiration_time") is not None and value["expiration_time"] < current_time:
                        keys_to_delete.append(key)
                # Delete all expired keys
                for key in keys_to_delete:
                    del self.data[key]
            time.sleep(1)

    def clear(self):
        with self.lock:
            self.data.clear()
        self.logger.log("Cleared all data in the database")

    def exists(self, key):
        self.logger.log(f"Checking existence of {key}")
        return key in self.data
    
    def keys(self):
        self.logger.log("Retrieving all keys")
        return list(self.data.keys())
    
    def values(self):
        self.logger.log("Retrieving all values")
        return list(self.data.values())
    
    def items(self):
        self.logger.log("Retrieving all key-value pairs")
        return list(self.data.items())
    
    def size(self):
        self.logger.log(f"Retrieving size of the database: {len(self.data)}")
        return len(self.data)
    
    def help(self):
        return (
            "Commands:\n"
            "put <key> <value> <expiration_time> - Store a value with a key and an expiration time in seconds (default 7 seconds)\n"
            "get <key> - Retrieve a value by key \n"
            "delete <key> - Remove a key-value pair\n"
            "clear - Clear the database\n"
            "exists <key> - Check if a key exists\n"
            "keys - List all keys\n"
            "values - List all values\n"
            "items - List all key-value pairs\n"
            "size - Get the number of items in the database\n"
            "exit - Exit the command interface"
        )

