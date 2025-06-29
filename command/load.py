from command.command import Command
from command.registry import register_command, parse_command

@register_command("load")
class Load(Command):
    def __init__(self):
        super().__init__()

    def execute(self, memdb, persistence_manager, session_id=None):
        self.memdb = memdb
        self.persistence_manager = persistence_manager

        with self.memdb.lock:
            # Load snapshot data
            self._load_snapshot()

            # Load alias commands
            self._load_alias()

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
            if action in ["put", "delete", "clear"]:
                self.memdb.execute(parse_command(command))
            else:
                continue
        self.memdb.in_load = False

    def _load_alias(self):
        alias_data = self.persistence_manager.load_alias()
        if alias_data:
            self.memdb.alias_command = alias_data
        else:
            self.memdb.alias_command = {}