import time
from threading import Thread, Lock
from logger import Logger
from persistence_manager import PesistenceManager

class inMemoryDB:
    __instance = None

    @staticmethod
    def get_instance():
        if inMemoryDB.__instance is None:
            inMemoryDB.__instance = inMemoryDB()
        return inMemoryDB.__instance

    def __init__(self):
        self.data = {}
        self.org_data = {}

        self.lock = Lock()  # To ensure thread safety

        self.in_transaction = False  # Flag to indicate if a transaction is in progress
        self.transaction_commands = []

        self.in_load = False # when loading data, we should not lock & transaction

        self.alias_command = {}  # Dictionary to store alias commands

        self.logger = Logger.get_logger()
        self._log("Initialized in-memory database")
        # Initialize persistence manager if needed
        self.persistence_manager = PesistenceManager.get_instance()

        # Start a background thread to periodically delete expired keys
        self.expiration_thread = Thread(target=self._delete_expired, daemon=True)
        self.expiration_thread.start()

        # Start a background thread to save data periodically
        self.save_thread = Thread(target=self._save, daemon=True)
        self.save_thread.start()

    def execute(self, command):
        return command.execute(self, self.persistence_manager)

    def _delete_expired(self):
        while True:
            time.sleep(1)
            if not self.in_transaction:
                self._clean_expired()

    # This method is used to clean expired keys from the database.
    # method for external calls to clean expired keys
    def clean_expired_keys(self):
        if self.lock.locked():
            self._clean_expired()
    
    def _clean_expired(self):
        current_time = time.time()
        keys_to_delete = []
        for key, value in self.data.items():
            if value.get("expiration_time") is not None and value["expiration_time"] < current_time:
                keys_to_delete.append(key)
        # Delete all expired keys
        for key in keys_to_delete:
            del self.data[key]

    def _save(self):
        while True:
            time.sleep(10)
            with self.lock:
                if self.persistence_manager:
                    self.persistence_manager.save_snapshot(self.data)

    def _log(self, message):
        self.logger.log(message, name=self.__class__.__name__)
