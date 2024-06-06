import sqlite3

def create_connection():
    conn = sqlite3.connect('money.db')
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS periods (
        id INTEGER PRIMARY KEY,
        period TEXT UNIQUE,
        comment TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS incomes (
        id INTEGER PRIMARY KEY,
        period_id INTEGER,
        category TEXT,
        amount INTEGER,
        FOREIGN KEY (period_id) REFERENCES periods(id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        period_id INTEGER,
        category TEXT,
        amount INTEGER,
        FOREIGN KEY (period_id) REFERENCES periods(id)
    )
    ''')
    conn.commit()
    conn.close()

create_tables()

def insert_period(period, incomes, expenses, comment):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('INSERT OR IGNORE INTO periods (period, comment) VALUES (?, ?)', (period, comment))
    period_id = cursor.execute('SELECT id FROM periods WHERE period = ?', (period,)).fetchone()[0]
    
    for category, amount in incomes.items():
        cursor.execute('INSERT INTO incomes (period_id, category, amount) VALUES (?, ?, ?)', (period_id, category, amount))
    
    for category, amount in expenses.items():
        cursor.execute('INSERT INTO expenses (period_id, category, amount) VALUES (?, ?, ?)', (period_id, category, amount))
    
    conn.commit()
    conn.close()

def fetch_all_periods():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT period FROM periods')
    periods = cursor.fetchall()
    conn.close()
    return periods

def get_period(period):
    conn = create_connection()
    cursor = conn.cursor()
    
    period_id = cursor.execute('SELECT id FROM periods WHERE period = ?', (period,)).fetchone()[0]
    comment = cursor.execute('SELECT comment FROM periods WHERE period = ?', (period,)).fetchone()[0]
    
    incomes = cursor.execute('SELECT category, amount FROM incomes WHERE period_id = ?', (period_id,)).fetchall()
    expenses = cursor.execute('SELECT category, amount FROM expenses WHERE period_id = ?', (period_id,)).fetchall()
    
    incomes = {category: amount for category, amount in incomes}
    expenses = {category: amount for category, amount in expenses}
    
    conn.close()
    
    return {"comment": comment, "incomes": incomes, "expenses": expenses}
