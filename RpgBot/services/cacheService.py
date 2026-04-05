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

class MonsterCache:
    def __init__(self):
        self.floors = []

    def set(self, floorIndex, key, value):
        try:
            floor = self.floors[floorIndex]
            floor[key] = value
        except:
            cache = {}
            cache[key] = value
            self.floors.append(cache)

    def get(self, floorIndex, key):
        return self.floors[floorIndex][key]

    def delete(self, floorIndex, key):
        self.floors[floorIndex].pop(key, None)

    def clear(self):
        self.floors = []

    def clearFloor(self, floorIndex):
        self.floors[floorIndex] = {}
