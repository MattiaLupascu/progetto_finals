import sqlite3
import requests
import time
import os
import shutil

# Assicuriamoci che la directory favicon esista
os.makedirs('static/favicon', exist_ok=True)

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Configurazione API TMDB
API_KEY = "7899a364b71c3b9f125f24e9588a599c"  # Nuova chiave API gratuita per TMDB
BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Funzioni per importare film da TMDB
def get_movies_from_api(page=1, language="it-IT"):
    """Recupera i film più popolari da TMDB"""
    endpoint = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": API_KEY,
        "language": language,
        "page": page
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        print(f"Successo: ottenuti dati dalla pagina {page}")
        return response.json()
    else:
        print(f"Errore API {response.status_code}: {response.text}")
        return None

def get_movie_details(movie_id, language="it-IT"):
    """Recupera dettagli completi di un film"""
    endpoint = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": language,
        "append_to_response": "credits"
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        print(f"Successo: ottenuti dettagli per film ID {movie_id}")
        return response.json()
    else:
        print(f"Errore API {response.status_code} per film {movie_id}: {response.text}")
        return None

def download_poster(poster_path, save_dir="static/favicon"):
    """Scarica il poster del film"""
    if not poster_path:
        print("Nessun poster path fornito")
        return None
    
    # Crea la directory se non esiste
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Nome file locale
    filename = os.path.basename(poster_path)
    save_path = f"{save_dir}/{filename}"
    
    # Se il file esiste già, restituisci il nome
    if os.path.exists(save_path):
        print(f"Il poster esiste già: {filename}")
        return filename
    
    # Scarica l'immagine
    try:
        poster_url = f"{POSTER_BASE_URL}{poster_path}"
        print(f"Download del poster da: {poster_url}")
        response = requests.get(poster_url, stream=True)
        
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            print(f"Poster salvato come: {filename}")
            return filename
        else:
            print(f"Errore nel download del poster {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Errore nel download del poster: {e}")
    
    return None

def create_default_genres_and_directors():
    """Crea generi e registi predefiniti"""
    # Generi predefiniti
    default_genres = [
        'Azione', 'Avventura', 'Animazione', 'Commedia', 'Crime', 'Documentario',
        'Dramma', 'Famiglia', 'Fantasy', 'Storia', 'Horror', 'Musica', 
        'Mistero', 'Romance', 'Fantascienza', 'Film TV', 'Thriller', 'Guerra', 'Western'
    ]
    
    # Inserisci i generi se non esistono
    for genre in default_genres:
        c.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (genre,))
    
    conn.commit()
    print(f"Inseriti {len(default_genres)} generi predefiniti")

def import_movies_from_tmdb(conn, num_pages=1):
    """Importa film da TMDB nel database"""
    c = conn.cursor()
    
    # Recupera i generi esistenti
    c.execute("SELECT name, id FROM genres")
    genres_db = {row[0]: row[1] for row in c.fetchall()}
    
    # Recupera i registi esistenti
    c.execute("SELECT name, id FROM directors")
    directors_db = {row[0]: row[1] for row in c.fetchall()}
    
    movies_imported = 0
    
    for page in range(1, num_pages + 1):
        print(f"Elaborazione pagina {page} di {num_pages}...")
        movies_data = get_movies_from_api(page=page)
        
        if not movies_data or "results" not in movies_data:
            print(f"Nessun dato trovato nella pagina {page}")
            continue
        
        print(f"Trovati {len(movies_data['results'])} film nella pagina {page}")
        
        for movie in movies_data["results"]:
            # Ottieni dettagli completi
            movie_details = get_movie_details(movie["id"])
            if not movie_details:
                continue
            
            # Estrai informazioni del film
            title = movie_details.get("title", "Titolo sconosciuto")
            description = movie_details.get("overview", "")
            if not description:
                description = "Nessuna descrizione disponibile."
            
            # Verifica se il film esiste già
            c.execute("SELECT id FROM films WHERE title = ?", (title,))
            existing = c.fetchone()
            if existing:
                print(f"Film già presente: {title}")
                continue
            
            print(f"Elaborazione film: {title}")
            
            # Gestisci il poster
            poster_path = movie_details.get("poster_path")
            image_filename = download_poster(poster_path) if poster_path else None
            
            # Se non c'è l'immagine, usa un'immagine di default
            if not image_filename:
                image_filename = "default_movie.png"
                default_path = f"static/favicon/{image_filename}"
                if not os.path.exists(default_path):
                    # Crea un'immagine segnaposto se non esiste
                    with open(default_path, "w") as f:
                        f.write("placeholder")
            
            # Trova il regista
            director_name = "Regista sconosciuto"
            if "credits" in movie_details and "crew" in movie_details["credits"]:
                directors = [crew for crew in movie_details["credits"]["crew"] if crew["job"] == "Director"]
                if directors:
                    director_name = directors[0]["name"]
            
            print(f"Regista: {director_name}")
            
            # Inserisci o recupera l'ID del regista
            if director_name in directors_db:
                director_id = directors_db[director_name]
            else:
                c.execute("INSERT INTO directors (name) VALUES (?)", (director_name,))
                director_id = c.lastrowid
                directors_db[director_name] = director_id
                print(f"Nuovo regista inserito: {director_name} con ID {director_id}")
            
            # Inserisci il film
            c.execute(
                "INSERT INTO films (title, description, image, director_id) VALUES (?, ?, ?, ?)",
                (title, description, image_filename, director_id)
            )
            film_id = c.lastrowid
            print(f"Film inserito con ID: {film_id}")
            
            # Associa generi
            genres_added = 0
            if "genres" in movie_details and movie_details["genres"]:
                for genre in movie_details["genres"]:
                    genre_name = genre["name"]
                    
                    # Inserisci o recupera l'ID del genere
                    if genre_name in genres_db:
                        genre_id = genres_db[genre_name]
                    else:
                        c.execute("INSERT INTO genres (name) VALUES (?)", (genre_name,))
                        genre_id = c.lastrowid
                        genres_db[genre_name] = genre_id
                        print(f"Nuovo genere inserito: {genre_name} con ID {genre_id}")
                    
                    # Associa il genere al film
                    try:
                        c.execute(
                            "INSERT INTO film_genres (film_id, genre_id) VALUES (?, ?)",
                            (film_id, genre_id)
                        )
                        genres_added += 1
                    except sqlite3.IntegrityError:
                        print(f"Genere {genre_name} già associato al film {title}")
            else:
                print(f"Nessun genere trovato per il film {title}")
            
            print(f"Associati {genres_added} generi al film {title}")
            
            movies_imported += 1
            print(f"Film importato con successo: {title}")
            
            # Commit ogni 5 film per evitare perdita di dati
            if movies_imported % 5 == 0:
                conn.commit()
                print(f"Commit parziale effettuato dopo {movies_imported} film")
            
            # Piccolo ritardo per evitare troppi request all'API
            time.sleep(0.5)
            
        conn.commit()
        print(f"Commit effettuato dopo la pagina {page}")
    
    print(f"Importazione completata! {movies_imported} film importati.")
    return movies_imported

# Creazione tabelle (aggiunte le tabelle per i registi e generi)
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS directors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    image TEXT,
    director_id INTEGER,
    FOREIGN KEY(director_id) REFERENCES directors(id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS film_genres (
    film_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (film_id, genre_id),
    FOREIGN KEY(film_id) REFERENCES films(id),
    FOREIGN KEY(genre_id) REFERENCES genres(id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    film_id INTEGER,
    user_id INTEGER,
    review TEXT,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    FOREIGN KEY(film_id) REFERENCES films(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Verifica se esiste l'utente admin
c.execute('SELECT COUNT(*) FROM users WHERE username = "admin"')
if c.fetchone()[0] == 0:
    print("Inserimento utente admin...")
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
else:
    print("L'utente admin esiste già nel database, salto l'inserimento.")

# Verifica se ci sono già dei film nel database
c.execute('SELECT COUNT(*) FROM films')
film_count = c.fetchone()[0]
print(f"Ci sono attualmente {film_count} film nel database.")

if film_count == 0:
    # Crea generi e registi predefiniti
    create_default_genres_and_directors()
    
    # Esegui automaticamente l'importazione da TMDB all'avvio
    print("Nessun film trovato nel database. Avvio importazione automatica da TMDB...")
    films_imported = import_movies_from_tmdb(conn, num_pages=2)  # Importa 2 pagine (circa 40 film)
    print(f"Importazione automatica completata: {films_imported} film importati.")
else:
    print("Ci sono già film nel database. L'importazione automatica è stata saltata.")

conn.commit()
conn.close()
print("Database creato e inizializzato con successo!")
