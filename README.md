# Online Bank Management System

A full-stack banking web application built with Flask and SQLite, supporting core banking operations including account management, fund transfers, and transaction history.

---

## Features

- **Account Management** — Create and manage customer accounts with secure authentication
- **Deposits & Withdrawals** — Perform real-time balance updates with input validation
- **Fund Transfers** — Transfer funds between accounts with atomic transactions
- **Transaction History** — View a complete, timestamped log of all account activity
- **Session Management** — Secure login/logout with Flask session handling

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, Jinja2 Templates |
| Auth | Flask Sessions |

---

## Project Structure

```
bank-management-system/
├── app.py               # Main Flask application & route handlers
├── database.py          # DB initialization and query helpers
├── schema.sql           # SQLite schema (accounts, transactions)
├── templates/
│   ├── index.html       # Home / login page
│   ├── dashboard.html   # Account dashboard
│   ├── transfer.html    # Fund transfer form
│   └── history.html     # Transaction history view
├── static/
│   └── style.css        # Styling
└── requirements.txt     # Python dependencies
```

---

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/zaid-sid/bank-management-system.git
cd bank-management-system

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python database.py

# Run the application
python app.py
```

The app will be running at `http://localhost:5000`

---

## Database Schema

**Accounts Table**
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    balance REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Transactions Table**
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    type TEXT,         -- 'deposit', 'withdrawal', 'transfer'
    amount REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

---

## Background

This project originated from a high school coding workshop where I first built a Python/MySQL bank management system — my introduction to programming. I later rebuilt it at university using Flask and SQLite, applying proper web framework patterns, relational database design, and session-based authentication.

---

## Future Improvements

- Password hashing with bcrypt
- REST API layer
- Admin dashboard for multi-account oversight
- Deployment to Render or Railway

---

## Author

**Zaid Siddiqui**  
CS & Engineering @ University of Toledo  
[GitHub](https://github.com/zaid-sid)
