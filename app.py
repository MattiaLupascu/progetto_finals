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
    genre_id = request.args.get('genre_id', type=int)
    
    conn = get_db_connection()
    # Recupera tutti i generi per il filtro
    genres = conn.execute('SELECT * FROM genres ORDER BY name').fetchall()
    
    # Costruisci la query in base alla presenza del filtro per genere
    if genre_id:
        films = conn.execute('''
            SELECT f.* FROM films f
            JOIN film_genres fg ON f.id = fg.film_id
            WHERE fg.genre_id = ?
        ''', (genre_id,)).fetchall()
    else:
        films = conn.execute('SELECT * FROM films').fetchall()
    
    conn.close()
    return render_template('index.html', films=films, genres=genres, current_genre=genre_id)

@app.route('/director/<int:director_id>')
def director_films(director_id):
    conn = get_db_connection()
    director = conn.execute('SELECT * FROM directors WHERE id = ?', (director_id,)).fetchone()
    films = conn.execute('''
        SELECT * FROM films 
        WHERE director_id = ?
    ''', (director_id,)).fetchall()
    conn.close()
    
    if not director:
        flash('Regista non trovato')
        return redirect(url_for('index'))
    
    return render_template('director_films.html', director=director, films=films)

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
        new_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        session['user_id'] = new_user['id']
        session['username'] = new_user['username']
        flash(f'Registrazione avvenuta con successo, benvenuto {new_user["username"]}')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/film/<int:film_id>', methods=['GET', 'POST'])
def film_detail(film_id):
    conn = get_db_connection()
    # Recupera il film con il nome del regista
    film = conn.execute('''
        SELECT f.*, d.id as director_id, d.name as director_name 
        FROM films f
        JOIN directors d ON f.director_id = d.id
        WHERE f.id = ?
    ''', (film_id,)).fetchone()
    
    # Recupera i generi del film
    genres = conn.execute('''
        SELECT g.name FROM genres g
        JOIN film_genres fg ON g.id = fg.genre_id
        WHERE fg.film_id = ?
    ''', (film_id,)).fetchall()
    
    # Recupera le recensioni
    reviews = conn.execute('''
        SELECT r.*, u.username 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE film_id = ?
    ''', (film_id,)).fetchall()
    
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Devi essere loggato per scrivere una recensione')
            return redirect(url_for('login'))
        review_text = request.form['review']
        rating = request.form['rating']
        user_id = session['user_id']
        conn.execute('INSERT INTO reviews (film_id, user_id, review, rating) VALUES (?, ?, ?, ?)', 
                     (film_id, user_id, review_text, rating))
        conn.commit()
        conn.close()
        return redirect(url_for('film_detail', film_id=film_id))
    
    conn.close()
    return render_template('film.html', film=film, reviews=reviews, genres=genres)

if __name__ == '__main__':
    app.run(debug=True,port=60001)
