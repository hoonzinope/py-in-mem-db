from command.command import Command
import time

from command.registry import register_command
from logger import Logger
from response import Response, STATUS_CODE


@register_command("put")
class Put(Command):
    def __init__(self, key, value, expiration_time=None, original_command=None):
        super().__init__()
        self.key = key
        self.value = value
        self.expiration_time = expiration_time
        self.original_command = original_command
        self.logger = Logger.get_logger()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        if self.memdb.in_load:
            self._execute_put(self.key, self.value, self.expiration_time)

        if self.memdb.in_transaction:
            self.memdb.transaction_commands.append(self.original_command)
            self._execute_put(self.key, self.value, self.expiration_time)
        else:
            with self.memdb.lock:
                self.persistence_manager.append_aof(self.original_command)
                self._execute_put(self.key, self.value, self.expiration_time)
        return Response(
            status_code=STATUS_CODE["OK"],
            message=f"Key '{self.key}' set with value '{self.value}' and expiration time '{self.expiration_time}'",
            data= None
        )

    def _execute_put(self, key, value, expiration_time):
        self._check_key_value(key, value)
        expiration_time = self._convert_expiration_time_parameter(expiration_time)
        self.memdb.data[key] = {
            "value": value,
            "expiration_time": expiration_time
        }

    def _check_key_value(self, key, value):
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("Key and value must be strings")
        if not key:
            raise ValueError("Key cannot be empty")
        if not value:
            raise ValueError("Value cannot be empty")
        
    def _convert_expiration_time_parameter(self, expiration_time = None):
        if expiration_time is None:
            # Default expiration time of 7 seconds
            expiration_time = time.time() + 7

        # Convert expiration_time to a timestamp if it's not already
        if isinstance(expiration_time, int):
            if expiration_time < 0:
                raise ValueError("Expiration time must be a non-negative integer")
            else:
                expiration_time = time.time() + expiration_time
        elif isinstance(expiration_time, float):
            if expiration_time < 0:
                raise ValueError("Expiration time must be a non-negative float")
            else:
                expiration_time = time.time() + expiration_time
        elif isinstance(expiration_time, str):
            try:
                expiration_time = int(expiration_time)
                if expiration_time < 0:
                    raise ValueError("Expiration time must be a non-negative integer")
                else:
                    # Convert string to integer and add current time
                    expiration_time = time.time() + int(expiration_time)
            except ValueError:
                raise ValueError("Expiration time must be an integer")
        elif isinstance(expiration_time, (list, tuple)):
            try:
                expiration_time = time.time() + int(expiration_time[0])
            except (ValueError, IndexError):
                raise ValueError("Expiration time must be an integer")

        else:
            raise ValueError("Expiration time must be an integer")

        return expiration_time