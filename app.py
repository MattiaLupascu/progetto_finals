from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'la_tua_chiave_segreta'  # Cambia in produzione

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    films = conn.execute('SELECT * FROM films').fetchall()
    conn.close()
    return render_template('index.html', films=films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Credenziali non valide')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        # Verifica se l'utente esiste già
        if conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            flash('Username già usato')
            conn.close()
            return redirect(url_for('register'))
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Registrazione avvenuta con successo, effettua il login')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/film/<int:film_id>', methods=['GET', 'POST'])
def film_detail(film_id):
    conn = get_db_connection()
    film = conn.execute('SELECT * FROM films WHERE id = ?', (film_id,)).fetchone()
    reviews = conn.execute('SELECT r.*, u.username FROM reviews r JOIN users u ON r.user_id = u.id WHERE film_id = ?', (film_id,)).fetchall()
    
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Devi essere loggato per scrivere una recensione')
            return redirect(url_for('login'))
        review_text = request.form['review']
        user_id = session['user_id']
        conn.execute('INSERT INTO reviews (film_id, user_id, review) VALUES (?, ?, ?)', (film_id, user_id, review_text))
        conn.commit()
        conn.close()
        return redirect(url_for('film_detail', film_id=film_id))
    conn.close()
    return render_template('film.html', film=film, reviews=reviews)

if __name__ == '__main__':
    app.run(debug=True)
