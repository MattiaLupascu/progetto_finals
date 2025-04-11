# progetto_finals

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string password
    }
    
    DIRECTORS {
        int id PK
        string name UK
    }
    
    GENRES {
        int id PK
        string name UK
    }
    
    FILMS {
        int id PK
        string title
        string description
        string image
        int director_id FK
    }
    
    FILM_GENRES {
        int film_id PK,FK
        int genre_id PK,FK
    }
    
    REVIEWS {
        int id PK
        int film_id FK
        int user_id FK
        string review
        int rating
    }
    
    USERS ||--o{ REVIEWS : "scrive"
    FILMS ||--o{ REVIEWS : "riceve"
    DIRECTORS ||--o{ FILMS : "dirige"
    FILMS ||--o{ FILM_GENRES : "appartiene a"
    GENRES ||--o{ FILM_GENRES : "categorizza"
```

progetto_finals-1/
├── app.py                 # File principale dell'applicazione Flask
├── database.db            # Database SQLite
├── database_setup.py      # Script per inizializzare il database
├── Er-Diagram.md          # Documentazione del diagramma ER
├── static/
│   ├── favicon/           # Contiene le immagini dei film
│   │   ├── inception.png
│   │   ├── thematrix.png
│   │   ├── interstellar.png
│   │   ├── ...
│   │   └── immaginesottomarino.png
│   └── styles/
│       └── style.css      # Fogli di stile CSS
└── templates/
    ├── layout.html        # Template base per tutte le pagine
    ├── index.html         # Homepage con lista film e filtri per genere
    ├── film.html          # Pagina dettaglio film con recensioni
    ├── director_films.html # Pagina con i film di un regista
    ├── login.html         # Pagina di login
    └── register.html      # Pagina di registrazione