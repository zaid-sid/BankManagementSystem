import sqlite3
import bcrypt
from config import Config


def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_number TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );
    ''')

    conn.commit()
    conn.close()


def create_user(full_name, email, password, is_admin=0):
    conn = get_db()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute(
            'INSERT INTO users (full_name, email, password, is_admin) VALUES (?, ?, ?, ?)',
            (full_name, email, hashed.decode('utf-8'), is_admin)
        )
        user_id = cursor.lastrowid
        account_number = f"ACC{user_id:08d}"
        cursor.execute(
            'INSERT INTO accounts (user_id, account_number, balance) VALUES (?, ?, ?)',
            (user_id, account_number, 1000.0)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_user(email, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None


def get_account(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
    account = cursor.fetchone()
    conn.close()
    return account


def get_transactions(account_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM transactions WHERE account_id = ? ORDER BY created_at DESC',
        (account_id,)
    )
    transactions = cursor.fetchall()
    conn.close()
    return transactions


def deposit(account_id, amount, description="Deposit"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE accounts SET balance = balance + ? WHERE id = ?',
        (amount, account_id)
    )
    cursor.execute(
        'INSERT INTO transactions (account_id, type, amount, description) VALUES (?, ?, ?, ?)',
        (account_id, 'DEPOSIT', amount, description)
    )
    conn.commit()
    conn.close()


def withdraw(account_id, amount, description="Withdrawal"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
    account = cursor.fetchone()
    if account['balance'] < amount:
        conn.close()
        return False
    cursor.execute(
        'UPDATE accounts SET balance = balance - ? WHERE id = ?',
        (amount, account_id)
    )
    cursor.execute(
        'INSERT INTO transactions (account_id, type, amount, description) VALUES (?, ?, ?, ?)',
        (account_id, 'WITHDRAWAL', amount, description)
    )
    conn.commit()
    conn.close()
    return True


def transfer(from_account_id, to_account_number, amount):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts WHERE id = ?', (from_account_id,))
    from_account = cursor.fetchone()
    if from_account['balance'] < amount:
        conn.close()
        return False, "Insufficient funds"
    cursor.execute('SELECT * FROM accounts WHERE account_number = ?', (to_account_number,))
    to_account = cursor.fetchone()
    if not to_account:
        conn.close()
        return False, "Account not found"
    cursor.execute(
        'UPDATE accounts SET balance = balance - ? WHERE id = ?',
        (amount, from_account_id)
    )
    cursor.execute(
        'UPDATE accounts SET balance = balance + ? WHERE id = ?',
        (amount, to_account['id'])
    )
    cursor.execute(
        'INSERT INTO transactions (account_id, type, amount, description) VALUES (?, ?, ?, ?)',
        (from_account_id, 'TRANSFER OUT', amount, f'Transfer to {to_account_number}')
    )
    cursor.execute(
        'INSERT INTO transactions (account_id, type, amount, description) VALUES (?, ?, ?, ?)',
        (to_account['id'], 'TRANSFER IN', amount, f'Transfer from {from_account["account_number"]}')
    )
    conn.commit()
    conn.close()
    return True, "Transfer successful"


def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.*, a.account_number, a.balance
        FROM users u
        LEFT JOIN accounts a ON u.id = a.user_id
        ORDER BY u.created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    return users
