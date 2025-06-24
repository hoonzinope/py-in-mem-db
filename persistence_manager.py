class PesistenceManager:
    def __init__(self):
        self.persistence_type = 'file'  # Default to file-based persistence
        self.snapshot_file = 'snapshot.db'
        self.aof_file = 'AOF.txt'

    # Save snapshot of the current state
    def save_snapshot(self, data):
        self._save_to_file(data)
        self._initalize_AOF()  # Ensure AOF is initialized

    def _save_to_file(self, data):
        with open(self.snapshot_file, 'wb') as file:
            file.write(data)

    # Append data to the AOF (Append-Only File)
    def append_AOF(self, data):
        self._append_to_file(data)

    def _append_to_file(self, data):
        with open(self.aof_file, 'a') as file:
            file.write(data)

    def _initalize_AOF(self):
        with open(self.aof_file, 'w') as file:
            file.write('')

    def _load_snapshot(self):
        data = {}
        with open(self.snapshot_file, 'rb') as file:
            data = file.read()
        return data
    
    def _load_AOF(self):
        commands = []
        with open(self.aof_file, 'r') as file:
            commands = file.readlines()
        return commands