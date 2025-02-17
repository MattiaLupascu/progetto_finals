import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Creazione tabelle
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    image TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    film_id INTEGER,
    user_id INTEGER,
    review TEXT,
    FOREIGN KEY(film_id) REFERENCES films(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Inserimento di 7 film di esempio con immagini locali
# Questi film vengono inseriti nel database. 
# Nota: l'ordine di inserimento determina l'ID.
films = [
    ('Inception', 'Un film che esplora i sogni.', 'inception.png'),
    ('The Matrix', 'Un hacker scopre la realtà simulata.', 'thematrix.png'),
    ('Interstellar', 'Viaggio attraverso lo spazio e il tempo.', 'interstellar.png'),
    ('Titanic', 'Una storia d\'amore a bordo della famosa nave.', 'titanic.png'),
    ('The Godfather', 'La storia di una famiglia mafiosa.', 'thegodfather.png'),
    ('Pulp Fiction', 'Storie intrecciate in un mondo criminale.', 'pulpfiction.png'),
    ('Fight Club', 'Un uomo crea un club segreto di combattimento.', 'fightclub.png')
]
#c.executemany('INSERT INTO films (title, description, image) VALUES (?, ?, ?)', films)

# Tentativo di cancellare i primi 7 film inseriti:
# Questa query dovrebbe cancellare i film con i 7 ID più bassi (quelli appena inseriti).
# Se la cancellazione non funziona, verificare l'ordinamento degli ID e i commit.
c.execute("DELETE FROM films WHERE id IN (SELECT id FROM films ORDER BY id ASC LIMIT 7)")

conn.commit()
conn.close()
print("Database creato e i primi 7 film sono stati cancellati.")
