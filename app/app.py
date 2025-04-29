from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from data_structures import Stack, Queue, MenuList, CategoryTree
from algorithms import merge_sort
from menu_data import menu_data

app = Flask(__name__)
CORS(app)

# In-memory Data Structures
order_queue = Queue()         
undo_stack = Stack()           
menu_list = MenuList()         
category_tree = CategoryTree()  
booked_tables = [False] * 5     
orders_per_table = [[] for _ in range(5)]  
tips_per_table = [0] * 5        
sales_history = []  # Store completed sales for reporting

# Load Menu Data
for item in menu_data:
    menu_list.add(item)
    category_tree.insert(item['category'], item)

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Table Booking Page
@app.route('/booking')
def booking():
    return render_template('booking.html', tables=booked_tables)

# Book a Table
@app.route('/book_table/<int:table_id>', methods=['POST'])
def book_table(table_id):
    if 0 <= table_id < len(booked_tables):
        if not booked_tables[table_id]:
            booked_tables[table_id] = True
            return jsonify({'message': f'Table {table_id + 1} booked successfully!', 'status': 'booked'})
        else:
            return jsonify({'message': f'Table {table_id + 1} is already booked.', 'status': 'already_booked'})
    return jsonify({'message': 'Invalid table ID', 'status': 'error'})

# Order Processing Page
@app.route('/order')
def order_page():
    return render_template('order.html', menu=menu_list.get_all(), tables=booked_tables)

# Place an Order
@app.route('/place_order/<int:table_id>', methods=['POST'])
def place_order(table_id):
    order = request.json
    if 0 <= table_id < len(booked_tables) and booked_tables[table_id]:
        for _ in range(order['quantity']):
            orders_per_table[table_id].append(order)
            order_queue.enqueue(order)
            undo_stack.push((table_id, order))
        return jsonify({'message': f'Order added successfully for Table {table_id + 1}.', 'status': 'success'})
    return jsonify({'message': 'Invalid table ID or table not booked', 'status': 'error'})

# Billing Page
@app.route('/billing')
def billing():
    return render_template('billing.html', tables=booked_tables)

# Get Billing Details for a Specific Table
@app.route('/billing/<int:table_id>')
def get_table_billing(table_id):
    if 0 <= table_id < len(orders_per_table):
        table_orders = orders_per_table[table_id]
        itemized_billing = {}
        for order in table_orders:
            if order['name'] in itemized_billing:
                itemized_billing[order['name']]['quantity'] += 1
            else:
                itemized_billing[order['name']] = {'price': order['price'], 'quantity': 1}

        total = sum(item['price'] * item['quantity'] for item in itemized_billing.values())
        return jsonify({'orders': itemized_billing, 'total': total})
    return jsonify({'message': 'Invalid table ID'}), 404

# Handle Payment and Reset Table
@app.route('/process_payment/<int:table_id>', methods=['POST'])
def process_payment(table_id):
    data = request.json
    payment_method = data.get('method')
    tip_amount = float(data.get('tip', 0))
    
    if 0 <= table_id < len(orders_per_table):
        table_orders = orders_per_table[table_id]
        base_total = sum(item['price'] for item in table_orders)
        
        # Add tips to the total tips collected
        tips_per_table[table_id] = tip_amount

        # Calculate total with tip
        total_with_tip = base_total + tip_amount

        # Apply a 10% surcharge for card payments
        if payment_method == 'card':
            total_with_tip *= 1.1
            message = f'Payment completed via card. Total: ${total_with_tip:.2f}'
        else:
            message = f'Payment completed via cash. Total: ${total_with_tip:.2f}'
        
        # Store completed orders in sales history with table ID
        for order in table_orders:
            sales_history.append({'table_id': table_id + 1, **order})
        
        # Clear orders and reset the table status
        orders_per_table[table_id] = []
        booked_tables[table_id] = False 
        
        return jsonify({'message': message, 'status': 'success'})
    
    return jsonify({'message': 'Invalid table ID', 'status': 'error'}), 404

# End-of-Day Report Page
@app.route('/report')
def report_page():
    return render_template('report.html')

# API for End-of-Day Report Data
@app.route('/report/data')
def report_data():
    total_income = sum(item['price'] for item in sales_history)
    total_tips = sum(tips_per_table)
    
    # Determine the highest spending table using sales history
    table_totals = {}
    for order in sales_history:
        table_id = order['table_id']
        table_totals[table_id] = table_totals.get(table_id, 0) + order['price']
    
    highest_spending_table = max(table_totals, key=table_totals.get, default=0)

    # Calculate item popularity from sales history
    item_popularity = {}
    for order in sales_history:
        item_popularity[order['name']] = item_popularity.get(order['name'], 0) + 1
    
    sorted_items = sorted(item_popularity.items(), key=lambda x: x[1], reverse=True)
    
    return jsonify({
        'totalIncome': total_income,
        'highestSpendingTable': highest_spending_table,
        'totalTips': total_tips,
        'sortedItems': sorted_items
    })

if __name__ == '__main__':
    app.run(debug=True)




