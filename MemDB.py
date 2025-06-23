import time
from threading import Thread, Lock
from SysLog import logger
import copy
class inMemoryDB:
    def __init__(self):
        self.data = {}
        self.org_data = {}
        self.lock = Lock()  # To ensure thread safety
        self.in_transaction = False  # Flag to indicate if a transaction is in progress
        self.logger = logger(self.__class__.__name__)
        self.logger.log("Initialized in-memory database")

        self.key_data_type = str  # Default key type
        self.value_data_type = str  # Default value type

        # Start a background thread to periodically delete expired keys
        self.expiration_thread = Thread(target=self._delete_expired, daemon=True)
        self.expiration_thread.start()

    def set_key_data_type(self, key_data_type):
        if not isinstance(key_data_type, type):
            self.logger.log(f"Invalid key data type: {key_data_type}. Must be a type.")
            raise TypeError("Key data type must be a type")
        self.key_data_type = key_data_type
        self.logger.log(f"Set key data type to {self.key_data_type.__name__}")

    def set_value_data_type(self, value_data_type):
        if not isinstance(value_data_type, type):
            self.logger.log(f"Invalid value data type: {value_data_type}. Must be a type.")
            raise TypeError("Value data type must be a type")
        self.value_data_type = value_data_type
        self.logger.log(f"Set value data type to {self.value_data_type.__name__}")

    def begin_transaction(self):
        self.lock.acquire()  # Acquire the lock to ensure thread safety
        try:
            if self.in_transaction:
                self.logger.log("Transaction already in progress")
                raise RuntimeError("Transaction already in progress")
            self.org_data = copy.deepcopy(self.data)  # Store the original data
            self.in_transaction = True
            self.logger.log("Transaction started")
        except Exception as e:
            self.logger.log(f"Error starting transaction: {e}")
            self.lock.release()
            raise

    def commit_transaction(self):
        try:
            if not self.in_transaction:
                self.logger.log("No transaction in progress to commit")
                raise RuntimeError("No transaction in progress")
            self.org_data = {}
            self.in_transaction = False
            self.logger.log("Transaction committed")
        except Exception as e:
            self.logger.log(f"Error during commit: {e}")
            self.rollback_transaction()
            raise
        finally:
            self.lock.release()

    def rollback_transaction(self):
        try:
            if not self.in_transaction:
                self.logger.log("No transaction in progress to rollback")
                raise RuntimeError("No transaction in progress")
            self.data = copy.deepcopy(self.org_data)  # Restore the original data
            self.org_data = {}  # Clear the original data
            self.in_transaction = False
            self.logger.log("Transaction rolled back")
        except Exception as e:
            self.logger.log(f"Error during rollback: {e}")
        finally:
            self.lock.release()

    # Store a value with a key and an optional expiration time in days
    # If expiration_time is None, it defaults to 7 seconds
    def put(self, key, value, expiration_time):
        self._check_key_value_types(key, value)
        if self.in_transaction:
            self._put(key, value, expiration_time)
        else:
            with self.lock:  # Ensure thread safety when modifying the data
                self._put(key, value, expiration_time)

    def _put(self, key, value, expiration_time):
        expiration_time = self._convert_expiration_time_parameter(expiration_time)
        self.data[key] = { "value": value, "expiration_time": expiration_time }
        self.logger.log(f"Internally stored {key}: {value} with expiration time of {expiration_time - time.time()} seconds")

    def _check_key_value_types(self, key, value):
        if not isinstance(key, self.key_data_type):
            self.logger.log(f"Invalid key type: {type(key)}. Must be {self.key_data_type.__name__}.")
            raise TypeError(f"Key must be of type {self.key_data_type.__name__}")
        if not isinstance(value, self.value_data_type):
            self.logger.log(f"Invalid value type: {type(value)}. Must be {self.value_data_type.__name__}.")
            raise TypeError(f"Value must be of type {self.value_data_type.__name__}")

    def _convert_expiration_time_parameter(self, expiration_time):
        if expiration_time is not None:
            # Convert expiration_time to a timestamp if it's not already
            if isinstance(expiration_time, int):
                if expiration_time < 0:
                    self.logger.log(f"Invalid expiration time: {expiration_time}. Must be a non-negative integer.")
                    raise ValueError("Expiration time must be a non-negative integer")
                else:
                    expiration_time = time.time() + expiration_time
            elif isinstance(expiration_time, float):
                if expiration_time < 0:
                    self.logger.log(f"Invalid expiration time: {expiration_time}. Must be a non-negative float.")
                    raise ValueError("Expiration time must be a non-negative float")
                else:
                    expiration_time = time.time() + expiration_time
            elif isinstance(expiration_time, str):
                try:
                    expiration_time = int(expiration_time)
                    if expiration_time < 0:
                        self.logger.log(f"Invalid expiration time: {expiration_time}. Must be a non-negative integer.")
                        raise ValueError("Expiration time must be a non-negative integer")
                    else:
                        # Convert string to integer and add current time
                        expiration_time = time.time() + int(expiration_time)
                except ValueError:
                    self.logger.log(f"Invalid expiration time string: {expiration_time}. Must be an integer.")
                    raise ValueError("Expiration time must be an integer")
            elif isinstance(expiration_time, (list, tuple)):
                try:
                    expiration_time = time.time() + int(expiration_time[0])
                except (ValueError, IndexError):
                    self.logger.log(f"Invalid expiration time list/tuple: {expiration_time}. Must be an integer.")
                    raise ValueError("Expiration time must be an integer")
                
            else:
                self.logger.log(f"Invalid expiration time type: {type(expiration_time)}. Must be an integer.")
                raise ValueError("Expiration time must be an integer")
        else:# Default expiration time of 7 seconds
            expiration_time = time.time() + 7

        return expiration_time
    # lazy expiration
    # If the key has an expiration time, check if it has expired before returning the value
    def get(self, key):
        if self.in_transaction:
            return self._get(key)
        else:
            with self.lock:  # Ensure thread safety when accessing the data
                return self._get(key)
    
    def _get(self, key):
        if key in self.data:
            if self.data[key].get("expiration_time") is not None:
                if self.data[key]["expiration_time"] < time.time():
                    del self.data[key]
                    self.logger.log(f"Key {key} has expired and was deleted")
                    return None
                else:
                    return self.data[key]["value"]
            else:
                return self.data[key]["value"]
        else:
            self.logger.log(f"Key {key} not found")
            return None

    def delete(self, key):
        if self.in_transaction:
            self._delete(key)
        else:
            with self.lock:
                self._delete(key)

    def _delete(self, key):
        if key in self.data:
            del self.data[key]
            self.logger.log(f"Internally deleted {key}")
        else:
            self.logger.log(f"Attempted to internally delete {key}, but it does not exist")

    def _delete_expired(self):
        if not self.in_transaction:
            while True:
                self._clean_expired()
                time.sleep(1)

    def clear(self):
        if self.in_transaction:
            self._clear()
        else:
            with self.lock:
                self._clear()
        self.logger.log("Cleared all data in the database")

    def _clear(self):
        self.data.clear()
        self.logger.log("Internally cleared all data in the database")

    def exists(self, key):
        if self.in_transaction:
            return self._exists(key)
        else:
            with self.lock:
                return self._exists(key)
    
    def _exists(self, key):
        if key in self.data:
            if self.data[key].get("expiration_time") is not None:
                if self.data[key]["expiration_time"] < time.time():
                    del self.data[key]
                    self.logger.log(f"Key {key} has expired and was deleted")
                    return False
                else:
                    return True
            else:
                return True
        else:
            self.logger.log(f"Key {key} not found")
            return False

    def keys(self):
        self.logger.log("Retrieving all keys")
        if self.in_transaction:
            return list(self.data.keys())
        else:
            self._clean_expired()
            return list(self.data.keys())
    
    def values(self):
        self.logger.log("Retrieving all values")
        if self.in_transaction:
            return list(self.data.values())
        else:    
            self._clean_expired()
            return list(self.data.values())
    
    def items(self):
        self.logger.log("Retrieving all key-value pairs")
        if self.in_transaction:
            return list(self.data.items())
        else:
            self._clean_expired()
            return list(self.data.items())
    
    def size(self):
        self.logger.log(f"Retrieving size of the database")
        if self.in_transaction:
            return len(self.data)
        else:
            self._clean_expired()
            return len(self.data)
    
    def _clean_expired(self):
        with self.lock:
            current_time = time.time()
            keys_to_delete = []
            for key, value in self.data.items():
                if value.get("expiration_time") is not None and value["expiration_time"] < current_time:
                    keys_to_delete.append(key)
            # Delete all expired keys
            for key in keys_to_delete:
                del self.data[key]

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

