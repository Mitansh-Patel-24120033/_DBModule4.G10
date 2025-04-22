import os
import pickle  # Using pickle for simple object persistence

# Use relative imports within the package
from .table import Table
from .bplustree import BPlusTree # May not be needed directly if only interacting via Table
from .bruteforce import BruteForceDB # For comparison/testing if needed here


DEFAULT_PERSISTENCE_FILE = "my_database.pkl"

class Database:
    """
    Manages a collection of tables within the lightweight DBMS.
    Handles table creation, deletion, listing, and persistence.
    """
    @staticmethod
    def list_databases(directory='.'):
        """Return all database names (filenames without .pkl extension) in the directory."""
        files = [f for f in os.listdir(directory) if f.endswith('.pkl')]
        return [os.path.splitext(f)[0] for f in files]

    @staticmethod
    def create_database(name, directory='.'):
        """Create a new empty database file and return a Database instance."""
        filename = os.path.join(directory, f"{name}.pkl")
        if os.path.exists(filename):
            raise FileExistsError(f"Database '{name}' already exists.")
        db = Database(filename)
        db.save_database()
        return db

    @staticmethod
    def get_database(name, directory='.'):
        """Load an existing database file and return its Database instance."""
        filename = os.path.join(directory, f"{name}.pkl")
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Database '{name}' not found.")
        return Database(filename)

    @staticmethod
    def delete_database(name, directory='.'):
        """Delete the database file with the given name."""
        filename = os.path.join(directory, f"{name}.pkl")
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False

    def __init__(self, persistence_path=DEFAULT_PERSISTENCE_FILE):
        self.tables = {}  # Dictionary to store tables {table_name: Table_object}
        self.persistence_path = persistence_path
        self._load_database() # Attempt to load existing data on init

    def create_table(self, name, order=4):
        """ Creates a new table with the given name and B+ Tree order. """
        if name in self.tables:
            print(f"Error: Table '{name}' already exists.")
            return None
        new_table = Table(name=name, order=order)
        self.tables[name] = new_table
        print(f"Database: Table '{name}' created successfully.")
        return new_table

    def delete_table(self, name):
        """ Deletes a table by name. """
        if name not in self.tables:
            print(f"Error: Table '{name}' not found.")
            return False
        del self.tables[name]
        print(f"Database: Table '{name}' deleted.")
        return True

    def get_table(self, name):
        """ Retrieves a table object by name. """
        table = self.tables.get(name)
        if not table:
            print(f"Error: Table '{name}' not found.")
        return table

    def list_tables(self):
        """ Returns a list of names of all tables in the database. """
        return list(self.tables.keys())

    def save_database(self, filepath=None):
        """ Saves the current state of the database (all tables) to a file. """
        path = filepath if filepath else self.persistence_path
        try:
            with open(path, 'wb') as f:
                pickle.dump(self.tables, f)
            print(f"Database state saved successfully to '{path}'.")
        except Exception as e:
            print(f"Error saving database to '{path}': {e}")

    def _load_database(self):
        """ Loads the database state from the persistence file, if it exists and is non-empty. """
        path = self.persistence_path
        # If file missing or empty, start with an empty database
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            print(f"Persistence file '{path}' not found or empty. Starting with empty database.")
            self.tables = {}
            return
        # Attempt to load existing data
        try:
            with open(path, 'rb') as f:
                self.tables = pickle.load(f)
            print(f"Database state loaded successfully from '{path}'.")
            # Reinitialize any transient state, such as parent pointers
            self._restore_transient_state()
        except (EOFError, pickle.UnpicklingError) as e:
            print(f"Error loading database from '{path}': {e}. Starting with empty database.")
            self.tables = {}
        except Exception as e:
            print(f"Error loading database from '{path}': {e}. Starting with empty database.")
            self.tables = {}

    def _restore_transient_state(self):
         """ If pickle doesn't save everything (like parent pointers), restore it. """
         print("Restoring transient state (e.g., parent pointers)...")
         for table in self.tables.values():
             if isinstance(table.index, BPlusTree):
                 self._restore_parents(table.index.root)

    def _restore_parents(self, node):
        """ Helper function to recursively set parent pointers after loading. """
        if node and not node.is_leaf:
            for child in node.children:
                child.parent = node
                self._restore_parents(child)


# --- Example Usage (can be run if this file is executed directly) ---
if __name__ == "__main__":
    # Example of how to use the Database manager
    db = Database("test_db.pkl") # Use a different file for testing

    print("\n--- Initial State ---")
    print("Tables:", db.list_tables())

    # Create tables if they don't exist
    if "users" not in db.list_tables():
        db.create_table("users", order=3)
    if "products" not in db.list_tables():
         db.create_table("products", order=5)

    users_table = db.get_table("users")
    products_table = db.get_table("products")

    print("\n--- After Creation ---")
    print("Tables:", db.list_tables())

    if users_table:
        print("\n--- Populating Users ---")
        # Check if data already exists from previous load
        if not users_table.select(1):
             users_table.insert(1, {"name": "Alice", "email": "alice@example.com"})
             users_table.insert(5, {"name": "Bob", "email": "bob@example.com"})
             users_table.insert(3, {"name": "Charlie", "email": "charlie@example.com"})
        else:
             print("User data seems to exist already.")

        print("User 3:", users_table.select(3))
        print("User 4 (non-existent):", users_table.select(4))
        users_table.visualize("test_users_table.gv")

    if products_table:
        print("\n--- Populating Products ---")
        if not products_table.select(101):
             products_table.insert(101, {"name": "Laptop", "price": 1200})
             products_table.insert(205, {"name": "Mouse", "price": 25})
             products_table.insert(150, {"name": "Keyboard", "price": 75})
        else:
            print("Product data seems to exist already.")

        print("Products 100-200:", products_table.range_query(100, 200))
        products_table.visualize("test_products_table.gv")


    print("\n--- Saving Database ---")
    db.save_database()

    print("\n--- Deleting a table ---")
    db.delete_table("products")
    print("Tables after delete:", db.list_tables())

    print("\n--- Loading Database Again (from file) ---")
    db_loaded = Database("test_db.pkl") # Should load users and products
    print("Loaded tables:", db_loaded.list_tables())
    loaded_users = db_loaded.get_table("users")
    if loaded_users:
        print("User 5 from loaded DB:", loaded_users.select(5))

    # Clean up the test persistence file
    # import os
    # if os.path.exists("test_db.pkl"):
    #     os.remove("test_db.pkl")
    # if os.path.exists("test_users_table.gv.png"):
    #     os.remove("test_users_table.gv.png")
    #     os.remove("test_users_table.gv")
    # if os.path.exists("test_products_table.gv.png"):
    #      os.remove("test_products_table.gv.png")
    #      os.remove("test_products_table.gv")