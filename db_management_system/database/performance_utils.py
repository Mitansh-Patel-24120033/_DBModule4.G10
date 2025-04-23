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
        'bplus_memory': [], 'brute_memory': []
    }

    for n in sizes:
        print(f"\n--- Benchmarking with {n} records ---")
        
        # --- Setup for size N ---
        # Use fresh instances for each size to isolate tests
        bpt = BPlusTree(order=10) # Example order, can be parameterized
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
        
        print(f"Finished benchmarking for size {n}.")

    return results

# Example usage (optional, for testing the utility directly)
if __name__ == '__main__':
    test_sizes = [100, 500]
    benchmark_results = run_performance_benchmarks(test_sizes)
    print("\n--- Benchmark Results ---")
    import json
    print(json.dumps(benchmark_results, indent=2)) 