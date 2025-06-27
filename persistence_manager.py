import os
import json
import pickle

class PesistenceManager:
    __instance = None

    def __init__(self):
        self.persistence_type = 'file'  # Default to file-based persistence
        self.snapshot_file = os.path.join(os.path.dirname(__file__), 'meta-data', 'snapshot.db')
        self.aof_file = os.path.join(os.path.dirname(__file__), 'meta-data', 'AOF.txt')
        self.alias_file = os.path.join(os.path.dirname(__file__), 'meta-data', 'alias.json')

        # Ensure the directory exists
        self.make_files()

    @staticmethod
    def get_instance():
        if PesistenceManager.__instance is None:
            PesistenceManager.__instance = PesistenceManager()
        return PesistenceManager.__instance

    def make_files(self):
        # Create snapshot and AOF files if they do not exist
        os.makedirs(os.path.dirname(self.snapshot_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.aof_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.alias_file), exist_ok=True)

        if not os.path.exists(self.snapshot_file):
            with open(self.snapshot_file, 'wb') as file:
                pickle.dump({}, file)

        if not os.path.exists(self.aof_file):
            with open(self.aof_file, 'w') as file:
                file.write('')

        if not os.path.exists(self.alias_file):
            with open(self.alias_file, 'w') as file:
                json.dump({}, file)

    # Save snapshot of the current state
    def save_snapshot(self, data):
        self._save_to_file(data)
        self._initialize_aof()  # Ensure AOF is initialized

    def _save_to_file(self, data):
        with open(self.snapshot_file, 'wb') as file:
            pickle.dump(data, file)

    # Append data to the AOF (Append-Only File)
    def append_aof(self, data):
        self._append_to_file(data)

    def _append_to_file(self, data):
        with open(self.aof_file, 'a') as file:
            file.write(data + '\n')

    def _initialize_aof(self):
        with open(self.aof_file, 'w') as file:
            file.write('')

    def load_data(self):
        return self._load_snapshot()

    def _load_snapshot(self):
        data = {}
        with open(self.snapshot_file, 'rb') as file:
            data = pickle.load(file)
        return data

    def load_command(self):
        return self._load_aof()

    def _load_aof(self):
        commands = []
        with open(self.aof_file, 'r') as file:
            commands = file.readlines()
        return commands

    def save_alias(self, alias_dict):
        with open(self.alias_file, 'w') as file:
            json.dump(alias_dict, file)

    def load_alias(self):
        with open(self.alias_file, 'r') as file:
            alias_dict = json.load(file)
        return alias_dict