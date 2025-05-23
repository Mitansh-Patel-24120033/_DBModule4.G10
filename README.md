# _DBModule4.G10
This is the repository containing the files for Module 4 Task of Databases(2025) at IIT Gandhinagar performed by Group 10

# B+ Tree Database Management System

This repository contains a Python-based lightweight Database Management System using B+ trees for indexing. It fulfills Module 4 requirements for the Databases (2025) course at IIT Gandhinagar by Group 10.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [Demo Script](#demo-script)
  - [Report](#report)
- [Performance Testing](#performance-testing)
- [Project Structure](#project-structure)
- [Contributors](#contributors)

## Features

- **B+ Tree Core**: Balanced tree with efficient insertion, deletion, exact search, and range query operations.
- **Brute-Force Comparison**: Benchmark insertion, search, delete, range queries, random operations, and memory usage against a naive implementation.
- **Visualization**: Generate Graphviz PNGs of tree structures in real time.
- **Web-based UI**: Flask app to perform CRUD and range operations on tables and view the B+ tree.
- **Automated Benchmarking**: Matplotlib plots for performance across multiple dataset sizes.
- **Persistence**: Store and reload the database state using pickle serialization.
- **Report Template**: Jupyter notebook (`report.ipynb`) with placeholders for documentation and analysis.

## Getting Started

### Requirements

- Python 3.6+ installed
- `pip` package manager
- System Graphviz binaries (e.g., `sudo apt-get install graphviz` on Ubuntu)

### Installation

```bash
# Clone the repo
git clone <repository-url>
cd db_management_system
# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Web Interface

Start the Flask-based UI:

```bash
python app.py
```

Open your browser at http://127.0.0.1:5000/ to:
- View the homepage:
  ![Homepage Screenshot](db_management_system/homepage.png)
  *Homepage showing options for database management and batch performance analysis.*
- Create or delete tables
- Insert, update, delete, search, and range query records
- View the live B+ tree structure SVG

From the homepage:
*   **Databases:** Click this button to view, create, or delete databases and manage tables within them.
*   **Batch Performance Analysis:** Click this button to run and view performance benchmarks (insertion, search, deletion, range query, random operations, memory usage) comparing the B+ Tree and Brute Force methods across various dataset sizes (`[500, 1000, 5000, 10000]`) using randomly generated keys.

### Demo Script

Run a demonstration of table creation, sample data insertion, basic CRUD, tree visualization (SVG), and performance benchmarking. You can control the number of demo rows inserted using the `--rows` argument:

```bash
# Default: Insert 100 rows
python run_demo.py

# Custom: Insert 500 rows (recommended)
python run_demo.py --rows 500
```

Outputs:
- Demo tables under `customdb/demo_database.pkl` with the specified number of records each
- CRUD operation logs
- B+ tree SVGs in `visualizations/`
- Performance charts (insertion, search, delete, range, memory) in `visualizations/`

### Report

Launch Jupyter Notebook and open the template to write your analysis:

```bash
jupyter notebook report.ipynb
```

Run all cells to regenerate charts and visualizations.

## Performance Testing

Benchmarks are run for dataset sizes `[500, 1000, 5000, 10000]`. Metrics measured:
- Insertion time
- Search time
- Deletion time
- Range query time
- Random mixed operations
- Memory usage

Charts are saved under `visualizations/` for comparison between the B+ tree and brute-force approaches.

## Project Structure

```
.
├── app.py                      # Flask web interface
├── run_demo.py                 # Demo script & performance benchmarking
├── database/                   # Core database modules
│   ├── bplustree.py            # B+ tree implementation
│   ├── bruteforce.py           # Brute force comparator
│   ├── db_manager.py           # Database manager & persistence
│   ├── table.py                # Table abstraction (uses BPlusTree)
│   └── performance_utils.py    # Performance benchmark utility functions
├── templates/                  # HTML templates for Flask
├── static/                     # Static assets & visualizations
│   └── visualizations/         # Generated SVGs (trees) and PNG charts
├── report.ipynb                # Jupyter notebook report template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```


## Contributors

| Name                  | ID        | Email                           |
|-----------------------|-----------|---------------------------------|
| Mitansh Patel         | 24120033  | mitansh.patel@iitgn.ac.in       |
| Nishit Prajapati      | 24120036  | nishit.prajapati@iitgn.ac.in    |
| Chinteshwar Dhakate   | 24120024  | chinteshwar.dhakate@iitgn.ac.in |

## Module 4 Tasks

Below is an outline of the deliverables for Module 4, with the status of each implementation:

| Task | Description                                               | Status      |
|------|-----------------------------------------------------------|-------------|
| 1    | Implement B+ tree core operations (insert, delete, search, range) | ✅ Completed |
| 2    | Implement BruteForceDB comparator for benchmarking         | ✅ Completed |
| 3    | Create Database manager and `Table` abstraction            | ✅ Completed |
| 4    | Conduct comprehensive performance testing                 | ✅ Completed |
| 5    | Visualize B+ tree structures with Graphviz                | ✅ Completed |
| 6    | Add persistence (save/load database to disk)              | ✅ Completed |
| 7    | Provide Jupyter Notebook Report                           | ✅ Completed |
| ➕   | Bonus: Develop a web-based UI for CRUD and visualization  | ✅ Completed |
