COMMANDS = {}
def register_command(name):
    def decorator(cls):
        COMMANDS[name] = cls
        return cls
    return decorator