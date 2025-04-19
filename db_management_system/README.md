# _DBModule4.G10
This is the repository containing the files for Module 4 Task of Databases(2025) at IIT Gandhinagar performed by Group 10

# B+ Tree Database Management System

A database management system implementation using B+ trees for efficient indexing and querying.

## Features

- B+ tree implementation with efficient insertion, deletion, search, and range query operations
- Table creation and management with automatic indexing
- Performance comparison with brute force approaches
- Tree structure visualization using Graphviz
- Database persistence through file storage
- Comprehensive performance testing framework

## Requirements

- Python 3.6+
- matplotlib
- graphviz (for visualization)
- jupyter (for running the report notebook)

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install matplotlib graphviz jupyter
```

3. Install Graphviz system package (required for visualization):

**On Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**On Fedora/CentOS:**
```bash
sudo dnf install graphviz
```

**On macOS:**
```bash
brew install graphviz
```

## Usage

### Running the Demo

To run the demonstration script which creates sample tables, performs operations, and generates visualizations:

```bash
python run_demo.py
```

This will:
- Create sample tables (students and courses)
- Populate the tables with data
- Demonstrate basic operations (insert, select, update, delete, range query)
- Generate B+ tree visualizations
- Run performance comparison between B+ tree and brute force approaches
- Create performance comparison charts

### Generating the Report

To generate the project report:

1. Start Jupyter Notebook:

```bash
jupyter notebook
```

2. Open `report.ipynb` in the Jupyter interface
3. Run all cells to generate the complete report with visualizations

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

## Performance Testing

The system includes comprehensive performance testing that compares B+ tree with brute force approaches on:

- Insertion time
- Search time
- Deletion time
- Range query time
- Random operations
- Memory usage

Multiple dataset sizes are tested to demonstrate how performance scales with data volume.

## Web Interface

A web-based UI is provided for interacting with the database system. This allows you to:

- Create and delete tables
- Insert, update, delete, and search for records
- Perform range queries
- Visualize the B+ tree structure in real-time

To run the web interface:

```bash
python app.py
```

Then open your browser and go to http://127.0.0.1:5000/

### Web UI Features:

1. **Home Page**: Lists all tables and provides form to create new tables
2. **Table View**: Shows all records in a table with options to:
   - Insert new records
   - Update existing records
   - Delete records
   - Search for specific keys
   - Perform range queries
3. **B+ Tree Visualization**: Each table page displays a visualization of its current B+ tree structure

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

| Name | ID | Email |
|------|-------|-------|
| Mitansh Patel | 24120033 | mitansh.patel@iitgn.ac.in |
| Nishit Prajapati | 24120000 | nishit.prajapati@iitgn.ac.in |
| Chinteshwar Dhakate | 24120000 | chinteshwar.dhakate@iitgn.ac.in |
