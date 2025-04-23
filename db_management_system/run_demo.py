#!/usr/bin/env python3
"""
Demo script to run and demonstrate the B+ Tree database functionality.
This script creates tables, performs operations, and visualizes the B+ Tree structure.
"""

import os
import time
import random
import argparse
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid QSocketNotifier warnings
import matplotlib.pyplot as plt

from database.db_manager import Database
from database.bplustree import BPlusTree
from database.bruteforce import BruteForceDB
from database.performance_utils import run_performance_benchmarks

# Persist demo database under customdb/
CUSTOM_DB_DIR = 'customdb'
os.makedirs(CUSTOM_DB_DIR, exist_ok=True)
DB_FILE = os.path.join(CUSTOM_DB_DIR, 'demo_database.pkl')

def demonstrate_tables(num_rows):
    """Create sample tables and demonstrate basic operations."""
    print("=== Creating and testing tables ===")
    
    # Create a database (overwrite any existing demo_database.pkl)
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Existing demo database removed. Starting fresh at {DB_FILE}.")
    db = Database(DB_FILE)
    
    # Create tables (customers and orders)
    customers_table = db.create_table("customers", order=4)
    orders_table = db.create_table("orders", order=4)
    
    # Add data to the customers table
    print(f"\nPopulating customers table with {num_rows} entries...")
    for i in range(1, num_rows+1):
        cust_info = {
            "customer_name": f"Customer {i}",
            "Age": random.randint(20, 70),
            "customer_email": f"customer{i}@example.com",
            "customer_phone": f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "customer_address": f"{random.randint(100, 999)} Main St",
            "customer_image": None
        }
        customers_table.insert(i, cust_info)
    
    # Add data to the orders table
    print(f"\nPopulating orders table with {num_rows} entries...")
    for i in range(1, num_rows+1):
        status = random.choice(["Pending", "Delivered", "Picked up"])
        pickup_date = f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        delivery_date = None if status == "Pending" else f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        order_info = {
            "customer_id": random.randint(1, 100),
            "order_status": status,
            "Total_Amount": round(random.uniform(50.0, 500.0), 2),
            "Pickup_Date": pickup_date,
            "Delivery_Date": delivery_date
        }
        orders_table.insert(i, order_info)
    
    # Generate visualizations of the B+ trees
    print("\nGenerating B+ Tree visualizations...")
    os.makedirs("visualizations", exist_ok=True)
    
    # Visualize customers table B+ tree
    try:
        customers_table.visualize("visualizations/customers_bplus_tree")
        print("Customers B+ Tree visualization saved to visualizations/customers_bplus_tree.svg")
    except Exception as e:
        print(f"Error visualizing customers table: {e}")
    
    # Visualize orders table B+ tree
    try:
        orders_table.visualize("visualizations/orders_bplus_tree")
        print("Orders B+ Tree visualization saved to visualizations/orders_bplus_tree.svg")
    except Exception as e:
        print(f"Error visualizing orders table: {e}")
    
    # Demonstrate select operation
    mid = num_rows // 2 or 1
    print("\nSelecting data:")
    customer = customers_table.select(mid)
    print(f"Customer with ID {mid}: {customer}")
    
    order = orders_table.select(mid)
    print(f"Order with ID {mid}: {order}")
    
    # Demonstrate range query
    lo, hi = 1, min(2, num_rows)
    print("\nRange queries:")
    cs_orders = orders_table.range_query(lo, hi)
    print(f"Orders with IDs {lo}-{hi}:")
    for order_id, order_info in cs_orders:
        print(f"  ID: {order_id}, Status: {order_info['order_status']}")
    
    # Demonstrate update
    print("\nUpdating data:")
    customers_table.update(1, {"customer_name": "Alice Smith", "Age": 31, "customer_email": "alice@example.com", "customer_phone": "111-111-1111", "customer_address": "123 Main St", "customer_image": None})
    updated_customer = customers_table.select(1)
    print(f"Updated customer with ID 1: {updated_customer}")
    
    # Demonstrate delete
    del_key = min(5, num_rows)
    print("\nDeleting data:")
    customers_table.delete(del_key)
    deleted_customer = customers_table.select(del_key)
    print(f"Customer with ID {del_key} after deletion: {deleted_customer}")
    
    # Generate visualization after modifications
    try:
        customers_table.visualize("visualizations/customers_bplus_tree_after")
        print("Modified Customers B+ Tree visualization saved to visualizations/customers_bplus_tree_after.svg")
    except Exception as e:
        print(f"Error visualizing modified customers table: {e}")
    
    # Save the database
    print("\nSaving database...")
    db.save_database()
    
    # Demonstrate persistence by reloading
    print("\nReloading database to verify persistence...")
    loaded_db = Database(DB_FILE)
    loaded_tables = loaded_db.list_tables()
    print(f"Tables in loaded database: {loaded_tables}")

def run_performance_comparison():
    """Run a comprehensive performance comparison between B+ Tree and BruteForceDB."""
    print("\n=== Performance Comparison: B+ Tree vs Brute Force ===")
    
    # Test with different set sizes
    set_sizes = [500, 1000, 5000, 10000]
    
    # Run the benchmarks using the utility function
    results = run_performance_benchmarks(set_sizes)
    
    # Generate performance visualizations
    try:
        os.makedirs("visualizations", exist_ok=True)
        
        # Plot metrics for multiple set sizes
        plt.figure(figsize=(10, 8))
        plt.subplot(2, 2, 1)
        plt.plot(results['sizes'], [t*1000 for t in results['bplus_insert']], 'o-', label='B+ Tree')
        plt.plot(results['sizes'], [t*1000 for t in results['brute_insert']], 's-', label='Brute Force')
        plt.title('Insertion Time')
        plt.xlabel('Number of Records')
        plt.ylabel('Time (ms)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 2)
        plt.plot(results['sizes'], [t*1000 for t in results['bplus_search']], 'o-', label='B+ Tree')
        plt.plot(results['sizes'], [t*1000 for t in results['brute_search']], 's-', label='Brute Force')
        plt.title('Search Time')
        plt.xlabel('Number of Records')
        plt.ylabel('Time (ms)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 3)
        plt.plot(results['sizes'], [t*1000 for t in results['bplus_delete']], 'o-', label='B+ Tree')
        plt.plot(results['sizes'], [t*1000 for t in results['brute_delete']], 's-', label='Brute Force')
        plt.title('Deletion Time')
        plt.xlabel('Number of Records')
        plt.ylabel('Time (ms)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 4)
        plt.plot(results['sizes'], [t*1000 for t in results['bplus_range']], 'o-', label='B+ Tree')
        plt.plot(results['sizes'], [t*1000 for t in results['brute_range']], 's-', label='Brute Force')
        plt.title('Range Query Time')
        plt.xlabel('Number of Records')
        plt.ylabel('Time (ms)')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('visualizations/performance_comparison.png')
        print("Saved performance comparison chart to visualizations/performance_comparison.png")
        
        # Memory usage chart
        plt.figure(figsize=(8, 6))
        plt.plot(results['sizes'], [m/1024 for m in results['bplus_memory']], 'o-', label='B+ Tree')
        plt.plot(results['sizes'], [m/1024 for m in results['brute_memory']], 's-', label='Brute Force')
        plt.title('Memory Usage')
        plt.xlabel('Number of Records')
        plt.ylabel('Memory (KB)')
        plt.legend()
        plt.grid(True)
        plt.savefig('visualizations/memory_comparison.png')
        print("Saved memory comparison chart to visualizations/memory_comparison.png")
        
        # Individual metric charts
        metrics = [
            {
                'name': 'Insertion Time (ms)',
                'bplus': results['bplus_insert'][-1] * 1000,
                'brute': results['brute_insert'][-1] * 1000,
                'filename': 'insertion_time'
            },
            {
                'name': 'Search Time (ms)',
                'bplus': results['bplus_search'][-1] * 1000,
                'brute': results['brute_search'][-1] * 1000,
                'filename': 'search_time'
            },
            {
                'name': 'Deletion Time (ms)',
                'bplus': results['bplus_delete'][-1] * 1000,
                'brute': results['brute_delete'][-1] * 1000,
                'filename': 'deletion_time'
            },
            {
                'name': 'Range Query Time (ms)',
                'bplus': results['bplus_range'][-1] * 1000,
                'brute': results['brute_range'][-1] * 1000,
                'filename': 'range_query_time'
            },
            {
                'name': 'Memory Usage (KB)',
                'bplus': results['bplus_memory'][-1] / 1024,
                'brute': results['brute_memory'][-1] / 1024,
                'filename': 'memory_usage'
            }
        ]
        
        # Create bar charts for the largest dataset
        for metric in metrics:
            plt.figure(figsize=(8, 5))
            
            # Create bars
            bars = plt.bar(['B+ Tree', 'Brute Force'], 
                          [metric['bplus'], metric['brute']],
                          color=['#1f77b4', '#ff7f0e'],
                          width=0.6)
            
            # Add value labels on top of each bar
            for bar in bars:
                height = bar.get_height()
                # Format small values with more decimal places
                if height < 0.1:
                    value_text = f'{height:.6f}'
                else:
                    value_text = f'{height:.4f}'
                    
                plt.text(bar.get_x() + bar.get_width()/2., 
                        height * 1.02,
                        value_text,
                        ha='center', va='bottom', fontsize=10)
            
            # Add title and labels
            plt.title(f'Performance Comparison: B+ Tree vs Brute Force')
            plt.ylabel(metric['name'])
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Save figure
            filename = f"visualizations/{metric['filename']}.png"
            plt.savefig(filename)
            print(f"Saved {filename}")
            
            plt.close()
            
    except Exception as e:
        print(f"Error generating performance comparison charts: {e}")

    # Random operations performance test
    print("\n=== Testing Random Operations Performance ===")
    
    # Set up data structures
    data_size = 1000
    bplus_tree = BPlusTree(order=10)
    brute_force = BruteForceDB()
    
    # Fill with initial data
    keys = list(range(data_size))
    values = [f"value_{k}" for k in keys]
    
    for i, key in enumerate(keys[:data_size//2]):
        bplus_tree.insert(key, values[i])
        brute_force.insert(key, values[i])
    
    # Random operations
    num_operations = 500
    operations = []
    for _ in range(num_operations):
        op = random.choice(['insert', 'search', 'delete'])
        if op == 'insert':
            key = random.randint(data_size//2, data_size-1)
            operations.append(('insert', key, f"value_{key}"))
        else:
            key = random.randint(0, data_size//2-1)
            operations.append((op, key))
    
    # Test B+ Tree
    start_time = time.time()
    for op in operations:
        if op[0] == 'insert':
            bplus_tree.insert(op[1], op[2])
        elif op[0] == 'search':
            bplus_tree.search(op[1])
        elif op[0] == 'delete':
            bplus_tree.delete(op[1])
    bplus_random_time = time.time() - start_time
    
    # Test Brute Force
    start_time = time.time()
    for op in operations:
        if op[0] == 'insert':
            brute_force.insert(op[1], op[2])
        elif op[0] == 'search':
            brute_force.search(op[1])
        elif op[0] == 'delete':
            brute_force.delete(op[1])
    brute_random_time = time.time() - start_time
    
    print(f"B+ Tree random operations time: {bplus_random_time:.6f} seconds")
    print(f"Brute Force random operations time: {brute_random_time:.6f} seconds")
    
    # Create bar chart for random operations
    plt.figure(figsize=(8, 5))
    bars = plt.bar(['B+ Tree', 'Brute Force'], 
                  [bplus_random_time * 1000, brute_random_time * 1000],
                  color=['#1f77b4', '#ff7f0e'],
                  width=0.6)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., 
                height * 1.02,
                f'{height:.4f}',
                ha='center', va='bottom', fontsize=10)
    
    plt.title('Random Operations Performance: B+ Tree vs Brute Force')
    plt.ylabel('Time (ms)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save figure
    filename = "visualizations/random_operations.png"
    plt.savefig(filename)
    print(f"Saved {filename}")
    
    plt.close()

def main():
    """Main function to run the demo script."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run B+ Tree database demo and performance tests.')
    parser.add_argument('--rows', type=int, default=100, 
                        help='Number of rows to insert into demo tables (default: 100)')
    args = parser.parse_args()

    print("Starting B+ Tree DBMS Demo...")

    # Run table demonstrations
    demonstrate_tables(num_rows=args.rows)

    # Run performance comparisons
    run_performance_comparison()

    print("\nDemonstration completed successfully!")
    print("B+ Tree visualizations have been saved in the 'visualizations' directory.")

if __name__ == "__main__":
    main() 