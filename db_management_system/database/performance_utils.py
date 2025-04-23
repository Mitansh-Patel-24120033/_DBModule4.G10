import time
import random
from .bplustree import BPlusTree
from .bruteforce import BruteForceDB

def run_performance_benchmarks(sizes):
    """
    Runs performance benchmarks for B+ Tree vs BruteForceDB across given sizes.
    """
    results = {
        'sizes': sizes,
        'bplus_insert': [], 'brute_insert': [],
        'bplus_search': [], 'brute_search': [],
        'bplus_delete': [], 'brute_delete': [],
        'bplus_range': [], 'brute_range': [],
        'bplus_memory': [], 'brute_memory': [],
        'bplus_random': [], 'brute_random': []
    }

    for n in sizes:
        print(f"\n--- Benchmarking with {n} records ---")
        
        # --- Setup for size N ---
        # Use fresh instances for each size to isolate tests
        bpt = BPlusTree(order=10)
        bf = BruteForceDB()
        keys = random.sample(range(n * 5), n) # Generate unique keys
        vals = [f'value_{k}' for k in keys]
        
        # --- Insertion ---
        print("Benchmarking Insertion...")
        t0 = time.time()
        for i, k in enumerate(keys): bpt.insert(k, vals[i])
        results['bplus_insert'].append(time.time() - t0)
        
        t0 = time.time()
        for i, k in enumerate(keys): bf.insert(k, vals[i])
        results['brute_insert'].append(time.time() - t0)
        
        # --- Search ---
        print("Benchmarking Search...")
        # Search for a subset of existing keys
        search_keys = random.sample(keys, min(100, n)) 
        t0 = time.time()
        for k in search_keys: bpt.search(k)
        results['bplus_search'].append(time.time() - t0)
        
        t0 = time.time()
        for k in search_keys: bf.search(k)
        results['brute_search'].append(time.time() - t0)
        
        # --- Deletion ---
        print("Benchmarking Deletion...")
        # Delete a subset of existing keys from copies of the structures
        # Create copies to avoid affecting range query results
        bpt_del_copy = BPlusTree(order=10) 
        bf_del_copy = BruteForceDB()
        for i, k in enumerate(keys): 
            bpt_del_copy.insert(k, vals[i])
            bf_del_copy.insert(k, vals[i])
            
        delete_keys = random.sample(keys, min(100, n))
        t0 = time.time()
        for k in delete_keys: bpt_del_copy.delete(k)
        results['bplus_delete'].append(time.time() - t0)
        
        t0 = time.time()
        for k in delete_keys: bf_del_copy.delete(k)
        results['brute_delete'].append(time.time() - t0)
        
        # --- Range Query ---
        print("Benchmarking Range Query...")
        # Define a range covering roughly half the key space
        range_start = n // 4
        range_end = range_start + n // 2
        t0 = time.time()
        bpt.range_query(range_start, range_end)
        results['bplus_range'].append(time.time() - t0)
        
        t0 = time.time()
        bf.range_query(range_start, range_end)
        results['brute_range'].append(time.time() - t0)
        
        # --- Memory Usage (After Insertions) ---
        print("Benchmarking Memory Usage...")
        # Measure memory of the original structures after all insertions
        results['bplus_memory'].append(bpt.get_memory_usage())
        results['brute_memory'].append(bf.get_memory_usage())
        
        # --- Random Mixed Operations ---
        print("Benchmarking Random Operations...")
        # Test on fresh copies to ensure consistent starting state
        bpt_rand_copy = BPlusTree(order=10)
        bf_rand_copy = BruteForceDB()
        # Initial population (e.g., half the keys)
        initial_keys = keys[:n//2]
        initial_vals = vals[:n//2]
        for i, k in enumerate(initial_keys):
            bpt_rand_copy.insert(k, initial_vals[i])
            bf_rand_copy.insert(k, initial_vals[i])

        # Generate random operations (e.g., half the size)
        num_ops = n // 2
        operations = []
        for _ in range(num_ops):
            op_type = random.choice(['insert', 'search', 'delete'])
            if op_type == 'insert':
                # Insert keys from the second half of the original keys
                insert_key_index = random.randrange(n // 2, n)
                key_to_insert = keys[insert_key_index]
                val_to_insert = vals[insert_key_index]
                operations.append(('insert', key_to_insert, val_to_insert))
            elif op_type == 'search':
                # Search for keys from the initial set
                search_key_index = random.randrange(0, n // 2)
                key_to_search = keys[search_key_index]
                operations.append(('search', key_to_search))
            else: # delete
                # Delete keys from the initial set
                delete_key_index = random.randrange(0, n // 2)
                key_to_delete = keys[delete_key_index]
                operations.append(('delete', key_to_delete))

        # Time B+ Tree random operations
        t0 = time.time()
        for op in operations:
            if op[0] == 'insert': bpt_rand_copy.insert(op[1], op[2])
            elif op[0] == 'search': bpt_rand_copy.search(op[1])
            elif op[0] == 'delete': bpt_rand_copy.delete(op[1])
        results['bplus_random'].append(time.time() - t0)

        # Time Brute Force random operations
        t0 = time.time()
        for op in operations:
            if op[0] == 'insert': bf_rand_copy.insert(op[1], op[2])
            elif op[0] == 'search': bf_rand_copy.search(op[1])
            elif op[0] == 'delete': bf_rand_copy.delete(op[1])
        results['brute_random'].append(time.time() - t0)
        
        print(f"Finished benchmarking for size {n}.")

    return results

# Example usage (optional, for testing the utility directly)
if __name__ == '__main__':
    test_sizes = [100, 500]
    benchmark_results = run_performance_benchmarks(test_sizes)
    print("\n--- Benchmark Results ---")
    import json
    print(json.dumps(benchmark_results, indent=2)) 