import shlex

COMMANDS = {}
def register_command(name):
    def decorator(cls):
        COMMANDS[name] = cls
        return cls
    return decorator

def parse_command(cmd):
    parts = shlex.split(cmd.strip())
    if not parts:
        return None
    action = parts[0].lower()
    if action == "put" and len(parts) in (3, 4):
        key = parts[1]
        value = parts[2]
        expiration_time = int(parts[3]) if len(parts) == 4 else None
        return COMMANDS['put'](key, value, expiration_time, original_command=cmd)
    elif action == "get" and len(parts) == 2:
        key = parts[1]
        return COMMANDS['get'](key, original_command=cmd)
    elif action == "delete" and len(parts) == 2:
        key = parts[1]
        return COMMANDS['delete'](key, original_command=cmd)
    elif action == "clear":
        return COMMANDS['clear'](original_command=cmd)
    elif action == "exists" and len(parts) == 2:
        key = parts[1]
        return COMMANDS['exists'](key, original_command=cmd)
    elif action == "keys":
        return COMMANDS['keys'](original_command=cmd)
    elif action == "values":
        return COMMANDS['values'](original_command=cmd)
    elif action == "items":
        return COMMANDS['items'](original_command=cmd)
    elif action == "size":
        return COMMANDS['size'](original_command=cmd)
    elif action == "help":
        return COMMANDS['help'](original_command=cmd)
    elif action == "begin":
        return COMMANDS['begin'](original_command=cmd)
    elif action == "commit":
        return COMMANDS['commit'](original_command=cmd)
    elif action == "rollback":
        return COMMANDS['rollback'](original_command=cmd)
    elif action == "load":
        return COMMANDS['load']()
    elif action == "alias":
        return COMMANDS['alias'](original_command=cmd)
    elif action == "show-alias":
        return COMMANDS['show-alias'](original_command=cmd)
    elif action == "reset-alias":
        return COMMANDS['reset-alias'](original_command=cmd)
    elif action == "batch":
        commands = cmd[len("batch "):].strip()
        return COMMANDS['batch'](commands)
    else:
        return None