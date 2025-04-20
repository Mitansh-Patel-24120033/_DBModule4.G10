#!/usr/bin/env python3
"""
Demo script to run and demonstrate the B+ Tree database functionality.
This script creates tables, performs operations, and visualizes the B+ Tree structure.
"""

import os
import sys
import time
import random
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid QSocketNotifier warnings
import matplotlib.pyplot as plt

from database.db_manager import Database
from database.bplustree import BPlusTree
from database.bruteforce import BruteForceDB

def demonstrate_tables():
    """Create sample tables and demonstrate basic operations."""
    print("=== Creating and testing tables ===")
    
    # Create a database (overwrite any existing demo_database.pkl)
    if os.path.exists("demo_database.pkl"):
        os.remove("demo_database.pkl")
        print("Existing demo database removed. Starting fresh with demo_database.pkl.")
    db = Database("demo_database.pkl")
    
    # Create tables (customers and orders)
    customers_table = db.create_table("customers", order=4)
    orders_table = db.create_table("orders", order=4)
    
    # Add data to the customers table
    print("\nPopulating customers table...")
    customers_data = [
        (1, {"customer_name": "Alice Smith", "Age": 30, "customer_email": "alice@example.com", "customer_phone": "111-111-1111", "customer_address": "123 Main St", "customer_image": None}),
        (2, {"customer_name": "Bob Jones", "Age": 45, "customer_email": "bob@example.com", "customer_phone": "222-222-2222", "customer_address": "456 Oak Ave", "customer_image": None}),
        (3, {"customer_name": "Carol Taylor", "Age": 28, "customer_email": "carol@example.com", "customer_phone": "333-333-3333", "customer_address": "789 Pine Rd", "customer_image": None}),
        (4, {"customer_name": "David Brown", "Age": 52, "customer_email": "david@example.com", "customer_phone": "444-444-4444", "customer_address": "135 Elm St", "customer_image": None}),
        (5, {"customer_name": "Eva Green", "Age": 35, "customer_email": "eva@example.com", "customer_phone": "555-555-5555", "customer_address": "246 Maple Dr", "customer_image": None}),
        (6, {"customer_name": "Frank White", "Age": 40, "customer_email": "frank@example.com", "customer_phone": "666-666-6666", "customer_address": "358 Cedar Ln", "customer_image": None}),
        (7, {"customer_name": "Grace Black", "Age": 27, "customer_email": "grace@example.com", "customer_phone": "777-777-7777", "customer_address": "468 Birch Blvd", "customer_image": None}),
        (8, {"customer_name": "Henry Wood", "Age": 60, "customer_email": "henry@example.com", "customer_phone": "888-888-8888", "customer_address": "579 Spruce Ct", "customer_image": None}),
        (9, {"customer_name": "Ivy Hill", "Age": 33, "customer_email": "ivy@example.com", "customer_phone": "999-999-9999", "customer_address": "680 Willow Way", "customer_image": None}),
        (10, {"customer_name": "Jack King", "Age": 47, "customer_email": "jack@example.com", "customer_phone": "101-010-1010", "customer_address": "791 Aspen Pl", "customer_image": None}),
        (11, {"customer_name": "Kim Lee", "Age": 29, "customer_email": "kim@example.com", "customer_phone": "121-212-1212", "customer_address": "802 Chestnut Cir", "customer_image": None}),
        (12, {"customer_name": "Leo Scott", "Age": 55, "customer_email": "leo@example.com", "customer_phone": "131-313-1313", "customer_address": "913 Redwood Trl", "customer_image": None}),
        (13, {"customer_name": "Mia Adams", "Age": 31, "customer_email": "mia@example.com", "customer_phone": "141-414-1414", "customer_address": "102 Fir St", "customer_image": None}),
        (14, {"customer_name": "Noah Clark", "Age": 41, "customer_email": "noah@example.com", "customer_phone": "151-515-1515", "customer_address": "203 Poplar Rd", "customer_image": None}),
        (15, {"customer_name": "Olga Evans", "Age": 38, "customer_email": "olga@example.com", "customer_phone": "161-616-1616", "customer_address": "304 Cypress Ln", "customer_image": None})
    ]
    for cust_id, cust_info in customers_data:
        customers_table.insert(cust_id, cust_info)
    
    # Add data to the orders table
    print("\nPopulating orders table...")
    orders_data = [
        (1, {"customer_id": 1, "order_status": "Pending",   "Total_Amount": 100.00, "Pickup_Date": "2023-01-01", "Delivery_Date": "2023-01-05"}),
        (2, {"customer_id": 2, "order_status": "Delivered", "Total_Amount": 250.50, "Pickup_Date": "2023-02-10", "Delivery_Date": "2023-02-15"}),
        (3, {"customer_id": 3, "order_status": "Picked up", "Total_Amount": 75.25,  "Pickup_Date": "2023-03-05", "Delivery_Date": "2023-03-06"}),
        (4, {"customer_id": 4, "order_status": "Pending",   "Total_Amount": 125.75, "Pickup_Date": "2023-04-12", "Delivery_Date": None}),
        (5, {"customer_id": 5, "order_status": "Delivered", "Total_Amount": 300.00, "Pickup_Date": "2023-05-20", "Delivery_Date": "2023-05-25"}),
        (6, {"customer_id": 6, "order_status": "Picked up", "Total_Amount": 50.00,  "Pickup_Date": "2023-06-15", "Delivery_Date": "2023-06-16"}),
        (7, {"customer_id": 7, "order_status": "Pending",   "Total_Amount": 80.80,  "Pickup_Date": "2023-07-01", "Delivery_Date": None}),
        (8, {"customer_id": 8, "order_status": "Delivered", "Total_Amount": 220.40, "Pickup_Date": "2023-08-22", "Delivery_Date": "2023-08-27"}),
        (9, {"customer_id": 9, "order_status": "Picked up", "Total_Amount": 60.60,  "Pickup_Date": "2023-09-10", "Delivery_Date": "2023-09-11"}),
        (10, {"customer_id": 10, "order_status": "Pending",   "Total_Amount": 150.15, "Pickup_Date": "2023-10-05", "Delivery_Date": None}),
        (11, {"customer_id": 11, "order_status": "Delivered", "Total_Amount": 175.75, "Pickup_Date": "2023-11-12", "Delivery_Date": "2023-11-17"}),
        (12, {"customer_id": 12, "order_status": "Picked up", "Total_Amount": 90.90,  "Pickup_Date": "2023-12-01", "Delivery_Date": "2023-12-02"}),
        (13, {"customer_id": 13, "order_status": "Pending",   "Total_Amount": 110.10, "Pickup_Date": "2024-01-03", "Delivery_Date": None}),
        (14, {"customer_id": 14, "order_status": "Delivered", "Total_Amount": 130.30, "Pickup_Date": "2024-02-14", "Delivery_Date": "2024-02-19"}),
        (15, {"customer_id": 15, "order_status": "Picked up", "Total_Amount": 140.40, "Pickup_Date": "2024-03-20", "Delivery_Date": "2024-03-21"})
    ]
    for order_id, order_info in orders_data:
        orders_table.insert(order_id, order_info)
    
    # Generate visualizations of the B+ trees
    print("\nGenerating B+ Tree visualizations...")
    os.makedirs("visualizations", exist_ok=True)
    
    # Visualize customers table B+ tree
    try:
        customers_table.visualize("visualizations/customers_bplus_tree")
        print("Customers B+ Tree visualization saved to visualizations/customers_bplus_tree.png")
    except Exception as e:
        print(f"Error visualizing customers table: {e}")
    
    # Visualize orders table B+ tree
    try:
        orders_table.visualize("visualizations/orders_bplus_tree")
        print("Orders B+ Tree visualization saved to visualizations/orders_bplus_tree.png")
    except Exception as e:
        print(f"Error visualizing orders table: {e}")
    
    # Demonstrate select operation
    print("\nSelecting data:")
    customer = customers_table.select(3)
    print(f"Customer with ID 3: {customer}")
    
    order = orders_table.select(3)
    print(f"Order with ID 3: {order}")
    
    # Demonstrate range query
    print("\nRange queries:")
    cs_orders = orders_table.range_query(1, 2)
    print("Orders with IDs 1-2:")
    for order_id, order_info in cs_orders:
        print(f"  ID: {order_id}, Status: {order_info['order_status']}")
    
    # Demonstrate update
    print("\nUpdating data:")
    customers_table.update(1, {"customer_name": "Alice Smith", "Age": 31, "customer_email": "alice@example.com", "customer_phone": "111-111-1111", "customer_address": "123 Main St", "customer_image": None})
    updated_customer = customers_table.select(1)
    print(f"Updated customer with ID 1: {updated_customer}")
    
    # Demonstrate delete
    print("\nDeleting data:")
    customers_table.delete(5)
    deleted_customer = customers_table.select(5)
    print(f"Customer with ID 5 after deletion: {deleted_customer}")
    
    # Generate visualization after modifications
    try:
        customers_table.visualize("visualizations/customers_bplus_tree_after")
        print("Modified Customers B+ Tree visualization saved to visualizations/customers_bplus_tree_after.png")
    except Exception as e:
        print(f"Error visualizing modified customers table: {e}")
    
    # Save the database
    print("\nSaving database...")
    db.save_database()
    
    # Demonstrate persistence by reloading
    print("\nReloading database to verify persistence...")
    loaded_db = Database("demo_database.pkl")
    loaded_tables = loaded_db.list_tables()
    print(f"Tables in loaded database: {loaded_tables}")

def run_performance_comparison():
    """Run a comprehensive performance comparison between B+ Tree and BruteForceDB."""
    print("\n=== Performance Comparison: B+ Tree vs Brute Force ===")
    
    # Test with different set sizes
    set_sizes = [500, 1000, 5000, 10000]
    
    # Store results for plotting
    results = {
        'sizes': set_sizes,
        'bplus_insert': [],
        'brute_insert': [],
        'bplus_search': [],
        'brute_search': [],
        'bplus_delete': [],
        'brute_delete': [],
        'bplus_range': [],
        'brute_range': [],
        'bplus_memory': [],
        'brute_memory': []
    }
    
    for data_size in set_sizes:
        print(f"\n--- Testing with {data_size} records ---")
        
        # Set up data structures
        bplus_tree = BPlusTree(order=10)
        brute_force = BruteForceDB()
        
        # Generate test data
        keys = random.sample(range(data_size * 5), data_size)
        values = [f"value_{k}" for k in keys]
        
        # Compare insertion
        print("\nComparing insertion performance:")
        
        start_time = time.time()
        for i, key in enumerate(keys):
            bplus_tree.insert(key, values[i])
        bplus_insert_time = time.time() - start_time
        results['bplus_insert'].append(bplus_insert_time)
        print(f"B+ Tree insertion time: {bplus_insert_time:.6f} seconds")
        
        start_time = time.time()
        for i, key in enumerate(keys):
            brute_force.insert(key, values[i])
        brute_insert_time = time.time() - start_time
        results['brute_insert'].append(brute_insert_time)
        print(f"Brute Force insertion time: {brute_insert_time:.6f} seconds")
        
        # Visualize the performance B+ tree for the largest dataset only
        if data_size == max(set_sizes):
            # Skip visualizing the tree as it can be resource-intensive
            # try:
            #     os.makedirs("visualizations", exist_ok=True)
            #     bplus_tree.visualize_tree("visualizations/performance_bplus_tree")
            #     print("\nPerformance B+ Tree visualization saved to visualizations/performance_bplus_tree.png")
            # except Exception as e:
            #     print(f"\nError visualizing performance B+ tree: {e}")
            pass
        
        # Compare search
        print("\nComparing search performance:")
        search_keys = random.sample(keys, min(100, data_size))
        
        start_time = time.time()
        for key in search_keys:
            bplus_tree.search(key)
        bplus_search_time = time.time() - start_time
        results['bplus_search'].append(bplus_search_time)
        print(f"B+ Tree search time: {bplus_search_time:.6f} seconds")
        
        start_time = time.time()
        for key in search_keys:
            brute_force.search(key)
        brute_search_time = time.time() - start_time
        results['brute_search'].append(brute_search_time)
        print(f"Brute Force search time: {brute_search_time:.6f} seconds")
        
        # Compare deletion (new)
        print("\nComparing deletion performance:")
        delete_keys = random.sample(keys, min(100, data_size))
        
        start_time = time.time()
        for key in delete_keys:
            bplus_tree.delete(key)
        bplus_delete_time = time.time() - start_time
        results['bplus_delete'].append(bplus_delete_time)
        print(f"B+ Tree deletion time: {bplus_delete_time:.6f} seconds")
        
        start_time = time.time()
        for key in delete_keys:
            brute_force.delete(key)
        brute_delete_time = time.time() - start_time
        results['brute_delete'].append(brute_delete_time)
        print(f"Brute Force deletion time: {brute_delete_time:.6f} seconds")
        
        # Compare range query
        print("\nComparing range query performance:")
        range_start = data_size // 4
        range_end = range_start + data_size // 2
        
        start_time = time.time()
        bplus_result = bplus_tree.range_query(range_start, range_end)
        bplus_range_time = time.time() - start_time
        results['bplus_range'].append(bplus_range_time)
        print(f"B+ Tree range query time: {bplus_range_time:.6f} seconds, found {len(bplus_result)} results")
        
        start_time = time.time()
        brute_result = brute_force.range_query(range_start, range_end)
        brute_range_time = time.time() - start_time
        results['brute_range'].append(brute_range_time)
        print(f"Brute Force range query time: {brute_range_time:.6f} seconds, found {len(brute_result)} results")
        
        # Compare memory usage
        print("\nComparing memory usage:")
        bplus_memory = bplus_tree.get_memory_usage()
        results['bplus_memory'].append(bplus_memory)
        print(f"B+ Tree memory usage: {bplus_memory} bytes")
        
        brute_memory = brute_force.get_memory_usage()
        results['brute_memory'].append(brute_memory)
        print(f"Brute Force memory usage: {brute_memory} bytes")
    
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
    """Run the demonstration of the B+ Tree database functionality."""
    print("=== B+ Tree Database Demonstration ===\n")
    
    # Demonstrate table operations
    demonstrate_tables()
    
    # Run performance comparison
    run_performance_comparison()
    
    print("\nDemonstration completed successfully!")
    print("B+ Tree visualizations have been saved in the 'visualizations' directory.")

if __name__ == "__main__":
    main() 