# Appendix B provided code

class BruteForceDB:
    """
    Serves as a baseline for performance comparison against the B+ Tree.
    Uses a simple list to store keys/data and performs operations via linear iteration.
    NOTE: This basic version only stores keys. For fair comparison with a B+ Tree
    storing key-value pairs, this might need modification to store (key, value) tuples.
    """
    def __init__(self):
        # Store data as a list of tuples: [(key1, value1), (key2, value2), ...]
        # Or adjust B+ tree comparison to only compare key operations if needed.
        # Let's assume storing key-value pairs for better comparison.
        self.data = []

    def insert(self, key, value):
        """ Inserts a key-value pair. Overwrites if key exists. """
        # Check if key exists (linear scan)
        for i in range(len(self.data)):
            if self.data[i][0] == key:
                self.data[i] = (key, value) # Update existing
                # print(f"Warning: Key {key} already exists in BruteForceDB. Value updated.")
                return
        # If key doesn't exist, append
        self.data.append((key, value))

    def search(self, key):
        """ Searches for a key. Returns the value if found, else None. """
        for k, v in self.data:
            if k == key:
                return v
        return None # Key not found

    def delete(self, key):
        """ Deletes a key-value pair by key. Returns True if deleted, False otherwise. """
        original_length = len(self.data)
        self.data = [(k, v) for k, v in self.data if k != key]
        return len(self.data) < original_length # Return True if an item was removed

    def update(self, key, new_value):
        """ Updates the value for an existing key. Returns True if updated, False otherwise. """
        for i in range(len(self.data)):
            if self.data[i][0] == key:
                self.data[i] = (key, new_value)
                return True
        return False # Key not found to update

    def range_query(self, start_key, end_key):
        """ Returns a list of (key, value) pairs within the specified range (inclusive). """
        return [(k, v) for k, v in self.data if start_key <= k <= end_key]

    def get_all(self):
        """ Returns all key-value pairs. """
        return list(self.data) # Return a copy

    def get_memory_usage(self):
        """ Basic memory usage estimation (may not be fully accurate for complex objects). """
        import sys
        # Size of the list itself plus size of tuples/keys/values (approx)
        size = sys.getsizeof(self.data)
        if self.data:
            # Add size of a sample element multiplied by number of elements
            # This is a rough estimate!
            size += len(self.data) * sys.getsizeof(self.data[0])
            # Could iterate and sum sizes for more accuracy, but slower
        return size