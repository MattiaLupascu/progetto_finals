from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import sys
import os

# Aggiungi la directory corrente al path per poter importare database_setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database_setup import import_movies_from_tmdb

app = Flask(__name__)
app.secret_key = 'la_tua_chiave_segreta'  # Cambia in produzione
app.config['SESSION_PERMANENT'] = False  # Disabilita la persistenza della sessione

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    
    # Recupera tutti i generi per il filtro
    genres = conn.execute('SELECT * FROM genres ORDER BY name').fetchall()
    
    # Recupera il parametro genre_id se presente
    genre_id = request.args.get('genre_id', type=int)
    
    # Costruisci la query in base alla presenza del filtro per genere
    if genre_id:
        # Query filtrata per genere
        films = conn.execute('''
            SELECT DISTINCT f.*, d.name as director_name 
            FROM films f
            LEFT JOIN directors d ON f.director_id = d.id
            JOIN film_genres fg ON f.id = fg.film_id
            WHERE fg.genre_id = ?
        ''', (genre_id,)).fetchall()
    else:
        # Query per tutti i film
        films = conn.execute('''
            SELECT f.*, d.name as director_name 
            FROM films f
            LEFT JOIN directors d ON f.director_id = d.id
        ''').fetchall()
    
    # Calcola il punteggio medio per ogni film
    film_list = []
    for film in films:
        film_dict = dict(film)
        film_id = film_dict['id']
        try:
            rating_data = conn.execute(
                'SELECT AVG(rating) as avg_rating, COUNT(id) as review_count FROM reviews WHERE film_id = ?', 
                (film_id,)  # Nota la virgola alla fine per creare una tupla
            ).fetchone()
            
            # Assicurati che i valori non siano None
            film_dict['avg_rating'] = 0 if rating_data['avg_rating'] is None else rating_data['avg_rating']
            film_dict['review_count'] = 0 if rating_data['review_count'] is None else rating_data['review_count']
        except Exception as e:
            # In caso di errore, usa valori predefiniti
            film_dict['avg_rating'] = 0
            film_dict['review_count'] = 0
            print(f"Errore nel calcolare il rating per il film {film_id}: {str(e)}")
            
        film_list.append(film_dict)
    
    conn.close()
    
    return render_template('index.html', films=film_list, genres=genres, current_genre=genre_id)

@app.route('/ajax/films')
def ajax_films():
    """Endpoint AJAX per ottenere i film filtrati per genere"""
    genre_id = request.args.get('genre_id', type=int)
    
    conn = get_db_connection()
    
    # Debug: stampa quanti film ci sono
    film_count = conn.execute('SELECT COUNT(*) as count FROM films').fetchone()['count']
    print(f"DEBUG: ci sono {film_count} film nel database")
    
    # Costruisci la query in base alla presenza del filtro per genere
    if genre_id:
        films = conn.execute('''
            SELECT f.*, d.name as director_name, AVG(r.rating) as avg_rating, COUNT(r.id) as review_count 
            FROM films f
            LEFT JOIN directors d ON f.director_id = d.id
            JOIN film_genres fg ON f.id = fg.film_id
            LEFT JOIN reviews r ON f.id = r.film_id
            WHERE fg.genre_id = ?
            GROUP BY f.id
        ''', (genre_id,)).fetchall()
    else:
        films = conn.execute('''
            SELECT f.*, d.name as director_name, AVG(r.rating) as avg_rating, COUNT(r.id) as review_count 
            FROM films f
            LEFT JOIN directors d ON f.director_id = d.id
            LEFT JOIN reviews r ON f.id = r.film_id
            GROUP BY f.id
        ''').fetchall()
    
    print(f"DEBUG: la query ha trovato {len(films)} film")
    
    # Converti i risultati in un formato JSON-serializzabile
    film_list = []
    for film in films:
        film_dict = dict(film)
        # Formatta il punteggio medio per il JSON
        if film_dict['avg_rating'] is not None:
            film_dict['avg_rating'] = round(film_dict['avg_rating'], 1)
        else:
            film_dict['avg_rating'] = 0
        film_list.append(film_dict)
    
    conn.close()
    return jsonify({'films': film_list})

@app.route('/ajax/search')
def ajax_search_films():
    """Endpoint AJAX per cercare film per titolo (con fuzzy matching)"""
    search_query = request.args.get('query', '').strip().lower()
    
    if not search_query or len(search_query) < 2:
        return jsonify({
            'films': [],
            'status': 'Inserisci almeno 2 caratteri per iniziare la ricerca'
        })
    
    conn = get_db_connection()
    
    # Utilizziamo LIKE con % per fare un fuzzy matching basilare
    # Cerchiamo la stringa ovunque nel titolo
    search_pattern = f"%{search_query}%"
    
    films = conn.execute('''
        SELECT f.*, d.name as director_name, AVG(r.rating) as avg_rating, COUNT(r.id) as review_count 
        FROM films f
        LEFT JOIN directors d ON f.director_id = d.id
        LEFT JOIN reviews r ON f.id = r.film_id
        WHERE LOWER(f.title) LIKE ?
        GROUP BY f.id
        ORDER BY 
            CASE 
                WHEN LOWER(f.title) = ? THEN 1  -- Corrispondenza esatta (massima priorità)
                WHEN LOWER(f.title) LIKE ? THEN 2  -- Inizia con la query
                ELSE 3  -- Contiene la query ovunque
            END,
            f.title
    ''', (search_pattern, search_query, f"{search_query}%")).fetchall()
    
    # Converti i risultati in un formato JSON-serializzabile
    film_list = []
    for film in films:
        film_dict = dict(film)
        # Formatta il punteggio medio per il JSON
        if film_dict['avg_rating'] is not None:
            film_dict['avg_rating'] = round(film_dict['avg_rating'], 1)
        else:
            film_dict['avg_rating'] = 0
        film_list.append(film_dict)
    
    status_message = f"Trovati {len(film_list)} risultati per '{search_query}'"
    
    conn.close()
    return jsonify({
        'films': film_list,
        'status': status_message
    })

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
    # Recupera il film con il nome del regista e il punteggio medio
    film = conn.execute('''
        SELECT f.*, d.id as director_id, d.name as director_name,
               AVG(r.rating) as avg_rating, COUNT(r.id) as review_count
        FROM films f
        LEFT JOIN directors d ON f.director_id = d.id
        LEFT JOIN reviews r ON f.id = r.film_id
        WHERE f.id = ?
        GROUP BY f.id
    ''', (film_id,)).fetchone()
    
    if not film:
        flash('Film non trovato')
        conn.close()
        return redirect(url_for('index'))
    
    # Converti in dict per poter modificare i valori
    film = dict(film)
    # Assicurati che avg_rating non sia None
    film['avg_rating'] = film['avg_rating'] if film['avg_rating'] else 0
    film['review_count'] = film['review_count'] if film['review_count'] else 0
    
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
            conn.close()
            return redirect(url_for('login'))
            
        review_text = request.form['review']
        rating = int(request.form['rating'])  # Converti esplicitamente in intero
        user_id = session['user_id']
        
        conn.execute('INSERT INTO reviews (film_id, user_id, review, rating) VALUES (?, ?, ?, ?)', 
                    (film_id, user_id, review_text, rating))
        conn.commit()
        conn.close()
        return redirect(url_for('film_detail', film_id=film_id))
    
    conn.close()
    return render_template('film.html', film=film, reviews=reviews, genres=genres)

@app.route('/admin/import_movies', methods=['GET', 'POST'])
def admin_import_movies():
    """Pagina di amministrazione per importare film da TMDB"""
    # Verifica che l'utente sia admin (presumiamo che l'admin abbia id=1)
    if not session.get('user_id') or session.get('user_id') != 1:
        flash('Accesso negato: devi essere amministratore')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            num_pages = int(request.form.get('num_pages', 1))
            # Aumentiamo il limite massimo di pagine da 5 a 20
            if num_pages < 1:
                num_pages = 1
            elif num_pages > 20:
                num_pages = 20  # Permette fino a circa 400 film
            
            # Esegue l'importazione usando la funzione spostata in database_setup.py
            conn = get_db_connection()
            import_movies_from_tmdb(conn, num_pages)
            conn.close()
            
            flash(f'Importazione completata! Film importati da {num_pages} pagine.')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Errore durante l\'importazione: {str(e)}')
    
    return render_template('admin_import.html')

@app.route('/debug')
def debug():
    """Pagina di debug per visualizzare lo stato del database"""
    conn = get_db_connection()
    films = conn.execute('''
        SELECT f.*, d.name as director_name 
        FROM films f
        LEFT JOIN directors d ON f.director_id = d.id
    ''').fetchall()
    
    # Calcola il punteggio medio per ogni film
    for i in range(len(films)):
        film_id = films[i]['id']
        rating_data = conn.execute('''
            SELECT AVG(rating) as avg_rating, COUNT(id) as review_count
            FROM reviews
            WHERE film_id = ?
        ''', (film_id,)).fetchone()
        
        films[i] = dict(films[i])
        films[i]['avg_rating'] = rating_data['avg_rating']
        films[i]['review_count'] = rating_data['review_count']
    
    genres = conn.execute('SELECT * FROM genres ORDER BY name').fetchall()
    conn.close()
    
    return render_template('debug.html', films=films, genres=genres)

if __name__ == '__main__':
    app.run(debug=True,port=60001)
