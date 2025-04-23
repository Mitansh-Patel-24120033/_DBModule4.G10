import math
import bisect # Import bisect for optimized searching
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
        self.values = [] if is_leaf else None  # Only leaf nodes store values
        self.children = [] if not is_leaf else None  # Only internal nodes store children
        self.parent = None
        self.next_leaf = None # Only used if is_leaf is True
        self.order = order # Store order for split/merge logic

    def ensure_valid_structure(self, silent=False):
        """Ensure internal nodes maintain the B+ tree property of n+1 children for n keys"""
        if self.is_leaf:
            return True  # Leaf nodes don't need structure validation
            
        # For internal nodes: must have exactly n+1 children for n keys
        expected_children = len(self.keys) + 1
        
        if len(self.children) != expected_children:
            # Structure is invalid
            if len(self.children) < expected_children:
                # Add missing children (all leaves for simplicity)
                while len(self.children) < expected_children:
                    new_child = BPlusTreeNode(is_leaf=True, order=self.order)
                    new_child.parent = self
                    self.children.append(new_child)
            else:
                # Too many children - trim to correct number
                # Keep first and last child pointers for range integrity
                if len(self.children) > 1:
                    # Keep the first child + one child per key
                    self.children = [self.children[0]] + self.children[1:expected_children]
            
            if not silent:
                print(f"Fixed B+ Tree node: adjusted from {len(self.children)-(expected_children)} children to {expected_children} children for {len(self.keys)} keys")
            return False  # Structure needed fixing
        return True  # Structure was valid

    def is_full(self):
        return len(self.keys) >= self.order - 1 # Max keys allowed is order - 1

    def is_underflow(self):
        # Root can have fewer keys, handle separately in BPlusTree class
        # Minimum keys is ceil(order / 2) - 1 for internal, ceil((order-1)/2) for leaf
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
        
        # Validate the root if it's not a leaf
        if not node.is_leaf:
            node.ensure_valid_structure(silent=True)
        
        while not node.is_leaf:
            # Use bisect_right to find the insertion point, which gives the correct child index
            i = bisect.bisect_right(node.keys, key)
            
            # Get the appropriate child - should always be valid now
            child = node.children[i]
            
            # If the child is an internal node, validate its structure too
            if not child.is_leaf:
                child.ensure_valid_structure(silent=True)
                
            node = child
            
        return node

    def search(self, key):
        """ Search for a key in the B+ tree. Return associated value if found, else None """
        leaf_node = self._find_leaf(key)
        
        # Use bisect_left to find the potential index of the key
        index = bisect.bisect_left(leaf_node.keys, key)

        # Check if the key actually exists at that index
        if index < len(leaf_node.keys) and leaf_node.keys[index] == key:
            # Verify that the values list has the corresponding value
            if index < len(leaf_node.values):
                 return leaf_node.values[index]

        return None # Key not found or values list inconsistent

    def insert(self, key, value):
        """
        Insert key-value pair into the B+ tree.
        Handle root splitting if necessary.
        Maintain sorted order and balance properties.
        """
        # If this is the very first insert and root is empty, just add directly
        if not self.root.keys and self.root.is_leaf:
            self.root.keys.append(key)
            self.root.values.append(value)
            return
        
        # Find the appropriate leaf node
        leaf_node = self._find_leaf(key)
        
        # Verify we have a leaf node - should always be true with fixed _find_leaf
        if not leaf_node.is_leaf:
            # Create a new leaf node
            new_leaf = BPlusTreeNode(is_leaf=True, order=self.order)
            
            # Insert it as a child of the current node if possible
            if not leaf_node.children:
                leaf_node.children = [new_leaf]
            else:
                leaf_node.children.append(new_leaf)
                
            new_leaf.parent = leaf_node
            leaf_node.ensure_valid_structure(silent=True)
            leaf_node = new_leaf

        # Add key/value to leaf (maintaining sorted order)
        # Find insertion point using bisect_left
        insert_idx = bisect.bisect_left(leaf_node.keys, key)

        # Avoid duplicates - update existing key if found
        if insert_idx < len(leaf_node.keys) and leaf_node.keys[insert_idx] == key:
            leaf_node.values[insert_idx] = value  # Update existing key
            return

        # Insert the new key-value pair at the appropriate position
        leaf_node.keys.insert(insert_idx, key)
        leaf_node.values.insert(insert_idx, value)

        # Check if node needs splitting
        if leaf_node.is_full():
            self._split_node(leaf_node)

    def _split_node(self, node):
        """
        Split a node (leaf or internal) into two nodes.
        Improved version of _split_child with more consistent naming and handling.
        """
        # Calculate split point
        mid_index = self.order // 2  # Split point
        
        # Create new sibling node with the same properties as the original
        new_sibling = BPlusTreeNode(is_leaf=node.is_leaf, order=self.order)
        new_sibling.parent = node.parent  # Both will share the same parent initially
        
        # Handle the split based on node type
        if node.is_leaf:
            # For leaf nodes
            # Copy second half of keys and values to the new sibling
            new_sibling.keys = node.keys[mid_index:]
            new_sibling.values = node.values[mid_index:]
            
            # The key to add to parent (copied up)
            parent_key = new_sibling.keys[0]
            
            # Update linked list pointers for leaves
            new_sibling.next_leaf = node.next_leaf
            node.next_leaf = new_sibling
            # Truncate the original node
            node.keys = node.keys[:mid_index]
            node.values = node.values[:mid_index]
        else:
            # For internal nodes
            # Key that moves up to parent (not kept in this node)
            parent_key = node.keys[mid_index]
            
            # Copy keys after the middle key to the new sibling
            new_sibling.keys = node.keys[mid_index+1:]
            
            # Make sure both nodes have appropriate child pointers
            new_sibling.children = node.children[mid_index+1:]
            node.children = node.children[:mid_index+1]
            
            # Update parent pointers for all children of the new sibling
            for child in new_sibling.children:
                if child:
                    child.parent = new_sibling
            
            # Truncate the original node keys (remove middle key that moved up)
            node.keys = node.keys[:mid_index]
            
            # Validate structure
            node.ensure_valid_structure(silent=True)
            new_sibling.ensure_valid_structure(silent=True)
        
        # Handle parent updates
        if node.parent is None:
            # If splitting the root, create a new root
            new_root = BPlusTreeNode(is_leaf=False, order=self.order)
            new_root.keys = [parent_key]
            new_root.children = [node, new_sibling]
            
            # Update parent references
            node.parent = new_root
            new_sibling.parent = new_root
            
            # This is now the new root
            self.root = new_root
        else:
            # Otherwise insert into existing parent
            parent = node.parent
            
            # Use bisect_left to find the insertion point for the key in the parent
            insert_idx = bisect.bisect_left(parent.keys, parent_key)
            
            # Insert the key and child pointer in the parent
            parent.keys.insert(insert_idx, parent_key)
            
            # Find the index of the original node in parent's children list
            for i, child in enumerate(parent.children):
                if child == node:
                    # Insert the new sibling right after the original node
                    parent.children.insert(i+1, new_sibling)
                    break
            
            # Set parent reference for new sibling
            new_sibling.parent = parent
            
            # Ensure parent structure is valid
            parent.ensure_valid_structure(silent=True)
            
            # Check if parent needs splitting too
            if parent.is_full():
                self._split_node(parent)

    def delete(self, key):
        """
        Delete key from the B+ tree.
        Handle underflow by borrowing from siblings or merging nodes.
        Update root if it becomes empty.
        Return True if deletion succeeded, False otherwise.
        """
        # First find the leaf node containing the key
        leaf_node = self._find_leaf(key)

        # Try to find the key in the leaf
        # Use bisect_left to find the potential index
        index = bisect.bisect_left(leaf_node.keys, key)

        # Check if key exists at the found index
        if not (index < len(leaf_node.keys) and leaf_node.keys[index] == key):
             return False # Key not found

        # Remove key and value
        leaf_node.keys.pop(index)
        leaf_node.values.pop(index)

        # Check for underflow (except if it's the root and now empty)
        if leaf_node.is_underflow() and not (leaf_node == self.root and len(leaf_node.keys) == 0):
            # Need to find the node's index in its parent's children list
            parent = leaf_node.parent
            if parent: # Root underflow handled differently (tree height shrinks)
                 # Ensure parent structure is valid
                 parent.ensure_valid_structure(silent=True)
                 
                 child_index = -1
                 for i, child in enumerate(parent.children):
                     if child == leaf_node:
                         child_index = i
                         break
                 if child_index != -1:
                     self._fill_child(parent, child_index)
                 else:
                     # This should never happen with our improved structure validation
                     pass
            elif len(self.root.keys) == 0 and not self.root.is_leaf:
                 # Root is internal and became empty after deletion/merge from below
                 self.root = self.root.children[0] # Promote the single child
                 self.root.parent = None

        return True

    def _fill_child(self, node, index):
        """
        Ensure child at given index has enough keys by borrowing from siblings or merging.
        """
        # Make sure the node we're working with has a valid structure
        node.ensure_valid_structure(silent=True)
        
        # Verify the index is valid
        if index < 0 or index >= len(node.children):
            return
        
        child = node.children[index]
        min_keys = math.ceil(self.order / 2) - 1

        # Try borrowing from left sibling
        if index > 0:
            left_sibling = node.children[index-1]
            left_sibling.ensure_valid_structure(silent=True)
            
            if len(left_sibling.keys) > min_keys:
                self._borrow_from_prev(node, index)
                return

        # Try borrowing from right sibling
        if index < len(node.children) - 1:
            right_sibling = node.children[index + 1]
            right_sibling.ensure_valid_structure(silent=True)
            
            if len(right_sibling.keys) > min_keys:
                self._borrow_from_next(node, index)
                return

        # Merge with a sibling
        # If last child, merge with previous
        if index == len(node.children)-1:
            self._merge(node, index-1)
        # Otherwise merge with next
        else:
            self._merge(node, index)
        
        # Ensure the node still has valid structure after merging
        node.ensure_valid_structure(silent=True)

    def _borrow_from_prev(self, node, index):
        """
        Borrow a key from the left sibling to prevent underflow.
        """
        child = node.children[index]
        left_sibling = node.children[index-1]
        
        # For leaf nodes
        if child.is_leaf:
            # Move the last key-value from left sibling to child
            child.keys.insert(0, left_sibling.keys.pop())
            child.values.insert(0, left_sibling.values.pop())
            
            # Update parent key to match first key in right child
            node.keys[index-1] = child.keys[0]
        else:
            # For internal nodes
            # Move parent's key down to child
            child.keys.insert(0, node.keys[index-1])
            
            # Move right-most child pointer from left sibling if needed
            if left_sibling.children:
                child.children.insert(0, left_sibling.children.pop())
                # Update its parent pointer
                if child.children[0]:
                    child.children[0].parent = child
            
            # Move left sibling's last key up to parent
            node.keys[index-1] = left_sibling.keys.pop()

    def _borrow_from_next(self, node, index):
        """
        Borrow a key from the right sibling to prevent underflow.
        """
        child = node.children[index]
        right_sibling = node.children[index + 1]
        
        # For leaf nodes
        if child.is_leaf:
            # Move the first key-value from right sibling to child
            child.keys.append(right_sibling.keys.pop(0))
            child.values.append(right_sibling.values.pop(0))
            
            # Update parent key
            node.keys[index] = right_sibling.keys[0]
        else:
            # For internal nodes
            # Move parent's key down to child
            child.keys.append(node.keys[index])
            
            # Move left-most child pointer from right sibling
            if right_sibling.children:
                child.children.append(right_sibling.children.pop(0))
                # Update its parent pointer
                if child.children[-1]:
                    child.children[-1].parent = child
            
            # Move right sibling's first key up to parent
            node.keys[index] = right_sibling.keys.pop(0)

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
                      self._fill_child(grandparent, parent_index)
                 else:
                      print("Error: Could not find parent index during recursive underflow.")

    def _handle_underflow(self, parent, child_index):
        """
        Handle underflow at a node by borrowing from siblings or merging.
        This is a wrapper for the _fill_child method for backward compatibility.
        """
        self._fill_child(parent, child_index)

    def update(self, key, new_value):
        """ Update value associated with an existing key. Return True if successful. """
        leaf_node = self._find_leaf(key)
        # Use bisect_left to find the potential index
        index = bisect.bisect_left(leaf_node.keys, key)

        # Check if the key exists at the index
        if index < len(leaf_node.keys) and leaf_node.keys[index] == key:
            leaf_node.values[index] = new_value
            return True
        else:
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

        dot = graphviz.Digraph(comment='B+ Tree', format='svg')
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
            print(f"Tree visualization saved to {filename}.svg")
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