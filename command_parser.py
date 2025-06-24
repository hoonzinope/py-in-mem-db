from command.get import Get
from command.put import Put
from command.delete import Delete
from command.clear import Clear
from command.exists import Exists
from command.keys import Keys
from command.values import Values
from command.items import Items
from command.size import Size
from command.help import Help
from command.begin import Begin
from command.commit import Commit
from command.rollback import Rollback

class Parser:
    def parse(self, cmd):
        parts = cmd.split()
        if not parts:
            return None
        action = parts[0].lower()
        if action == "put" and len(parts) in (3, 4):
            key = parts[1]
            value = parts[2]
            expiration_time = int(parts[3]) if len(parts) == 4 else None
            return Put(key, value, expiration_time, original_command=cmd)
        elif action == "get" and len(parts) == 2:
            key = parts[1]
            return Get(key, original_command=cmd)
        elif action == "delete" and len(parts) == 2:
            key = parts[1]
            return Delete(key, original_command=cmd)
        elif action == "clear":
            return Clear(original_command=cmd)
        elif action == "exists" and len(parts) == 2:
            key = parts[1]
            return Exists(key, original_command=cmd)
        elif action == "keys":
            return Keys(original_command=cmd)
        elif action == "values":
            return Values(original_command=cmd)
        elif action == "items":
            return Items(original_command=cmd)
        elif action == "size":
            return Size(original_command=cmd)
        elif action == "help":
            return Help(original_command=cmd)
        elif action == "begin":
            return Begin(original_command=cmd)
        elif action == "commit":
            return Commit(original_command=cmd)
        elif action == "rollback":
            return Rollback(original_command=cmd)
        else:
            return None