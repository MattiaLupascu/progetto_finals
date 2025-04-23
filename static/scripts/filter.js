document.addEventListener('DOMContentLoaded', function() {
    // Ottieni tutti i pulsanti del filtro per genere
    const genreButtons = document.querySelectorAll('.genre-filter-btn');
    const searchInput = document.getElementById('film-search');
    const searchButton = document.getElementById('search-btn');
    const searchStatus = document.getElementById('search-status');
    
    // Variabile per tenere traccia del timer per il debounce
    let searchTimer;
    
    // Aggiungi event listener per ogni pulsante di genere
    genreButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Rimuovi la classe 'active' da tutti i pulsanti
            genreButtons.forEach(btn => btn.classList.remove('active'));
            
            // Aggiungi la classe 'active' al pulsante cliccato
            this.classList.add('active');
            
            // Ottieni l'ID del genere dal pulsante
            const genreId = this.getAttribute('data-genre-id');
            
            // Aggiorna l'URL senza ricaricare la pagina
            const url = new URL(window.location.href);
            if (genreId) {
                url.searchParams.set('genre_id', genreId);
            } else {
                url.searchParams.delete('genre_id');
            }
            window.history.pushState({}, '', url);
            
            // Resetta il campo di ricerca
            if (searchInput) searchInput.value = '';
            if (searchStatus) searchStatus.textContent = '';
            
            // Esegui la chiamata AJAX per ottenere i film filtrati
            fetch(`/ajax/films${genreId ? '?genre_id=' + genreId : ''}`)
                .then(response => response.json())
                .then(data => {
                    updateFilmDisplay(data.films);
                })
                .catch(error => {
                    console.error('Error fetching films:', error);
                });
        });
    });

    // Funzione di ricerca films
    function searchFilms(query) {
        if (query.length < 2) {
            searchStatus.textContent = 'Inserisci almeno 2 caratteri per iniziare la ricerca';
            return;
        }
        
        searchStatus.textContent = 'Ricerca in corso...';
        
        fetch(`/ajax/search?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                updateFilmDisplay(data.films);
                searchStatus.textContent = data.status;
                
                // Resetta il filtro per genere attivo
                genreButtons.forEach(btn => btn.classList.remove('active'));
                document.querySelector('.genre-filter-btn[data-genre-id=""]').classList.add('active');
            })
            .catch(error => {
                console.error('Error searching films:', error);
                searchStatus.textContent = 'Errore durante la ricerca';
            });
    }
    
    // Event listener per il pulsante di ricerca
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            if (searchInput) {
                searchFilms(searchInput.value.trim());
            }
        });
    }
    
    // Event listener per la ricerca durante la digitazione (con debounce)
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimer);
            
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchStatus.textContent = 'Inserisci almeno 2 caratteri per iniziare la ricerca';
                return;
            }
            
            // Imposta un timer per evitare troppe richieste durante la digitazione
            searchStatus.textContent = 'Digita per cercare...';
            searchTimer = setTimeout(() => {
                searchFilms(query);
            }, 500); // Aspetta 500ms dopo l'ultima digitazione
        });
        
        // Event listener per il tasto Invio nel campo di ricerca
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                clearTimeout(searchTimer);
                searchFilms(this.value.trim());
            }
        });
    }
    
    // Funzione per aggiornare la visualizzazione dei film
    function updateFilmDisplay(films) {
        const filmContainer = document.getElementById('film-container');
        
        // Se non ci sono film da mostrare
        if (films.length === 0) {
            filmContainer.innerHTML = '<div class="alert alert-info">Nessun film trovato per i criteri specificati.</div>';
            return;
        }
        
        // Crea il contenuto HTML per i film
        let html = '';
        
        films.forEach(film => {
            html += `
                <div class="col">
                    <div class="card h-100">
                        <a href="/film/${film.id}" class="card-img-link">
                            ${film.image ? 
                                `<img src="/static/favicon/${film.image}" class="card-img-top" alt="${film.title}">` : 
                                '<div class="no-image">Nessuna immagine</div>'
                            }
                        </a>
                        <div class="card-body">
                            <h5 class="card-title">${film.title}</h5>
                            <p class="text-muted">${film.director_name}</p>
                            ${film.avg_rating ? 
                                `<div class="rating">
                                    <span class="badge bg-primary">${film.avg_rating.toFixed(1)} ⭐</span>
                                </div>` : 
                                ''
                            }
                        </div>
                    </div>
                </div>
            `;
        });
        
        filmContainer.innerHTML = html;
    }
});