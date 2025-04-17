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
        (5, {"name": "Daniel Taylor", "age": 20, "major": "Chemistry"})
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
        (301, {"title": "Quantum Mechanics", "credits": 5, "department": "Physics"})
    ]
    
    for course_id, course_info in courses_data:
        courses_table.insert(course_id, course_info)
    
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
    """Run a simple performance comparison between B+ Tree and BruteForceDB."""
    print("\n=== Performance Comparison: B+ Tree vs Brute Force ===")
    
    # Set up data structures
    bplus_tree = BPlusTree(order=10)
    brute_force = BruteForceDB()
    
    # Generate test data
    data_size = 1000
    keys = random.sample(range(data_size * 5), data_size)
    values = [f"value_{k}" for k in keys]
    
    # Compare insertion
    print("\nComparing insertion performance:")
    
    start_time = time.time()
    for i, key in enumerate(keys):
        bplus_tree.insert(key, values[i])
    bplus_time = time.time() - start_time
    print(f"B+ Tree insertion time: {bplus_time:.6f} seconds")
    
    start_time = time.time()
    for i, key in enumerate(keys):
        brute_force.insert(key, values[i])
    brute_time = time.time() - start_time
    print(f"Brute Force insertion time: {brute_time:.6f} seconds")
    
    # Compare search
    print("\nComparing search performance:")
    search_keys = random.sample(keys, 100)
    
    start_time = time.time()
    for key in search_keys:
        bplus_tree.search(key)
    bplus_time = time.time() - start_time
    print(f"B+ Tree search time: {bplus_time:.6f} seconds")
    
    start_time = time.time()
    for key in search_keys:
        brute_force.search(key)
    brute_time = time.time() - start_time
    print(f"Brute Force search time: {brute_time:.6f} seconds")
    
    # Compare range query
    print("\nComparing range query performance:")
    range_start = data_size // 4
    range_end = range_start + data_size // 2
    
    start_time = time.time()
    bplus_result = bplus_tree.range_query(range_start, range_end)
    bplus_time = time.time() - start_time
    print(f"B+ Tree range query time: {bplus_time:.6f} seconds, found {len(bplus_result)} results")
    
    start_time = time.time()
    brute_result = brute_force.range_query(range_start, range_end)
    brute_time = time.time() - start_time
    print(f"Brute Force range query time: {brute_time:.6f} seconds, found {len(brute_result)} results")
    
    # Compare memory usage
    print("\nComparing memory usage:")
    bplus_memory = bplus_tree.get_memory_usage()
    brute_memory = brute_force.get_memory_usage()
    print(f"B+ Tree memory usage: {bplus_memory} bytes")
    print(f"Brute Force memory usage: {brute_memory} bytes")

def main():
    """Run the demonstration of the B+ Tree database functionality."""
    print("=== B+ Tree Database Demonstration ===\n")
    
    # Demonstrate table operations
    demonstrate_tables()
    
    # Run performance comparison
    run_performance_comparison()
    
    print("\nDemonstration completed successfully!")

if __name__ == "__main__":
    main() 
