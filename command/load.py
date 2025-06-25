from command.command import Command
from command.registry import register_command, COMMANDS

@register_command("load")
class Load(Command):
    def __init__(self):
        super().__init__()

    def execute(self, memdb, persistence_manager):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        with self.memdb.lock:
            # Load snapshot data
            self._load_snapshot()

            # Load AOF commands
            self._load_aof()

    def _load_snapshot(self):
        snapshot_data = self.persistence_manager.load_data()
        if snapshot_data:
            self.memdb.data = snapshot_data

    def _load_aof(self):
        aof_commands = self.persistence_manager.load_command()
        self.memdb.in_load = True
        for command in aof_commands:
            parts = command.strip().split()
            if not parts:
                continue
            action = parts[0].lower()
            if action == "put" and len(parts) in (3, 4):
                key = parts[1]
                value = parts[2]
                expiration_time = int(parts[3]) if len(parts) == 4 else None
                cmd_obj = COMMANDS['put'](key, value, expiration_time, original_command=command)
                self.memdb.execute(cmd_obj)
            elif action == "delete" and len(parts) == 2:
                key = parts[1]
                cmd_obj = COMMANDS['delete'](key, original_command=command)
                self.memdb.execute(cmd_obj)
            elif action == "clear":
                cmd_obj = COMMANDS['clear'](original_command=command)
                self.memdb.execute(cmd_obj)
            elif action == "begin" or action == "commit":
                continue
            else:
                continue
        self.memdb.in_load = False
