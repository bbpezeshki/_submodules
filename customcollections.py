from collections import OrderedDict, defaultdict

class RecursiveDefaultDict:
    def __init__(self):
        # Initialize the internal defaultdict with a factory method
        self._dict = defaultdict(self._new_instance)
    
    def _new_instance(self):
        # Method to create a new instance of RecursiveDefaultDict
        return RecursiveDefaultDict()
    
    def __getitem__(self, key):
        # Allow dictionary-like access
        return self._dict[key]
    
    def __setitem__(self, key, value):
        # Allow setting values like a dictionary
        self._dict[key] = value
    
    def __repr__(self):
        # Nicely represent the instance
        return repr(self._dict)

    def as_dict(self):
        # Convert the nested structure to regular dictionaries
        # This is handy for serialization and debugging
        def convert(d):
            if isinstance(d, RecursiveDefaultDict):
                return {k: convert(v) for k, v in d._dict.items()}
            return d
        return convert(self)

# # Example usage
# nested_dict = RecursiveDefaultDict()
# nested_dict['level1']['level2']['level3'] = 'deep_value'

# print(nested_dict)
# # Output will still be of RecursiveDefaultDict class, showing nested structure

# # Convert to a standard dictionary for more familiar display
# print(nested_dict.as_dict())
# # Output: {'level1': {'level2': {'level3': 'deep_value'}}}







class OrderedSet:
    def __init__(self, iterable=None):
        self._dict = OrderedDict()
        if iterable is not None:
            self._dict.update((item, None) for item in iterable)

    def add(self, item):
        self._dict[item] = None

    def update(self, iterable):
        for item in iterable:
            self.add(item)

    def discard(self, item):
        self._dict.pop(item, None)

    def __contains__(self, item):
        return item in self._dict

    def __iter__(self):
        return iter(self._dict.keys())

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return f"{type(self).__name__}({list(self._dict)})"