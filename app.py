from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, create_user, verify_user, get_account, get_transactions, deposit, withdraw, transfer, get_all_users
from config import Config
import functools

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize database on startup
with app.app_context():
    init_db()


def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        if create_user(full_name, email, password):
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists.', 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = verify_user(email, password)

        if user:
            session['user_id'] = user['id']
            session['full_name'] = user['full_name']
            session['is_admin'] = user['is_admin']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            if user['is_admin']:
                return redirect(url_for('admin'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    account = get_account(session['user_id'])
    message = None

    if request.method == 'POST':
        action = request.form.get('action')
        amount = float(request.form.get('amount', 0))

        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
        elif action == 'deposit':
            deposit(account['id'], amount)
            flash(f'${amount:.2f} deposited successfully.', 'success')
            account = get_account(session['user_id'])
        elif action == 'withdraw':
            if withdraw(account['id'], amount):
                flash(f'${amount:.2f} withdrawn successfully.', 'success')
                account = get_account(session['user_id'])
            else:
                flash('Insufficient funds.', 'error')

    return render_template('dashboard.html', account=account, full_name=session['full_name'])


@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer_funds():
    account = get_account(session['user_id'])

    if request.method == 'POST':
        to_account_number = request.form['to_account']
        amount = float(request.form['amount'])

        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
        elif to_account_number == account['account_number']:
            flash('Cannot transfer to your own account.', 'error')
        else:
            success, message = transfer(account['id'], to_account_number, amount)
            if success:
                flash(message, 'success')
                return redirect(url_for('dashboard'))
            else:
                flash(message, 'error')

    return render_template('transfer.html', account=account)


@app.route('/transactions')
@login_required
def transactions():
    account = get_account(session['user_id'])
    txns = get_transactions(account['id'])
    return render_template('transactions.html', transactions=txns, account=account)


@app.route('/admin')
@admin_required
def admin():
    users = get_all_users()
    return render_template('admin.html', users=users)


@app.route('/admin/create', methods=['POST'])
@admin_required
def admin_create_user():
    full_name = request.form['full_name']
    email = request.form['email']
    password = request.form['password']
    is_admin = 1 if request.form.get('is_admin') else 0

    if create_user(full_name, email, password, is_admin):
        flash(f'User {full_name} created successfully.', 'success')
    else:
        flash('Email already exists.', 'error')

    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)