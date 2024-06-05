from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import sql
import datetime
import re
app = Flask(__name__)

app.secret_key = 'the random string'
app.config['SESSION_PERMANENT'] = False

def get_db_connection():
    conn = psycopg2.connect(
        dbname="ExpenseTracker",
        user="postgres",
        password="3230",
        host="localhost",
        port="5432"
    )
    return conn

@app.route('/', methods=['GET'])
def index():
    filter_value = request.args.get('expense-filter')
    specific_date = request.args.get('specific-date')
    today = datetime.date.today()
    month_start = datetime.date(today.year, today.month, 1)
    
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    username = session.get('username')

    query = """
        SELECT e.expenseID, u.username, e.name, e.amount, e.date, e.category 
        FROM Expenses e
        JOIN Users u ON e.userID = u.userID
        WHERE u.username = %s
    """
    params = [username]

    if filter_value == 'Today':
        query += " AND e.date = %s"
        params.append(today)
    elif filter_value == 'This Month':
        query += " AND e.date >= %s"
        params.append(month_start)
    elif filter_value == 'Specific Date' and specific_date:
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$') # Our regular expression
        if date_pattern.match(specific_date):
            query += " AND e.date = %s"
            params.append(specific_date)
    query += " ORDER BY e.date DESC"

    cur.execute(query, tuple(params))
    expenses = cur.fetchall()

    total_amount = sum(expense[3] for expense in expenses)

    cur.close()
    conn.close()

    return render_template('index.html', expenses=expenses, username=username, total_amount=total_amount, filter_value=filter_value, specific_date=specific_date)

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        date = request.form['date']
        category = request.form['category']

        cur.execute("UPDATE Expenses SET name = %s, amount = %s, date = %s, category = %s WHERE expenseID = %s",
                    (name, amount, date, category, expense_id))
        conn.commit()

        
        cur.close()
        conn.close()

        return redirect(url_for('index')) 

    cur.execute("SELECT * FROM Expenses WHERE expenseID = %s", (expense_id,))
    expense = cur.fetchone()
    cur.close()
    conn.close()

    if not expense:
        return redirect(url_for('index'))

    return render_template('edit_expense.html', expense=expense)

@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'username' not in session:
        return redirect(url_for('login'))  
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM Expenses WHERE expenseID = %s", (expense_id,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('index')) 
    
@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'username' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    amount = request.form['amount']
    date = request.form['date']
    category = request.form['category']

    conn = psycopg2.connect(
        dbname="ExpenseTracker",
        user="postgres",
        password="3230",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    username = session.get('username')
    cur.execute("SELECT userID FROM Users WHERE username = %s", (username,))
    result = cur.fetchone()
    if result:
        userID = result[0]
    cur.execute("INSERT INTO Expenses (userID, name, amount, date, category) VALUES (%s, %s, %s, %s, %s)", (userID, name, amount, date, category))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

