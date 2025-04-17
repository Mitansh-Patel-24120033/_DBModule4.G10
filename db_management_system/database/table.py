from .bplustree import BPlusTree

class Table:
    """
    Represents a database table, using a B+ Tree for indexing and storage.
    """
    def __init__(self, name, order=4): # Pass B+ Tree order
        self.name = name
        # Each table has its own B+ Tree index.
        # The keys of the B+ Tree are the primary keys (or indexed column) of the table.
        # The values can be the entire record/row (e.g., as a dictionary or tuple).
        self.index = BPlusTree(order=order)
        print(f"Table '{self.name}' created with B+ Tree index (order={order}).")

    def insert(self, key, value):
        """ Inserts a record (value) associated with a key into the table's index. """
        # In a real DB, value would be a row/record (dict, tuple, object)
        print(f"Table '{self.name}': Inserting key={key}") #, value={value}")
        self.index.insert(key, value)

    def select(self, key):
        """ Selects (retrieves) the record associated with a specific key. """
        print(f"Table '{self.name}': Selecting key={key}")
        return self.index.search(key)

    def delete(self, key):
        """ Deletes the record associated with a specific key. """
        print(f"Table '{self.name}': Deleting key={key}")
        return self.index.delete(key)

    def update(self, key, new_value):
        """ Updates the record associated with a specific key. """
        print(f"Table '{self.name}': Updating key={key}") # with value={new_value}")
        return self.index.update(key, new_value)

    def range_query(self, start_key, end_key):
        """ Retrieves all records where the key falls within the specified range. """
        print(f"Table '{self.name}': Range query from {start_key} to {end_key}")
        return self.index.range_query(start_key, end_key)

    def get_all_records(self):
        """ Retrieves all records from the table. """
        print(f"Table '{self.name}': Getting all records")
        return self.index.get_all()

    def visualize(self, filename=None):
        """ Visualizes the B+ Tree structure of this table's index. """
        if filename is None:
            filename = f"table_{self.name}_index.gv"
        print(f"Table '{self.name}': Generating visualization")
        self.index.visualize_tree(filename)

    # Add methods related to persistence if needed at the table level,
    # although usually handled by the DB manager.
    # def get_data_for_persistence(self):
    #     return self.index.get_all() # Or a more optimized serialization