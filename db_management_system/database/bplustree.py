import math
# Import graphviz if you have it installed, otherwise handle the optional dependency
try:
    import graphviz
except ImportError:
    graphviz = None

# --- B+ Tree Node ---
# You might want separate classes for Internal and Leaf nodes,
# or use flags within a single class.
class BPlusTreeNode:
    def __init__(self, is_leaf=False, order=4): # Default order, adjust as needed
        self.is_leaf = is_leaf
        self.keys = []
        self.values = [] # Only used if is_leaf is True
        self.children = [] # Only used if is_leaf is False
        
        # For internal nodes, ensure there's at least one child slot
        if not is_leaf:
            self.children = [None]  # Initialize with one empty child pointer
            
        self.parent = None
        self.next_leaf = None # Only used if is_leaf is True
        self.order = order # Store order for split/merge logic

    def is_full(self):
        return len(self.keys) >= self.order - 1 # Max keys allowed is order - 1

    def is_underflow(self):
        # Root can have fewer keys, handle separately in BPlusTree class
        # Minimum keys is ceil(order / 2) - 1 for internal, ceil((order-1)/2) for leaf
        # Simplified for now: Check if below half (adjust based on precise definition)
        min_keys = math.ceil((self.order -1) / 2) # Common minimum for leaves
        if not self.is_leaf:
            min_keys = math.ceil(self.order / 2) - 1 # Common minimum for internal
        return len(self.keys) < min_keys

# --- B+ Tree Class ---
class BPlusTree:
    def __init__(self, order=4): # Default order, must be >= 3
        if order < 3:
            raise ValueError("B+ Tree order must be at least 3")
        self.root = BPlusTreeNode(is_leaf=True, order=order)
        self.order = order

    def _find_leaf(self, key):
        """ Helper: Traverse tree to find the leaf node where the key should reside. """
        node = self.root
        while not node.is_leaf:
            # Find the first key greater than the target key
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
                
            # Make sure we don't access an index that doesn't exist
            if not node.children or i >= len(node.children):
                # This shouldn't happen in a properly constructed B+ Tree
                # But we'll handle it gracefully by returning the current node
                print(f"Warning: B+ Tree structure issue. Node has {len(node.keys)} keys but {len(node.children) if node.children else 0} children.")
                return node
                
            node = node.children[i] # Follow the appropriate child pointer
        return node

    def search(self, key):
        """ Search for a key in the B+ tree. Return associated value if found, else None """
        leaf_node = self._find_leaf(key)
        
        # Check if this is really a leaf node (should be, but just in case)
        if not leaf_node.is_leaf:
            print(f"Warning: Expected leaf node but got internal node during search for key {key}")
            return None
            
        # Simple linear search within the leaf node (can optimize with binary search)
        try:
            index = leaf_node.keys.index(key)
            # Verify that the values list has enough elements
            if index < len(leaf_node.values):
                return leaf_node.values[index]
            else:
                print(f"Warning: Found key {key} at index {index}, but values list only has {len(leaf_node.values)} elements")
                return None
        except ValueError:
            return None # Key not found

    def insert(self, key, value):
        """ Insert key-value pair into the B+ tree. Handle root splitting if necessary. """
        # Find the appropriate leaf node
        leaf_node = self._find_leaf(key)
        
        # Make sure we're working with a leaf node
        if not leaf_node.is_leaf:
            print(f"Warning: Expected leaf node but got internal node during insert for key {key}")
            # Create a leaf node as fallback
            leaf_node = BPlusTreeNode(is_leaf=True, order=self.order)
            # If root is not a leaf, we need to recreate the structure
            if self.root != leaf_node:
                self.root = leaf_node

        # Add key/value to leaf (maintaining sorted order)
        # Find insertion point
        insert_idx = 0
        while insert_idx < len(leaf_node.keys) and leaf_node.keys[insert_idx] < key:
            insert_idx += 1

        # Avoid duplicates if necessary (policy decision - here we allow update/overwrite)
        if insert_idx < len(leaf_node.keys) and leaf_node.keys[insert_idx] == key:
             leaf_node.values[insert_idx] = value # Update existing key
             return

        # Insert the new key-value pair at the appropriate position
        leaf_node.keys.insert(insert_idx, key)
        leaf_node.values.insert(insert_idx, value)

        # Check if node needs splitting
        if leaf_node.is_full():
            self._split_child(leaf_node) # Use a generalized split function

    def _insert_non_full(self, node, key, value):
        """ Recursive helper to insert into a non-full node (more complex than initial insert).
            Often used when inserting involves traversing down and potentially splitting children.
            The basic insert above handles the common case directly for simplicity here.
            This function signature from appendix might be for a different B-Tree variant or approach.
            We'll rely on splitting *after* insertion in the leaf for this skeleton.
        """
        # This function is complex to implement correctly with recursive splitting.
        # The simpler approach is: insert into leaf, then split upwards if needed.
        # We will use the simpler approach and leave this as per the appendix signature.
        pass # Implementation depends heavily on chosen insertion strategy

    def _split_child(self, node):
        """ Split a node (leaf or internal) into two nodes. Propagate split upwards. """
        # This needs careful handling for both leaf and internal nodes,
        # updating parent pointers, and potentially splitting the root.
        mid_index = self.order // 2 # Split point (adjust based on definition)

        # Create the new sibling node
        new_node = BPlusTreeNode(is_leaf=node.is_leaf, order=self.order)
        new_node.parent = node.parent # Sibling shares the same parent initially

        # Move keys/values/children to the new node
        new_node.keys = node.keys[mid_index:]
        if node.is_leaf:
            new_node.values = node.values[mid_index:]
            middle_key_to_parent = new_node.keys[0] # Copy-up for leaves
            # Update linked list pointers
            new_node.next_leaf = node.next_leaf
            node.next_leaf = new_node
        else: # Internal node
            new_node.children = node.children[mid_index + 1:] # Children pointers shift
            middle_key_to_parent = node.keys[mid_index] # Push-up for internal
            # Update parent pointers of moved children
            for child in new_node.children:
                child.parent = new_node

        # Truncate the original node
        node.keys = node.keys[:mid_index]
        if node.is_leaf:
            node.values = node.values[:mid_index]
        else:
            # Adjust children list for internal node (keep first mid+1 children)
            node.children = node.children[:mid_index + 1]

        # --- Handle Parent ---
        if node.parent is None:
            # Splitting the root
            new_root = BPlusTreeNode(is_leaf=False, order=self.order)
            new_root.keys = [middle_key_to_parent]
            new_root.children = [node, new_node]  # Explicitly set both children
            node.parent = new_root
            new_node.parent = new_root
            self.root = new_root
        else:
            # Insert middle key into parent
            parent = node.parent
            # Find index in parent where new key/child should go
            insert_idx = 0
            while insert_idx < len(parent.keys) and parent.keys[insert_idx] < middle_key_to_parent:
                insert_idx += 1
            parent.keys.insert(insert_idx, middle_key_to_parent)
            parent.children.insert(insert_idx + 1, new_node)

            # Check if parent also needs splitting
            if parent.is_full():
                self._split_child(parent) # Recursive split

    def delete(self, key):
        """ Delete key from the B+ tree. Handle underflow by borrowing or merging. """
        leaf_node = self._find_leaf(key)

        # Try to find the key in the leaf
        try:
            index = leaf_node.keys.index(key)
        except ValueError:
            print(f"Key {key} not found for deletion.")
            return False # Key not found

        # Remove key and value
        leaf_node.keys.pop(index)
        leaf_node.values.pop(index)

        # Check for underflow (except if it's the root and now empty)
        if leaf_node.is_underflow() and not (leaf_node == self.root and len(leaf_node.keys) == 0):
            # Need to find the node's index in its parent's children list
            parent = leaf_node.parent
            if parent: # Root underflow handled differently (tree height shrinks)
                 child_index = -1
                 for i, child in enumerate(parent.children):
                     if child == leaf_node:
                         child_index = i
                         break
                 if child_index != -1:
                     self._handle_underflow(parent, child_index)
                 else:
                     # This case should ideally not happen if tree structure is correct
                     print("Error: Could not find child index during underflow handling.")
            elif len(self.root.keys) == 0 and not self.root.is_leaf:
                 # Root is internal and became empty after deletion/merge from below
                 self.root = self.root.children[0] # Promote the single child
                 self.root.parent = None

        return True

    def _handle_underflow(self, parent, child_index):
        """ Handles underflow in the child at parent.children[child_index]. """
        child = parent.children[child_index]

        # Try borrowing from left sibling
        if child_index > 0:
            left_sibling = parent.children[child_index - 1]
            if len(left_sibling.keys) > math.ceil((self.order - 1) / 2): # Check if left sibling has extra keys
                self._borrow_from_prev(child, parent, child_index, left_sibling)
                return

        # Try borrowing from right sibling
        if child_index < len(parent.children) - 1:
            right_sibling = parent.children[child_index + 1]
            if len(right_sibling.keys) > math.ceil((self.order - 1) / 2): # Check if right sibling has extra keys
                 self._borrow_from_next(child, parent, child_index, right_sibling)
                 return

        # If borrowing failed, merge
        if child_index > 0:
            # Merge with left sibling
            self._merge(parent, child_index - 1)
        else:
            # Merge with right sibling (merge child at index 0 with child at index 1)
             self._merge(parent, child_index)

    def _delete(self, node, key):
        """ Recursive helper for deletion. Handles leaf and internal nodes.
            Ensures all nodes maintain minimum keys after deletion.
            (Alternative deletion strategy to the one implemented above)
        """
        # This is complex, involves finding key, handling internal node key deletion
        # (replacing with successor), and recursive calls. The above strategy
        # deletes from leaf and handles underflow upwards, which is common for B+.
        pass # Not implemented in this skeleton using the leaf-first approach

    def _fill_child(self, node, index):
        """ Ensure child at given index has enough keys by borrowing or merging.
            (Helper function often used in top-down deletion strategies)
        """
        # This is part of the alternative deletion strategy where you ensure
        # a node is not minimum *before* recursing into it.
        pass # Not implemented in this skeleton

    def _borrow_from_prev(self, node, parent, node_index, left_sibling):
        """ Borrow a key from the left sibling to prevent underflow. """
        # Move parent key down, move sibling key up
        # Careful with indices and whether node is leaf or internal
        print(f"Borrowing from previous sibling for node {node_index}")

        # Move separator key from parent down to the start of the current node
        separator_index_in_parent = node_index - 1
        node.keys.insert(0, parent.keys[separator_index_in_parent])

        if node.is_leaf:
            # Move last key-value from left sibling
            borrowed_value = left_sibling.values.pop()
            borrowed_key = left_sibling.keys.pop()
            node.values.insert(0, borrowed_value)
            # Update parent's separator key to the new first key of the right node (which is the borrowed key)
            parent.keys[separator_index_in_parent] = borrowed_key # In B+, parent key matches first key in right subtree boundary
        else: # Internal node
            # Move last child pointer from left sibling
            borrowed_child = left_sibling.children.pop()
            node.children.insert(0, borrowed_child)
            borrowed_child.parent = node
            # Update parent's separator key with the last key from the left sibling
            parent.keys[separator_index_in_parent] = left_sibling.keys.pop()

    def _borrow_from_next(self, node, parent, node_index, right_sibling):
        """ Borrow a key from the right sibling to prevent underflow. """
        # Move parent key down, move sibling key up
        print(f"Borrowing from next sibling for node {node_index}")

        # Move separator key from parent down to the end of the current node
        separator_index_in_parent = node_index
        node.keys.append(parent.keys[separator_index_in_parent])

        if node.is_leaf:
            # Move first key-value from right sibling
            borrowed_key = right_sibling.keys.pop(0)
            borrowed_value = right_sibling.values.pop(0)
            node.values.append(borrowed_value)
            # Update parent's separator key to the new first key of the right sibling
            parent.keys[separator_index_in_parent] = right_sibling.keys[0]
        else: # Internal node
            # Move first child pointer from right sibling
            borrowed_child = right_sibling.children.pop(0)
            node.children.append(borrowed_child)
            borrowed_child.parent = node
             # Update parent's separator key with the first key from the right sibling
            parent.keys[separator_index_in_parent] = right_sibling.keys.pop(0)

    def _merge(self, parent, merge_start_index):
        """ Merge child at index with its right sibling. Update parent keys. """
        # merge_start_index is the index of the *left* node in the merge pair
        left_child = parent.children[merge_start_index]
        right_child = parent.children[merge_start_index + 1]
        print(f"Merging child {merge_start_index} and {merge_start_index + 1}")

        # Pull separator key from parent down into the left child
        separator_key = parent.keys.pop(merge_start_index)

        if left_child.is_leaf:
             left_child.keys.extend(right_child.keys)
             left_child.values.extend(right_child.values)
             # Update linked list
             left_child.next_leaf = right_child.next_leaf
        else: # Internal node merge
            left_child.keys.append(separator_key) # Add separator from parent
            left_child.keys.extend(right_child.keys)
            left_child.children.extend(right_child.children)
            # Update parent pointers for moved children
            for child in right_child.children:
                child.parent = left_child

        # Remove right child pointer from parent
        parent.children.pop(merge_start_index + 1)

        # --- Handle Parent Underflow ---
        # If parent is root and now empty
        if parent == self.root and not parent.keys:
            self.root = left_child # The merged node becomes the new root
            left_child.parent = None
        # If parent is not root and is now underflow
        elif parent != self.root and parent.is_underflow():
             # Find parent's index in *its* parent
             grandparent = parent.parent
             if grandparent:
                 parent_index = -1
                 for i, child in enumerate(grandparent.children):
                     if child == parent:
                         parent_index = i
                         break
                 if parent_index != -1:
                      self._handle_underflow(grandparent, parent_index)
                 else:
                      print("Error: Could not find parent index during recursive underflow.")


    def update(self, key, new_value):
        """ Update value associated with an existing key. Return True if successful. """
        leaf_node = self._find_leaf(key)
        try:
            index = leaf_node.keys.index(key)
            leaf_node.values[index] = new_value
            return True
        except ValueError:
            return False # Key not found

    def range_query(self, start_key, end_key):
        """ Retrieves all key-value pairs within the given range (inclusive). """
        if start_key > end_key:
            return []  # Invalid range
        
        result = []
        # Find the leaf node containing the start key
        leaf = self._find_leaf(start_key)
        
        # Traverse through leaf nodes until we've passed the end key
        current_leaf = leaf
        while current_leaf is not None:
            # Check each key in the current leaf
            for i, key in enumerate(current_leaf.keys):
                if start_key <= key <= end_key:
                    result.append((key, current_leaf.values[i]))
                elif key > end_key:
                    return result  # Reached keys beyond our range
            
            # Move to the next leaf if needed
            current_leaf = current_leaf.next_leaf
            
            # If there are no more leaves or we've gone past the range, exit
            if current_leaf is None or (current_leaf.keys and current_leaf.keys[0] > end_key):
                break
            
        return result

    def get_all(self):
        """ Return all key-value pairs in the tree using leaf node traversal. """
        results = []
        node = self.root
        # Find the leftmost leaf node
        while not node.is_leaf:
            node = node.children[0]

        # Traverse through all leaf nodes
        while node is not None:
            for i, k in enumerate(node.keys):
                results.append((k, node.values[i]))
            node = node.next_leaf
        return results

    def visualize_tree(self, filename="bplus_tree.gv"):
        """ Generate Graphviz representation of the B+ tree structure. """
        if not graphviz:
            print("Graphviz library not found. Cannot visualize tree.")
            print("Install it: pip install graphviz")
            print("Ensure the Graphviz binaries are also installed and in your PATH.")
            return None

        dot = graphviz.Digraph(comment='B+ Tree', format='png')
        dot.attr(splines='false') # Use straight lines for parent-child

        if self.root:
            self._add_nodes(dot, self.root)
            self._add_edges(dot, self.root)

            # Add leaf node connections (optional: rank constraint)
            with dot.subgraph() as leaf_sg:
                leaf_sg.attr(rank='same') # Try to align leaves horizontally
                q = [self.root]
                first_leaf_id = None
                visited_ids = set() # Prevent adding nodes multiple times if graph is complex
                # Find first leaf
                curr = self.root
                while curr and not curr.is_leaf:
                    if not curr.children: break
                    curr = curr.children[0]

                # Add edges between leaves
                prev_leaf_id = None
                while curr:
                    curr_id = f'node{id(curr)}'
                    if curr_id not in visited_ids: # Add leaf nodes to subgraph if not already there
                       leaf_sg.node(curr_id, self._node_label(curr), shape='box', style='filled', fillcolor='lightyellow')
                       visited_ids.add(curr_id)

                    if prev_leaf_id:
                         leaf_sg.edge(prev_leaf_id, curr_id, style='dashed', arrowhead='none', constraint='true') # Draw dashed line between leaves
                    prev_leaf_id = curr_id
                    curr = curr.next_leaf


        # print(dot.source) # For debugging the generated DOT language
        try:
            dot.render(filename, view=False) # Saves file, doesn't auto-open
            print(f"Tree visualization saved to {filename}.png")
        except Exception as e:
             print(f"Error rendering graphviz: {e}")
             print("Ensure Graphviz executables (dot) are installed and in your system's PATH.")

        return dot # Return the object if needed


    def _node_label(self, node):
        """ Helper to create a label for a node in Graphviz. """
        if node.is_leaf:
            # Show keys and potentially values (can get crowded)
            # return f"Leaf | {' | '.join(map(str, node.keys))} | Values: {' | '.join(map(str, node.values))}"
            return f"Leaf | {' | '.join(map(str, node.keys))}"
        else:
            # Show keys for internal nodes
            return f"Internal | {' | '.join(map(str, node.keys))}"


    def _add_nodes(self, dot, node):
        """ Recursively add nodes to Graphviz object (for visualization). """
        if node is None:
            return

        node_id = f'node{id(node)}'
        label = self._node_label(node)

        # Color leaves differently
        fill_color = 'lightblue'
        if node.is_leaf:
             fill_color = 'lightyellow'

        dot.node(node_id, label, shape='box', style='filled', fillcolor=fill_color)

        # Recursively add children if it's an internal node
        if not node.is_leaf:
            for child in node.children:
                 self._add_nodes(dot, child)


    def _add_edges(self, dot, node):
        """ Add edges between nodes for visualization. """
        if node is None or node.is_leaf:
             return

        node_id = f'node{id(node)}'
        for i, child in enumerate(node.children):
             child_id = f'node{id(child)}'
             # Add edge from parent to child
             dot.edge(node_id, child_id) # Add label later if needed
             # Recursively add edges for children
             self._add_edges(dot, child)

        # Note: Leaf linking edges are added separately in visualize_tree for better layout control

    def get_memory_usage(self):
        """ Basic memory usage estimation of the B+ Tree structure. """
        import sys
        
        def get_node_size(node):
            if node is None:
                return 0
            
            # Size of the node object itself
            size = sys.getsizeof(node)
            
            # Add size of keys list and keys
            size += sys.getsizeof(node.keys)
            for key in node.keys:
                size += sys.getsizeof(key)
            
            # For leaf nodes, add size of values
            if node.is_leaf:
                size += sys.getsizeof(node.values)
                for value in node.values:
                    size += sys.getsizeof(value)
            # For internal nodes, recursively calculate children sizes
            else:
                size += sys.getsizeof(node.children)
                for child in node.children:
                    size += get_node_size(child)
            
            return size
        
        return get_node_size(self.root)