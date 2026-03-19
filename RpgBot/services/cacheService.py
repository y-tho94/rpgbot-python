class SimpleCache:
    def __init__(self):
        self.cache = {} 
    def set(self, key, value):
        self.cache[key] = value

    def get(self, key):
        return self.cache.get(key)

    def delete(self, key):
        self.cache.pop(key, None)

    def clear(self):
        self.cache = {}
