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

@app.route('/')
def index():
    tables = db.list_tables()
    return render_template('index.html', tables=tables)

@app.route('/create_table', methods=['POST'])
def create_table():
    table_name = request.form.get('table_name')
    order = int(request.form.get('order', 4))
    
    if not table_name:
        flash('Table name is required', 'error')
        return redirect(url_for('index'))
    
    try:
        # Check if table already exists
        if table_name in db.list_tables():
            flash(f'Table {table_name} already exists', 'error')
        else:
            db.create_table(table_name, order=order)
            flash(f'Table {table_name} created successfully', 'success')
        
        # Save the database
        db.save_database()
    except Exception as e:
        flash(f'Error creating table: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/table/<table_name>')
def view_table(table_name):
    if table_name not in db.list_tables():
        flash(f'Table {table_name} does not exist', 'error')
        return redirect(url_for('index'))
    
    table = db.get_table(table_name)
    data = table.get_all_records()
    
    # Generate visualization
    try:
        os.makedirs('static/visualizations', exist_ok=True)
        viz_path = f'static/visualizations/{table_name}_bplus_tree'
        table.visualize(viz_path)
        viz_image = f'{viz_path}.png'
    except Exception as e:
        flash(f'Error generating visualization: {str(e)}', 'warning')
        viz_image = None
    
    return render_template('table.html', table_name=table_name, data=data, viz_image=viz_image)

@app.route('/table/<table_name>/insert', methods=['POST'])
def insert_record(table_name):
    if table_name not in db.list_tables():
        flash(f'Table {table_name} does not exist', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get form data
        key = request.form.get('key')
        value_json = request.form.get('value')
        
        # Convert key to integer if possible
        try:
            key = int(key)
        except ValueError:
            pass
        
        # Parse JSON value
        try:
            value = json.loads(value_json)
        except json.JSONDecodeError:
            flash('Value must be valid JSON', 'error')
            return redirect(url_for('view_table', table_name=table_name))
            
        # Insert into table
        table = db.get_table(table_name)
        table.insert(key, value)
        
        # Save database
        db.save_database()
        
        flash(f'Record with key {key} inserted successfully', 'success')
    except Exception as e:
        flash(f'Error inserting record: {str(e)}', 'error')
    
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/table/<table_name>/update', methods=['POST'])
def update_record(table_name):
    if table_name not in db.list_tables():
        flash(f'Table {table_name} does not exist', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get form data
        key = request.form.get('key')
        value_json = request.form.get('value')
        
        # Convert key to integer if possible
        try:
            key = int(key)
        except ValueError:
            pass
        
        # Parse JSON value
        try:
            value = json.loads(value_json)
        except json.JSONDecodeError:
            flash('Value must be valid JSON', 'error')
            return redirect(url_for('view_table', table_name=table_name))
            
        # Update table
        table = db.get_table(table_name)
        if table.update(key, value):
            flash(f'Record with key {key} updated successfully', 'success')
            db.save_database()
        else:
            flash(f'Record with key {key} not found', 'error')
        
    except Exception as e:
        flash(f'Error updating record: {str(e)}', 'error')
    
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/table/<table_name>/delete', methods=['POST'])
def delete_record(table_name):
    if table_name not in db.list_tables():
        flash(f'Table {table_name} does not exist', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get key
        key = request.form.get('key')
        
        # Convert key to integer if possible
        try:
            key = int(key)
        except ValueError:
            pass
            
        # Delete from table
        table = db.get_table(table_name)
        if table.delete(key):
            flash(f'Record with key {key} deleted successfully', 'success')
            db.save_database()
        else:
            flash(f'Record with key {key} not found', 'error')
        
    except Exception as e:
        flash(f'Error deleting record: {str(e)}', 'error')
    
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/table/<table_name>/search', methods=['POST'])
def search_record(table_name):
    if table_name not in db.list_tables():
        flash(f'Table {table_name} does not exist', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get key
        key = request.form.get('key')
        
        # Convert key to integer if possible
        try:
            key = int(key)
        except ValueError:
            pass
            
        # Search in table
        table = db.get_table(table_name)
        result = table.select(key)
        
        if result:
            return render_template('search_result.html', table_name=table_name, key=key, value=result)
        else:
            flash(f'Record with key {key} not found', 'error')
        
    except Exception as e:
        flash(f'Error searching record: {str(e)}', 'error')
    
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/table/<table_name>/range', methods=['POST'])
def range_query(table_name):
    if table_name not in db.list_tables():
        flash(f'Table {table_name} does not exist', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get range keys
        start_key = request.form.get('start_key')
        end_key = request.form.get('end_key')
        
        # Convert keys to integers if possible
        try:
            start_key = int(start_key)
        except ValueError:
            pass
            
        try:
            end_key = int(end_key)
        except ValueError:
            pass
            
        # Execute range query
        table = db.get_table(table_name)
        results = table.range_query(start_key, end_key)
        
        return render_template('range_result.html', table_name=table_name, 
                               start_key=start_key, end_key=end_key, results=results)
        
    except Exception as e:
        flash(f'Error executing range query: {str(e)}', 'error')
    
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/delete_table/<table_name>', methods=['POST'])
def delete_table(table_name):
    if table_name not in db.list_tables():
        flash(f'Table {table_name} does not exist', 'error')
        return redirect(url_for('index'))
    
    try:
        # Delete table
        db.delete_table(table_name)
        db.save_database()
        flash(f'Table {table_name} deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting table: {str(e)}', 'error')
    
    return redirect(url_for('index'))

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

if __name__ == '__main__':
    os.makedirs('static/visualizations', exist_ok=True)
    app.run(debug=True) 