document.addEventListener('DOMContentLoaded', function() {
    // Ottieni tutti i pulsanti del filtro per genere
    const genreButtons = document.querySelectorAll('.genre-filter-btn');
    
    // Aggiungi event listener per ogni pulsante
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
    
    // Funzione per aggiornare la visualizzazione dei film
    function updateFilmDisplay(films) {
        const filmContainer = document.getElementById('film-container');
        
        // Se non ci sono film da mostrare
        if (films.length === 0) {
            filmContainer.innerHTML = '<div class="alert alert-info">Nessun film trovato per questo genere.</div>';
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