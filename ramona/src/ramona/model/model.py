class Model:
    def __init__(self, data: dict, source: str | None = None):
        self.data = data
        self.source = source

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data