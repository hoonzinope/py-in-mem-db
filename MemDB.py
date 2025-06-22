import time
from threading import Thread, Lock
class inMemoryDB:
    def __init__(self):
        self.data = {}
        self.lock = Lock()  # To ensure thread safety
        # Start a background thread to periodically delete expired keys
        self.expiration_thread = Thread(target=self._delete_expired, daemon=True)
        self.expiration_thread.start()

    # Store a value with a key and an optional expiration time in days
    # If expiration_time is None, it defaults to 7 seconds
    def put(self, key, value, expiration_time):
        if expiration_time is not None:
            # Convert expiration_time to a timestamp if it's not already
            if isinstance(expiration_time, int):
                expiration_time = time.time() + expiration_time
        else:# Default expiration time of 7 seconds
            expiration_time = time.time() + 7
        self.data[key] = { "value" : value, "expiration_time": expiration_time }

    # lazy expiration
    # If the key has an expiration time, check if it has expired before returning the value
    def get(self, key):
        if key not in self.data:
            return None
        
        if self.data[key].get("expiration_time") is not None:
            # Check if the key has expired
            if self.data[key]["expiration_time"] < time.time():
                del self.data[key]
                return None
            else:
                # If the key has not expired, return the value
                return self.data[key]["value"]
        else:
            # If no expiration time is set, return the value
            return self.data[key]["value"]

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    def _delete_expired(self):
        current_time = time.time()
        keys_to_delete = []
        for key, value in self.data.items():
            if value.get("expiration_time") is not None and value["expiration_time"] < current_time:
                keys_to_delete.append(key)
        # Delete all expired keys
        for key in keys_to_delete:
            del self.data[key]
        # Schedule the next run of this method
        Thread(target=self._delete_expired, daemon=True).start()

    def clear(self):
        self.data.clear()

    def exists(self, key):
        return key in self.data
    
    def keys(self):
        return list(self.data.keys())
    
    def values(self):
        return list(self.data.values())
    
    def items(self):
        return list(self.data.items())
    
    def size(self):
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

