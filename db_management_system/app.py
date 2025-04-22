from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
from database.db_manager import Database
from database.bplustree import BPlusTree
from database.bruteforce import BruteForceDB
import random
import time

app = Flask(__name__)
app.secret_key = 'bplus_tree_secret_key'  # For flash messages

# Global database instance
DB_FILE = 'web_database.pkl'
db = Database(DB_FILE)

# Set up custom database folder
CUSTOM_DB_DIR = 'customdb'
os.makedirs(CUSTOM_DB_DIR, exist_ok=True)

@app.route('/')
def index():
    tables = db.list_tables()
    return render_template('index.html', tables=tables)

@app.route('/performance')
def performance():
    """Run performance comparison and render results in UI."""
    # Prepare dataset sizes and result storage
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    sizes = [500, 1000, 5000, 10000]
    results = { 'sizes': sizes,
                'bplus_insert': [], 'brute_insert': [],
                'bplus_search': [], 'brute_search': [],
                'bplus_delete': [], 'brute_delete': [],
                'bplus_range': [], 'brute_range': [],
                'bplus_memory': [], 'brute_memory': [] }

    for n in sizes:
        bpt = BPlusTree(order=10)
        bf = BruteForceDB()
        keys = random.sample(range(n*5), n)
        vals = [f'value_{k}' for k in keys]
        # insertion
        t0 = time.time()
        for i, k in enumerate(keys): bpt.insert(k, vals[i])
        results['bplus_insert'].append(time.time()-t0)
        t0 = time.time()
        for i, k in enumerate(keys): bf.insert(k, vals[i])
        results['brute_insert'].append(time.time()-t0)
        # search
        sample = random.sample(keys, min(100, n))
        t0 = time.time(); [bpt.search(k) for k in sample]
        results['bplus_search'].append(time.time()-t0)
        t0 = time.time(); [bf.search(k) for k in sample]
        results['brute_search'].append(time.time()-t0)
        # delete
        dels = random.sample(keys, min(100, n))
        t0 = time.time(); [bpt.delete(k) for k in dels]
        results['bplus_delete'].append(time.time()-t0)
        t0 = time.time(); [bf.delete(k) for k in dels]
        results['brute_delete'].append(time.time()-t0)
        # range
        r0, r1 = n//4, n//4 + n//2
        t0 = time.time(); bpt.range_query(r0, r1)
        results['bplus_range'].append(time.time()-t0)
        t0 = time.time(); bf.range_query(r0, r1)
        results['brute_range'].append(time.time()-t0)
        # memory
        results['bplus_memory'].append(bpt.get_memory_usage())
        results['brute_memory'].append(bf.get_memory_usage())

    # generate charts
    out_dir = os.path.join('static', 'visualizations')
    os.makedirs(out_dir, exist_ok=True)
    # Combined comparison chart
    plt.figure(figsize=(10,8))
    plt.subplot(2,2,1)
    plt.plot(sizes, [t*1000 for t in results['bplus_insert']], 'o-', label='B+ Tree')
    plt.plot(sizes, [t*1000 for t in results['brute_insert']], 's-', label='Brute')
    plt.title('Insertion Time'); plt.xlabel('Records'); plt.ylabel('ms'); plt.legend(); plt.grid(True)
    plt.subplot(2,2,2)
    plt.plot(sizes, [t*1000 for t in results['bplus_search']], 'o-', label='B+ Tree')
    plt.plot(sizes, [t*1000 for t in results['brute_search']], 's-', label='Brute')
    plt.title('Search Time'); plt.xlabel('Records'); plt.ylabel('ms'); plt.legend(); plt.grid(True)
    plt.subplot(2,2,3)
    plt.plot(sizes, [t*1000 for t in results['bplus_delete']], 'o-', label='B+ Tree')
    plt.plot(sizes, [t*1000 for t in results['brute_delete']], 's-', label='Brute')
    plt.title('Deletion Time'); plt.xlabel('Records'); plt.ylabel('ms'); plt.legend(); plt.grid(True)
    plt.subplot(2,2,4)
    plt.plot(sizes, [t*1000 for t in results['bplus_range']], 'o-', label='B+ Tree')
    plt.plot(sizes, [t*1000 for t in results['brute_range']], 's-', label='Brute')
    plt.title('Range Query Time'); plt.xlabel('Records'); plt.ylabel('ms'); plt.legend(); plt.grid(True)
    plt.tight_layout()
    cmp_file = os.path.join(out_dir, 'performance_comparison.png')
    plt.savefig(cmp_file); plt.close()
    # Memory usage
    plt.figure()
    plt.plot(sizes, [m/1024 for m in results['bplus_memory']], 'o-', label='B+ Tree')
    plt.plot(sizes, [m/1024 for m in results['brute_memory']], 's-', label='Brute')
    plt.title('Memory Usage (KB)'); plt.xlabel('Records'); plt.ylabel('KB'); plt.legend(); plt.grid(True)
    mem_file = os.path.join(out_dir, 'memory_comparison.png')
    plt.savefig(mem_file); plt.close()

    images = {
        'Comparison Chart': 'visualizations/performance_comparison.png',
        'Memory Usage': 'visualizations/memory_comparison.png'
    }
    return render_template('performance.html', images=images)

# --- API: Database and Table Management ---
@app.route('/databases', methods=['GET', 'POST'])
def manage_databases():
    """Handle DB list page (HTML) and API for listing/creation via JSON."""
    if request.method == 'GET':
        # fetch database names from custom directory
        dbs = Database.list_databases(CUSTOM_DB_DIR)
        # If browser expects HTML, render page; else return JSON
        accept = request.accept_mimetypes
        if accept.accept_html and accept['text/html'] >= accept['application/json']:
            return render_template('databases.html', databases=dbs)
        return jsonify({'databases': dbs})
    # Creation logic: JSON API or HTML form
    if request.content_type and 'application/json' in request.content_type:
        # JSON API request
        data = request.get_json() or {}
        name = data.get('dbname')
        if not name:
            return jsonify({'error': 'Missing "dbname" parameter'}), 400
        try:
            Database.create_database(name, CUSTOM_DB_DIR)
        except FileExistsError as e:
            return jsonify({'error': str(e)}), 400
        return jsonify({'message': 'Database created', 'dbname': name}), 201
    else:
        # HTML form submission
        name = request.form.get('dbname')
        if not name:
            flash('Database name is required', 'error')
            return redirect(url_for('manage_databases'))
        try:
            Database.create_database(name, CUSTOM_DB_DIR)
            flash(f"Database '{name}' created successfully", 'success')
        except FileExistsError as e:
            flash(str(e), 'error')
        return redirect(url_for('manage_databases'))

@app.route('/databases/<dbname>', methods=['DELETE', 'POST'])
def api_delete_database(dbname):
    filename = os.path.join(CUSTOM_DB_DIR, f"{dbname}.pkl")
    if not os.path.exists(filename):
        if request.method == 'DELETE':
            return jsonify({'error': 'Database not found'}), 404
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    os.remove(filename)
    if request.method == 'DELETE':
        return jsonify({'message': 'Database deleted'}), 200
    flash(f"Database '{dbname}' deleted successfully", 'success')
    return redirect(url_for('manage_databases'))

@app.route('/databases/<dbname>/tables', methods=['GET'])
def api_list_tables(dbname):
    filename = os.path.join(CUSTOM_DB_DIR, f"{dbname}.pkl")
    # Check if database file exists
    if not os.path.exists(filename):
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    dbx = Database(filename)
    tables = dbx.list_tables()
    # Render HTML UI for listing tables
    return render_template('db_tables.html', dbname=dbname, tables=tables)

@app.route('/databases/<dbname>/tables/<table_name>', methods=['GET'])
def api_table_rows(dbname, table_name):
    filename = os.path.join(CUSTOM_DB_DIR, f"{dbname}.pkl")
    # Ensure database exists
    if not os.path.exists(filename):
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    dbx = Database(filename)
    # Ensure table exists in this database
    if table_name not in dbx.list_tables():
        flash(f"Table '{table_name}' not found in database '{dbname}'", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))
    table = dbx.get_table(table_name)
    # Detect if browser expects HTML
    accept = request.accept_mimetypes
    if accept.accept_html and accept['text/html'] >= accept['application/json']:
        # Render same UI as global table view, with DB context
        data = table.get_all_records()
        # Generate visualization
        try:
            os.makedirs('static/visualizations', exist_ok=True)
            viz_path = f"static/visualizations/{dbname}_{table_name}_bplus_tree"
            table.visualize(viz_path)
            viz_image = f"{viz_path}.svg"
        except Exception as e:
            flash(f'Error generating visualization: {str(e)}', 'warning')
            viz_image = None
        current_order = table.index.order
        return render_template('table.html', table_name=table_name, data=data, viz_image=viz_image, current_order=current_order, dbname=dbname)
    # Fallback to JSON API
    records = table.get_all_records()
    rows = [{'key': k, 'value': v} for k, v in records]
    return jsonify({'rows': rows})

# --- API: Create/Delete tables in a specific database ---
@app.route('/databases/<dbname>/tables', methods=['POST'])
def api_create_table_in_db(dbname):
    filename = os.path.join(CUSTOM_DB_DIR, f"{dbname}.pkl")
    # Ensure database file exists
    if not os.path.exists(filename):
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))

    # HTML Form submission (create via UI)
    if 'table_name' in request.form:
        table_name = request.form['table_name']
        try:
            order = int(request.form.get('order', 4) or 4)
        except ValueError:
            order = 4
        dbx = Database(filename)
        if table_name in dbx.list_tables():
            flash(f"Table '{table_name}' already exists", 'error')
        else:
            try:
                dbx.create_table(table_name, order=order)
                dbx.save_database()
                flash(f"Table '{table_name}' created successfully", 'success')
            except Exception as e:
                flash(f"Error creating table: {str(e)}", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))

    # JSON API submission (create via API)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Missing JSON payload'}), 400
    table_name = data.get('table_name')
    order = int(data.get('order', 4))
    if not table_name:
        return jsonify({'error': 'Missing "table_name" parameter'}), 400
    dbx = Database(filename)
    if table_name in dbx.list_tables():
        return jsonify({'error': 'Table already exists'}), 400
    dbx.create_table(table_name, order=order)
    dbx.save_database()
    return jsonify({'message': 'Table created', 'table': table_name}), 201

@app.route('/databases/<dbname>/tables/<table_name>', methods=['DELETE', 'POST'])
def api_delete_table_in_db(dbname, table_name):
    filename = os.path.join(CUSTOM_DB_DIR, f"{dbname}.pkl")
    # Check if database exists
    if not os.path.exists(filename):
        if request.method == 'DELETE':
            return jsonify({'error': 'Database not found'}), 404
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    dbx = Database(filename)
    # Check if table exists
    if table_name not in dbx.list_tables():
        if request.method == 'DELETE':
            return jsonify({'error': 'Table not found'}), 404
        flash(f"Table '{table_name}' not found in database '{dbname}'", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))
    # Perform deletion
    dbx.delete_table(table_name)
    dbx.save_database()
    if request.method == 'DELETE':
        return jsonify({'message': 'Table deleted', 'table': table_name}), 200
    flash(f"Table '{table_name}' deleted successfully", 'success')
    return redirect(url_for('api_list_tables', dbname=dbname))

# --- Record-level CRUD in a specific database ---
@app.route('/databases/<dbname>/tables/<table_name>/insert', methods=['POST'])
def insert_record_in_db(dbname, table_name):
    try:
        dbx = Database.get_database(dbname, CUSTOM_DB_DIR)
    except FileNotFoundError:
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    table = dbx.get_table(table_name)
    if not table:
        flash(f"Table '{table_name}' not found", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))
    key = request.form.get('key')
    value_json = request.form.get('value')
    try:
        key = int(key)
    except ValueError:
        pass
    try:
        value = json.loads(value_json)
    except Exception:
        flash('Value must be valid JSON', 'error')
        return redirect(url_for('api_table_rows', dbname=dbname, table_name=table_name))
    table.insert(key, value)
    dbx.save_database()
    flash(f'Record with key {key} inserted', 'success')
    return redirect(url_for('api_table_rows', dbname=dbname, table_name=table_name))

@app.route('/databases/<dbname>/tables/<table_name>/update', methods=['POST'])
def update_record_in_db(dbname, table_name):
    try:
        dbx = Database.get_database(dbname, CUSTOM_DB_DIR)
    except FileNotFoundError:
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    table = dbx.get_table(table_name)
    if not table:
        flash(f"Table '{table_name}' not found", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))
    key = request.form.get('key')
    value_json = request.form.get('value')
    try:
        key = int(key)
    except ValueError:
        pass
    try:
        value = json.loads(value_json)
    except Exception:
        flash('Value must be valid JSON', 'error')
        return redirect(url_for('api_table_rows', dbname=dbname, table_name=table_name))
    if table.update(key, value):
        dbx.save_database()
        flash(f'Record with key {key} updated', 'success')
    else:
        flash(f'Record with key {key} not found', 'error')
    return redirect(url_for('api_table_rows', dbname=dbname, table_name=table_name))

@app.route('/databases/<dbname>/tables/<table_name>/delete', methods=['POST'])
def delete_record_in_db(dbname, table_name):
    try:
        dbx = Database.get_database(dbname, CUSTOM_DB_DIR)
    except FileNotFoundError:
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    table = dbx.get_table(table_name)
    if not table:
        flash(f"Table '{table_name}' not found", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))
    key = request.form.get('key')
    try:
        key = int(key)
    except ValueError:
        pass
    if table.delete(key):
        dbx.save_database()
        flash(f'Record with key {key} deleted', 'success')
    else:
        flash(f'Record with key {key} not found', 'error')
    return redirect(url_for('api_table_rows', dbname=dbname, table_name=table_name))

@app.route('/databases/<dbname>/tables/<table_name>/search', methods=['POST'])
def search_record_in_db(dbname, table_name):
    try:
        dbx = Database.get_database(dbname, CUSTOM_DB_DIR)
    except FileNotFoundError:
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    table = dbx.get_table(table_name)
    if not table:
        flash(f"Table '{table_name}' not found", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))
    key = request.form.get('key')
    try:
        key = int(key)
    except ValueError:
        pass
    result = table.select(key)
    if result is not None:
        return render_template('search_result.html', table_name=table_name, key=key, value=result, dbname=dbname)
    else:
        flash(f'Record with key {key} not found', 'error')
        return redirect(url_for('api_table_rows', dbname=dbname, table_name=table_name))

@app.route('/databases/<dbname>/tables/<table_name>/range', methods=['POST'])
def range_query_in_db(dbname, table_name):
    try:
        dbx = Database.get_database(dbname, CUSTOM_DB_DIR)
    except FileNotFoundError:
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    table = dbx.get_table(table_name)
    if not table:
        flash(f"Table '{table_name}' not found", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))
    start_key = request.form.get('start_key')
    end_key = request.form.get('end_key')
    try:
        start_key = int(start_key)
    except ValueError:
        pass
    try:
        end_key = int(end_key)
    except ValueError:
        pass
    results = table.range_query(start_key, end_key)
    return render_template('range_result.html', table_name=table_name, start_key=start_key, end_key=end_key, results=results, dbname=dbname)

# --- Performance for a specific database table ---
@app.route('/databases/<dbname>/tables/<table_name>/performance')
def table_performance_in_db(dbname, table_name):
    # Ensure database exists
    filename = os.path.join(CUSTOM_DB_DIR, f"{dbname}.pkl")
    if not os.path.exists(filename):
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    # Load DB and table
    try:
        dbx = Database.get_database(dbname, CUSTOM_DB_DIR)
    except FileNotFoundError:
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    if table_name not in dbx.list_tables():
        flash(f"Table '{table_name}' not found in database '{dbname}'", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))
    table = dbx.get_table(table_name)
    # Prepare data structures
    data = table.get_all_records()
    keys = [k for k, _ in data]
    bf = BruteForceDB()
    for k, v in data:
        bf.insert(k, v)
    bpt = table.index
    # Measure search performance
    start = time.time()
    for k in keys:
        bpt.search(k)
    bpt_search = time.time() - start
    start = time.time()
    for k in keys:
        bf.search(k)
    bf_search = time.time() - start

    # Measure range query performance
    lo, hi = min(keys) if keys else (None, None), max(keys) if keys else (None, None)
    if keys:
        start = time.time(); bpt.range_query(lo, hi)
        bpt_range = time.time() - start
        start = time.time(); bf.range_query(lo, hi)
        bf_range = time.time() - start
    else:
        bpt_range = bf_range = 0

    # Measure memory usage
    bpt_mem = bpt.get_memory_usage()
    bf_mem = bf.get_memory_usage()

    # Generate charts
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out_dir = os.path.join('static', 'visualizations')
    os.makedirs(out_dir, exist_ok=True)
    # Search time chart
    plt.figure(figsize=(6,4))
    plt.bar(['B+ Tree','Brute Force'], [bpt_search*1000, bf_search*1000], color=['#1f77b4','#ff7f0e'])
    plt.title(f'Search Time ({dbname}.{table_name})')
    plt.ylabel('Time (ms)')
    fname_search = f'search_{dbname}_{table_name}.png'
    plt.savefig(os.path.join(out_dir, fname_search)); plt.close()

    # Range query chart
    plt.figure(figsize=(6,4))
    plt.bar(['B+ Tree','Brute Force'], [bpt_range*1000, bf_range*1000], color=['#1f77b4','#ff7f0e'])
    plt.title(f'Range Query Time ({dbname}.{table_name})')
    plt.ylabel('Time (ms)')
    fname_range = f'range_{dbname}_{table_name}.png'
    plt.savefig(os.path.join(out_dir, fname_range)); plt.close()

    # Memory usage chart
    plt.figure(figsize=(6,4))
    plt.bar(['B+ Tree','Brute Force'], [bpt_mem/1024, bf_mem/1024], color=['#1f77b4','#ff7f0e'])
    plt.title(f'Memory Usage ({dbname}.{table_name})')
    plt.ylabel('Memory (KB)')
    fname_mem = f'memory_{dbname}_{table_name}.png'
    plt.savefig(os.path.join(out_dir, fname_mem)); plt.close()

    images = {
        'Search Time': f'visualizations/{fname_search}',
        'Range Query Time': f'visualizations/{fname_range}',
        'Memory Usage': f'visualizations/{fname_mem}'
    }
    return render_template('performance.html', images=images, table_name=table_name, dbname=dbname)

# --- Modify order for a specific database table ---
@app.route('/databases/<dbname>/tables/<table_name>/modify_order', methods=['POST'])
def modify_order_in_db(dbname, table_name):
    # Ensure database exists
    filename = os.path.join(CUSTOM_DB_DIR, f"{dbname}.pkl")
    if not os.path.exists(filename):
        flash(f"Database '{dbname}' not found", 'error')
        return redirect(url_for('manage_databases'))
    # Parse new order
    try:
        new_order = int(request.form.get('new_order', 0))
        if new_order < 3:
            raise ValueError("Order must be at least 3")
    except Exception as e:
        flash(f"Invalid order value: {e}", 'error')
        return redirect(url_for('api_table_rows', dbname=dbname, table_name=table_name))
    # Load DB and table
    dbx = Database.get_database(dbname, CUSTOM_DB_DIR)
    if table_name not in dbx.list_tables():
        flash(f"Table '{table_name}' not found in database '{dbname}'", 'error')
        return redirect(url_for('api_list_tables', dbname=dbname))
    table = dbx.get_table(table_name)
    # Rebuild the index
    records = table.get_all_records()
    new_tree = BPlusTree(order=new_order)
    for key, value in records:
        new_tree.insert(key, value)
    table.index = new_tree
    dbx.save_database()
    flash(f"Rebuilt '{table_name}' with order={new_order}", 'success')
    return redirect(url_for('api_table_rows', dbname=dbname, table_name=table_name))

if __name__ == '__main__':
    os.makedirs('static/visualizations', exist_ok=True)
    app.run(debug=True) 