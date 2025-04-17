# _DBModule4.G10
This is the repository containing the files for Module 4 Task of Databases(2025) at IIT Gandhinagar performed by Group 10

# Lightweight DBMS with B+ Tree Index (Module 4)

A lightweight Database Management System (DBMS) implementation in Python that uses a B+ Tree for indexing. This project enables efficient data storage and retrieval, with support for basic database operations like insertion, update, deletion, selection, and range queries.

## Project Structure

```
db_management_system/
├── database/
│   ├── __init__.py       # Package initialization
│   ├── bplustree.py      # B+ Tree implementation
│   ├── bruteforce.py     # Brute force implementation for comparison
│   ├── db_manager.py     # Database manager
│   └── table.py          # Table abstraction
├── report.ipynb          # Report with analysis and visualizations
└── requirements.txt      # Project dependencies
```

## Features

### B+ Tree Implementation
- Balanced tree structure for O(log n) search complexity
- Separate handling for leaf and internal nodes
- Parent pointers for upward traversal
- Next-leaf pointers for efficient range queries
- Automatic node splitting and merging to maintain balance
- Visualization capability using graphviz

### Database Management
- Create, delete, and retrieve tables
- Insert, update, delete and select operations
- Range queries for efficient data retrieval
- Persistence using pickle serialization
- Memory usage tracking

### Performance Analysis
- Comparison with brute force approach
- Benchmarking for insertion, search, deletion, and range queries
- Memory usage comparison

## Running the Demo

The included demo script demonstrates the database functionality:

```bash
python run_demo.py
```

This demonstrates:
1. Creating database tables
2. Performing CRUD operations (Create, Read, Update, Delete)
3. Executing range queries
4. Testing database persistence
5. Comparing performance with a brute force approach

## Performance Results

The B+ Tree implementation significantly outperforms the brute force approach:
- **Insertion**: B+ Tree's O(log n) vs. Brute Force's O(n) complexity
- **Search**: Efficient traversal with logarithmic complexity
- **Range Queries**: Fast retrieval using leaf node connections
- **Memory Usage**: More efficient memory utilization

## Implementation Notes

The B+ Tree implementation follows standard algorithms with:
- Keys stored in sorted order within nodes
- Non-leaf nodes containing only keys and child pointers
- Leaf nodes containing keys and associated values
- Leaf nodes linked together for efficient sequential access
- Automatic balancing through node splitting and merging

## Dependencies

- Python 3.6+
- matplotlib (for visualization)
- graphviz (for tree visualization)
- numpy (for numerical operations)

Install dependencies with:
```
pip install -r requirements.txt
```

## Contributors

| Name | ID | Email |
|------|-------|-------|
| Mitansh Patel | 24120033 | mitansh.patel@iitgn.ac.in |
| Nishit Prajapati | 24120000 | nishit.prajapati@iitgn.ac.in |
| Chinteshwar Dhakate | 24120000 | chinteshwar.dhakate@iitgn.ac.in |

