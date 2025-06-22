class inMemoryDB:
    def __init__(self):
        self.data = {}

    def put(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key, None)

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    def clear(self):
        self.data.clear()

    def exists(self, key):
        return key in self.data
    
    def keys(self):
        return list(self.data.keys())
    
    def values(self):
        return list(self.data.values())
    
    def items(self):
        return list(self.data.items())
    
    def size(self):
        return len(self.data)
    
    def help(self):
        return (
            "Commands:\n"
            "put <key> <value> - Store a value with a key\n"
            "get <key> - Retrieve a value by key\n"
            "delete <key> - Remove a key-value pair\n"
            "clear - Clear the database\n"
            "exists <key> - Check if a key exists\n"
            "keys - List all keys\n"
            "values - List all values\n"
            "items - List all key-value pairs\n"
            "size - Get the number of items in the database\n"
            "exit - Exit the command interface"
        )

