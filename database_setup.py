import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

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

# Inserimento dei generi
genres = [
    ('Azione',),
    ('Commedia',),
    ('Drammatico',),
    ('Fantascienza',),
    ('Horror',),
    ('Thriller',),
    ('Western',),
    ('Romantico',),
    ('Avventura',),
    ('Animazione',)
]
c.executemany('INSERT INTO genres (name) VALUES (?)', genres)

# Inserimento dei registi
directors = [
    ('Christopher Nolan',),
    ('Lana Wachowski',),
    ('James Cameron',),
    ('Francis Ford Coppola',),
    ('Quentin Tarantino',),
    ('David Fincher',),
    ('Robert Zemeckis',),
    ('Frank Darabont',),
    ('Sergio Leone',),
    ('Steven Spielberg',),
    ('Peter Jackson',)
]
c.executemany('INSERT INTO directors (name) VALUES (?)', directors)

# Inserimento dei film con i rispettivi registi
films = [
    ('Inception', "L'inizio di Inception (2010) di Christopher Nolan è intrigante e misterioso...", 'inception.png', 1),
    ('The Matrix', "L'inizio di The Matrix (1999) è un mix di azione e mistero...", 'thematrix.png', 2),
    ('Interstellar', "L'inizio di Interstellar (2014) introduce un futuro distopico...", 'interstellar.png', 1),
    ('Titanic', "L'inizio di Titanic (1997) si svolge nel presente (nel 1996)...", 'titanic.png', 3),
    ('The Godfather', "L'inizio di The Godfather (Il Padrino, 1972) è una delle aperture più iconiche...", 'thegodfather.png', 4),
    ('Pulp Fiction', "L'inizio di Pulp Fiction (1994) di Quentin Tarantino presenta una struttura narrativa...", 'pulpfiction.png', 5),
    ('Fight Club', "All'inizio di Fight Club, il protagonista (che rimane senza nome) è un impiegato insoddisfatto...", 'fightclub.png', 6),
    ('Forrest Gump', "L'inizio di Forrest Gump (1994) è iconico e commovente...", 'forrestgump.png', 7),
    ('The Shawshank Redemption', "L'inizio di The Shawshank Redemption (Le ali della libertà, 1994)...", 'shawshank.png', 8),
    ('The Godfather Part II', "L'inizio di The Godfather Part II (Il Padrino - Parte II, 1974)...", 'godfather2.png', 4),
    ('The Good,the Bad and the Ugly', "L'inizio di The Good, the Bad and the Ugly (Il buono, il brutto, il cattivo, 1966)...", 'goodbadugly.png', 9),
    ('Schindler\'s list', "L'inizio di Schindler's List (1993) è un potente e toccante racconto...", 'schindler.png', 10),
    ('The Dark Knight', "L'inizio di The Dark Knight (2008) è un capolavoro del cinema supereroistico...", 'darkknight.png', 1),
    ('Lord of the Rings: Return of the King', "L'inizio di The Lord of the Rings: The Return of the King (2003)...", 'lotrreturnking.png', 11)
]
c.executemany('INSERT INTO films (title, description, image, director_id) VALUES (?, ?, ?, ?)', films)

# Associazione dei film ai generi
film_genres = [
    (1, 1), (1, 6), (1, 4),  # Inception: Azione, Thriller, Fantascienza
    (2, 1), (2, 4), (2, 6),  # The Matrix: Azione, Fantascienza, Thriller
    (3, 4), (3, 3),          # Interstellar: Fantascienza, Drammatico
    (4, 3), (4, 8),          # Titanic: Drammatico, Romantico
    (5, 3), (5, 6),          # The Godfather: Drammatico, Thriller
    (6, 3), (6, 6), (6, 2),  # Pulp Fiction: Drammatico, Thriller, Commedia
    (7, 3), (7, 6),          # Fight Club: Drammatico, Thriller
    (8, 3), (8, 2),          # Forrest Gump: Drammatico, Commedia
    (9, 3),                  # The Shawshank Redemption: Drammatico
    (10, 3), (10, 6),        # The Godfather Part II: Drammatico, Thriller
    (11, 7), (11, 9),        # The Good,the Bad and the Ugly: Western, Avventura
    (12, 3), (12, 5),        # Schindler's list: Drammatico, Horror
    (13, 1), (13, 6),        # The Dark Knight: Azione, Thriller
    (14, 9), (14, 4)         # Lord of the Rings: Avventura, Fantascienza
]
c.executemany('INSERT INTO film_genres (film_id, genre_id) VALUES (?, ?)', film_genres)

conn.commit()
conn.close()
print("Database creato")
