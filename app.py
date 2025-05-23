from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session


# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define database model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
# Home route to display a summary of transactions
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/') 
def index():
    # Get total income and total expenses
    income = Transaction.query.filter_by(type='income').all()
    expenses = Transaction.query.filter_by(type='expense').all()

    total_income = sum([transaction.amount for transaction in income])
    total_expense = sum([transaction.amount for transaction in expenses])

    # Count transactions
    total_transactions = len(income) + len(expenses)

    return render_template('index.html', 
                           total_income=total_income,
                           total_expense=total_expense,
                           total_transactions=total_transactions)
# Route to display all transactions
@app.route('/transactions')
def all_transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

# Route to add a new transaction
@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        # Get form data
        type = request.form['type']
        amount = float(request.form['amount'])
        category = request.form['category']
        
        # Create a new Transaction object and add it to the database
        new_transaction = Transaction(type=type, amount=amount, category=category)
        db.session.add(new_transaction)
        db.session.commit()

        # Redirect to the transactions page
        return redirect(url_for('all_transactions'))

    # GET request: display the form
    return render_template('add_transaction.html')

# Route to display financial report with chart data
@app.route('/report')
def report():
    expenses = Transaction.query.filter_by(type='expense').all()
    income = Transaction.query.filter_by(type='income').all()

    total_expense = sum([expense.amount for expense in expenses])
    total_income = sum([income.amount for income in income])

    # Group data by category for the chart
    categories = set()
    income_data = {}
    expense_data = {}

    # Prepare income data by category
    for t in income:
        categories.add(t.category)
        income_data[t.category] = income_data.get(t.category, 0) + t.amount

    # Prepare expense data by category
    for t in expenses:
        categories.add(t.category)
        expense_data[t.category] = expense_data.get(t.category, 0) + t.amount

    # Sort categories for consistent ordering in chart
    categories = sorted(categories)
    income_chart_data = [income_data.get(cat, 0) for cat in categories]
    expense_chart_data = [expense_data.get(cat, 0) for cat in categories]

    return render_template(
        'report.html',
        total_income=total_income,
        total_expense=total_expense,
        income=income,
        expenses=expenses,
        categories=categories,
        income_data=income_chart_data,
        expense_data=expense_chart_data
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
