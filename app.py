import os
import hashlib
import sqlite3
from flask import Flask, render_template, redirect, url_for, session, request, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def create_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS houses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        house_name TEXT NOT NULL,
                        location TEXT NOT NULL,
                        price INTEGER NOT NULL,
                        description TEXT NOT NULL,
                        owner_name TEXT NOT NULL,
                        owner_email TEXT NOT NULL,
                        owner_phone TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def demo():
    return render_template('index.html')

@app.route('/home')
def home():
    if 'email' in session:
        return f"Hello, {session['email']}! <br><a href='/logout'>Logout</a>"
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['email'] = email
            return redirect(url_for('info'))
        else:
            error = 'Invalid email or password'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = 'Email already registered'
        finally:
            conn.close()
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/rentsearch', methods=['GET', 'POST'])
def rent():
    results = None
    if request.method == 'POST':
        location = request.form['location']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT house_name, location, price, description, owner_name, owner_email, owner_phone FROM houses WHERE location = ?", (location,))
        results = cursor.fetchall()
        conn.close()

    return render_template('rentsearch.html', results=results)

@app.route('/info')
def info():
    if 'email' in session:
        return render_template('info.html')
    return redirect(url_for('login'))

@app.route('/rentout', methods=['GET', 'POST'])
def rentout():
    if request.method == 'POST':
        house_name = request.form['house_name']
        location = request.form['location']
        price = request.form['price']
        description = request.form['description']
        owner_name = request.form['owner_name']
        owner_email = request.form['owner_email']
        owner_phone = request.form['owner_phone']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO houses (house_name, location, price, description, owner_name, owner_email, owner_phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (house_name, location, price, description, owner_name, owner_email, owner_phone))
        conn.commit()
        conn.close()

        flash('House information submitted successfully!')
        return redirect(url_for('rentout'))
    return render_template('rentout.html')

if __name__ == '__main__':
    create_database()
    app.run(debug=True)