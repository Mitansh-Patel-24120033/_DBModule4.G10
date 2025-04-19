#!/usr/bin/env python3
"""
Demo script to run and demonstrate the B+ Tree database functionality.
This script creates tables, performs operations, and visualizes the B+ Tree structure.
"""

import os
import sys
import time
import random
import matplotlib.pyplot as plt

from database.db_manager import Database
from database.bplustree import BPlusTree
from database.bruteforce import BruteForceDB

def demonstrate_tables():
    """Create sample tables and demonstrate basic operations."""
    print("=== Creating and testing tables ===")
    
    # Create a database
    db = Database("demo_database.pkl")
    
    # Create tables (students and courses)
    students_table = db.create_table("students", order=4)
    courses_table = db.create_table("courses", order=4)
    
    # Add data to the students table
    print("\nPopulating students table...")
    students_data = [
        (1, {"name": "John Smith", "age": 20, "major": "Computer Science"}),
        (2, {"name": "Emma Johnson", "age": 22, "major": "Physics"}),
        (3, {"name": "Michael Davis", "age": 21, "major": "Mathematics"}),
        (4, {"name": "Sophia Wilson", "age": 23, "major": "Engineering"}),
        (5, {"name": "Daniel Taylor", "age": 20, "major": "Chemistry"}),
        (6, {"name": "Olivia Brown", "age": 19, "major": "Biology"}),
        (7, {"name": "William Jones", "age": 22, "major": "Psychology"}),
        (8, {"name": "Ava Miller", "age": 21, "major": "Economics"}),
        (9, {"name": "James Garcia", "age": 20, "major": "Business"}),
        (10, {"name": "Charlotte Martinez", "age": 23, "major": "Sociology"}),
        (11, {"name": "Benjamin Lee", "age": 24, "major": "Anthropology"}),
        (12, {"name": "Mia Rodriguez", "age": 19, "major": "English Literature"}),
        (13, {"name": "Henry Wilson", "age": 22, "major": "Art History"}),
        (14, {"name": "Amelia Thomas", "age": 21, "major": "Political Science"}),
        (15, {"name": "Alexander White", "age": 20, "major": "Communications"})
    ]
    
    for student_id, student_info in students_data:
        students_table.insert(student_id, student_info)
    
    # Add data to the courses table
    print("\nPopulating courses table...")
    courses_data = [
        (101, {"title": "Introduction to Programming", "credits": 3, "department": "Computer Science"}),
        (102, {"title": "Data Structures", "credits": 4, "department": "Computer Science"}),
        (201, {"title": "Calculus I", "credits": 4, "department": "Mathematics"}),
        (202, {"title": "Linear Algebra", "credits": 3, "department": "Mathematics"}),
        (301, {"title": "Quantum Mechanics", "credits": 5, "department": "Physics"}),
        (302, {"title": "Thermodynamics", "credits": 4, "department": "Physics"}),
        (401, {"title": "Organic Chemistry", "credits": 5, "department": "Chemistry"}),
        (402, {"title": "Biochemistry", "credits": 4, "department": "Chemistry"}),
        (501, {"title": "Molecular Biology", "credits": 4, "department": "Biology"}),
        (502, {"title": "Ecology", "credits": 3, "department": "Biology"}),
        (601, {"title": "Cognitive Psychology", "credits": 3, "department": "Psychology"}),
        (602, {"title": "Microeconomics", "credits": 4, "department": "Economics"}),
        (701, {"title": "Marketing Principles", "credits": 3, "department": "Business"}),
        (702, {"title": "Social Theory", "credits": 4, "department": "Sociology"}),
        (801, {"title": "Literary Analysis", "credits": 3, "department": "English Literature"})
    ]
    
    for course_id, course_info in courses_data:
        courses_table.insert(course_id, course_info)
    
    # Generate visualizations of the B+ trees
    print("\nGenerating B+ Tree visualizations...")
    # Create visualizations directory if it doesn't exist
    os.makedirs("visualizations", exist_ok=True)
    
    # Visualize students table B+ tree
    try:
        students_table.visualize("visualizations/students_bplus_tree")
        print("Students B+ Tree visualization saved to visualizations/students_bplus_tree.png")
    except Exception as e:
        print(f"Error visualizing students table: {e}")
    
    # Visualize courses table B+ tree
    try:
        courses_table.visualize("visualizations/courses_bplus_tree")
        print("Courses B+ Tree visualization saved to visualizations/courses_bplus_tree.png")
    except Exception as e:
        print(f"Error visualizing courses table: {e}")
    
    # Demonstrate select operation
    print("\nSelecting data:")
    student = students_table.select(3)
    print(f"Student with ID 3: {student}")
    
    course = courses_table.select(102)
    print(f"Course with ID 102: {course}")
    
    # Demonstrate range query
    print("\nRange queries:")
    cs_courses = courses_table.range_query(101, 102)
    print("Computer Science courses (IDs 101-102):")
    for course_id, course_info in cs_courses:
        print(f"  ID: {course_id}, Title: {course_info['title']}")
    
    # Demonstrate update
    print("\nUpdating data:")
    students_table.update(1, {"name": "John Smith", "age": 21, "major": "Computer Science"})
    updated_student = students_table.select(1)
    print(f"Updated student with ID 1: {updated_student}")
    
    # Demonstrate delete
    print("\nDeleting data:")
    students_table.delete(5)
    deleted_student = students_table.select(5)
    print(f"Student with ID 5 after deletion: {deleted_student}")
    
    # Generate visualization after modifications
    try:
        students_table.visualize("visualizations/students_bplus_tree_after")
        print("Modified Students B+ Tree visualization saved to visualizations/students_bplus_tree_after.png")
    except Exception as e:
        print(f"Error visualizing modified students table: {e}")
    
    # Save the database
    print("\nSaving database...")
    db.save_database()
    
    # Demonstrate persistence by reloading
    print("\nReloading database to verify persistence...")
    loaded_db = Database("demo_database.pkl")
    loaded_tables = loaded_db.list_tables()
    print(f"Tables in loaded database: {loaded_tables}")
    
    # Clean up the database file
    if os.path.exists("demo_database.pkl"):
        os.remove("demo_database.pkl")
        print("Cleaned up demo database file.")

def run_performance_comparison():
    """Run a comprehensive performance comparison between B+ Tree and BruteForceDB."""
    print("\n=== Performance Comparison: B+ Tree vs Brute Force ===")
    
    # Test with different set sizes
    set_sizes = [50, 100, 200, 500]
    
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
            try:
                os.makedirs("visualizations", exist_ok=True)
                bplus_tree.visualize_tree("visualizations/performance_bplus_tree")
                print("\nPerformance B+ Tree visualization saved to visualizations/performance_bplus_tree.png")
            except Exception as e:
                print(f"\nError visualizing performance B+ tree: {e}")
        
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