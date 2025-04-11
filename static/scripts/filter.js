document.addEventListener('DOMContentLoaded', function() {
    // Seleziona tutti i pulsanti di filtro per genere
    const filterButtons = document.querySelectorAll('.genre-filter-btn');
    const filmContainer = document.querySelector('#film-container');
    
    // Aggiungi event listener a ciascun pulsante
    filterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Rimuovi la classe 'active' da tutti i pulsanti
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Aggiungi la classe 'active' al pulsante cliccato
            this.classList.add('active');
            
            // Ottieni l'ID del genere dal data attribute
            const genreId = this.dataset.genreId;
            
            // Mostra un indicatore di caricamento
            filmContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Caricamento...</span></div></div>';
            
            // Esegui la richiesta AJAX
            fetch(`/ajax/films${genreId ? '?genre_id=' + genreId : ''}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Errore nel caricamento dei film');
                    }
                    return response.json();
                })
                .then(data => {
                    // Aggiorna la sezione dei film con i nuovi risultati
                    updateFilmDisplay(data.films);
                })
                .catch(error => {
                    console.error('Errore:', error);
                    filmContainer.innerHTML = `<div class="alert alert-danger">Errore nel caricamento dei film: ${error.message}</div>`;
                });
        });
    });
    
    // Funzione per aggiornare la visualizzazione dei film
    function updateFilmDisplay(films) {
        // Cancella il contenitore
        filmContainer.innerHTML = '';
        
        if (films.length === 0) {
            filmContainer.innerHTML = '<div class="alert alert-info">Nessun film trovato per questo genere.</div>';
            return;
        }
        
        // Crea una nuova riga
        const row = document.createElement('div');
        row.className = 'row row-cols-1 row-cols-md-3 g-4';
        
        // Aggiungi ogni film alla riga
        films.forEach(film => {
            const col = document.createElement('div');
            col.className = 'col';
            
            // Prepara il display del punteggio
            let ratingDisplay = '';
            if (film.avg_rating > 0) {
                ratingDisplay = `
                    <span class="badge bg-primary">
                        <i class="bi bi-star-fill"></i> 
                        ${film.avg_rating.toFixed(1)} 
                        (${film.review_count} recensioni)
                    </span>
                `;
            } else {
                ratingDisplay = '<span class="badge bg-secondary">Nessuna recensione</span>';
            }
            
            col.innerHTML = `
                <div class="card h-100">
                    <a href="/film/${film.id}">
                        <img src="/static/favicon/${film.image}" class="card-img-bottom layout-img" alt="${film.title}">
                    </a>
                    <div class="card-body">
                        <h5 class="card-title text-center">${film.title}</h5>
                        <div class="text-center mt-2">
                            <div class="review-score">
                                ${ratingDisplay}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            row.appendChild(col);
        });
        
        // Aggiungi la riga al contenitore
        filmContainer.appendChild(row);
    }
});